import os
from selenium import webdriver
from selenium.webdriver import Edge
from selenium.webdriver.edge.options import Options

class Main:
    def __init__(self, account, index=0):
        self.index = index
        self.account = account

        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-infobars")
        options.add_argument("--start-maximized")
        options.add_argument("--window-size=375,812")
        options.add_argument("user-agent=Mozilla/5.0 ... Safari/537.36")

        # Tạo thư mục profile riêng cho từng instance
        profile_dir = os.path.abspath(f"edge_profile_{self.index}")
        options.add_argument(f"--user-data-dir={profile_dir}")

        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        }
        options.add_experimental_option("prefs", prefs)

        self.driver = Edge(options=options)

Main("dsfsdf")