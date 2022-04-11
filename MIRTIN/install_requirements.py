import subprocess
import sys
#Short helper script to install dependencies for the project, must have pip and python setup with PATH
#pip install -r requirements.txt
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("Dependencies successfully installed!")
    input("Waiting for input to exit program...")
    quit()
except Exception as e:
    print("ERROR:")
    print(e)
    input("Waiting for input to exit program...")
    quit() 
