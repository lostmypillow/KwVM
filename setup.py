import shutil
import requests
import socket
import subprocess
import json
import os
import sys
from vdiclient import main as start_client
from typing import Literal
import argparse
import glob
import FreeSimpleGUI as sg
vm_info: dict = {
    "vm_name": "Ma VM 1",
    'proxmox': 1,
    'username':  "lostmypillow",
    'token_name': "lostmypillow",
    'token_value':  "245a4a7a-581f-434d-be48-e393d9578aa0",
    'vm_id':  301,
    'proxy_from':  "pve1.kaowei.tw:3128",
    'proxy_to':  "192.168.2.13:3128",  # needed for both
    'password': '',  # needed for custom
    'status_code': 200
}


def check_db(filename: str | None) -> list[dict]:
    try:
        print("[SETUP] Getting vm info...", end="")
        url = "http://192.168.2.32:8005" + '/user/' + filename
        # Send GET request
        # response = requests.get(url)

  
     

        # Ensure the request was successful (status code 200)
        # if response.status_code == 200:
        if 1==1:
            # data: list[dict] = response.json()
            data = [vm_info, {
    "vm_name": "Ma VM 2",
    'proxmox': 1,
    'username':  "lostmypillow",
    'token_name': "lostmypillow",
    'token_value':  "245a4a7a-581f-434d-be48-e393d9578aa0",
    'vm_id':  301,
    'proxy_from':  "pve1.kaowei.tw:3128",
    'proxy_to':  "192.168.2.13:3128",  # needed for both
    'password': '',  # needed for custom
    'status_code': 200
}]
            print('ok.')
            return data
        else:
            print(f'error!')
            print(
                f'[ERROR]\nStatus code: {response.status_code}.\nResponse text: {response.text}.')
            print(f'[ERROR: Request Error] Hostname or username: {filename}')
            sys.exit(1)
    except Exception as e:
        print('error!')
        print(e)
        print(f'[ERROR: General Error] Hostname or username: {filename}')

    # return {
    #     'proxmox': 1,
    #     'username':  "lostmypillow",
    #     'token_name': "lostmypillow",
    #     'token_value':  "245a4a7a-581f-434d-be48-e393d9578aa0",
    #     'vm_id':  301,
    #     'proxy_from':  "pve1.kaowei.tw:3128",
    #     'proxy_to':  "192.168.2.13:3128"
    # }




def setup_custom(type: Literal['login', 'no_login'], vm_info: dict):
    """_summary_

    Parameters
    ----------
    type : Literal[&#39;login&#39;, &#39;no_login&#39;]
        _description_
    """
    file_name = vm_info['vm_name'] + '.vv'
    host = vm_info['proxy_to'].split(':')[0]
    port = vm_info['proxy_to'].split(':')[1]
    print(f'[CUSTOM] Opening {vm_info["vm_name"]}.vv file...', end="")
    with open(file_name, 'r') as file:
        print('done')

        print('[CUSTOM] Reading lines from vdiclient.ini file...', end="")
        lines = file.readlines()
        print('done')

        print(f'[CUSTOM] Replacing host line with {host}...', end="")
        lines[2] = 'host=' + host + '\n'
        print('done')

        print(f'[CUSTOM] Replacing port line with {port}...', end="")
        lines[3] = 'port=' + port + '\n'
        print('done')

        print(
            f'[CUSTOM] Replacing password line with {vm_info["password"]}...', end="")
        lines[4] = 'password=' + vm_info['password'] + '\n'
        print('done')

    print(f'[CUSTOM] Writing lines to {file_name}...', end="")
    with open(file_name, 'w') as file:
        file.writelines(lines)
    print('done.')
    if type == 'no_login':
        create_desktop_file()


def launch_custom():
    subprocess.run([
        "remote-viewer",
        "client.vv",
        "-k",
    ], check=True)


