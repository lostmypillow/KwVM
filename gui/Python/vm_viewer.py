import logging
import subprocess
import os
import proxmoxer
import json
import socket
from pynput.keyboard import Listener, Key
from PySide6.QtCore import QThread
from pprint import pformat
config_folder_path = os.path.join(os.path.expanduser("~"), '.kwvm')

class NodeNotFoundError(Exception):
    pass


class NodeNotOnlineError(Exception):
    pass


class NodeStatusClearError(Exception):
    pass


class VMViewer(QThread):
    def __init__(self, on_complete=None):
        super().__init__()
        self.config_filepath = None
        self.on_complete = on_complete
        self.virt_process = None
        self.running = True
        self.allow_usb = False

    def run(self):
        try:
            command = ["remote-viewer", "-v", "-k"]
            if self.allow_usb:
                command.append("--spice-usbredir-auto-redirect-filter='0x08,-1,-1,-1,1|-1,-1,-1,-1,0'")
            command.append("--spice-disable-effects=all")
            command.append(self.config_filepath)
            logging.info(
                f"Launching setup with config: {self.config_filepath}")
            logging.info(
                f"Running command: {' '.join(command)}")
            logging.info(1)

            self.virt_process = subprocess.Popen(command)
            logging.info(2)

            logging.info(3)

            logging.info(
                "Running virt-viewer in kiosk mode. Press 'Control + Right Control' to exit.")

            exit_keys = {Key.ctrl, Key.ctrl_r}
            pressed_keys = set()

            listener = Listener(
                on_press=lambda key: pressed_keys.add(
                    key) if key in exit_keys else None,
                on_release=lambda key: pressed_keys.discard(
                    key) if key in exit_keys else None
            )
            listener.start()

            try:
                while self.virt_process.poll() is None and self.running:
                    self.msleep(100)
                    if exit_keys.issubset(pressed_keys):
                        logging.info(
                            "Exit key combo pressed, closing remote-viewer.")
                        self.virt_process.terminate()
                        logging.info(
                            "remote-viewer closed!")
            finally:
                listener.stop()
            logging.info("Remote-viewer process has exited.")

        except Exception as e:
            logging.exception(e)
            logging.error(f"Worker error: {e}")

        finally:
            if self.virt_process and self.virt_process.poll() is None:
                self.virt_process.terminate()
                self.virt_process.wait()

            self.on_complete.emit()

    def stop(self):
        self.running = False
        if self.virt_process and self.virt_process.poll() is None:
            self.virt_process.terminate()
            self.virt_process.wait()

    def _construct_config_info(self, vm_info: dict) -> str:
        # Construct owner field
        owner = vm_info["human_owner"] if vm_info["human_owner"] else vm_info["pc_owner"]

        # Construct config filename
        config_filename = owner + '_' + vm_info["vm_name"] + '.vv'

        if vm_info["usb"] == True:
            self.allow_usb= True

        # Construct config file path (assuming config_filepath is set earlier in the code)
        # You can replace this with the actual path if needed
        config_filepath = os.path.join(config_folder_path, config_filename)

        return config_filepath

    def _setup_custom_vm(self, vm_info: dict) -> str:

        # Construct owner field
        config_filepath = self._construct_config_info(vm_info=vm_info)

        with open(config_filepath, 'w') as file:
            config_contents = f'''[virt-viewer]
type=spice
kiosk-quit=on-disconnect
host={vm_info['spice_proxy'].split(':')[0]}
port={vm_info['spice_proxy'].split(':')[1]}
password={vm_info['vm_password']}
title={vm_info['vm_name']}
'''
            if self.allow_usb:
                config_contents += 'enable-usb-autoshare=1\nenable-usbredir=1'
            file.write(config_contents)

        if vm_info['pc_owner'] == socket.gethostname():
            self.create_desktop_file(
                config_filepath=config_filepath, vm_info=vm_info)

        return config_filepath

    def _setup_proxmox_vm(self, vm_info: dict) -> str:

        config_filepath = self._construct_config_info(vm_info=vm_info)

        logging.info(vm_info)

        proxmox_obj = proxmoxer.ProxmoxAPI(
            host=vm_info["pve_host"].split(':')[0],
            port=vm_info["pve_host"].split(':')[1],
            user=f"{vm_info['pve_token_username']}@pve",
            token_name=vm_info['pve_token_name'],
            token_value=vm_info['pve_token_value'],
            verify_ssl=False,
        )

        node_name = vm_info["pve_proxy"].split('.')[0]
        logging.info(f"Node name: {node_name}")
        available_nodes = proxmox_obj.cluster.resources.get(type='node')
        logging.info(f"Available nodes: {available_nodes}")

        if not any(node["node"] == node_name for node in available_nodes):
            logging.info("Node not found")
            raise NodeNotFoundError(f"Node '{node_name}' does not exist.")
        else:
            # Node does exist, check if it's online
            existing_node = next(
                online_node for online_node in available_nodes if online_node["node"] == node_name)
            if existing_node['status'] != 'online':
                logging.info("Node not online")
                raise NodeNotOnlineError(f"Node '{node_name}' is not online.")

        config_contents = '\n'.join(f"{k}={v}" for k, v in proxmox_obj.nodes(node_name).qemu(
            str(vm_info["pve_vm_id"])).spiceproxy.post().items() if k != 'proxy' and k != 'delete-this-file')

        config_contents += f"\nproxy={vm_info['spice_proxy']}\n"

        with open(config_filepath, 'w') as file:
            file.write("[virt-viewer]\n")
            file.write(config_contents)
        logging.info(config_contents)

        if vm_info['pc_owner'] == socket.gethostname():
            try:
                self.create_desktop_file(
                    config_filepath=config_filepath, vm_info=vm_info)
            except Exception as e:
                logging.exception(e)

        return config_filepath

    def setup(self, vm_info: dict):
        if vm_info['pve'] == 1:
            self.config_filepath = self._setup_proxmox_vm(vm_info)
        elif vm_info['pve'] == 0:
            self.config_filepath = self._setup_custom_vm(vm_info=vm_info)

    def create_desktop_file(self, config_filepath, vm_info):
        json_filepath = config_filepath[:-3] + '.json'
        with open(json_filepath, 'w') as json_file:
            json.dump(vm_info, json_file, indent=4)
            logging.info(f'Saved JSON to {json_filepath}')
            
            if 'win7' in vm_info['vm_name'].lower().replace('-', '').replace('_', '').replace(' ', ''):
                icon_path = f"Icon={os.path.expanduser('~')}/.kwvm/win7.png"
            else:
                icon_path = f"Icon={os.path.expanduser('~')}/.kwvm/win10.png"


            desktop_content = f"""[Desktop Entry]
Version=0.2.2
Name={vm_info['vm_name']}
Comment=Launch {vm_info['vm_name']} Directly with KwVM
Exec=sh -c "LC_ALL=C wmctrl -l | grep '高偉虛擬機 0.2.2' && wmctrl -c '高偉虛擬機 0.2.2'; sleep 0.5; {os.path.expanduser('~')}/.kwvm/高偉虛擬機.bin -p '{json_filepath}'"
Type=Application
{icon_path}
Categories=Utility;
"""


            desktop_folder_en = os.path.join(
                os.path.expanduser("~"), "Desktop")
            desktop_folder_zh = os.path.join(os.path.expanduser(
                "~"), "桌面")  # Traditional Chinese Desktop folder

            desktop_folder = desktop_folder_en if os.path.exists(
                desktop_folder_en) else desktop_folder_zh

            desktop_filepath = os.path.join(
                desktop_folder,  vm_info["vm_name"] + '.desktop')

            with open(desktop_filepath, 'w')as desktop_file:
                desktop_file.write(desktop_content)
            logging.info('Desktop file created')
            subprocess.run(
                'for f in ~/Desktop/*.desktop; do chmod +x "$f"; gio set -t string "$f" metadata::xfce-exe-checksum "$(sha256sum "$f" | awk \'{print $1}\')"; done', shell=True, executable='/bin/bash')
            if os.name != 'nt':  # Skip this for Windows
                os.chmod(desktop_filepath, 0o755)
