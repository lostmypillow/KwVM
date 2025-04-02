import os
import sys
import argparse
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
from autogen import resources
from autogen.settings import url, import_paths
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, QTimer
from vm_selection_model import VMSelectionModel
from central_controller import CentralController
from vm_viewer import VMViewer
import subprocess

# Configure logging

version= "0.0.8"

def main():
    logging.info(f"KwVM {version} starting...")
    
    misc_files_location = os.path.join(os.path.expanduser("~"), '.kwvm')

    os.makedirs(misc_files_location, exist_ok=True)

    logging.basicConfig(
        filename=os.path.join(misc_files_location, 'app.log'),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8"
    )

    load_dotenv()

    parser = argparse.ArgumentParser(description="KwVM")

    parser.add_argument(
        "-p",
        "--proxmox",
        type=str,
        help="Run Proxmox VM instead of the GUI"
    )
    
    selected_dict = None
    args = parser.parse_args()

    if args.proxmox:
        # it will receive path to json
        with open(args.proxmox, 'r') as file:
            vm_info = json.load(file)
            selected_dict = vm_info

    app = QGuiApplication(sys.argv)

    app.setWindowIcon(QIcon(":/images/logo.png"))

    engine: QQmlApplicationEngine = QQmlApplicationEngine()

    app_dir = Path(__file__).parent.parent

    engine.addImportPath(os.fspath(app_dir))

    for path in import_paths:
        engine.addImportPath(os.fspath(app_dir / path))

    model = VMSelectionModel()
    controller = CentralController(model=model, selected_dict=selected_dict)

    engine.rootContext().setContextProperty("controller", controller)
    engine.rootContext().setContextProperty("selectionModel", model)

    engine.load(os.fspath(app_dir / url))

    if not engine.rootObjects():
        sys.exit(-1)

    root: QObject = engine.rootObjects()[0]

    controller.set_engine(engine)
    controller.initialize(root)

    QTimer.singleShot(0, controller.run_vm_now)

    app.exec()


if __name__ == '__main__':
    sys.exit(main())
