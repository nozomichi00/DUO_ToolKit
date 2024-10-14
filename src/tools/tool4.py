from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QDateEdit, QLineEdit, QMessageBox, QScrollArea
from PyQt6.QtCore import Qt, QDate
import logging
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import json

class Tool4(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        logging.info("Initializing Tool4")
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

        self.outlook_account_label = QLabel("Outlook Account:", self)
        self.outlook_account_input = QLineEdit(self)
        self.outlook_account_input.setPlaceholderText("lucas_lan")
        layout.addWidget(self.outlook_account_label, 0, 0)
        layout.addWidget(self.outlook_account_input, 0, 1)

        self.outlook_password_label = QLabel("Outlook Password:", self)
        self.outlook_password_input = QLineEdit(self)
        self.outlook_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.outlook_password_label, 1, 0)
        layout.addWidget(self.outlook_password_input, 1, 1)

        self.copy_date_label = QLabel("Select Date to Copy:", self)
        self.copy_date_edit = QDateEdit(self)
        self.copy_date_edit.setCalendarPopup(True)
        self.copy_date_edit.setDate(QDate.currentDate().addDays(-1))
        layout.addWidget(self.copy_date_label, 2, 0)
        layout.addWidget(self.copy_date_edit, 2, 1)

        self.fill_date_label = QLabel("Select Date to Fill:", self)
        self.fill_date_edit = QDateEdit(self)
        self.fill_date_edit.setCalendarPopup(True)
        self.fill_date_edit.setDate(QDate.currentDate())
        layout.addWidget(self.fill_date_label, 3, 0)
        layout.addWidget(self.fill_date_edit, 3, 1)

        button_frame = QWidget(self)
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)

        execute_button = QPushButton("Execute Copy")
        execute_button.clicked.connect(self.execute_copy)
        about_button = QPushButton("About")
        about_button.clicked.connect(self.show_about)

        button_layout.addWidget(execute_button)
        button_layout.addWidget(about_button)

        layout.addWidget(button_frame, 4, 0, 1, 2)

        self.result_label = QLabel("", self)
        layout.addWidget(self.result_label, 5, 0, 1, 2)

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
            QLineEdit, QDateEdit {
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

    def execute_copy(self):
        logging.info("Execute copy function called")
        
        # 前置檢查
        allowed_ips = ["175.98.153.34", "60.251.209.66"]
        try:
            response = requests.get('https://api.ipify.org?format=json', timeout=10)
            response.raise_for_status()
            external_ip = response.json().get('ip', '')
        except requests.RequestException as e:
            logging.error(f"Error obtaining external IP: {e}")
            QMessageBox.critical(self, "錯誤", "無法獲取外部IP地址。")
            return
        
        if external_ip not in allowed_ips:
            QMessageBox.critical(self, "權限錯誤", f"請連接公司VPN才有權限訪問WRS系統。當前IP: {external_ip}")
            logging.error(f"Unauthorized access attempt from IP: {external_ip}")
            return

        if not self.outlook_account_input.text().strip():
            QMessageBox.critical(self, "錯誤", "請輸入Outlook帳號。")
            logging.error("Outlook account not provided")
            return

        if not self.outlook_password_input.text().strip():
            QMessageBox.critical(self, "錯誤", "請輸入Outlook密碼。")
            logging.error("Outlook password not provided")
            return

        copy_date = self.copy_date_edit.date().toString("yyyy/MM/dd")
        fill_date = self.fill_date_edit.date().toString("yyyy/MM/dd")
        if copy_date >= fill_date:
            QMessageBox.critical(self, "錯誤", "複製日期必須早於填寫日期。")
            logging.error("Invalid date range: copy date is not earlier than fill date")
            return

        # 執行複製
        try:
            service = Service(executable_path=os.path.join('bin', 'chromedriver.exe'))
            driver = webdriver.Chrome(service=service)
            driver.get("http://setw-eep:7890/#/Login?RefType=logout")

            # 等待頁面加載並輸入帳號和密碼
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "userAccount"))).send_keys(self.outlook_account_input.text())
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "passwords"))).send_keys(self.outlook_password_input.text())
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".MuiButtonBase-root[type='submit']"))).click()

            # 檢查是否成功登入
            try:
                WebDriverWait(driver, 5).until(EC.url_contains("http://setw-eep:7890/#/WorkingHours/PersonalWeeklyReview"))
                logging.info("Login successful")
            except:
                logging.error("Login failed")
                QMessageBox.critical(self, "錯誤", "登入失敗，請檢查帳號和密碼。")
                driver.quit()
                return

            # 轉移到新增報工頁面
            driver.get("http://setw-eep:7890/#/WorkingHours/AddWH")
            time.sleep(2)

            # 填寫日期
            start_date_input = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, ":re:")))
            start_date_input.clear()
            start_date_input.send_keys(copy_date)
            time.sleep(2)  # 等待系統更新

            end_date_input = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, ":rg:")))
            end_date_input.clear()
            end_date_input.send_keys(fill_date)
            time.sleep(2)  # 等待系統更新

            # 取得資料
            try:
                # 等待表格加載完成
                table = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".MuiTable-root"))
                )

                # 提取表格行
                rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")

                # 整理數據
                data = []
                for row in rows:
                    cells = row.find_elements(By.CSS_SELECTOR, "td")
                    row_data = {
                        "Edit": cells[0].text,
                        "Category": cells[1].text,
                        "Location": cells[2].text,
                        "Case": cells[3].text,
                        "Workday": cells[4].text,
                        "Begin/End": cells[5].text,
                        "Subject": cells[6].text,
                        "Content": cells[7].text,
                    }
                    data.append(row_data)

                # 將數據轉換為 JSON 格式
                json_data = json.dumps(data, ensure_ascii=False, indent=4)
                logging.info("Data extracted successfully")
                logging.info(json_data)

            except Exception as e:
                logging.error(f"Error extracting data: {e}")
                QMessageBox.critical(self, "錯誤", "無法提取表格數據。")
                driver.quit()
                return

        except Exception as e:
            logging.error(f"Error during login or navigation: {e}")
            driver.quit()
            QMessageBox.critical(self, "錯誤", "操作失敗，請檢查帳號密碼是否錯誤。")
            return
        
        # 完成通知
        QMessageBox.information(self, "Execute Copy", "This function will execute the copy operation.")

    def show_about(self):
        logging.info("Showing about dialog")
        QMessageBox.information(self, "About", 
                                "選擇要複製的日期，執行後會將該日期的WRS內容全部複製到指定天數。")