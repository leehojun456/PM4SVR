from PyQt6.QtWidgets import QApplication, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QLabel

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # QListWidget 인스턴스 생성
        self.list_widget = QListWidget()

        # 예제 데이터 추가
        self.add_item_with_button('1234')
        self.add_item_with_button('ehdgo')

        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

        # 윈도우 설정
        self.setWindowTitle('QListWidget with Delete Buttons')
        self.resize(300, 200)

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
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, item_widget)

    def delete_item(self, item):
        # 삭제 버튼 클릭 시 항목 삭제
        row = self.list_widget.row(item)
        self.list_widget.takeItem(row)
        # 추가로, 여기서 항목과 관련된 데이터도 삭제할 수 있습니다

# 애플리케이션 실행
app = QApplication([])
window = MainWindow()
window.show()
app.exec()
