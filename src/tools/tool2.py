from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QComboBox, QLineEdit, QScrollArea
from PyQt6.QtCore import Qt
import os, re, random, base64, textwrap, logging
from datetime import datetime, timedelta

class Tool2(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        logging.info("Initializing Tool2")
        self.init_ui()

    def init_ui(self):
        logging.info("Setting up UI")
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setContentsMargins(15, 15, 15, 15)

        layout = QGridLayout()
        layout.setVerticalSpacing(10)
        layout.setHorizontalSpacing(10)

        self.input_path = QLineEdit(self)
        self.input_path.setPlaceholderText("Select input log (log/txt/bak/csv)")
        browse_input_button = QPushButton("Browse")
        browse_input_button.clicked.connect(self.select_input_file)
        layout.addWidget(QLabel("Select input log:"), 0, 0)
        layout.addWidget(self.input_path, 0, 1)
        layout.addWidget(browse_input_button, 0, 2)

        self.output_folder = QLineEdit(self)
        self.output_folder.setPlaceholderText("Select output folder")
        browse_output_button = QPushButton("Browse")
        browse_output_button.clicked.connect(self.select_output_folder)
        layout.addWidget(QLabel("Select output folder:"), 1, 0)
        layout.addWidget(self.output_folder, 1, 1)
        layout.addWidget(browse_output_button, 1, 2)

        self.conversion_combobox = QComboBox(self)
        self.conversion_combobox.addItems(["COM16", "COM17", "COM18", "COM20"])
        self.conversion_combobox.setCurrentText("COM16")
        layout.addWidget(QLabel("Log type:"), 2, 0)
        layout.addWidget(self.conversion_combobox, 2, 1)

        self.output_file_name = QLineEdit(self)
        self.output_file_name.setText("OutputFileName")
        layout.addWidget(QLabel("Output file name:"), 3, 0)
        layout.addWidget(self.output_file_name, 3, 1)

        button_frame = QWidget(self)
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)

        convert_button = QPushButton("Convert")
        convert_button.clicked.connect(self.convert_file)
        about_button = QPushButton("About")
        about_button.clicked.connect(self.show_about)

        button_layout.addWidget(convert_button)
        button_layout.addWidget(about_button)

        layout.addWidget(button_frame, 4, 0, 1, 3)

        self.result_label = QLabel("", self)
        layout.addWidget(self.result_label, 5, 0, 1, 3)

        layout.addWidget(QLabel("Selected files:"), 6, 0, 1, 3)
        self.selected_files_label = QLabel("", self)
        layout.addWidget(self.selected_files_label, 7, 0, 1, 3)

        main_layout.addLayout(layout)
        scroll_area.setWidget(container)

        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(scroll_area)
        self.setLayout(outer_layout)

        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border-radius: 10px;
                font-size: 14px;
            }
            QLabel {
                font-weight: bold;
            }
            QLineEdit, QComboBox {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #ccc;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)

    def select_input_file(self):
        try:
            selected_files, _ = QFileDialog.getOpenFileNames(self, "Select Input File", "", "All Files (*)")
            if selected_files:
                self.input_path.setText("\n".join(selected_files))
                self.selected_files_label.setText("\n".join(selected_files))
                logging.info(f"Selected input files: {selected_files}")
        except Exception as e:
            logging.error(f"Error selecting input file: {e}")

    def select_output_folder(self):
        try:
            selected_folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
            if selected_folder:
                self.output_folder.setText(selected_folder)
                logging.info(f"Selected output folder: {selected_folder}")
        except Exception as e:
            logging.error(f"Error selecting output folder: {e}")

    def convert_file(self):
        logging.info("Starting file conversion")

        selected_files = self.input_path.text().split("\n")
        if not selected_files:
            QMessageBox.critical(self, "Error", "Please select files for restoration.")
            logging.error("No files selected for restoration")
            return

        if not all(file.endswith(".txt") for file in selected_files):
            QMessageBox.critical(self, "Error", "Please select valid .txt files for restoration.")
            logging.error("Invalid file type for restoration")
            return

        if not self.output_folder.text():
            QMessageBox.critical(self, "Error", "Please select an output folder.")
            logging.error("No output folder selected")
            return

        if not self.output_file_name.text().strip():
            QMessageBox.critical(self, "Error", "Output file name cannot be empty.")
            logging.error("Empty output file name")
            return

        self.result_label.setText("Converting file, please wait...")
        self.repaint()

        try:
            with open(selected_files[0], "rb") as f:
                data = f.read()
            logging.info("Read input file successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error reading file: {str(e)}")
            logging.error(f"Error reading file: {e}")
            return

        conversion_type = self.conversion_combobox.currentText()
        logging.info(f"Conversion type selected: {conversion_type}")

        # 轉換代碼

        logging.info("File conversion completed successfully")

    def show_about(self):
        logging.info("Showing about dialog")
        QMessageBox.information(self, "About", 
                                "")