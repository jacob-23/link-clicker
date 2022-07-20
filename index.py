import json
import site
import requests
import time
import random
import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import windscribe
import socketio
from dotenv import load_dotenv

load_dotenv()

# mobile_emulation = {
#     "deviceMetrics": { "width": 360, "height": 640, "pixelRatio": 3.0 },
#     "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"
#     }
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument("start-maximized")
options.add_argument("--disable-infobars")
options.add_argument("--disable-extensions")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.headless = True
# options.add_experimental_option("mobileEmulation", mobile_emulation)



# Install Chrome Webdrive
# driver = None
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)

# base_url = "http://api-clicker.go-wi.com"


base_url = os.environ.get("BASE_URL")
token = os.environ.get("TOKEN")

params = {
    "username": "admin",
    "password": "password123"
}

headers = {
    "accept": "application/json",
    "Content-Type": "application/json",
}


current_ip = ''
searchTerm = ''
countries = []
country_id = None

def login():
    try:
        response = requests.post(
            base_url + "/admins/login", headers=headers, data=json.dumps(params))
        token = json.loads(response.text)['token']
        status_code = response.status_code

        return token, status_code
    except:
        print('Something went wrong')
        time.sleep(3)
        login()


def fetch_sites():
    headers['Authorization'] = "Bearer " + token

    # Fetch datas and display
    try:
        response = requests.get(base_url + "/sites", headers=headers)
        if response.status_code == 200:
            sites = json.loads(response.text)['list']
            start_up(sites)
            return

        print('Failed to fetch sites')
        time.sleep(3)
        fetch_sites()
    except:
        print('Something went wrong when fetching sites')
        time.sleep(3)
        fetch_sites()


def fetch_countries():
    headers['Authorization'] = "Bearer " + token

    # Fetch datas and display
    try:
        response = requests.get(base_url + "/countries?filter_by=status&q=enabled", headers=headers)
        list = json.loads(response.text)['list']
        for country in list:
            countries.append(country)

        print("Countries has been successfully fetched.")
    except:
        print('Something went wrong when fetching countries')
        time.sleep(3)
        fetch_countries()


def login_vpn():
    try:
        username = os.environ.get("WINDSCRIBE_USERNAME")
        password = os.environ.get("WINDSCRIBE_PASSWORD")

        windscribe.login(username, password)
        return True
    except Exception as e:
        # print(e)
        return False


def connect_vpn():
    os.system('windscribe disconnect')

    country = random.choice(countries)
    
    result = os.popen('windscribe connect ' + country['code']).read()

    arr = result.split(' ')
    ip = arr[-1]
    filtered_characters = list(s for s in ip if s.isprintable())
    filtered_ip = ''.join(filtered_characters)

    is_not_valid = re.search('is not a valid location', result)
    if is_not_valid or (filtered_ip == 'location'):
        print(country['name'] + ' is not a valid location. Reconnecting other country...')
        connect_vpn()

    # location = arr[2] + ' ' + arr[3]
    print('VPN Connected IP: ' + ip + ' ' + country['name'])
    return ip, country['id']


def send_log(is_update = False, site_tag_id = None, status = None, page = None, s_startedAt = None, s_endedAT = None, ip = '', searchTerm = None, country_id = None):

    if is_update:
        payload = {'site_tag_id': site_tag_id, 'status': status, 'page': page, 'finished_at': s_endedAT}

        send_log = requests.patch(base_url + "/logs", headers=headers, json=payload)

        print('Succesfully Updated!')
        return

    payload = {'site_tag_id': site_tag_id, 'country_id': country_id, 'ip': ip, 'term': searchTerm, 'started_at': s_startedAt}

    send_log = requests.post(base_url + "/logs", headers=headers, json=payload)

    print('Succesfully Saved!')


def check_modal_element():
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//div//button[@id='L2AGLb']")))
        return True
    except (TimeoutException, WebDriverException) as e:
        # print("No modal found -----> Processing...")
        return False
    

