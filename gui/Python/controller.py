import os
import json
import logging
from pprint import pprint
from typing import Optional
import ast
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtCore import QObject, Slot, QUrl, QByteArray, QTimer, Qt
from PySide6.QtGui import QGuiApplication, QKeyEvent
# Configure logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)


class Controller(QObject):
    def __init__(self):
        super().__init__()

        # Initialize member variables
        self.engine: Optional[QQmlApplicationEngine] = None
        self.kb_btn: Optional[QObject] = None
        self.numpad_layout: Optional[QObject] = None
        self.status_view: Optional[QObject] = None
        self.teacher_text: Optional[QObject] = None
        self.input_id: Optional[QObject] = None

        self.network_manager = QNetworkAccessManager(self)
        self.current_reply = None

    def set_engine(self, engine):
        """Store engine reference for UI control."""
        self.engine = engine

    @Slot(QObject)
    def initialize(self, root: QObject):
        """Find UI elements from QML."""

        # Get references to QML elements
        # self.kb_btn = root.findChild(QObject, "kb_btn")
        # self.numpad_layout = root.findChild(QObject, "numpad_layout")
        self.status_view = root.findChild(QObject, "status_view")
        self.input_id: QObject = root.findChild(QObject, "input_id")
        self.input_id.accepted.connect(self.handle_input)

    @Slot(str)
    def handle_input(self):
        """Handle input text when Enter key is pressed."""
        self.make_api_call(self.input_id.property('text'))


# API Logic START

    def make_api_call(self, input_text):
        """Send API request without freezing UI."""
        url = QUrl()
        url.setScheme("http")
        # url.setHost(str(os.getenv('SERVER_HOST')))
        # url.setPort(int(os.getenv('SERVER_PORT')))
        url.setHost("localhost")
        url.setPort(8000)
        url.setPath(f"/vm/{input_text}")
        logging.info(url)

        request = QNetworkRequest(url)
        self.current_reply = self.network_manager.get(request)
        self.status_view.setProperty('text', '處理中')

        self.abort_timer = QTimer()
        self.abort_timer.setSingleShot(True)
        self.abort_timer.timeout.connect(self.abort_request)
        self.abort_timer.start(5000)

        self.current_reply.finished.connect(self.handle_api_response)

    def abort_request(self):
        """Abort the API request if it times out."""
        if self.current_reply and self.current_reply.isRunning():
            logging.info("Request timed out.")
            self.current_reply.abort()

        # Stop the timer and clean up
        if self.abort_timer:
            self.abort_timer.stop()
            self.abort_timer = None

    def handle_api_response(self):
        """Handle the API response asynchronously."""
        if self.abort_timer:
            self.abort_timer.stop()
            self.abort_timer = None
        if not self.current_reply:
            return

        if self.current_reply.error() != QNetworkReply.NoError:
            # Handle error response
            logging.error(
                f"Error: {self.current_reply.errorString()}, Code: {self.current_reply.error()}")
            self.status_view.setProperty('text', '刷卡失敗')
            QTimer.singleShot(
                3000, lambda: self.status_view.setProperty('text', '待命中'))
            return
        else:
            # Process successful response
            response_data = self.current_reply.readAll().data()
            try:
                response_json = json.loads(QByteArray(response_data).data().decode(
                    "utf-8"))
                self.status_view.setProperty(
                    'text', response_json[0]['vm_name'])

                QTimer.singleShot(
                    3000, lambda: self.status_view.setProperty('text', '待命中'))
            except Exception as e:
                logging.info(f"Error decoding response: {e}")
                self.status_view.setProperty('text', '刷卡失敗')
                QTimer.singleShot(
                    3000, lambda: self.status_view.setProperty('text', '待命中'))

        # Reset input and refocus
        self.input_id.setProperty('text', '')
        self.input_id.forceActiveFocus()
        self.current_reply.deleteLater()
# API Logic END
