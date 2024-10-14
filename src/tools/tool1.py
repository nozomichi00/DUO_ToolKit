from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QComboBox, QLineEdit, QScrollArea
from PyQt6.QtCore import Qt
import os, re, random, base64, textwrap, logging
from datetime import datetime, timedelta

class Tool1(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        logging.info("Initializing Tool1")
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
        self.input_path.setPlaceholderText("Select input file (zip/txt)")
        browse_input_button = QPushButton("Browse")
        browse_input_button.clicked.connect(self.select_input_file)
        layout.addWidget(QLabel("Select input file:"), 0, 0)
        layout.addWidget(self.input_path, 0, 1)
        layout.addWidget(browse_input_button, 0, 2)

        self.output_folder = QLineEdit(self)
        self.output_folder.setPlaceholderText("Select output folder")
        browse_output_button = QPushButton("Browse")
        browse_output_button.clicked.connect(self.select_output_folder)
        layout.addWidget(QLabel("Select output folder:"), 1, 0)
        layout.addWidget(self.output_folder, 1, 1)
        layout.addWidget(browse_output_button, 1, 2)

        self.start_time_combobox = QComboBox(self)
        self.start_time_combobox.addItems(self.generate_time_options())
        self.start_time_combobox.setCurrentIndex(0)
        layout.addWidget(QLabel("Select start time:"), 2, 0)
        layout.addWidget(self.start_time_combobox, 2, 1)

        self.end_time_combobox = QComboBox(self)
        self.end_time_combobox.addItems(self.generate_time_options())
        self.end_time_combobox.setCurrentIndex(len(self.generate_time_options()) - 1)
        layout.addWidget(QLabel("Select end time:"), 3, 0)
        layout.addWidget(self.end_time_combobox, 3, 1)

        self.max_line_length = QLineEdit(self)
        self.max_line_length.setText("100")
        layout.addWidget(QLabel("Max line length:"), 4, 0)
        layout.addWidget(self.max_line_length, 4, 1)

        self.max_file_size = QLineEdit(self)
        self.max_file_size.setText("3000")
        layout.addWidget(QLabel("Max file size (KB):"), 5, 0)
        layout.addWidget(self.max_file_size, 5, 1)

        self.conversion_combobox = QComboBox(self)
        self.conversion_combobox.addItems(["Binary", "Decimal", "Hexadecimal", "Base64"])
        self.conversion_combobox.setCurrentText("Hexadecimal")
        layout.addWidget(QLabel("Conversion type:"), 6, 0)
        layout.addWidget(self.conversion_combobox, 6, 1)

        self.output_file_name = QLineEdit(self)
        self.output_file_name.setText("OutputFileName")
        layout.addWidget(QLabel("Output file name:"), 7, 0)
        layout.addWidget(self.output_file_name, 7, 1)

        button_frame = QWidget(self)
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)

        convert_button = QPushButton("Convert")
        convert_button.clicked.connect(self.convert_file)
        restore_button = QPushButton("Restore")
        restore_button.clicked.connect(self.restore_file)
        about_button = QPushButton("About")
        about_button.clicked.connect(self.show_about)

        button_layout.addWidget(convert_button)
        button_layout.addWidget(restore_button)
        button_layout.addWidget(about_button)

        layout.addWidget(button_frame, 8, 0, 1, 3)

        self.result_label = QLabel("", self)
        layout.addWidget(self.result_label, 9, 0, 1, 3)

        layout.addWidget(QLabel("Selected files:"), 10, 0, 1, 3)
        self.selected_files_label = QLabel("", self)
        layout.addWidget(self.selected_files_label, 11, 0, 1, 3)

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

    def generate_time_options(self):
        now = datetime.now()
        options = []
        try:
            for day_offset in range(-3, 1):
                current_day = now + timedelta(days=day_offset)
                for hour in range(0, 24, 3):
                    time_option = current_day.replace(hour=hour, minute=0).strftime('%Y/%m/%d %H:00')
                    options.append(time_option)
            logging.info("Generated time options")
        except Exception as e:
            logging.error(f"Error generating time options: {e}")
        return options

    def convert_file(self):
        logging.info("Starting file conversion")

        selected_files = self.input_path.text().split("\n")
        if len(selected_files) > 1:
            QMessageBox.critical(self, "Error", "Please select only one file for conversion.")
            logging.error("Multiple files selected for conversion")
            return

        if not self.input_path.text():
            QMessageBox.critical(self, "Error", "Please select a compressed file.")
            logging.error("No input file selected")
            return

        if not selected_files[0].endswith(('.zip', '.txt')):
            QMessageBox.critical(self, "Error", "Unsupported file type. Please select a .zip or .txt file.")
            logging.error("Unsupported file type selected")
            return

        if not self.output_folder.text():
            QMessageBox.critical(self, "Error", "Please select an output folder.")
            logging.error("No output folder selected")
            return

        if not self.output_file_name.text().strip():
            QMessageBox.critical(self, "Error", "Output file name cannot be empty.")
            logging.error("Empty output file name")
            return

        try:
            max_line_length = int(self.max_line_length.text())
            max_file_size_kb = int(self.max_file_size.text())
        except ValueError:
            QMessageBox.critical(self, "Error", "Max line length and max file size must be valid integers.")
            logging.error("Invalid max line length or file size")
            return

        try:
            start_time = datetime.strptime(self.start_time_combobox.currentText(), '%Y/%m/%d %H:%M')
            end_time = datetime.strptime(self.end_time_combobox.currentText(), '%Y/%m/%d %H:%M')
            if start_time >= end_time:
                QMessageBox.critical(self, "Error", "Start time must be earlier than end time.")
                logging.error("Invalid time range")
                return
        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Invalid time format: {str(e)}")
            logging.error(f"Time format error: {e}")
            return

        if not os.path.exists(selected_files[0]):
            QMessageBox.critical(self, "Error", "The selected file does not exist.")
            logging.error("Selected file does not exist")
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

        try:
            if conversion_type == "Binary":
                converted_data = ' '.join(format(byte, '08b') for byte in data)
            elif conversion_type == "Decimal":
                converted_data = ' '.join(str(byte) for byte in data)
            elif conversion_type == "Hexadecimal":
                converted_data = ' '.join(format(byte, '02x') for byte in data)
            elif conversion_type == "Base64":
                converted_data = base64.b64encode(data).decode()
            logging.info("Data conversion successful")
        except Exception as e:
            logging.error(f"Error during data conversion: {e}")
            return

        wrapped_converted_data = textwrap.fill(converted_data, width=int(self.max_line_length.text()))

        output_lines = []
        wrapped_lines = wrapped_converted_data.split('\n')
        total_lines = len(wrapped_lines)

        time_delta = (end_time - start_time) / total_lines if total_lines > 0 else timedelta(0)
        previous_milliseconds = 0

        for i, line in enumerate(wrapped_lines):
            random_milliseconds = random.randint(previous_milliseconds + 1, 999) if previous_milliseconds < 999 else 999
            current_time = start_time + time_delta * i + timedelta(milliseconds=random_milliseconds)
            previous_milliseconds = random_milliseconds
            timestamp = current_time.strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]
            output_lines.append(f"{timestamp} {line.strip()}")

        output_text = "\n".join(output_lines)
        file_data = []
        current_file_size = 0
        max_file_size_kb = int(self.max_file_size.text()) * 1024
        num_files = 1

        for line in output_text.splitlines():
            file_data.append(line + "\n")
            current_file_size += len(line.encode('utf-8'))

            if current_file_size >= max_file_size_kb:
                output_file_path = os.path.join(self.output_folder.text(), f"{self.output_file_name.text()}_{num_files}.txt")
                with open(output_file_path, "w") as f:
                    f.writelines(file_data)
                logging.info(f"Saved file: {output_file_path}")
                num_files += 1
                file_data = []
                current_file_size = 0

        if file_data:
            output_file_path = os.path.join(self.output_folder.text(), f"{self.output_file_name.text()}_{num_files}.txt")
            with open(output_file_path, "w") as f:
                f.writelines(file_data)
            logging.info(f"Saved file: {output_file_path}")

        self.result_label.setText(f"Conversion successful, saved as {num_files} file(s)")
        logging.info("File conversion completed successfully")

    def restore_file(self):
        logging.info("Starting file restoration")

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

        self.result_label.setText("Restoring file, please wait...")
        self.repaint()

        combined_data = []
        for file in selected_files:
            if not os.path.exists(file):
                QMessageBox.critical(self, "Error", f"The file {file} does not exist.")
                logging.error(f"File does not exist: {file}")
                return

            try:
                with open(file, "r") as f:
                    combined_data.extend(f.readlines())
                logging.info(f"Read file: {file}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error reading file: {str(e)}")
                logging.error(f"Error reading file: {e}")
                return

        clean_data = []
        for line in combined_data:
            clean_line = re.sub(r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\.\d{3}\s+', '', line)
            clean_data.append(clean_line.strip())

        clean_data = ' '.join(clean_data)

        try:
            if all(len(b) == 8 for b in clean_data.split()):  # 二進制
                byte_data = bytearray([int(b, 2) for b in clean_data.split()])
            elif all(b.isdigit() for b in clean_data.split()):  # 十進制
                byte_data = bytearray([int(b) for b in clean_data.split()])
            elif all(all(c in '0123456789abcdefABCDEF' for c in b) and len(b) % 2 == 0 for b in clean_data.split()):  # 十六進制
                byte_data = bytearray([int(b, 16) for b in clean_data.split()])
            else:
                byte_data = base64.b64decode(clean_data)
            logging.info("Data restoration successful")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to decode data: {str(e)}")
            logging.error(f"Error decoding data: {e}")
            return

        output_path = os.path.join(self.output_folder.text(), f"{self.output_file_name.text()}.zip")
        try:
            with open(output_path, "wb") as f:
                f.write(byte_data)
            logging.info(f"Restored file saved as: {output_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error writing restored file: {str(e)}")
            logging.error(f"Error writing restored file: {e}")
            return

        self.result_label.setText(f"Restoration successful, saved as {output_path}")
        logging.info("File restoration completed successfully")

    def show_about(self):
        logging.info("Showing about dialog")
        QMessageBox.information(self, "About", 
                                "This tool converts compressed files into strings. Please send the string via email,\n"
                                "and then convert it back to the compressed file.\n"
                                "It is recommended to use the Hexadecimal mode.\n\n"
                                "Example of file compression ratio:\n"
                                "1. Original Log: 174 MB\n"
                                "2. Compressed Size: 9.24 MB\n"
                                "3. Compressed String Sizes for Different Types:\n"
                                "   Binary_output.txt: 104 MB\n"
                                "   Decimal_output.txt: 41.0 MB\n"
                                "   Hexadecimal_output.txt: 34.7 MB\n"
                                "   Base64_output.txt: 15.5 MB\n"
                                "4. Restored Size: 9.24 MB; Uncompressed Size: 174 MB\n\n"
                                "===============================================\n\n"
                                "此工具使用方式是將壓縮檔案轉換成字串，請客戶信件寄出後，\n"
                                "再將字串轉換回壓縮檔。\n"
                                "建議使用: Hexadecimal 模式\n\n"
                                "以下是檔案壓縮率的範例：\n"
                                "1. 原始Log共 174 MB\n"
                                "2. 壓縮後共 9.24 MB\n"
                                "3. 轉換字串後不同類型的壓縮：\n"
                                "   Binary_output.txt: 104 MB\n"
                                "   Decimal_output.txt: 41.0 MB\n"
                                "   Hexadecimal_output.txt: 34.7 MB\n"
                                "   Base64_output.txt: 15.5 MB\n"
                                "4. 還原後共 9.24 MB，解壓縮後共 174 MB")