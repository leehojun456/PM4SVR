import threading
import os
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QListWidget, QFileDialog
from PyQt6.QtCore import QTimer
from PyQt6.QtCore import QStandardPaths

from controller import AppController  # controller 모듈에 AppController가 정의되어 있다고 가정합니다.

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SteamVR 상태 확인")
        self.setGeometry(100, 100, 600, 400)

        self.label = QLabel("SteamVR 상태: 확인 중...", self)
        self.label.setGeometry(50, 50, 500, 50)

        self.btn_add_program = QPushButton("프로그램 추가", self)
        self.btn_add_program.setGeometry(50, 150, 150, 30)
        self.btn_add_program.clicked.connect(self.add_program_dialog)

        self.btn_start_program = QPushButton("모든 프로그램 시작", self)
        self.btn_start_program.setGeometry(250, 150, 150, 30)
        self.btn_start_program.clicked.connect(self.start_all_programs)

        self.btn_stop_program = QPushButton("모든 프로그램 중지", self)
        self.btn_stop_program.setGeometry(450, 150, 150, 30)
        self.btn_stop_program.clicked.connect(self.stop_all_programs)

        self.list_programs = QListWidget(self)
        self.list_programs.setGeometry(50, 200, 550, 150)

        self.app_controller = AppController()

        # 파일에서 프로그램 목록을 불러옵니다.
        self.load_programs_from_file()

        # 스레드를 생성하여 SteamVR 상태를 주기적으로 확인합니다.
        self.thread = threading.Thread(target=self.app_controller.check_steamvr_status)
        self.thread.daemon = True  # 메인 스레드 종료 시 함께 종료되도록 설정
        self.thread.start()

        # QTimer를 설정하여 1초마다 SteamVR 상태를 업데이트합니다.
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)  # 1초마다 update_status() 메서드를 호출합니다.

    def update_status(self):
        # SteamVR 상태에 따라 라벨을 업데이트합니다.
        if self.app_controller.is_steamvr_running:
            self.label.setText("SteamVR 상태: 실행 중")
        else:
            self.label.setText("SteamVR 상태: 실행 중이 아님")

    def add_program_dialog(self):
        # 파일 다이얼로그를 통해 프로그램을 추가하고, 추가된 프로그램을 목록에 표시합니다.
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("실행 파일 (*.exe)")
        file_dialog.setViewMode(QFileDialog.ViewMode.List)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)

        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            for file_path in file_paths:
                self.list_programs.addItem(file_path)

        # 프로그램을 추가한 후 목록을 파일에 저장합니다.
        self.save_programs_to_file()

    def save_programs_to_file(self):
        try:
            file_name = "saved_programs.txt"

            # 사용자 AppData 폴더 경로 가져오기
            documents_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
            file_path = os.path.join(documents_dir, file_name)

            # 디렉토리가 존재하지 않으면 생성
            os.makedirs(documents_dir, exist_ok=True)

            # 파일 저장
            with open(file_path, "w") as file:
                for index in range(self.list_programs.count()):
                    program_path = self.list_programs.item(index).text()
                    file.write(program_path + '\n')
                    print(f"Program saved: {program_path}")

            print(f"File successfully saved at: {file_path}")
        except Exception as e:
            print(f"파일 저장 중 오류가 발생했습니다: {e}")

    def load_programs_from_file(self):
        # 'saved_programs.txt' 파일에서 저장된 프로그램 목록을 읽어와 목록에 추가합니다.
        try:
            file_name = "saved_programs.txt"

            # 사용자 AppData 폴더 경로 가져오기
            documents_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
            file_path = os.path.join(documents_dir, file_name)

            with open(file_path, 'r') as f:
                program_paths = f.readlines()
                for path in program_paths:
                    path = path.strip()
                    self.list_programs.addItem(path)
        except FileNotFoundError:
            # 파일이 없는 경우 아무 작업도 하지 않습니다.
            pass

    def start_all_programs(self):
        # 현재 등록된 모든 프로그램을 실행합니다.
        try:
            with open('saved_programs.txt', 'r') as f:
                program_paths = f.readlines()
                for path in program_paths:
                    path = path.strip()
                    self.app_controller.start_registered_programs(path)
        except FileNotFoundError:
            # 파일이 없는 경우 아무 작업도 하지 않습니다.
            pass

    def stop_all_programs(self):
        # 현재 목록에 있는 모든 프로그램을 중지합니다.
        for index in range(self.list_programs.count()):
            program_path = self.list_programs.item(index).text()
            self.app_controller.stop_registered_programs(program_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())