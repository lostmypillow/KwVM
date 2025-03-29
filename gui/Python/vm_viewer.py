import logging
import subprocess
import os
import proxmoxer
import sys
import json

import configparser
from pynput import keyboard
from PySide6.QtCore import QThread
config_folder_path = os.path.join(os.path.expanduser("~"), '.kwvm')
example_config_filepath = os.path.join(os.getcwd(), "client.vv.example")


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

    def run(self):
        try:
            logging.info(
                f"Launching setup with config: {self.config_filepath}")
            logging.info(f"Running command: remote-viewer  -v -k --spice-disable-effects=all {self.config_filepath}")
            logging.info(1)

            self.virt_process = subprocess.Popen(
                ["remote-viewer", "-v", "-k",
                    "--spice-disable-effects=all", self.config_filepath],
            )
            logging.info(2)
      
            logging.info(3)
         
            logging.info("Running virt-viewer in kiosk mode. Press 'Control + Alt' to exit.")

            exit_keys = {keyboard.Key.ctrl_l, keyboard.Key.alt_l}
            pressed_keys = set()

            listener = keyboard.Listener(
                on_press=lambda key: pressed_keys.add(key) if key in exit_keys else None,
                on_release=lambda key: pressed_keys.discard(key) if key in exit_keys else None
            )
            listener.start()

            try:
                while self.virt_process.poll() is None and self.running:
                    self.msleep(100)
                    if exit_keys.issubset(pressed_keys):
                        logging.info("Exit key combo pressed, closing virt-viewer.")
                        self.virt_process.terminate()
                        raise KeyboardInterrupt
            finally:
                listener.stop()
            logging.info("Remote-viewer process has exited.")

        except Exception as e:
            logging.info(e)
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

        # Construct config file path (assuming config_filepath is set earlier in the code)
        # You can replace this with the actual path if needed
        config_filepath = os.path.join(config_folder_path, config_filename)

        return config_filepath

    def _setup_custom_vm(self, vm_info: dict) -> str:

        # Construct owner field
        config_filepath = self._construct_config_info(vm_info=vm_info)

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
            self.create_desktop_file(config_filepath=config_filepath, vm_info=vm_info)

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
            str(vm_info["pve_vm_id"])).spiceproxy.post().items() if k != 'proxy' and k!= 'delete-this-file')
        
        config_contents += f"\nproxy={vm_info['spice_proxy']}\n"

        with open(config_filepath, 'w') as file:
            file.write("[virt-viewer]\n")
            file.write(config_contents)
        logging.info(config_contents)

        if vm_info['pc_owner'] != None:
            try:
                self.create_desktop_file(config_filepath=config_filepath, vm_info=vm_info)
            except Exception as e:
                logging.info(e)

            
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

            desktop_content = f"""[Desktop Entry]
Version=0.0.6-alpha1
Name={vm_info['vm_name']}
Comment=Launch {vm_info['vm_name']} Directly with KwVM
Exec=./高偉虛擬機.bin -p {json_filepath}
Terminal=true
Type=Application
Categories=Utility;
"""
            desktop_folder_en = os.path.join(os.path.expanduser("~"), "Desktop")
            desktop_folder_zh = os.path.join(os.path.expanduser("~"), "桌面")  # Traditional Chinese Desktop folder

            desktop_folder = desktop_folder_en if os.path.exists(desktop_folder_en) else desktop_folder_zh

            desktop_filepath = os.path.join(desktop_folder,  vm_info["vm_name"] + '.desktop')

            with open(desktop_filepath, 'w')as desktop_file:
                desktop_file.write(desktop_content)
            logging.info('Desktop file created')
            subprocess.run([
            'gio', 'set', desktop_filepath, 'metadata::trusted', 'yes'
        ], check=True)
            if os.name != 'nt':  # Skip this for Windows
                os.chmod(desktop_filepath, 0o755)

