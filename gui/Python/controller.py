import os
import json
import logging
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtCore import QObject, Slot, QUrl, QByteArray, QTimer, Qt, QRunnable, QThreadPool, Signal, QMetaObject
from PySide6.QtGui import QGuiApplication
from new_setup import setup_proxmox_vm, launch, setup
import sys
# Configure logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

class Worker(QRunnable):
    def __init__(self, config_filepath, on_complete):
        super().__init__()
        self.config_filepath = config_filepath
        self.on_complete = on_complete

    def run(self):
        try:
            logging.info(f"Launching setup with config: {self.config_filepath}")
            launch(self.config_filepath) 
            sys.exit(0) # Simulate a long task

            # Call back to the main thread when done
            QMetaObject.invokeMethod(self.on_complete, "emit", Qt.QueuedConnection)
            logging.info("Task completed!")
        except Exception as e:
            logging.error(f"Worker error: {e}")

class Controller(QObject):
    task_complete = Signal()

    def __init__(self):
        super().__init__()

        self.engine = None
        self.status_view = None
        self.input_id = None
        self.network_manager = QNetworkAccessManager(self)
        self.current_reply = None

        self.thread_pool = QThreadPool.globalInstance()
        self.task_complete.connect(self.on_task_complete)

    def set_engine(self, engine):
        self.engine = engine

    @Slot(QObject)
    def initialize(self, root: QObject):
        self.status_view = root.findChild(QObject, "status_view")
        self.input_id = root.findChild(QObject, "input_id")
        self.input_id.accepted.connect(self.handle_input)

    @Slot()
    def handle_input(self):
        self.make_api_call(self.input_id.property('text'))

    def make_api_call(self, input_text):
        url = QUrl(f"http://localhost:8000/vm/{input_text}")
        logging.info(f"Request URL: {url}")

        request = QNetworkRequest(url)
        self.current_reply = self.network_manager.get(request)
        self.status_view.setProperty('text', '處理中')

        # Start timer only on the main thread
        QTimer.singleShot(5000, self.abort_request)

        self.current_reply.finished.connect(self.handle_api_response)

    def abort_request(self):
        if self.current_reply and not self.current_reply.isRunning():
            self.current_reply = None
            return
        
        if self.current_reply and self.current_reply.isRunning():
            logging.info("Request timed out.")
            self.current_reply.abort()


    def handle_api_response(self):
        if not self.current_reply:
            return

        if self.current_reply.error() != QNetworkReply.NoError:
            logging.error(
                f"Error: {self.current_reply.errorString()}, Code: {self.current_reply.error()}")
            self.status_view.setProperty('text', '刷卡失敗')
            QTimer.singleShot(3000, lambda: self.status_view.setProperty('text', '待命中'))
        else:
            try:
                response_data = self.current_reply.readAll().data().decode("utf-8")
                response_json = json.loads(response_data)
                config_filepath = setup(response_json[0])

                # Use QThreadPool to execute worker task
                worker = Worker(config_filepath, self.task_complete)
                self.thread_pool.start(worker)

            except Exception as e:
                logging.error(f"Error decoding response: {e}")
                self.status_view.setProperty('text', '刷卡失敗')
                QTimer.singleShot(3000, lambda: self.status_view.setProperty('text', '待命中'))

        self.input_id.setProperty('text', '')
        self.input_id.forceActiveFocus()
        self.current_reply.deleteLater()

    @Slot()
    def on_task_complete(self):
        logging.info("Task completed signal received.")
        self.status_view.setProperty('text', '作業完成')
        QTimer.singleShot(3000, lambda: self.status_view.setProperty('text', '待命中'))

