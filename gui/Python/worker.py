import logging
import subprocess
from PySide6.QtCore import QThread
import keyboard

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

class Worker(QThread):
    def __init__(self, config_filepath, on_complete):
        super().__init__()
        self.config_filepath = config_filepath
        self.on_complete = on_complete
        self.virt_process = None
        self.running = True

    def run(self):
        try:
            logging.info(f"Launching setup with config: {self.config_filepath}")
            print("[CUSTOM] Running command: remote-viewer " + self.config_filepath)

            self.virt_process = subprocess.Popen(
                ["remote-viewer", "-v", "-k", "--spice-disable-effects=all", self.config_filepath],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            print("Running virt-viewer in kiosk mode. Press 'Control + Alt' to exit.")

            while self.virt_process.poll() is None and self.running:
                self.msleep(100)
                if keyboard.is_pressed('ctrl+alt'):
                    print("Exit key pressed, closing virt-viewer.")
                    self.virt_process.terminate()
                    raise KeyboardInterrupt  # Terminate the virt-viewer process


            logging.info("Remote-viewer process has exited.")

        except Exception as e:
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
