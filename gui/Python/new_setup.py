import os
import shutil
import proxmoxer
import signal
import sys
import keyboard
import subprocess
import configparser
config_folder_path = os.path.abspath('./kwvm_files')
os.makedirs(config_folder_path, exist_ok=True)
example_config_filepath = os.path.join(os.getcwd(), "client.vv.example")


class NodeNotFoundError(Exception):
    pass


class NodeNotOnlineError(Exception):
    pass


class NodeStatusClearError(Exception):
    pass


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


def construct_config_info(vm_info):
    # Construct owner field
    owner = vm_info["human_owner"] if vm_info["human_owner"] else vm_info["pc_owner"]

    # Construct config filename
    config_filename = owner + '_' + vm_info["vm_name"] + '.vv'

    # Construct config file path (assuming config_filepath is set earlier in the code)
    # You can replace this with the actual path if needed
    config_filepath = os.path.join(config_folder_path, config_filename)

    return config_filepath


def setup_custom_vm(vm_info: dict) -> str:

    # Construct owner field
    config_filepath = construct_config_info(vm_info=vm_info)

    with open(config_filepath, 'w') as file:
        file.write(f'''[virt-viewer]
type=spice
fullscreen=1
kiosk-quit=on-disconnect
host={vm_info['spice_proxy'].split(':')[0]}
port={vm_info['spice_proxy'].split(':')[1]}
password={vm_info['vm_password']}
title={vm_info['vm_name']}
''')

    if vm_info['pc_owner'] is not None:
        pass
        # TODO create desktop file pointing to the vv

    return config_filepath


def setup_proxmox_vm(vm_info: dict) -> str:

    config_filepath = construct_config_info(vm_info=vm_info)
    

    proxmox_obj = proxmoxer.ProxmoxAPI(
        host=vm_info["pve_host"].split(':')[0],
        port=vm_info["pve_host"].split(':')[1],
        user=f"{vm_info['pve_token_username']}@pve",
        token_name=vm_info['pve_token_name'],
        token_value=vm_info['pve_token_value'],
        verify_ssl=False,
    )
    node_name = vm_info["pve_proxy"].split('.')[0]
    available_nodes = proxmox_obj.cluster.resources.get(type='node')

    if not any(node["node"] == node_name for node in available_nodes):
        print("Node not found")
        raise NodeNotFoundError(f"Node '{node_name}' does not exist.")
    else:
        # Node does exist, check if it's online
        existing_node = next(
            online_node for online_node in available_nodes if online_node["node"] == node_name)
        if existing_node['status'] != 'online':
            print("Node not online")
            raise NodeNotOnlineError(f"Node '{node_name}' is not online.")

    config_contents = '\n'.join(f"{k} = {v}" for k, v in proxmox_obj.nodes(node_name).qemu(
        str(vm_info["pve_vm_id"])).spiceproxy.post().items())

    with open(config_filepath, 'w') as file:
        file.write("[virt-viewer]\n")
        file.write(config_contents)

    if vm_info['pc_owner'] is not None:
        ini = configparser.ConfigParser()

        for section, values in vm_info.items():
            ini.add_section(vm_info["vm_name"])
            for key, value in values.items():
                ini.set(section, key, str(value))  # Ensure values are strings

        with open(config_filepath[:-3] + '.ini', 'w') as inifile:
            ini.write(inifile)

        # TODO create desktop file pointing to this executable -p name_of_vm
    print(f'{config_filepath[:-3]}')
    return config_filepath


def launch(file_path):
    print("[CUSTOM] Running command: remote-viewer " + file_path)
    virt_process = subprocess.Popen(["remote-viewer", "-v", "-k", "--spice-disable-effects=all", file_path])

    try:
        print("Running virt-viewer in kiosk mode. Press 'Control + Alt' to exit.")
        while True:
            # Change this to any key you want
            if keyboard.is_pressed('ctrl+alt'):
                print("Exit key pressed, closing virt-viewer.")
                virt_process.terminate()
                sys.exit(0)  # Terminate the virt-viewer process
                break

            # Check if the process has exited
            if virt_process.poll() is not None:
                print("Remote-viewer process has exited.")
                break

    except KeyboardInterrupt:
        print("Process interrupted.")
        virt_process.terminate()


def launch_proxmox_desktop(filename):
    ini = configparser.ConfigParser()
    ini.read(os.path.join(config_folder_path, f"{filename}.ini"))
    config_filepath = setup_proxmox_vm(
        {key: value for key, value in ini.items(filename)})
    launch(config_filepath)


def setup(vm_info):
    if vm_info['pve'] == 1:
        return setup_proxmox_vm(vm_info)
    elif vm_info['pve'] == 0:
        print('setting up custom vm')
        return setup_custom_vm(vm_info=vm_info)