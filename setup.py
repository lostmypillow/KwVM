import shutil
import os
import requests
import asyncio
import socket
import subprocess

vm_info: dict = {
    'proxmox': 1,
    'user_name':  "lostmypillow",
    'token_name': "lostmypillow",
    'token_value':  "245a4a7a-581f-434d-be48-e393d9578aa0",
    'vm_id':  301,
    'proxy_from':  "pve1.kaowei.tw:3128",
    'proxy_to':  "192.168.2.13:3128", # needed for both
    'password': '' # needed for custom
}


def get_vm_info(hostname: str) -> dict:
    print("[SETUP] Getting vm info...", end="")
    url = "http://192.168.2.32:8005" + '/hostname' + hostname  # Replace with your actual endpoint

    # Send GET request
    response = requests.get(url)

    # Ensure the request was successful (status code 200)
    if response.status_code == 200:
        data: dict = response.json()
        print('ok.')
        return data  
    else:
        print('ERROR!')
        print(f"[ERROR] Status code: {response.status_code}.")
        print(f'[ERROR] Response text: {response.text}.')
        return {}
    # return {
    #     'proxmox': 1,
    #     'user_name':  "lostmypillow",
    #     'token_name': "lostmypillow",
    #     'token_value':  "245a4a7a-581f-434d-be48-e393d9578aa0",
    #     'vm_id':  301,
    #     'proxy_from':  "pve1.kaowei.tw:3128",
    #     'proxy_to':  "192.168.2.13:3128"
    # }


def run_custom_vm():
    full_ip: str = vm_info['proxy_to']
    host = full_ip.split(':')[0]
    port = full_ip.split(':')[1]
    print('[CUSTOM] Opening client.vv file...', end="")
    with open('client.vv', 'r') as file:
        print('done')

        print('[CUSTOM] Reading lines from vdiclient.ini file...', end="")
        lines = file.readlines()
        print('done')

        print(f'[CUSTOM] Replacing host line with {host}...', end="")
        lines[2] = 'host=' + host +  '\n'
        print('done')

        print(f'[CUSTOM] Replacing port line with {port}...', end="")
        lines[3] = 'port=' + port + '\n'
        print('done')

        print(f'[CUSTOM] Replacing password line with {vm_info['password']}...', end="")
        lines[4] = 'password=' + vm_info['password'] + '\n'
        print('done')

    print(f'[CUSTOM] Writing lines to client.vv...', end="")
    with open('client.vv', 'w') as file:
        file.writelines(lines)
    print('done.')

    print(f'[CUSTOM] Starting VM with remote-viewer...')
    # Build the executable
    subprocess.run([
        "remote-viewer",
        "client.vv",
        "-k",
    ], check=True)
    


def run_proxmox_vm():
    source_file = "vdiclient.ini.example"
    destination_file = "vdiclient.ini"

    shutil.copyfile(source_file, destination_file)
    print(f"[PROXMOX] Created {source_file} from {destination_file}.")

    # config_folder = os.path.expanduser("~/.config/VDIClient")
    # final_destination = os.path.join(config_folder, "vdiclient.ini")
    # os.makedirs(config_folder, exist_ok=True)
    # shutil.copyfile(destination_file, final_destination)
    # print(f"Copied {destination_file} to {final_destination}")
    print('[PROXMOX] Opening vdiclient.ini file...', end="")
    with open('vdiclient.ini', 'r') as file:
        print('done')
        print('[PROXMOX] Reading lines from vdiclient.ini file...', end="")
        lines = file.readlines()
        print('done.')
        
        print(f'[PROXMOX] Replacing user line with {vm_info['user_name']}...', end="")
        user_line = lines[43].replace("#", "").split(" ")
        user_line[2] = vm_info['user_name'] + "\n"
        lines[43] = " ".join(str(element) for element in user_line)
        print('done.')

        print(f'[PROXMOX] Replacing token name line with {vm_info['token_name']}...', end="")
        token_name_line = lines[45].replace("#", "").split(" ")
        token_name_line[2] = vm_info['token_name'] + "\n"
        lines[45] = " ".join(str(element) for element in token_name_line)
        print('done.')

        print(f'[PROXMOX] Replacing token value line with {vm_info['token_value']}...', end="")
        token_val_line = lines[47].replace("#", "").split(" ")
        token_val_line[2] = vm_info['token_value'] + "\n"
        lines[47] = " ".join(str(element) for element in token_val_line)
        print('done.')

        print(f'[PROXMOX] Replacing VM ID line with {str(vm_info['vm_id'])}...', end="")
        vmid_line = lines[51].replace("#", "").split(" ")
        vmid_line[2] = str(vm_info['vm_id']) + "\n"
        lines[51] = " ".join(str(element) for element in vmid_line)
        print('done.')

        print(f'[PROXMOX] Activating kiosk mode...', end="")
        lines[10] = 'kiosk = True\n'
        print('done.')

        print(f'[PROXMOX] Filling in main Proxmox URL 192.168.3.32:8006...', end="")
        lines[32] = '               "' + \
            '192.168.3.32' + '" : ' + '8006' + '\n'
        print('done.')
        
        
        
        print(f'[PROXMOX] Filling in proxy_from {vm_info['proxy_from']} to {vm_info['proxy_to']}...', end="")
        lines[86] = vm_info['proxy_from'] + " = " + vm_info['proxy_to'] + '\n'
        print('done.')

    print(f'[PROXMOX] Writing lines to vdiclient.ini...', end="")
    with open('vdiclient.ini', 'w') as file:
        file.writelines(lines)
    print('done.')

    print(f'[PROXMOX] Building executable...')
    cmd = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--noconfirm",
        "--hidden-import", "proxmoxer.backends",
        "--hidden-import", "proxmoxer.backends.https",
        "--hidden-import", "proxmoxer.backends.https.AuthenticationError",
        "--hidden-import", "proxmoxer.core",
        "--hidden-import", "proxmoxer.core.ResourceException",
        "--hidden-import", "subprocess.TimeoutExpired",
        "--hidden-import", "subprocess.CalledProcessError",
        "--hidden-import", "requests.exceptions",
        "--hidden-import", "requests.exceptions.ReadTimeout",
        "--hidden-import", "requests.exceptions.ConnectTimeout",
        "--hidden-import", "requests.exceptions.ConnectionError",
        "vdiclient.py"
    ]

    # Build the executable
    subprocess.run(cmd, check=True)
    print(f'[PROXMOX] Building executable...done.')

    src = "dist/vdiclient"
    dst = os.path.expanduser("~/Desktop/vdiclient")

    print(f'[PROXMOX] Copying executable to Desktop...', end="")
    shutil.copy(src, dst)
    print("done")
    print(f'[PROXMOX] Making executable...executable lol...', end="")
    os.chmod(dst, 0o755)
    print("done")

    subprocess.run([dst])  # Run the file

print('[SETUP] Getting hostname...', end="")
hostname: str = socket.gethostname()
print("ok")

vm_info = get_vm_info(hostname)

if vm_info['proxmox'] == 1:
    try:
        run_proxmox_vm()
    except Exception as e:
        print('[ERROR] Exception thrown when accessing Proxmox VM:')
        print(e)

elif vm_info['proxmox'] == 0:
    try:
        run_custom_vm()
    except Exception as e:
        print('[ERROR] Exception thrown when accessing Custom (non Proxmox) VM:')
        print(e)
else:
    print(
        f'[ERROR] No VM info exists for this computer. Computer name: {hostname}')
