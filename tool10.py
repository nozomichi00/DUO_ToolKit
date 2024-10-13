from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class Tool10(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("工具10正在开发中"))
        self.setLayout(layout)
