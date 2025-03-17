import os
import sys
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv
from autogen import resources
from autogen.settings import url, import_paths
from PySide6.QtCore import QObject
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Slot, QTimer,  Signal
from worker import Worker
from api_handler import APIHandler
# Configure logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)


class Controller(QObject):
    task_complete = Signal()

    def __init__(self):
        super().__init__()

        self.engine = None
        self.status_view = None
        self.input_id = None
        self.api_handler = APIHandler()
        self.api_handler.task_complete.connect(self.on_api_complete)
        self.worker = None

    def set_engine(self, engine):
        self.engine = engine

    @Slot(QObject)
    def initialize(self, root: QObject):
        self.status_view = root.findChild(QObject, "status_view")
        self.input_id = root.findChild(QObject, "input_id")
        self.input_id.accepted.connect(self.handle_input)

    @Slot()
    def handle_input(self):
        self.status_view.setProperty('text', '驗證中...')
        input_text = self.input_id.property('text')
        self.input_id.setProperty('text', '')
        if input_text and input_text != '':
            self.api_handler.make_api_call(input_text)
        elif not input_text:
            self.status_view.setProperty('text', f'驗證失敗: {input_text} 為無效字元')
            self.input_id.setProperty('text', '')
        elif input_text == '':
            self.status_view.setProperty('text', f'驗證失敗: {input_text} 不能為空格')
            self.input_id.setProperty('text', '')

    @Slot(str)
    def on_api_complete(self, result):
        if result == '刷卡失敗':
            self.status_view.setProperty('text', '驗證失敗: API 無回應')
            QTimer.singleShot(
                3000, lambda: self.status_view.setProperty('text', '準備就緒!'))
        else:
            try:
                if self.worker:
                    if self.worker.isRunning():
                        self.worker.stop()
                        self.worker.wait()
            except RuntimeError:
                pass

            self.worker = Worker(result, self.task_complete)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.start()
            self.status_view.setProperty('text', '正在啟動虛擬機...')
            QTimer.singleShot(
                10000, lambda: self.status_view.setProperty('text', '準備就緒!'))

    @Slot()
    def on_task_complete(self):
        logging.info("Task completed signal received.")
        QTimer.singleShot(
            3000, lambda: self.status_view.setProperty('text', '準備就緒!'))


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="KwVM")

    parser.add_argument("-p", "--proxmox", type=str,
                        help="Run Proxmox VM instead of the GUI")
    args = parser.parse_args()

    # if args.proxmox:
    #     launch_proxmox_desktop(args.proxmox)
    #     return

    app = QGuiApplication(sys.argv)  # autogen

    app.setWindowIcon(QIcon(":/images/logo.png"))

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
