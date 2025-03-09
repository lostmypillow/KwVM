import shutil
import requests
import socket
import subprocess
import json
import os
import sys
from typing import Literal
import argparse
import glob
import FreeSimpleGUI as sg
from pprint import pprint
from vdiclient import main as launch_proxmox
import tempfile
import pkg_resources
import keyboard


G = {'__module__': 'vdiclient', 'spiceproxy_conv': {}, 'proxmox': ProxmoxAPI (https backend for https://192.168.2.13:8006/api2/json), 'icon': 'logo.ico', 'vvcmd': 'C:\\Program Files\\VirtViewer v11.0-256\\bin\\remote-viewer.exe', 'scaling': 1, 'inidebug': False, 'addl_params': None, 'imagefile': 'logo.png', 'kiosk': False, 'viewer_kiosk': True, 'fullscreen': True, 'show_reset': False, 'show_hibernate': False, 'current_hostset': 'PVE', 'title': 'VDI Login', 'hosts': {'PVE': {'hostpool': [{'host': '192.168.2.13', 'port': 8006}], 'backend': 'pve', 'user': 'lostmypillow', 'token_name': 'lostmypillow', 'token_value': '245a4a7a-581f-434d-be48-e393d9578aa0', 'totp': False, 'verify_ssl': False, 'pwresetcmd': None, 'auto_vmid': 301, 'knock_seq': []}}, 'theme': 'LightBlue', 'guest_type': 'both', 'width': None, 'height': None, }


ini = """
[virt-viewer]
secure-attention = Ctrl+Alt+Ins
title = VM 301 - Win10-01
password = 925cc69bfbac5d5f34e57366551c9af757a3e732
host = pvespiceproxy:67cd5f74:301:pve1::19de4ce524b4e7fadc0ca57cf8d2f8303eb1adb9
type = spice
toggle-fullscreen = Shift+F11
delete-this-file = 1
host-subject = OU=PVE Cluster Node,O=Proxmox Virtual Environment,CN=pve1.kaowei.tw
release-cursor = Ctrl+Alt+R
proxy = http://pve1.kaowei.tw:3128
tls-port = 61001
ca = -----BEGIN CERTIFICATE-----\nMIIFzTCCA7WgAwIBAgIUZ54fcnkh478K3ENrQPmNOtBxDA8wDQYJKoZIhvcNAQEL\nBQAwdjEkMCIGA1UEAwwbUHJveG1veCBWaXJ0dWFsIEVudmlyb25tZW50MS0wKwYD\nVQQLDCRiMzgwMWRlYy0zYTFjLTRhM2ItYTRkNi1kYmU0MmU1OGUwNDUxHzAdBgNV\nBAoMFlBWRSBDbHVzdGVyIE1hbmFnZXIgQ0EwHhcNMjMwMzA1MjAwMDQ4WhcNMzMw\nMzAyMjAwMDQ4WjB2MSQwIgYDVQQDDBtQcm94bW94IFZpcnR1YWwgRW52aXJvbm1l\nbnQxLTArBgNVBAsMJGIzODAxZGVjLTNhMWMtNGEzYi1hNGQ2LWRiZTQyZTU4ZTA0\nNTEfMB0GA1UECgwWUFZFIENsdXN0ZXIgTWFuYWdlciBDQTCCAiIwDQYJKoZIhvcN\nAQEBBQADggIPADCCAgoCggIBALhzlTQ6JOhem+JgqzaSUlGio4ce/l1A9uZ1DXM4\nbouqyvAYIpl/BK+GazT9FvbNwnW6D9oBr6jNYnzQ42nKEOGQ2wPuKEFfBs909j8T\nStxXU7Bibj4NieatNkFx1ngOH7xSB3wYwIhkGD8LUJtp5/vgKb2wfp3s+v0MzcXQ\nvUx2C/oj9hhO0hDbOpEjzV7zhKgoeHam7AqmNgYCc9BIY6G3MDlzjwIG2FfTIqwA\n7brKW48LZpHgfay5mVmG5RMPsWpLbNXybfrwKvZjeD3QkzklKnrGn5aPoDd2CNUC\nOZrIArhVKsDlaXP9t+NiuvWS1WvNJrBbPin7uwM1GJOK1q51HlisyYns6xJNB3sZ\n9e37ZP7BIEzorm+N0wFoVp8I15hrMGxtc+zfKR/RNS7znccXdsZn1A6LxolAHwDR\nBXKfNQ4dKe/RkSh4a6zavy+9MPfMtkBf9Kp0ZLc3dtpO0aGAeDdkJyhE1Oj6Ne3R\ntHHATJ0RUOCEr1k5iEJPbDQnoWm2q2mIQOXaK+NBEmxyU+t2/FWjeP9qo6MISzJq\nMLhufVZjZC01enqxoDForAxYPJ1usi2Kn1pVtrHTZNzpSqCGIT/bEl2+gIIGPfat\nsx/l5izLe2e8zOEdiOqjoA7GRdVppzPcsmRi/5OpUfTf6tO7WKeQ5p082heyQw/W\nV7/rAgMBAAGjUzBRMB0GA1UdDgQWBBTbviPekcqWRexRX9tUsHVQkiv2pTAfBgNV\nHSMEGDAWgBTbviPekcqWRexRX9tUsHVQkiv2pTAPBgNVHRMBAf8EBTADAQH/MA0G\nCSqGSIb3DQEBCwUAA4ICAQAPD38CT/1Xbh+XUFV31UbV0DG7l6lSvzEXlIXIljdX\nJW3OzMwdzjFCEah2RumrlZJ1NmfFiVonQnMHfH47pMr3sh5mQDEcirVh30zpGyRK\nFLAJktAofPFHgCCMz/4fqAx07Qrle5v2dehl674z98S8KGzimUfPd9dz7KawGNUi\nF2omGqx1ELA1G0tzorZNTNibLIdo/UfvBCX3DsyztaKf0Oy7CVmfRZ8VnsKtHUtp\nHsbNT8sz+mxzS/JTLORIdt23wdZIe9TcnXIV8f9Qwq0Cmm5E1JCejoFpWnwU5y4W\ncH2xo/NQ5KUcUZr+hoLI9CGY1e3+RyDHVsX9vdt463Ih61LWfDgjxSEYmE3j71D0\nolJWAKrSENyu9U/VwcYQ+z8iCzBlt08M+iIAvK+5lQaPxoHWinDYq/FbduxBMd+G\nJF0KUZYKBA5IMb2WtzvhmaSPdhFJ22TTszIPLibbWN2F9ZGKI5dR68WwoRQRrqBZ\n71fI1kCZ9z5d3fdEA9PVX+y9g6BKQqVPBgdIv8d10ZAJX7kHmvUfcOKYC1/+bnAP\nZI0bGe1dpKaO6N6AhRrLeyjCwztRJHwkcVb9Fz441BMDiYZM+fvcmmje3BeapvmW\nu+jRbs2/2HkitDS8TwqXJ7406S2FVTa4jgWID8zHUQLeun0KFfCqDB2gMhEY+SQu\ndg==\n-----END CERTIFICATE-----\n

"""

version='0.0.1'

config_folder_path = os.path.abspath('./kwvm_files')
os.makedirs(config_folder_path, exist_ok=True)


def extract_bundled_resource(resource_name):
    """
    Extracts a resource (e.g., an image) from the bundled executable or source
    to a predefined directory if it doesn't already exist.

    :param resource_name: The name of the resource (e.g., 'icon.png')
    :param target_dir: The directory where the resource should be stored
    :param target_filename: The filename to use when storing the extracted resource
    :return: The path to the extracted resource
    """
    # Ensure the target directory exists

    # Define the full path where the resource should be stored
    resource_path = os.path.join(config_folder_path, resource_name)

    # If the resource doesn't exist in the predefined directory, extract it from the bundled executable
    if not os.path.exists(resource_path):
        if getattr(sys, 'frozen', False):
            print('Extracting from exec')
            # If running from a bundled executable, extract the resource
            with open(resource_path, 'wb') as resource_file:
                resource_file.write(pkg_resources.resource_string(
                    __name__, resource_name))  # Extract from the bundle
        else:
            print('Running from source')
            # If running from source, copy the resource from the current directory
            shutil.copy(resource_name, resource_path)

    return resource_path


actual_api_info = [{'created_at': '2025-03-05T19:15:40.063970',
                    'human_owner': '201350',
                    'id': 1,
                    'pc_owner': None,
                    'pve': True,
                    'pve_proxy': 'pve1.kaowei.tw:3128',
                    'pve_token_name': 'lostmypillow',
                    'pve_token_username': 'lostmypillow',
                    'pve_token_value': '245a4a7a-581f-434d-be48-e393d9578aa0',
                    'pve_vm_id': 301,
                    'spice_proxy': '192.168.2.13:3128',
                    'updated_at': '2025-03-05T19:40:38.287552',
                    'vm_name': 'Win10Max',
                    'vm_password': None}]


def check_db(vm_owner: str) -> list[dict]:
    try:
        print("[SETUP] Getting vm info...", end="")
        url = "http://localhost:8000/vm/" + vm_owner
        # Send GET request
        response = requests.get(url)

        # Ensure the request was successful (status code 200)
        if response.status_code == 200:
            # if 1 == 1:
            data: list[dict] = response.json()
#

            return data
        else:
            print(f'error!')
            print(
                f'[ERROR]\nStatus code: {response.status_code}.\nResponse text: {response.text}.')
            print(f'[ERROR: Request Error] Hostname or username: {vm_owner}')
            sys.exit(1)
    except Exception as e:
        print('error!')
        print(e)
        print(f'[ERROR: General Error] Hostname or username: {vm_owner}')

    # return {
    #     'proxmox': 1,
    #     'username':  "lostmypillow",
    #     'token_name': "lostmypillow",
    #     'token_value':  "245a4a7a-581f-434d-be48-e393d9578aa0",
    #     'vm_id':  301,
    #     'proxy_from':  "pve1.kaowei.tw:3128",
    #     'proxy_to':  "192.168.2.13:3128"
    # }

# Custom VM logic START


def setup_custom(vm_info: dict) -> str:
    owner: str = vm_info["human_owner"] if vm_info["human_owner"] else vm_info["pc_owner"]
    filename: str = owner + '_' + vm_info["vm_name"] + '.vv'
    shutil.copyfile(os.path.join(os.getcwd(), "client.vv.example"),
                    os.path.join(config_folder_path, filename))
    host: str = vm_info['spice_proxy'].split(':')[0]
    port: str = vm_info['spice_proxy'].split(':')[1]

    print(f'[CUSTOM] Opening {filename}...', end="")
    with open(os.path.join(config_folder_path, filename), 'r') as file:
        print('done')
        print(f'[CUSTOM] Reading lines from {filename}...', end="")
        lines = file.readlines()
        print('done')

        print(f'[CUSTOM] Replacing host line with {host}...', end="")
        lines[2] = 'host=' + host + '\n'
        print('done')

        print(f'[CUSTOM] Replacing port line with {port}...', end="")
        lines[3] = 'port=' + port + '\n'
        print('done')

        print(
            f'[CUSTOM] Replacing password line with {vm_info["vm_password"]}...', end="")
        lines[4] = 'password=' + vm_info['vm_password'] + '\n'
        print('done')

        print(f'[CUSTOM] Writing lines to {filename}...', end="")
        with open(os.path.join(config_folder_path, filename), 'w') as file:
            file.writelines(lines)
        print('done.')
        return os.path.join(config_folder_path, filename)


def launch_custom(file_path):
    print("[CUSTOM] Running command: remote-viewer " + file_path)
    virt_process = subprocess.Popen(["remote-viewer", "-k", file_path])
    try:
        print("Running virt-viewer in kiosk mode. Press 'Esc' to exit.")
        while True:
            if keyboard.is_pressed('ctrl+shift+f11'):  # Change this to any key you want
                print("Exit key pressed, closing virt-viewer.")
                virt_process.terminate()  # Terminate the virt-viewer process
                break
    except KeyboardInterrupt:
        print("Process interrupted.")
        virt_process.terminate()
# Custom VM logic END


def setup_proxmox(vm_info):
    owner: str = vm_info["human_owner"] if vm_info["human_owner"] else vm_info["pc_owner"]
    filename: str = owner + '_' + vm_info["vm_name"] + '.ini'
    file_path = os.path.join(config_folder_path, filename)
    shutil.copyfile(os.path.join(os.getcwd(), "vdiclient.ini.example"), file_path)

    print(f'[PROXMOX] Opening {filename}...', end="")
    with open(file_path, 'r') as file:
        print('done')
        print(f'[PROXMOX] Reading lines from {filename}...', end="")
        lines = file.readlines()
        print('done.')

        print(
            f'[PROXMOX] Replacing user line with {vm_info["pve_token_username"]}...', end="")
        user_line = lines[43].replace("#", "").split(" ")
        user_line[2] = vm_info['pve_token_username'] + "\n"
        lines[43] = " ".join(str(element) for element in user_line)
        print('done.')

        print(
            f'[PROXMOX] Replacing token name line with {vm_info["pve_token_name"]}...', end="")
        token_name_line = lines[45].replace("#", "").split(" ")
        token_name_line[2] = vm_info['pve_token_name'] + "\n"
        lines[45] = " ".join(str(element) for element in token_name_line)
        print('done.')

        print(
            f'[PROXMOX] Replacing token value line with {vm_info["pve_token_value"]}...', end="")
        token_val_line = lines[47].replace("#", "").split(" ")
        token_val_line[2] = vm_info['pve_token_value'] + "\n"
        lines[47] = " ".join(str(element) for element in token_val_line)
        print('done.')

        print(
            f'[PROXMOX] Replacing VM ID line with {str(vm_info["pve_vm_id"])}...', end="")
        vmid_line = lines[51].replace("#", "").split(" ")
        vmid_line[2] = str(vm_info['pve_vm_id']) + "\n"
        lines[51] = " ".join(str(element) for element in vmid_line)
        print('done.')

        # print(f'[PROXMOX] Activating kiosk mode...', end="")
        # lines[10] = 'kiosk = True\n'
        # print('done.')

        print(f'[PROXMOX] Filling in main Proxmox URL 192.168.2.13:8006...', end="")
        lines[32] = '               "' + \
            '192.168.2.13' + '" : ' + '8006' + '\n'
        print('done.')

        print(
            f'[PROXMOX] Filling in proxy_from {vm_info["pve_proxy"]} to {vm_info["spice_proxy"]}...', end="")
        # lines[86] = vm_info['pve_proxy'] + \
        #     " = " + vm_info['spice_proxy'].split(':')[0] + '\n'
        print('done.')

    print(f'[PROXMOX] Writing lines to {filename}...', end="")
    with open(file_path, 'w') as file:
        file.writelines(lines)
    print('done.')
    return file_path




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



def handle_login():
    username = ''
    sg.theme('SystemDefaultForReal')

    layout = [
        [
            sg.Text(
                '請登入',
                font=('Arial', 24),
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
                font=('Arial', 24),
                key='-LOGIN-')
        ],

    ]
    window = sg.Window(
        '高偉虛擬機',
        layout=layout,
        icon='logo.ico',
        finalize=True,
        return_keyboard_events=True,
        element_padding=(10, 5))
    window['-USERNAME-'].bind("<Return>", "_Enter")

    while True:
        event, values = window.read()
        print(event)
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "-USERNAME-" + "_Enter":
            username = values['-USERNAME-']
            break
        elif event == "F11:122":
            print("I hear you")
    window.close()
    return username if username != '' else None


def handle_vm_selection(vms):
    sg.theme('SystemDefaultForReal')

# Create layout with buttons based on list items
    layout = [[
        sg.Text(
            '請選擇虛擬機',
            font=('Arial', 24),
            justification='center'
        )
    ],]
    for vm in vms:
        layout.append([sg.Button(vm["vm_name"], size=(
            20, 2), key=vm["id"], font=("Arial", 12))])
# Create the window
    window = sg.Window('高偉虛擬機', layout=layout,
                       icon='logo.ico',  element_padding=(10, 5))

    selected_value = None
    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break

        if event:
            selected_value = event
            break  # Exit the loop upon selection

    window.close()

# Output the selected value
    if selected_value:
        return next((item for item in vms if item['id'] == selected_value), None)


def clean_desktop():
    desktop_path = os.path.expanduser("~/Desktop")
    for file in glob.glob(os.path.join(desktop_path, "*.desktop")):
        if os.path.basename(file) != "Login.desktop":
            os.remove(file)
            print(f"Deleted: {file}")
    print("Cleanup complete.")


def create_desktop_file(type, filename, name, exec_command, ):

    # Prepare the content for the .desktop file
    content = f"""
[Desktop Entry]
Version=0.0.
Name={filename.split('.')[0]}
Exec={exec_command}
Type=Application
Terminal=false
Icon={extract_bundled_resource('WIN.png')}
"""

    # Write the content to the .desktop file
    with open(filename, 'w') as f:
        f.write(content.strip())

    # Set the file permissions to be executable
    os.chmod(filename, 0o755)

    print(f"Created {filename}")
    return


if __name__ == "__main__":

    if not os.path.exists(config_folder_path):
        os.makedirs(config_folder_path)

    parser = argparse.ArgumentParser(
        description="KwVM script")

    # Add optional -l or --login argument (no value expected)
    parser.add_argument('-l', '--login', action='store_true',
                        help='Trigger login window')

    args = parser.parse_args()
    selected_vms: list = []
    username = handle_login() if args.login else socket.gethostname()
    list_of_vms = check_db(username)
    selected_vms = [handle_vm_selection(list_of_vms)] if args.login and len(
        list_of_vms) > 1 else list_of_vms
    for vm in selected_vms:
        file_path = setup_proxmox(
            vm) if vm["pve"] == True else setup_custom(vm)
        if selected_vms[0]["pve"] == True:
            if args.login:
                launch_proxmox(config_location=file_path)
            else:
                pass
                # create proxmox desktop
        else:
            if args.login:
                launch_custom(file_path=file_path)
            else:
                pass
                # create custom desktop
