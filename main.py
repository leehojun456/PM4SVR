import threading
from controller import AppController
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtCore import QTimer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SteamVR Status Checker")
        self.setGeometry(100, 100, 400, 300)  # Set window position (x, y) and size (width, height)

        self.label = QLabel("SteamVR Status: Checking...", self)
        self.label.setGeometry(50, 50, 300, 50)  # Set label position and size

        self.app_controller = AppController()

                # 스레드를 생성하여 check_steamvr_status() 메서드 실행
        self.thread = threading.Thread(target=self.app_controller.check_steamvr_status)
        self.thread.daemon = True  # 메인 스레드 종료시 함께 종료되도록 설정
        self.thread.start()

        # QTimer 설정
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)  # 1초마다 update_status() 호출

    def update_status(self):
        if self.app_controller.is_steamvr_running:
            self.label.setText("SteamVR Status: Running")
        else:
            self.label.setText("SteamVR Status: Not Running")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
