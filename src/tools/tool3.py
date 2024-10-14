from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class Tool3(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("開發中"))
        self.setLayout(layout)
