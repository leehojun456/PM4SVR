import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QListWidget,
    QFileDialog, QMessageBox, QListWidgetItem, QWidget, QHBoxLayout,
    QCheckBox, QVBoxLayout, QSystemTrayIcon, QMenu
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QTimer
from program_manager import AppController
import threading

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.app_controller = AppController()
        
        # 스레드를 생성하여 SteamVR 상태를 주기적으로 확인합니다.
        thread_steamvr = threading.Thread(target=self.app_controller.check_steamvr_status)
        thread_steamvr.daemon = True
        thread_steamvr.start()

        # 스레드를 생성하여 Vrchat 상태를 주기적으로 확인합니다.
        thread_vrchat = threading.Thread(target=self.app_controller.check_vrchat_status)
        thread_vrchat.daemon = True
        thread_vrchat.start()

        # 창 초기화
        self.setWindowTitle("OSC Manager For VRChat")
        self.setGeometry(100, 100, 600, 400)
        self.setFixedSize(600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 메인 레이아웃
        self.main_layout = QVBoxLayout(self.central_widget)

        # SteamVR 상태 및 체크박스 가로 레이아웃
        self.hbox_steamvr = QHBoxLayout()
        self.main_layout.addLayout(self.hbox_steamvr)

        # SteamVR 상태 라벨
        self.label_steamvr_status = QLabel("SteamVR 상태: 확인 중...", self)
        self.hbox_steamvr.addWidget(self.label_steamvr_status)
        
        # VRChat 실행 상태 라벨
        self.label_vrchat_status = QLabel("VRChat 실행 상태: 확인 중...", self)
        self.hbox_steamvr.addWidget(self.label_vrchat_status)

        # SteamVR 실행 중일 때 실행 체크박스
        self.checkbox_steamvr = QCheckBox("SteamVR 상태일 때 실행", self)
        self.hbox_steamvr.addWidget(self.checkbox_steamvr)

        # 프로그램 리스트
        self.list_programs = QListWidget(self)
        self.main_layout.addWidget(self.list_programs)

        # 파일 추가 버튼
        self.btn_add_program = QPushButton("프로그램 추가", self)
        self.btn_add_program.clicked.connect(self.add_program_dialog)
        self.main_layout.addWidget(self.btn_add_program)

        # 모든 프로그램 실행 및 중지 버튼을 위한 가로 레이아웃
        self.horizontal_layout = QHBoxLayout()
        self.main_layout.addLayout(self.horizontal_layout)

        self.btn_start_program = QPushButton("모든 프로그램 시작", self)
        self.btn_start_program.clicked.connect(self.app_controller.start_all_programs)
        self.horizontal_layout.addWidget(self.btn_start_program)

        self.btn_stop_program = QPushButton("모든 프로그램 중지", self)
        self.btn_stop_program.clicked.connect(self.app_controller.stop_all_programs)
        self.horizontal_layout.addWidget(self.btn_stop_program)

        # 파일에서 프로그램 목록을 불러옵니다.
        self.load_programs_from_file()

        # QTimer를 설정하여 1초마다 SteamVR 상태를 업데이트합니다.
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)  # 1초마다 update_status() 메서드를 호출합니다.

        # 시스템 트레이 아이콘 설정
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icon.png"))  # 아이콘 파일 경로 설정

        # 트레이 메뉴 설정
        self.tray_menu = QMenu(self)
        restore_action = QAction("복원", self)
        restore_action.triggered.connect(self.show)
        quit_action = QAction("종료", self)
        quit_action.triggered.connect(QApplication.instance().quit)

        self.tray_menu.addAction(restore_action)
        self.tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(self.tray_menu)

        # 시스템 트레이 아이콘 활성화
        self.tray_icon.show()

        # 창 최소화/닫기 이벤트 처리
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show()

    def closeEvent(self, event):
        if self.isVisible():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "OSC Manager For VRChat",
                "애플리케이션이 트레이로 최소화되었습니다.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )

    def add_item_with_button(self, text):
        # QListWidgetItem 생성
        item = QListWidgetItem(text)  # 텍스트 설정

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
        
        run_button = QPushButton('실행')
        run_button.clicked.connect(lambda: self.run_item(item))
        item_layout.addWidget(run_button)

        # 레이아웃을 항목 위젯에 설정
        item_widget.setLayout(item_layout)

        # QListWidget에 항목 추가
        self.list_programs.addItem(item)
        self.list_programs.setItemWidget(item, item_widget)

    def delete_item(self, item):
        # 삭제 버튼 클릭 시 항목 삭제
        index = self.list_programs.row(item)
        try:
            self.app_controller.remove_programs_to_file(index)
            self.load_programs_from_file()
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'프로그램 삭제 중 오류가 발생했습니다: {str(e)}')

    def run_item(self, item):
        # 실행 버튼 클릭 시 항목 실행
        program_path = item.text()  # item에서 텍스트 데이터 가져오기
        print(program_path)
        try:
            self.app_controller.start_registered_programs(program_path)
            self.load_programs_from_file()
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'프로그램 실행 중 오류가 발생했습니다: {str(e)}')

    def update_status(self):
        # SteamVR 상태에 따라 라벨을 업데이트합니다.
        if self.app_controller.is_steamvr_running:
            self.label_steamvr_status.setText("SteamVR 상태: 실행 중")
        else:
            self.label_steamvr_status.setText("SteamVR 상태: 실행 중이 아님")
            
        # VRChat 상태에 따라 라벨을 업데이트합니다.
        if self.app_controller.is_vrchat_running:
            self.label_vrchat_status.setText("VRChat 상태: 실행 중")
        else:
            self.label_vrchat_status.setText("VRChat 상태: 실행 중이 아님")            

    def add_program_dialog(self):
        # 파일 다이얼로그를 통해 프로그램을 추가하고, 추가된 프로그램을 목록에 표시합니다.
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("실행 파일 (*.exe)")
        file_dialog.setViewMode(QFileDialog.ViewMode.List)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)

        if file_dialog.exec():
            program_paths = file_dialog.selectedFiles()
            for program_path in program_paths:
                try:
                    success = self.app_controller.save_programs_to_file(program_path)
                    if success:
                        self.load_programs_from_file()
                    else:
                        QMessageBox.critical(self, 'Error', '이 프로그램은 이미 추가되었습니다.')
                except Exception as e:
                    QMessageBox.critical(self, 'Error', f'프로그램 추가 중 오류가 발생했습니다: {str(e)}')
                    
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
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'프로그램 목록을 불러오는 중 오류가 발생했습니다: {str(e)}')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
