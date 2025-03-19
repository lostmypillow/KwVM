import logging
from PySide6.QtCore import QObject, QUrl, QTimer, Signal
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

class APIController(QObject):
    task_complete = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.network_manager = QNetworkAccessManager(self)
        self.current_reply = None

    def make_api_call(self, input_text):
        url = QUrl(f"http://192.168.2.32:8005/vm/{input_text}")
        logging.info(f"Request URL: {url}")

        request = QNetworkRequest(url)
        self.current_reply = self.network_manager.get(request)

        # Start timeout timer
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
            self.task_complete.emit('刷卡失敗')
        else:
            try:
                response_data = self.current_reply.readAll().data().decode("utf-8")
                
                self.task_complete.emit(response_data)
            except Exception as e:
                logging.error(f"Error decoding response: {e}")
                self.task_complete.emit('刷卡失敗')

        self.current_reply.deleteLater()
        self.current_reply = None