def close_modal():
    try: 
        driver.find_element(By.XPATH, "//div//button[@id='L2AGLb']").click()

        return True
    except (TimeoutException, WebDriverException) as e:
        return False



def generate_date_time():
    return time.strftime('%Y-%m-%d %H:%M:%S')


def is_found_link(site):
        
    urls = get_urls()
    
    # print(list(filter(bool, map(lambda x: x.text, urls))))
    print(site)

    for url in urls:
            result = re.search(site, url.text)
            if result != None:
                url.click()
                return True

    return False


def get_urls():

    urls = []
    urls = driver.find_elements(By.XPATH, "//div//cite[@role='text']")

    return urls
    # return list(filter(bool, map(lambda x: x.text, urls)))


def search_in_browser(term, started_at):
    search_query = "https://www.google.com/search?q={q}".format(q=term)
    driver.get(search_query)
    if (check_modal_element()):
        close_modal()


def next_page(start, end):
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//tbody//tr//td//a[@id='pnnext']")))
        
        # Delay search time based from the admin settings
        # ...pick a random number between the start and end 
        randomNum = random.randint(start, end)
        time.sleep(randomNum)
        print("next page -----> Delay time: ", randomNum)

        driver.find_element(By.XPATH, "//tbody//tr//td//a[@id='pnnext']").click()
        
        return True
    except (TimeoutException, WebDriverException) as e:
        print("Last page reached")
        return False


def boot_strap(site, site_tag_id, _term, startTime, endTime, p_limit, algorithm = None):
    term = _term.lower().strip()

    started_at = generate_date_time()
    current_ip, country_id = connect_vpn()

    print(send_log(is_update=False, site_tag_id=site_tag_id, s_startedAt=started_at, ip=current_ip, searchTerm=algorithm, country_id=country_id))
    ended_at = started_at
    search_in_browser(term, started_at)

    PAGE_LIMIT = p_limit
    status_result = 'failed'
    page_number = "0"
    for i in range(PAGE_LIMIT):
        page_number = str(i + 1)
        print('Page number: ', page_number)
        if (is_found_link(site)):
            print("Found it! -----> Link has been clicked\n")
            status_result = 'success'
            time.sleep(5)
            break

        if (not next_page(startTime, endTime)):
            break

    ended_at = generate_date_time()
    print(send_log(is_update=True, site_tag_id=site_tag_id, status=status_result, page=page_number, s_endedAT=ended_at))
    print('============================')


def start_up(sites):
    for site in sites:
        id = site['id']
        site_name = site['name']
        url_handler = site['url']
        api = site['api']
        tag_names = site['tags']
        settings = site['settings']
        created_at = site['created_at']

    s_start = settings['start']
    s_end = settings['end']
    page_limit = settings['page_limit']

    # Get the tag names
    for tag_name in tag_names:
        tag_id = tag_name['id']
        site_tag_id = tag_name['site_tag_id']

        algorithms = [
        tag_name['name'],
        tag_name['name'] + ' ' + site_name,
        site_name + ' ' + tag_name['name'],
        ]

        for algorithm in algorithms:
            
            boot_strap(url_handler.replace("https://www.",""), 
                site_tag_id, algorithm, s_start, s_end, page_limit, algorithm)
            time.sleep(30)


    print('Re-run -----> ============================\n')
    start_up(sites)


# Activate this when using live
# Connect to vpn before login
is_logged_in = login_vpn()
if not is_logged_in:
    time.sleep(3)
    login_vpn()


fetch_countries()

# For Local
# current_ip = '192.168.142.128'

# Active this when using Live
current_ip, country_id = connect_vpn()

# # Attempt Login
# token, status_code = login()

# # Check status code login
# if status_code != 200:  # if fails, attempt again to relogin
#     time.sleep(3)
#     login()


# print('Logged in successfully \n')
fetch_sites()