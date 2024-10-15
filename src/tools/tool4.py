from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QDateEdit, QLineEdit, QMessageBox, QScrollArea
from PyQt6.QtCore import Qt, QDate
import logging
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import os
import time
import pandas as pd
from bs4 import BeautifulSoup

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

        self.wrs_account_label = QLabel("WRS Account:", self)
        self.wrs_account_input = QLineEdit(self)
        self.wrs_account_input.setPlaceholderText("lucas_lan")
        layout.addWidget(self.wrs_account_label, 0, 0)
        layout.addWidget(self.wrs_account_input, 0, 1)

        self.wrs_password_label = QLabel("WRS Password:", self)
        self.wrs_password_input = QLineEdit(self)
        self.wrs_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.wrs_password_label, 1, 0)
        layout.addWidget(self.wrs_password_input, 1, 1)

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

        if not self.wrs_account_input.text().strip():
            QMessageBox.critical(self, "錯誤", "請輸入WRS帳號。")
            logging.error("WRS account not provided")
            return

        if not self.wrs_password_input.text().strip():
            QMessageBox.critical(self, "錯誤", "請輸入WRS密碼。")
            logging.error("WRS password not provided")
            return

        copy_date = self.copy_date_edit.date().toString("yyyy/MM/dd")
        fill_date = self.fill_date_edit.date().toString("yyyy/MM/dd")
        if copy_date >= fill_date:
            QMessageBox.critical(self, "錯誤", "複製日期必須早於填寫日期。")
            logging.error("Invalid date range: copy date is not earlier than fill date")
            return

        try:
            # Set window size
            options = Options()
            options.add_argument("--window-size=1400,900")

            service = Service(executable_path=os.path.join('bin', 'chromedriver.exe'))
            driver = webdriver.Chrome(service=service, options=options)
            
            # Step 1: Login
            try:
                driver.get("http://setw-eep:7890/#/Login?RefType=logout")

                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "userAccount"))).send_keys(self.wrs_account_input.text())
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "passwords"))).send_keys(self.wrs_password_input.text())
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".MuiButtonBase-root[type='submit']"))).click()

                WebDriverWait(driver, 5).until(EC.url_contains("http://setw-eep:7890/#/WorkingHours/PersonalWeeklyReview"))
                logging.info("Login successful")
            except Exception as e:
                logging.error(f"Login failed: {e}")
                QMessageBox.critical(self, "錯誤", "登入失敗，請檢查帳號和密碼。")
                driver.quit()
                return

            # Step 2: Set Dates
            try:
                driver.get("http://setw-eep:7890/#/WorkingHours/AddWH")
                time.sleep(3)

                copy_day = int(copy_date.split('/')[2])

                start_date_button = driver.find_element(By.XPATH, "//*[@id='root']/div/div/main/div[2]/div[1]/div/div/div[1]/div/div/div/button")
                start_date_button.click()
                time.sleep(1)
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "MuiCalendarPicker-root")))
                start_day_button = driver.find_element(By.XPATH, f"//button[text()='{copy_day}']")
                start_day_button.click()
                time.sleep(2)

                end_date_button = driver.find_element(By.XPATH, "//*[@id='root']/div/div/main/div[2]/div[1]/div/div/div[3]/div/div/div/button")
                end_date_button.click()
                time.sleep(1)
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "MuiCalendarPicker-root")))
                end_day_button = driver.find_element(By.XPATH, f"//button[text()='{copy_day}']")
                end_day_button.click()
                time.sleep(2)

                driver.refresh()

                with open("modified_page.html", "w", encoding="utf-8") as file:
                    file.write(driver.page_source)
                logging.info("HTML content saved to modified_page.html")
                time.sleep(1)
            except Exception as e:
                logging.error(f"Error setting dates: {e}")
                QMessageBox.critical(self, "錯誤", f"日期設置失敗。")
                driver.quit()
                return

            # Step 3: Analyze and Create Reports
            try:
                with open("modified_page.html", "r", encoding="utf-8") as file:
                    soup = BeautifulSoup(file, "html.parser")
                    table = soup.find("table", {"class": "MuiTable-root"})
                    rows = table.find_all("tr")

                    data = []
                    for row in rows:
                        cells = row.find_all("td")
                        if cells:
                            row_data = [cell.get_text(separator="\n", strip=True) for cell in cells]
                            data.append(row_data)

            except Exception as e:
                logging.error(f"Error analyzing data or creating reports: {e}")
                QMessageBox.critical(self, "錯誤", "分析數據時出錯。")
                driver.quit()
                return
            
            # Step 4: Create Reports
            try:
                for row_data in data:
                    category = row_data[1]
                    category_parts = category.split("\\")

                    # 點擊新增日報按鈕
                    new_report_button = driver.find_element(By.XPATH, "//*[@id='root']/div/div/main/div[4]/button[1]")
                    new_report_button.click()
                    time.sleep(2)

                    # 點擊Category1選擇器
                    category1_selector = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[3]/div[2]/div[1]/div[1]/div/div[1]/div/div"))
                    )
                    category1_selector.click()
                    time.sleep(1)
                    if category_parts[0] == "有CRM":
                        crm_option = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//li[@data-value='1']"))
                        )
                        driver.execute_script("arguments[0].click();", crm_option)
                    elif category_parts[0] == "無CRM":
                        no_crm_option = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//li[@data-value='2']"))
                        )
                        driver.execute_script("arguments[0].click();", no_crm_option)
                    time.sleep(1)

                    # 點擊Category2選擇器
                    category2_selector = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[3]/div[2]/div[1]/div[1]/div/div[2]/div/div"))
                    )
                    category2_selector.click()
                    time.sleep(1)
                    category2_value_map = {
                        "Case": "3",
                        "Installation": "4",
                        "技術相關": "5",
                        "資料作成": "6",
                        "教育訓練": "7",
                        "會議": "8",
                        "待機": "9",
                        "移動": "10",
                        "On site": "11",
                        "Others": "12",
                        "用餐時間": "73"
                    }
                    category2_value = category2_value_map.get(category_parts[1], None)
                    if category2_value:
                        category2_option = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, f"//li[@data-value='{category2_value}']"))
                        )
                        driver.execute_script("arguments[0].click();", category2_option)
                        time.sleep(1)
                    else:
                        logging.error(f"Invalid category part: {category_parts[1]}")
                        QMessageBox.critical(self, "錯誤", f"無效的Category2選項: {category_parts[1]}")
                        driver.quit()
                        return
                    
                    # 點擊Category3選擇器
                    if category_parts[1] not in ["On site", "Others", "用餐時間"]:
                        category3_selector = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[3]/div[2]/div[1]/div[1]/div/div[3]/div/div"))
                        )
                        category3_selector.click()
                        time.sleep(1)

                        # 建立清單
                        category3_value_map = {
                            "會議資料": "40",
                            "其它": "41",
                            "工作日報": "42",
                            "表單申請": "43",
                            "Periodic maintenance": "21",
                            "Design change": "22",
                            "Question": "23",
                            "Problem": "24",
                            "Request": "25",
                            "MQFC": "26",
                            "Tool install": "27",
                            "Demolition": "28",
                            "Product backlog": "29",
                            "Design validation": "30",
                            "Modification": "31",
                            "H/W作業前後置": "35",
                            "S/W作業前後置": "36",
                            "現場作業": "37",
                            "客戶技術指導": "38",
                            "零件/圖面/倉庫整理": "39",
                            "P/E作業前後置": "78",
                            "證件製作": "44",
                            "教育訓練": "45",
                            "竹南教育訓練中心": "46",
                            "與客戶": "47",
                            "與公司內部": "48",
                            "廠商": "49",
                            "客戶端": "50",
                            "公司內": "51",
                            "客戶/Office": "52",
                            "廠商/其他據點": "53",
                            "FI/FO": "76"
                        }

                        category3_value = category3_value_map.get(category_parts[2], None)
                        if category3_value:
                            category3_option = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, f"//li[@data-value='{category3_value}']"))
                            )
                            driver.execute_script("arguments[0].click();", category3_option)
                            time.sleep(1)
                        else:
                            logging.error(f"Invalid category part: {category_parts[2]}")
                            QMessageBox.critical(self, "錯誤", f"無效的Category3選項: {category_parts[2]}")
                            driver.quit()
                            return
                    else:
                        logging.error(f"Invalid category part: {category_parts[1]}")
                        QMessageBox.critical(self, "錯誤", f"無效的Category3選項: {category_parts[1]}")
                        driver.quit()
                        return
                    
                    # CRM Number
                    if category_parts[0] == "有CRM":
                        crm_number_input = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[3]/div[2]/div[1]/div[2]/div/div/input"))
                        )
                        crm_number_input.click()
                        time.sleep(1)
                        actions = ActionChains(driver)
                        actions.send_keys(row_data[3])
                        actions.perform()
                        time.sleep(1)

                    # 選擇建立日期
                    fill_day = int(fill_date.split('/')[2])
                    fill_date_button = driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[2]/div[1]/div[4]/div/div[1]/div/div/div/button")
                    fill_date_button.click()
                    time.sleep(1)
                    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "MuiCalendarPicker-root")))
                    fill_day_button = driver.find_element(By.XPATH, f"//button[text()='{fill_day}']")
                    fill_day_button.click()
                    time.sleep(2)

                    # 取得起始時間跟結束時間
                    time_range = row_data[5].split()[0]
                    start_time, end_time = time_range.split("~")
                    start_hour, start_minute = map(int, start_time.split(":"))
                    end_hour, end_minute = map(int, end_time.split(":"))

                    # 選擇起始時間
                    start_time_button = driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[2]/div[1]/div[5]/div/div[2]/div/div/div/button")
                    start_time_button.click()

                    WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.CLASS_NAME, "MuiClock-clock"))
                    )
                    start_hour_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, f"//span[@aria-label='{start_hour} hours']")))
                    actions = ActionChains(driver)
                    actions.move_to_element(start_hour_element).click().perform()
                    time.sleep(1)
                
                    start_minute_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, f"//span[@aria-label='{start_minute} minutes']")))
                    actions = ActionChains(driver)
                    actions.move_to_element(start_minute_element).click().perform()
                    time.sleep(1)

                    # 選擇結束時間
                    end_time_button = driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[2]/div[1]/div[5]/div/div[4]/div/div/div/button")
                    end_time_button.click()

                    WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.CLASS_NAME, "MuiClock-clock"))
                    )
                    end_hour_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, f"//span[@aria-label='{end_hour} hours']")))
                    actions = ActionChains(driver)
                    actions.move_to_element(end_hour_element).click().perform()
                    time.sleep(1)
                    print(f"選擇了結束時間{end_hour}")

                    # 這裡卡住
                    end_minute_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, f"//span[@aria-label='{end_minute} minutes']")))
                    actions = ActionChains(driver)
                    actions.move_to_element(end_minute_element).click().perform()
                    time.sleep(1)
                    print(f"選擇了結束時間{end_minute}")

                    # 填寫標題
                    title_input = driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[2]/div[2]/div[1]/div/div/input")
                    title_input.send_keys(row_data[6])
                    time.sleep(1)

                    # 填寫內容
                    content_textarea = driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[2]/div[2]/div[2]/div/div/textarea[1]")
                    content_textarea.send_keys(row_data[7])
                    time.sleep(1)

                    # 儲存
                    save_button = driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[2]/div[2]/div[3]/div[2]/button[1]")
                    save_button.click()
                    time.sleep(1)

                QMessageBox.critical(self, "通知", "完成。")

            except Exception as e:
                logging.error(f"Error analyzing data or creating reports: {e}")
                QMessageBox.critical(self, "錯誤", "日報新增時出錯。")
                driver.quit()
                return
            
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            driver.quit()
            QMessageBox.critical(self, "錯誤", "操作失敗。")
            return
        
        QMessageBox.information(self, "Execute Copy", "This function will execute the copy operation.")

    def show_about(self):
        logging.info("Showing about dialog")
        QMessageBox.information(self, "About", 
                                "選擇要複製的日期，執行後會將該日期的WRS內容全部複製到指定天數。")
