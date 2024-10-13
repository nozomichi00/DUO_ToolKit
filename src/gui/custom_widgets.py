import importlib
import logging
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QTabBar
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
from .homepage import HomePage

class CustomTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDrawBase(False)
        self.setExpanding(False)

class CustomTabWidget(QTabWidget):
    add_tab_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabBar(CustomTabBar(self))
        
        self.add_tab_button = QPushButton("+")
        self.add_tab_button.setFixedSize(30, 30)
        self.add_tab_button.setStyleSheet("""
            QPushButton {
                border: none;
                font-weight: bold;
                font-size: 20px;
                background: transparent;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-radius: 15px;
            }
        """)
        self.add_tab_button.clicked.connect(self.add_tab_requested.emit)
        
        self.tab_layout = QHBoxLayout()
        self.tab_layout.setSpacing(0)
        self.tab_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tab_layout.addWidget(self.add_tab_button)
        
        self.tab_bar_container = QWidget()
        self.tab_bar_container.setLayout(self.tab_layout)
        
        self.setCornerWidget(self.tab_bar_container, Qt.Corner.TopLeftCorner)

    def setTabBar(self, tab_bar):
        super().setTabBar(tab_bar)
        if hasattr(self, 'tab_layout') and self.tab_layout:
            existing_tab_bar = self.tab_layout.itemAt(1).widget() if self.tab_layout.count() > 1 else None
            if existing_tab_bar:
                self.tab_layout.removeWidget(existing_tab_bar)
            self.tab_layout.addWidget(self.tabBar())

class DUO_ToolKit(QMainWindow):
    def __init__(self):
        super().__init__()
        logging.debug("Initializing DUO_ToolKit")
        self.setWindowTitle("DUO_ToolKit")
        self.setGeometry(100, 100, 800, 600)

        logging.debug("Creating central widget")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        logging.debug("Setting up main layout")
        main_layout = QVBoxLayout()
        self.central_widget.setLayout(main_layout)

        logging.debug("Creating CustomTabWidget")
        self.tab_widget = CustomTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.add_tab_requested.connect(self.add_home_tab)

        logging.debug("Setting tab widget style")
        self.tab_widget.setStyleSheet("""
            QTabBar::tab {
                padding: 5px;
                font-size: 16px;
            }
            QTabBar::tab:selected {
                font-weight: bold;
            }
            QTabBar::close-button {
                image: none;
                background: none;
                border: none;
            }
            QTabBar::close-button:hover {
                background: #e0e0e0;
                border-radius: 2px;
            }
        """)

        logging.debug("Adding tab widget to main layout")
        main_layout.addWidget(self.tab_widget)

        logging.debug("Adding home tab")
        self.add_home_tab()

        logging.debug("DUO_ToolKit initialization complete")

    def add_home_tab(self):
        logging.info("Adding home tab")
        home_page = HomePage(self)
        index = self.tab_widget.addTab(home_page, "Home")
        self.tab_widget.tabBar().setTabButton(index, QTabBar.ButtonPosition.RightSide, self.create_close_button())
        self.tab_widget.setCurrentIndex(index)

    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            tab_name = self.tab_widget.tabText(index)
            logging.info(f"Closing tab: {tab_name}")
            self.tab_widget.removeTab(index)

    def open_tool(self, tool_name):
        logging.info(f"Opening tool: {tool_name}")
        try:
            if tool_name == "Log Type Convert":
                module = importlib.import_module("src.tools.tool1")
                tool_class = getattr(module, "Tool1")
            elif tool_name == "工具2":
                module = importlib.import_module("src.tools.tool2")
                tool_class = getattr(module, "Tool2")
            else:
                logging.error(f"Tool {tool_name} not found")
                return

            tool = tool_class()
            current_tab = self.tab_widget.currentWidget()
            if isinstance(current_tab, HomePage):
                new_tab = QWidget()
                layout = QVBoxLayout()
                layout.addWidget(tool)
                new_tab.setLayout(layout)
                index = self.tab_widget.addTab(new_tab, tool_name)
                self.tab_widget.setCurrentIndex(index)
                self.tab_widget.tabBar().setTabButton(index, QTabBar.ButtonPosition.RightSide, self.create_close_button())
                logging.info(f"Created new tab for {tool_name}")
            else:
                current_tab.layout().itemAt(0).widget().setParent(None)
                current_tab.layout().addWidget(tool)
                self.tab_widget.setTabText(self.tab_widget.currentIndex(), tool_name)
                logging.info(f"Replaced current tab content with {tool_name}")
        except ImportError as e:
            logging.error(f"Error importing tool {tool_name}: {e}")

    def create_close_button(self):
        close_button = QPushButton("×")
        close_button.setStyleSheet("""
            QPushButton {
                color: black;
                font-weight: bold;
                font-size: 14px;
                border: none;
                padding: 0px;
                margin: 0px;
                width: 16px;
                height: 16px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-radius: 2px;
            }
        """)
        close_button.clicked.connect(lambda: self.close_tab(self.tab_widget.currentIndex()))
        return close_button