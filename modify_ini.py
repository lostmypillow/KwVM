import shutil
import os
from database.async_operations import async_engine, exec_sql
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
    'proxy_to':  "192.168.2.13:3128"
}


async def get_vm_info():
    print("getting vm info...")
    # global hostname
    # print(hostname)
    if async_engine:
        await async_engine.dispose()


def run_custom():
    pass


def run_proxmox():
    source_file = "vdiclient.ini.example"
    destination_file = "vdiclient.ini"

    shutil.copyfile(source_file, destination_file)
    print(f"Created {source_file} from {destination_file}")

    # config_folder = os.path.expanduser("~/.config/VDIClient")
    # final_destination = os.path.join(config_folder, "vdiclient.ini")
    # os.makedirs(config_folder, exist_ok=True)
    # shutil.copyfile(destination_file, final_destination)
    # print(f"Copied {destination_file} to {final_destination}")
    
    with open('vdiclient.ini', 'r') as file:
        lines = file.readlines()
        user_line = lines[43].replace("#", "").split(" ")
        user_line[2] = vm_info['user_name'] + "\n"
        token_name_line = lines[45].replace("#", "").split(" ")
        token_name_line[2] = vm_info['token_name'] + "\n"
        token_val_line = lines[47].replace("#", "").split(" ")
        token_val_line[2] = vm_info['token_value'] + "\n"
        vmid_line = lines[51].replace("#", "").split(" ")
        vmid_line[2] = str(vm_info['vm_id']) + "\n"

        lines[10] = 'kiosk = True\n'
        lines[32] = '               "' + \
            '192.168.3.32' + '" : ' + '8006' + '\n'
        lines[43] = " ".join(str(element) for element in user_line)
        lines[45] = " ".join(str(element) for element in token_name_line)
        lines[47] = " ".join(str(element) for element in token_val_line)
        lines[51] = " ".join(str(element) for element in vmid_line)
        lines[86] = vm_info['proxy_from'] + " = " + vm_info['proxy_to'] + '\n'

    with open('vdiclient.ini', 'w') as file:
        file.writelines(lines)

    src = "dist/vdiclient"
    dst = os.path.expanduser("~/Desktop/vdiclient")
    shutil.copy(src, dst)
    os.chmod(dst, 0o755)
    subprocess.run([dst])  # Run the file


# hostname: str = socket.gethostname()

asyncio.run(get_vm_info())

if vm_info['proxmox'] == 1:
    run_proxmox()
else:
    run_custom()
