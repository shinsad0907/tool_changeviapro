import eel
import threading
from time import sleep
import random
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import string

chrome_drivers = {}
uid_to_pass = {}  # Đặt ở đầu file hoặc nơi phù hợp
class main:
    def __init__(self, data_change_pass, index=0):
        self.index = index
        options = Options()
        self.auto_get_cookie = data_change_pass.get('auto_get_cookie', True)

        # Các tùy chọn như Chrome
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-infobars")
        options.add_argument("--start-maximized")
        options.add_argument("--window-size=375,812")

        # Fake User-Agent
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36")

        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        }
        options.add_experimental_option("prefs", prefs)

        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script(f"document.title = 'Chrome {self.index + 1}'")

        # Set vị trí cửa sổ
        SCREEN_WIDTH = 1920
        WINDOW_WIDTH = 400
        WINDOW_HEIGHT = 600
        COLUMNS = SCREEN_WIDTH // WINDOW_WIDTH
        row = self.index // COLUMNS
        col = self.index % COLUMNS
        x = col * WINDOW_WIDTH
        y = row * WINDOW_HEIGHT
        self.driver.set_window_position(x, y)

        def tao_mat_khau(do_dai=12, co_ky_tu_dac_biet=True):
            ky_tu = string.ascii_letters + string.digits
            if co_ky_tu_dac_biet:
                ky_tu += string.punctuation
            return ''.join(random.choice(ky_tu) for _ in range(do_dai))
        
        self.generated_pass = (
            tao_mat_khau() if data_change_pass['type_password'] == 2 else data_change_pass['password']
        )
    def wait_and_click(self, xpath, timeout=60):
        element = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        element.click()
        sleep(1.5)

    def wait_and_send_keys(self, xpath, keys, timeout=60):
        def human_typing(element, text, delay_range=(0.1, 0.3)):
            for char in text:
                element.send_keys(char)
                sleep(random.uniform(*delay_range))

        element = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        human_typing(element, keys)
    
    def wait_and_get_text(self, xpath, timeout=60):
        element = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element.text
    
    def status(self, message, color):
        uid = self.account.get("uid", "")
        eel.updateAccountStatus(uid, message, color)

    def get_cookies(self):
        return self.driver.get_cookies()
    
    def changepass(self, account):
        chrome_drivers[account['uid']] = self.driver
        self.account = account
        uid_to_pass[account['uid']] = self.generated_pass
        self.driver.get("https://m.facebook.com/login/identify/")
        eel.updateAccountStatus(account['uid'], "🔄 Đang xử lý...", "#dcdcaa")
        try:
            self.driver.get(f"https://www.facebook.com/recover/password/?u={account['uid']}&n={account['code']}&fl=default_recover&sih=0&msgr=0")
            try:
                self.wait_and_click("/html/body/div[3]/div[2]/div/div/div/div/div[3]/div[2]/div/div[2]/div[1]/div")
            except:
                pass
            self.wait_and_send_keys("/html/body/div[1]/div[1]/div[1]/div/div[2]/form/div/div[2]/div[2]/div[1]/div/input", self.generated_pass)
            self.wait_and_click("/html/body/div[1]/div[1]/div[1]/div/div[2]/form/div/div[3]/div/div[1]/button")
            self.driver.execute_script(f"document.title = 'Chrome {self.index + 1}'")
            
            if self.auto_get_cookie:
                sleep(20)
                cookies = self.get_cookies()
                # Gọi callback để cập nhật UI
                eel.onGetCookie(account['uid'], self.generated_pass, cookies)
                self.driver.quit()
                chrome_drivers.pop(account['uid'], None)
                return True, self.generated_pass, cookies
            else:
                # Không tự động lấy cookie, giữ Chrome mở
                eel.updateAccountStatus(account['uid'], "🟢 Đã đổi pass, chờ lấy cookie", "#4ec9b0")
                return True, self.generated_pass, []
        except Exception as e:
            print("Lỗi đổi mật khẩu:", e)
            eel.updateAccountStatus(account['uid'], "❌ Lỗi đổi pass", "#f44747")
            self.driver.quit()
            chrome_drivers.pop(account['uid'], None)
            return False, self.generated_pass, []

# Sửa tên function để khớp với JavaScript
@eel.expose
def thread(data_change_pass):
    print("Data nhận được:", data_change_pass)
    accounts = data_change_pass['account']
    threads = []
    for idx, acc in enumerate(accounts):
        t = threading.Thread(target=main(data_change_pass, idx).changepass, args=(acc,))
        t.start()
        threads.append(t)

# Sửa tên function để khớp với JavaScript
@eel.expose
def get_cookie_by_uid(uid):
    driver = chrome_drivers.get(uid)
    if driver:
        try:
            # Lấy cookie
            cookies = driver.get_cookies()
            # Lấy mật khẩu mới đã lưu (nếu có)
            new_pass = uid_to_pass.get(uid, "")
            # Gọi callback để cập nhật UI trước khi đóng driver
            eel.onGetCookie(uid, new_pass, cookies)
            # Đóng driver
            driver.quit()
            chrome_drivers.pop(uid, None)
            eel.updateAccountStatus(uid, "✅ Đã lấy cookie", "#4ec9b0")
            print(f"Cookies for {uid}: {cookies}")
            return cookies
        except Exception as e:
            print(f"Lỗi lấy cookie cho {uid}: {e}")
            eel.updateAccountStatus(uid, "❌ Lỗi lấy cookie", "#f44747")
            return []
    else:
        eel.updateAccountStatus(uid, "❌ Không tìm thấy Chrome", "#ce1126")
        return []

# Thêm function đóng Chrome
@eel.expose
def close_chrome_by_uid(uid):
    driver = chrome_drivers.get(uid)
    if driver:
        try:
            driver.quit()
            chrome_drivers.pop(uid, None)
            eel.updateAccountStatus(uid, "🔴 Đã đóng Chrome", "#f44747")
            print(f"Đã đóng Chrome cho {uid}")
            return True
        except Exception as e:
            print(f"Lỗi đóng Chrome cho {uid}: {e}")
            return False
    else:
        eel.updateAccountStatus(uid, "❌ Không tìm thấy Chrome", "#ce1126")
        return False
@eel.expose
def stop_all_selenium():
    print("Đang dừng tất cả Chrome Selenium...")
    for uid, driver in list(chrome_drivers.items()):
        try:
            driver.quit()
            print(f"Đã đóng Chrome cho {uid}")
        except Exception as e:
            print(f"Lỗi đóng Chrome cho {uid}: {e}")
        chrome_drivers.pop(uid, None)
    # Cập nhật trạng thái trên UI
    eel.updateAccountStatus("ALL", "🔴 Đã dừng tất cả Chrome", "#f44747")