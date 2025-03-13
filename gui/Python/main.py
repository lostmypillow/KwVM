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

load_dotenv()

if __name__ == '__main__':

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
