from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class Tool7(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("工具7正在开发中"))
        self.setLayout(layout)
