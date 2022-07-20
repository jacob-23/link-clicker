from sys import platform
import subprocess
import sys



def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])



if platform == "linux" or platform == "linux2":

    algorithms = [
        "selenium==4.3.0",
        "python-socketio==5.7.0",
        "python-dotenv==0.20.0",
        "python-windscribe==2020.9.16",
        "webdriver-manager==3.8.0",
        "random2==1.0.1",
        "times2==0.9",
        ]
        
    for algorithm in algorithms:
        install(algorithm)