def setup_proxmox():
    source_file = "vdiclient.ini.example"
    destination_file = "vdiclient.ini"

    shutil.copyfile(source_file, destination_file)
    print(f"[PROXMOX] Created {source_file} from {destination_file}.")

    print('[PROXMOX] Opening vdiclient.ini file...', end="")
    with open('vdiclient.ini', 'r') as file:
        print('done')
        print('[PROXMOX] Reading lines from vdiclient.ini file...', end="")
        lines = file.readlines()
        print('done.')

        print(
            f'[PROXMOX] Replacing user line with {vm_info["username"]}...', end="")
        user_line = lines[43].replace("#", "").split(" ")
        user_line[2] = vm_info['username'] + "\n"
        lines[43] = " ".join(str(element) for element in user_line)
        print('done.')

        print(
            f'[PROXMOX] Replacing token name line with {vm_info["token_name"]}...', end="")
        token_name_line = lines[45].replace("#", "").split(" ")
        token_name_line[2] = vm_info['token_name'] + "\n"
        lines[45] = " ".join(str(element) for element in token_name_line)
        print('done.')

        print(
            f'[PROXMOX] Replacing token value line with {vm_info["token_value"]}...', end="")
        token_val_line = lines[47].replace("#", "").split(" ")
        token_val_line[2] = vm_info['token_value'] + "\n"
        lines[47] = " ".join(str(element) for element in token_val_line)
        print('done.')

        print(
            f'[PROXMOX] Replacing VM ID line with {str(vm_info["vm_id"])}...', end="")
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

        print(
            f'[PROXMOX] Filling in proxy_from {vm_info["proxy_from"]} to {vm_info["proxy_to"]}...', end="")
        lines[86] = vm_info['proxy_from'] + " = " + vm_info['proxy_to'] + '\n'
        print('done.')

    print(f'[PROXMOX] Writing lines to vdiclient.ini...', end="")
    with open('vdiclient.ini', 'w') as file:
        file.writelines(lines)
    print('done.')
    # sys.exit(main(os.path.abspath("vdiclient.ini").replace('\\', '/')))

    # print(f'[PROXMOX] Building executable...')
    # cmd = [
    #     "pyinstaller",
    #     "--onefile",
    #     "--noconsole",
    #     "--noconfirm",
    #     "--hidden-import", "proxmoxer.backends",
    #     "--hidden-import", "proxmoxer.backends.https",
    #     "--hidden-import", "proxmoxer.backends.https.AuthenticationError",
    #     "--hidden-import", "proxmoxer.core",
    #     "--hidden-import", "proxmoxer.core.ResourceException",
    #     "--hidden-import", "subprocess.TimeoutExpired",
    #     "--hidden-import", "subprocess.CalledProcessError",
    #     "--hidden-import", "requests.exceptions",
    #     "--hidden-import", "requests.exceptions.ReadTimeout",
    #     "--hidden-import", "requests.exceptions.ConnectTimeout",
    #     "--hidden-import", "requests.exceptions.ConnectionError",
    #     "vdiclient.py"
    # ]

    # # Build the executable
    # subprocess.run(cmd, check=True)
    # print(f'[PROXMOX] Building executable...done.')

    # src = "dist/vdiclient"
    # dst = os.path.expanduser("~/Desktop/vdiclient")

    # print(f'[PROXMOX] Copying executable to Desktop...', end="")
    # shutil.copy(src, dst)
    # print("done")
    # print(f'[PROXMOX] Making executable...executable lol...', end="")
    # os.chmod(dst, 0o755)
    # print("done")

    # subprocess.run([dst])  # Run the file


def needs_update(new_vm_info: dict):  # Get data from DB

    if os.path.exists(new_vm_info["vm_name"] + '.tmp'):
        with open(filename + '.tmp', 'r') as file:
            old_vm_info = file.read().strip()
            return old_vm_info != new_vm_info
    else:
        with open(filename + '.tmp', 'w') as file:
            json.dump(new_vm_info, file)
        return False 
    # True if old data is not up to date, False if it's the same


