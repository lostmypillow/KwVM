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

version = "0.2.0"

def main():
    misc_files_location = os.path.join(os.path.expanduser("~"), '.kwvm')
    os.makedirs(misc_files_location, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(misc_files_location, 'app.log'), mode="a", encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ],
        force=True
    )

    logging.info(f"KwVM {version} starting...")

    try:
        load_dotenv()
        logging.info(".env loaded successfully")
    except Exception as e:
        logging.warning(f"Failed to load .env: {e}")

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
        try:
            with open(args.proxmox, 'r') as file:
                vm_info = json.load(file)
                selected_dict = vm_info
            logging.info(f"Loaded VM info from {args.proxmox}")
        except FileNotFoundError:
            logging.error(f"Proxmox file not found: {args.proxmox}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON from {args.proxmox}: {e}")
            sys.exit(1)

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

    qml_file = os.fspath(app_dir / url)
    try:
        engine.load(qml_file)
        logging.info(f"Loaded QML: {qml_file}")
    except Exception as e:
        logging.critical(f"Failed to load QML file {qml_file}: {e}")
        sys.exit(1)

    if not engine.rootObjects():
        logging.critical("No root objects found after QML load")
        sys.exit(-1)

    root: QObject = engine.rootObjects()[0]

    try:
        controller.set_engine(engine)
        controller.initialize(root)
    except Exception as e:
        logging.error(f"Failed to initialize controller: {e}")
        sys.exit(1)

    def safe_run_vm():
        try:
            controller.run_vm_now()
        except Exception as e:
            logging.error(f"run_vm_now failed: {e}")
            app.quit()

    QTimer.singleShot(0, safe_run_vm)

    try:
        app.exec()
    except Exception as e:
        logging.critical(f"Qt application crashed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    sys.exit(main())
