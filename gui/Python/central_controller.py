import json
import logging
import socket
import subprocess
from PySide6.QtCore import QObject, Slot, QTimer, Signal, QThread
from api_controller import APIController
from vm_viewer import VMViewer
from vm_selection_model import VMSelectionModel



class CentralController(QObject):
    task_complete = Signal()

    def __init__(self, model, selected_dict=None):
        super().__init__()

        self.engine = None
        self.status_view = None
        self.input_id = None
        self.api_controller = APIController()
        self.api_controller.task_complete.connect(self.on_api_complete)
        self.worker = None
        self._model: VMSelectionModel = model
        self.selected_dict = selected_dict
        self.response_list = []
        self.is_setup = False

    def set_engine(self, engine):
        self.engine = engine

    @Slot(QObject)
    def initialize(self, root: QObject):
        self.status_view = root.findChild(QObject, "status_view")
        self.input_id = root.findChild(QObject, "input_id")
        self.selection_view = root.findChild(QObject, "selection_view")
        self.input_btn = root.findChild(QObject, "input_btn")
        self.input_id.accepted.connect(self.handle_input)
        self.input_btn.clicked.connect(self.handle_input)
        self.status_view.setProperty('text', '設定中')
        self.input_id.setProperty('readOnly', True)
        self.is_setup = True
        self.api_controller.make_api_call(socket.gethostname())
    def update_status_view(self, text):
        self.status_view.setProperty('text', text)
    @Slot()
    def handle_input(self):
        self.input_id.setProperty('readOnly', True)
        
        input_text = self.input_id.property('text')
        if input_text and input_text != '':
            if input_text == 'setup':
                self.is_setup = True
                input_text = socket.gethostname()
                self.api_controller.make_api_call(input_text)
            else:
                self.status_view.setProperty('text', '驗證中...')
                self.api_controller.make_api_call(input_text)
        elif not input_text:
            if input_text == '':
                self.status_view.setProperty('text', f'驗證失敗: {input_text} 不能為空格')
            else:
                self.status_view.setProperty('text', f'驗證失敗: {input_text} 為無效字元')
        self.input_id.setProperty('text', '')
    @Slot(str)
    def on_api_complete(self, response_data):
        try:
            self.response_list: list[dict] = json.loads(response_data)
            logging.info(f'response list = {self.response_list}')
            if len(self.response_list) == 1:
                self.selected_dict = self.response_list[0]
                logging.info(self.selected_dict)
                if self.is_setup == False:
                    self.launch_remote_viewer()
                else:
                    dummy_viewer = VMViewer()
                    logging.info(self.selected_dict)
                    dummy_viewer.setup(self.selected_dict)
                    self.status_view.setProperty('text', '設定完成!')
                    QTimer.singleShot(
                3000, lambda: self.status_view.setProperty('text', '準備就緒!'))

            elif len(self.response_list) > 0:
                self.status_view.setProperty('visible', 'false')
                self._model.setData(self.response_list)
                self.selection_view.setProperty('visible', 'true')
            else:
                self.status_view.setProperty('text', '驗證失敗: 沒有虛擬機!')
                QTimer.singleShot(
                3000, lambda: self.status_view.setProperty('text', '準備就緒!'))

        except Exception as e:
            self.status_view.setProperty('text', '驗證失敗: API 無回應')
            QTimer.singleShot(
                3000, lambda: self.status_view.setProperty('text', '準備就緒!'))
        finally:
            self.input_id.setProperty('readOnly', False)
        
    
    @Slot()
    def on_task_complete(self):
        logging.info("Task completed signal received.")
        QTimer.singleShot(
            3000, lambda: self.status_view.setProperty('text', '準備就緒!'))

    @Slot(str)
    def select_vm(self, selection: str):
        self.selected_dict = next((item for item in self.response_list if item.get('vm_name') == selection), None)
        self.status_view.setProperty('text', f'已選擇{selection}')
        self.status_view.setProperty('visible', 'true')
        self.selection_view.setProperty('visible', 'false')
        self.launch_remote_viewer()
        
        
    def launch_remote_viewer(self):
        self.status_view.setProperty('text', f'正在啟動 {self.selected_dict["vm_name"]}...')
        try:
            if self.worker:
                if self.worker.isRunning():
                    self.worker.stop()
                    self.worker.wait()
        except RuntimeError:
            pass

        self.worker = VMViewer(self.task_complete)
        self.worker.finished.connect(self.on_viewer_exit)
        self.worker.setup(self.selected_dict)
        self.worker.start()

    def on_viewer_exit(self):
        self.worker.deleteLater()
        self.status_view.setProperty('text', f'已關閉 {self.selected_dict["vm_name"]}!')
        QTimer.singleShot(
            2000, lambda: self.status_view.setProperty('text', '準備就緒!'))
        
    def run_vm_now(self):
        if self.selected_dict is not None:
            self.launch_remote_viewer()
