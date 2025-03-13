import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from autogen import resources
from autogen.settings import url, import_paths
from PySide6.QtCore import QObject
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from controller import Controller
import argparse
import configparser
import os
from new_setup import launch_proxmox_desktop

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="KwVM")
    
    parser.add_argument("-p", "--proxmox", type=str, help="Run Proxmox VM instead of the GUI")
    args = parser.parse_args()

    if args.proxmox:
        launch_proxmox_desktop(args.proxmox)
        return

    app = QGuiApplication(sys.argv)  # autogen

    engine: QQmlApplicationEngine = QQmlApplicationEngine()  # autogen

    app_dir = Path(__file__).parent.parent  # autogen

    engine.addImportPath(os.fspath(app_dir))  # autogen

    for path in import_paths:  # autogen
        engine.addImportPath(os.fspath(app_dir / path))  # autogen

    controller = Controller()

    engine.rootContext().setContextProperty("controller", controller)

    engine.load(os.fspath(app_dir/url))  # autogen

    if not engine.rootObjects():  # autogen
        sys.exit(-1)  # autogen

    root: QObject = engine.rootObjects()[0]

    controller.set_engine(engine)

    controller.initialize(root)

    sys.exit(app.exec())    # autogen


if __name__ == '__main__':
    main()


    
