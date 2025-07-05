from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import eel
import threading
import time
import os
# Hàm chuyển cookie string thành danh sách dict
def convert_cookie_string_to_list(cookie_str):
    cookies = []
    for part in cookie_str.split(';'):
        if '=' in part:
            name, value = part.strip().split('=', 1)
            cookies.append({'name': name.strip(), 'value': value.strip()})
    return cookies

# Lớp xử lý scan friend
class main_scan_friend:
    def __init__(self, data_scan_friend, index):
        self.index = index
        options = Options()
        options.add_argument("--window-size=800,600")
        options.add_argument("--force-device-scale-factor=0.5")
        options.add_argument("--high-dpi-support=1")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-infobars")
        options.add_argument("--start-maximized")
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        }
        options.add_experimental_option("prefs", prefs)
        SCREEN_WIDTH = 1920
        SCREEN_HEIGHT = 1080

        WINDOW_WIDTH = 480
        WINDOW_HEIGHT = 400


        COLUMNS = SCREEN_WIDTH // WINDOW_WIDTH
        MARGIN = 0  # có thể thêm margin nếu muốn cách ra

        row = self.index // COLUMNS
        col = self.index % COLUMNS

        x = col * (WINDOW_WIDTH + MARGIN)
        y = row * (WINDOW_HEIGHT + MARGIN)
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_window_position(x, y)
        self.driver.get("https://www.facebook.com")

    def login(self, cookie):
        for c in cookie:
            c["domain"] = ".facebook.com"
            self.driver.add_cookie(c)
        self.driver.refresh()

    def wait_and_get_text(self, xpath, timeout=10):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return element.text
        except:
            return None

    
    def open_friend_list(self, uid):
        self.driver.get(f"https://www.facebook.com/{uid}")

    def get_sources(self, uid=None):
        page_source = self.driver.page_source
        return page_source

    def get_friend_from_source(self, source):
        try:
            return source.split('[{"length":1,"offset":0,"inline_style":"BOLD"}],"aggregated_ranges":[],"ranges":[],"color_ranges":[],"text":"')[1].split(' znajomy"')[0]
        except:
            return "UNKNOWN"

# Hàm chính scan
@eel.expose
def thread_scan_friend(data_scan_friend):
    print("Data nhận được:", data_scan_friend)

    accounts = data_scan_friend['account']
    uid_list = data_scan_friend['uidList']
    delay = data_scan_friend.get('delay', 1000) / 1000  # ms -> s
    max_threads = min(data_scan_friend.get('thread', 3), len(accounts))

    threads = []

    # Phân chia UID theo số account (luồng)
    uid_chunks = [[] for _ in range(max_threads)]
    for i, uid in enumerate(uid_list):
        uid_chunks[i % max_threads].append(uid)

    # Hàm chạy từng luồng
    def scan_uid_list(uid_sublist, acc, idx):
        print(f"[Thread {idx}] Bắt đầu với {len(uid_sublist)} UID bằng account UID={acc['uid']}")
        instance = main_scan_friend(data_scan_friend, idx)

        # Đăng nhập nếu có cookie
        if acc.get('cookie'):
            cookies = convert_cookie_string_to_list(acc['cookie'])
            instance.login(cookies)
            time.sleep(2)

        for uid in uid_sublist:
            try:
                print(f"[Thread {idx}] Đang mở bạn bè UID: {uid}")
                instance.open_friend_list(uid)
                time.sleep(2)

                # Kiểm tra trang die
                check_xpath = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div[1]/h2/span"
                text_check = instance.wait_and_get_text(check_xpath, timeout=5)

                if text_check == "Te materiały nie są teraz dostępne":
                    eel.statusscan(uid, '956', "#f44747")  # Profile die
                    continue

                source = instance.get_sources(uid)
                friend = instance.get_friend_from_source(source)

                if friend == "UNKNOWN":
                    eel.statusscan(uid, '000', "#4ec9b0")  # Không có bạn bè
                else:
                    eel.updateAccountStatus(uid, friend, "#4ec9b0")

            except Exception as e:
                print(f"[Thread {idx}] Lỗi xử lý UID {uid}: {e}")
                eel.statusscan(uid, 'ERR', "#f44747")
            time.sleep(delay)


    # Tạo luồng ứng với mỗi account
    for i in range(max_threads):
        acc = accounts[i]
        t = threading.Thread(target=scan_uid_list, args=(uid_chunks[i], acc, i))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
