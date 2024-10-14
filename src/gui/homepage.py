import json
import logging
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QScrollArea, QSizePolicy
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QSize

class HomePage(QWidget):
    def __init__(self, parent):
        super().__init__()
        logging.info("Initializing HomePage")
        self.parent = parent
        self.load_tool_descriptions()
        self.init_ui()

    def load_tool_descriptions(self):
        try:
            with open('data/tool_descriptions.json', 'r', encoding='utf-8') as f:
                self.tool_descriptions = json.load(f)
            logging.info("Tool descriptions loaded successfully")
        except FileNotFoundError:
            logging.error("tool_descriptions.json not found. Please ensure the file exists in the data directory.")
            self.tool_descriptions = {}
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding tool_descriptions.json: {e}")
            self.tool_descriptions = {}
        except Exception as e:
            logging.error(f"Unexpected error loading tool descriptions: {e}")
            self.tool_descriptions = {}

    def init_ui(self):
        main_layout = QHBoxLayout()

        left_widget = self.create_left_widget()
        self.right_widget = self.create_right_widget()

        main_layout.addWidget(left_widget)
        main_layout.addWidget(self.right_widget)

        self.setLayout(main_layout)
        self.set_styles()

    def create_left_widget(self):
        left_widget = QWidget()
        left_widget.setObjectName("leftWidget")
        left_layout = QVBoxLayout()

        title_label = QLabel("Function")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #333333;")
        left_layout.addWidget(title_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        tool1_btn = self.create_tool_button("Log Type Convert")
        scroll_layout.addWidget(tool1_btn)

        tool2_btn = self.create_tool_button("Log Content Convert")
        scroll_layout.addWidget(tool2_btn)

        tool3_btn = self.create_tool_button("New Tool Setup")
        scroll_layout.addWidget(tool3_btn)

        tool4_btn = self.create_tool_button("Copy WRS Daily")
        scroll_layout.addWidget(tool4_btn)

        tool5_btn = self.create_tool_button("To Be Decided5")
        scroll_layout.addWidget(tool5_btn)

        scroll_layout.addStretch()
        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        left_layout.addWidget(scroll_area)

        left_widget.setLayout(left_layout)
        left_widget.setFixedWidth(170)
        return left_widget

    def create_right_widget(self):
        right_widget = QWidget()
        right_widget.setObjectName("rightWidget")
        right_layout = QVBoxLayout()

        self.intro_label = QLabel()
        self.intro_label.setWordWrap(True)
        self.intro_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.intro_label.setTextFormat(Qt.TextFormat.RichText)
        self.intro_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.reset_intro()

        right_layout.addWidget(self.intro_label)
        right_widget.setLayout(right_layout)
        return right_widget

    def set_styles(self):
        self.setStyleSheet("""
            #leftWidget, #rightWidget {
                background-color: #f0f0f0;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton {
                background-color: #ffffff;
                border: none;
                padding: 10px;
                text-align: left;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QScrollArea {
                border: none;
            }
        """)

    def create_tool_button(self, text):
        btn = QPushButton(text)
        btn.clicked.connect(lambda: self.open_tool(text))
        btn.setFixedSize(QSize(150, 40))
        btn.enterEvent = lambda event: self.update_intro(text)
        btn.leaveEvent = lambda event: self.reset_intro()
        return btn

    def open_tool(self, text):
        logging.info(f"Tool button clicked: {text}")
        self.parent.open_tool(text)

    def update_intro(self, tool_name):
        logging.info(f"Mouse entered tool button: {tool_name}")
        intro_text = self.get_tool_intro(tool_name)
        self.intro_label.setText(intro_text)

    def get_tool_intro(self, tool_name):
        return self.tool_descriptions.get(tool_name, f"<h3 style='text-align:center;'>{tool_name}</h3><p style='text-align:center;'>開發中</p>")

    def reset_intro(self):
        logging.info("Mouse left tool button, resetting intro")
        intro_text = """
        <div style='display: flex; flex-direction: column; justify-content: center; height: 100%;'>
            <h2 style='text-align:center;'>歡迎使用 DUO_ToolKit！</h2>
            <p style='text-align:center;'>本工具集成了 DUO 機型的各類解析工具與自動化功能。</p>
            <p style='text-align:center;'>請將滑鼠懸停在左側工具上，即可查看各項功能的詳細說明。</p>
            <br>
            <h2 style='text-align:center;'>Welcome to DUO_ToolKit!</h2>
            <p style='text-align:center;'>This toolkit integrates various analysis and automation tools for DUO models.</p>
            <p style='text-align:center;'>Hover over the tools on the left to see detailed descriptions of each feature.</p>
        </div>
        """
        self.intro_label.setText(intro_text)
