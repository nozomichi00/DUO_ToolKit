from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

class Tool2(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("这是工具2的界面"))
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(QPushButton("功能X"))
        button_layout.addWidget(QPushButton("功能Y"))
        button_layout.addWidget(QPushButton("功能Z"))
        
        layout.addLayout(button_layout)
        layout.addStretch()
        self.setLayout(layout)
