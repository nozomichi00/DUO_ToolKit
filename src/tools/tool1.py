from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

class Tool1(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("这是工具1的界面"))
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(QPushButton("功能A"))
        button_layout.addWidget(QPushButton("功能B"))
        button_layout.addWidget(QPushButton("功能C"))
        
        layout.addLayout(button_layout)
        layout.addStretch()
        self.setLayout(layout)
