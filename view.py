import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QListWidget, QFileDialog, QMessageBox, QListWidgetItem, QWidget, QHBoxLayout
from PyQt6.QtCore import QTimer
from program_manager import AppController
import threading

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.app_controller = AppController()
        
        
        # 스레드를 생성하여 SteamVR 상태를 주기적으로 확인합니다.
        self.thread = threading.Thread(target=self.app_controller.check_steamvr_status)
        self.thread.daemon = True  # 메인 스레드 종료 시 함께 종료되도록 설정
        self.thread.start()

        self.setWindowTitle("SteamVR 상태 확인")
        self.setGeometry(100, 100, 600, 400)

        self.label = QLabel("SteamVR 상태: 확인 중...", self)
        self.label.setGeometry(50, 50, 500, 50)

        self.btn_add_program = QPushButton("프로그램 추가", self)
        self.btn_add_program.setGeometry(50, 150, 150, 30)
        self.btn_add_program.clicked.connect(self.add_program_dialog)

        self.btn_start_program = QPushButton("모든 프로그램 시작", self)
        self.btn_start_program.setGeometry(250, 150, 150, 30)
        self.btn_start_program.clicked.connect(self.app_controller.start_all_programs)

        self.btn_stop_program = QPushButton("모든 프로그램 중지", self)
        self.btn_stop_program.setGeometry(450, 150, 150, 30)
        self.btn_stop_program.clicked.connect(self.app_controller.stop_all_programs)

        self.list_programs = QListWidget(self)
        self.list_programs.setGeometry(50, 200, 550, 150)

        # 파일에서 프로그램 목록을 불러옵니다.
        self.load_programs_from_file()


        # QTimer를 설정하여 1초마다 SteamVR 상태를 업데이트합니다.
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)  # 1초마다 update_status() 메서드를 호출합니다.
        
        
    
    def add_item_with_button(self, text):
        # QListWidgetItem 생성
        item = QListWidgetItem()

        # 항목 레이아웃 생성
        item_widget = QWidget()
        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(0, 0, 0, 0)

        # 항목 텍스트
        label = QLabel(text)
        item_layout.addWidget(label)

        # 삭제 버튼 생성 및 설정
        delete_button = QPushButton('삭제')
        delete_button.clicked.connect(lambda: self.delete_item(item))
        item_layout.addWidget(delete_button)

        # 레이아웃을 항목 위젯에 설정
        item_widget.setLayout(item_layout)

        # QListWidget에 항목 추가
        self.list_programs.addItem(item)
        self.list_programs.setItemWidget(item, item_widget)

    def delete_item(self, item):
        # 삭제 버튼 클릭 시 항목 삭제
        index = self.list_programs.row(item)
        self.app_controller.remove_programs_to_file(index)
        self.load_programs_from_file()

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
            program_paths = file_dialog.selectedFiles()
            for program_path in program_paths:
                success = self.app_controller.save_programs_to_file(program_path)
                
                if success:
                    self.load_programs_from_file()
                else:
                    QMessageBox.critical(self,'Critical Title','This program has already been added.')
                    
        
        
        
    
    def load_programs_from_file(self):
        # 'saved_programs.txt' 파일에서 저장된 프로그램 목록을 읽어와 목록에 추가합니다.
        try:
            self.list_programs.clear()
            program_paths = self.app_controller.load_programs_to_file()
            
            for path in program_paths:
                self.add_item_with_button(path)
        except FileNotFoundError:
            # 파일이 없는 경우 아무 작업도 하지 않습니다.
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
