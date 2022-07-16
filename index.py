from encodings import search_function
from hashlib import algorithms_available
import json
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
driver = None
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)

base_url = "http://api-clicker.go-wi.com"

# print('IP Address:')
# base_url = input()

# print('Username:')
# username = input()

# print('Password:')
# password = input()

# sio = socketio.Client()
# sio.connect('http://10.0.10.11:4002', namespaces=['/logs'])
# print('Connection: ', sio)
# @sio.on('connected', namespace='/logs')
# def on_connected():
#     sio.emit('insert-log', {'site_id': 64}, namespace='/logs')
#     sio.disconnect()


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


def fetchSites(token):
    print('Fetching Sites...')
    headers['Authorization'] = "Bearer " + token

    # Fetch datas and display
    try:
        response = requests.get(base_url + "/sites", headers=headers)
        if response.status_code == 200:
            sites = json.loads(response.text)['list']
            start(sites)
            return

        print('Unsuccessfully when fetching sites')
        time.sleep(3)
        fetchSites(token)
    except:
        print('Something went wrong')
        time.sleep(3)
        fetchSites(token)


def fetchCountries():
    headers['Authorization'] = "Bearer " + token

    # Fetch datas and display
    try:
        response = requests.get(base_url + "/countries?filter_by=status&q=enabled", headers=headers)
        if response.status_code == 200:
            return json.loads(response.text)['list']
            # for country in countries:
            #     id = country['id']
            #     country = site['country']
            #     cca2 = site['cca2']
            #     created_at = site['created_at']
            # return cca2

        print('Failed to fetch settings')
        time.sleep(3)
        fetchCountries()
    except:
        print('Something went wrong')
        time.sleep(3)
        fetchCountries()


def login_vpn():
    try:
        windscribe.login('cubicsolutioninc2019', 'Cubic2@19')
        return True
    except Exception as e:
        print(e)
        return False


def connect_vpn():
    countries = ["kr", "cn", "jp"]
    country = random.choice(countries)
    result = os.popen('windscribe connect ' + country).read()
    arr = result.split(' ')
    ip = arr[-1]
    print('VPN Connected IP: ' + ip + country)
    return ip


def sendLog(isUpdate = False, site_tag_id = None, status = None, page = None, s_startedAt = None, s_endedAT = None, ip = '', searchTerm = None):

    if isUpdate:
        payload = {'site_tag_id': site_tag_id, 'status': status, 'page': page, 'finished_at': s_endedAT}

        send_log = requests.patch(base_url + "/logs", headers=headers, json=payload)

        print('Succesfully Updated!', send_log)
        return

    payload = {'site_tag_id': site_tag_id, 'ip': ip, 'term': searchTerm, 'started_at': s_startedAt}
    send_log = requests.post(base_url + "/logs", headers=headers, json=payload)

    print('Succesfully Saved!', send_log)


def checkModalElement():
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//div//button[@id='L2AGLb']")))
        return True
    except (TimeoutException, WebDriverException) as e:
        print("No modal found -----> Processing...")
        return False
    

def close_modal():
    try: 
        driver.find_element(By.XPATH, "//div//button[@id='L2AGLb']").click()

        return True
    except (TimeoutException, WebDriverException) as e:
        return False



def generateDateTime():
    return time.strftime('%Y-%m-%d %H:%M:%S')


def isFoundLink(site):
        
    urls = getUrls()
    
    print(list(filter(bool, map(lambda x: x.text, urls))))
    print(site)
    print('============================')

    for url in urls:
            result = re.search(site, url.text)
            if result != None:
                url.click()
                return True

    return False


def getUrls():

    urls = []
    urls = driver.find_elements(By.XPATH, "//div//cite[@role='text']")

    return urls
    # return list(filter(bool, map(lambda x: x.text, urls)))


def searchInBrowser(term, started_at):
    print('Started at: ', started_at)
    search_query = "https://www.google.com/search?q={q}".format(q=term)
    driver.get(search_query)
    if (checkModalElement()):
        close_modal()


def nextPage(start, end):
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


def bootstrap(site, site_tag_id, _term, startTime, endTime, p_limit, algorithm = None):
    term = _term.lower().strip()

    started_at = generateDateTime()
    current_ip = connect_vpn()
    print(sendLog(isUpdate=False, site_tag_id=site_tag_id, s_startedAt=started_at, ip=current_ip, searchTerm=algorithm))
    ended_at = started_at
    searchInBrowser(term, started_at)

    PAGE_LIMIT = p_limit
    status_result = 'failed'
    page_number = "0"
    for i in range(PAGE_LIMIT):
        page_number = str(i + 1)
        print('Page number: ', page_number)
        if (isFoundLink(site)):
            print("Found it! -----> Link has been clicked\n")
            print('Ended at: ', ended_at)
            print('\n\n')
            status_result = 'success'
            print('success')
            time.sleep(5)
            break

        if (not nextPage(startTime, endTime)):
            break

    ended_at = generateDateTime()
    print(sendLog(isUpdate=True, site_tag_id=site_tag_id, status=status_result, page=page_number, s_endedAT=ended_at))


def start(sites):
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

    print('Settings: \n', 'Start: ', s_start, '\nEnd: ',
              s_end, '\nPage Limit: ', page_limit, '\n')

    # Get the tag names
    for tag_name in tag_names:
        tag_id = tag_name['id']
        site_tag_id = tag_name['site_tag_id']

        algorithms = [
        tag_name['name'],
        site_name,
        tag_name['name'] + ' ' + site_name,
        site_name + ' ' + tag_name['name'],
        ]

        for algorithm in algorithms:
            
            bootstrap(url_handler.replace("https://www.",""), 
                site_tag_id, algorithm, s_start, s_end, page_limit, algorithm)
            print('INFO:\n URL: ', url_handler, '\n Site Name: ', site_name,
            '\n Site Tag ID: ', site_tag_id, '\n Tag Name: \n')


    print('Re-run ----->\n============================\n')
    start(sites)


# Connect to vpn before login
is_logged_in = login_vpn()
if not is_logged_in:
    time.sleep(3)
    login_vpn()

current_ip = connect_vpn()

# Attempt Login
token, status_code = login()

# Check status code login
if status_code != 200:  # if fails, attempt again to relogin
    time.sleep(3)
    login()


print('Logged in successfully \n')
fetchSites(token)