def compare(list_of_vms: list):
    vms_to_modify = []
    root_path = os.getcwd()  # Get script's directory
    desktop_path = os.path.expanduser("~/Desktop")

    # Get all .tmp files in the root directory
    tmp_files = set(glob.glob(os.path.join(root_path, "*.tmp")))
    valid_tmp_files = set(os.path.join(root_path, vm["vm_name"] + ".tmp") for vm in list_of_vms)
    print(valid_tmp_files)

    # If there are .tmp files to delete
    if tmp_files - valid_tmp_files:
        for file in tmp_files - valid_tmp_files:
            os.remove(file)
            print(f"[SETUP] Deleted unused .tmp file: {file}")
    else:
        print("[SETUP] No unused .tmp files to delete.")

    # Get all .desktop files on Desktop
    desktop_files = set(glob.glob(os.path.join(desktop_path, "*.desktop")))
    valid_desktop_files = set(os.path.join(desktop_path, vm["vm_name"] + ".desktop") for vm in list_of_vms)

    # If there are .desktop files to delete
    if desktop_files - valid_desktop_files:
        for file in desktop_files - valid_desktop_files:
            os.remove(file)
            print(f"[SETUP] Deleted unused .desktop file: {file}")
    else:
        print("[SETUP] No unused .desktop files to delete.")

    # Check and update .tmp files
    for vm in list_of_vms:
        tmp_path = os.path.join(root_path, vm["vm_name"] + ".tmp")
        if os.path.exists(tmp_path):
            with open(tmp_path, "r") as file:
                old_vm_info = file.read().strip()
                if old_vm_info != json.dumps(vm):  # Ensure correct comparison
                    vms_to_modify.append(vm)
        else:
            with open(tmp_path, "w") as file:
                json.dump(vm, file)
            vms_to_modify.append(vm)

    # Return None if no changes were made
    if not vms_to_modify:
        print("[SETUP] No changes to .tmp files.")
        return None

    return vms_to_modify


# def setup(username: str = None):

    # compare info


# setup()

def handle_login():
    username = ''
    sg.theme('SystemDefaultForReal')

    layout = [
        [
            sg.Text(
                '歡迎! 請登入~',
                font=('Arial', 36),
                justification='center'
            )
        ],
        [
            sg.Text(
                '員工編號:',
                font=('Arial', 24)
            ),
            sg.InputText(
                key='-USERNAME-',
                font=('Arial', 24),
                size=(6, 1)
            ),
            sg.Button(
                '登入',
                disabled=True,
                font=('Arial', 24),
                key='-LOGIN-')
        ],

    ]

    window = sg.Window(
        '高偉虛擬機登入 (KwVDI)',
        layout,
        icon='logo.ico',
        return_keyboard_events=True)

    while True:
        event, values = window.read()

        # Enable the button if the input field is not empty
        if values['-USERNAME-']:
            window['-LOGIN-'].update(disabled=False)
        elif values['-USERNAME-'] == '':
            window['-LOGIN-'].update(disabled=True)

        # Event handling
        if event in ('Submit', '\r'):
            if values['-USERNAME-'] != '':
                username = values['-USERNAME-']
                break
        elif event == sg.WIN_CLOSED:
            break

    window.close()
    return username if username != '' else None


def clean_desktop():
    desktop_path = os.path.expanduser("~/Desktop")
    for file in glob.glob(os.path.join(desktop_path, "*.desktop")):
        if os.path.basename(file) != "Login.desktop":
            os.remove(file)
            print(f"Deleted: {file}")
    print("Cleanup complete.")



def add_desktop_file(vm_name: str, content: str):
    desktop_path = os.path.expanduser("~/Desktop")
    desktop_file_path = os.path.join(desktop_path, f"{vm_name}.desktop")

    # Overwrite the file if it exists
    with open(desktop_file_path, 'w') as file:
        file.write(content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="KwVDI script")

    # Add optional -l or --login argument (no value expected)
    parser.add_argument('-l', '--login', action='store_true',
                        help='Trigger login window')
    parser.add_argument('-n','--name', type=str, help="Name of VM for a given desktop, -n my_vm , for example")

    args = parser.parse_args()

    if args.login:
        filename = handle_login()
    else:
        filename = socket.gethostname()

    print(f'[KWVDI] Launching VM for {filename}')

    
    vms_to_modify = compare(check_db(filename))
    if vms_to_modify:
        for vm in vms_to_modify:
            if vm_info['proxmox'] == 1:
                try:
                    setup_proxmox()
                except Exception as e:
                    print('[ERROR] Exception thrown when setting up Proxmox VM:')
                    print(e)

            elif vm_info['proxmox'] == 0:
                try:
                    setup_custom(vm_info)
                except Exception as e:
                    print(
                        '[ERROR] Exception thrown when setting up Custom (non Proxmox) VM:')
                    print(e)
            else:
                print(
                    f'[ERROR] proxmox value is not either 0 or 1. WTF did you do? The DB even has a constraint making it sure it gets either 0 or 1. No VM info exists for this computer.')
