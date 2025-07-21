# Thêm biến để quản lý trạng thái scanning
import threading
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import eel


thread_lock = threading.Lock()
is_running = False
class main_add_mail:
    def __init__(self, data_add_mail, index):
        scale = 0.5

        options = webdriver.ChromeOptions()
        options.add_argument(f"--force-device-scale-factor={scale}")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        self.driver = webdriver.Chrome(options=options)
        screen_width = 3840
        screen_height = 2160

        # Cấu hình scale

        # Tính số cột và hàng cần
        cols = 5
        rows = 4  # 5 x 4 = 20 cửa sổ

        # Kích thước cửa sổ thực tế = chia màn hình ra, rồi chia thêm theo scale
        window_width = int((screen_width / cols) * (1 / scale))
        window_height = int((screen_height / rows) * (1 / scale))
        # Vị trí cửa sổ
        col = index % cols
        row = index // cols
        x = int((screen_width / cols) * col)
        y = int((screen_height / rows) * row)

        # Đặt kích thước và vị trí
        self.driver.set_window_size(window_width, window_height)
        self.driver.set_window_position(x, y)

        self.driver.get("https://konto.onet.pl/en/signin?")

    def wait_and_get_text(self, xpath, timeout=10):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return element.text
        except:
            return None
        
    def wait_and_click(self, xpath, timeout=30):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            element.click()
        except Exception as e:
            print(f"Lỗi khi click vào {xpath}: {e}")

    def wait_and_send_keys(self, xpath, keys, timeout=20):
        element = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        element.clear()  # Thêm clear để đảm bảo không có text cũ
        element.send_keys(keys)

    def login(self,mail,password):
        xpath_options = [
            "/html/body/div[5]/div/div[2]/div/div[6]/button[2]",
            "/html/body/div[5]/div/div[2]/div/div[6]/button[2]",
        ]
        
        for xpath in xpath_options:
            try:
                # Kiểm tra flag dừng
                with thread_lock:
                    if not is_running:
                        print(f"Thread bị dừng, bỏ qua account: {mail}")
                        return False
                
                self.wait_and_click(xpath, timeout=10)
                click_success = True
                break
            except:
                continue

        xpath_options = [
            "/html/body/div[1]/main/div/div[1]/div[1]/div/div[1]/div/div[2]/form/div[1]/div/div[2]/div[1]/input",
            "/html/body/div[1]/main/div/div[1]/div[1]/div/div[1]/div/div[3]/form/div[1]/div/div[2]/div[1]/input",
            "/html/body/div[1]/main/div/div[1]/div[1]/div/div[1]/div/div[4]/form/div[1]/div/div[2]/div[1]/input",
        ]
        
        for xpath in xpath_options:
            try:
                # Kiểm tra flag dừng
                with thread_lock:
                    if not is_running:
                        print(f"Thread bị dừng, bỏ qua account: {mail}")
                        return False
                
                self.wait_and_send_keys(xpath,mail, timeout=10)
                click_success = True
                break
            except:
                continue

        xpath_options = [
            "/html/body/div[1]/main/div/div[1]/div[1]/div/div[1]/div/div[2]/form/div[2]/div/button",
            "/html/body/div[1]/main/div/div[1]/div[1]/div/div[1]/div/div[3]/form/div[2]/div/button",
            "/html/body/div[1]/main/div/div[1]/div[1]/div/div[1]/div/div[4]/form/div[2]/div/button",
        ]
        
        for xpath in xpath_options:
            try:
                # Kiểm tra flag dừng
                with thread_lock:
                    if not is_running:
                        print(f"Thread bị dừng, bỏ qua account: {mail}")
                        return False
                
                self.wait_and_click(xpath, timeout=10)
                click_success = True
                break
            except:
                continue
        xpath_options = [
            "/html/body/div[1]/main/div/div[1]/div[1]/div/div[1]/div/div[2]/form/div[3]/div[2]/div[1]/input",
            "/html/body/div[1]/main/div/div[1]/div[1]/div/div[1]/div/div[3]/form/div[3]/div[2]/div[1]/input",
            "/html/body/div[1]/main/div/div[1]/div[1]/div/div[1]/div/div[4]/form/div[3]/div[2]/div[1]/input",
        ]
        
        for xpath in xpath_options:
            try:
                # Kiểm tra flag dừng
                with thread_lock:
                    if not is_running:
                        print(f"Thread bị dừng, bỏ qua account: {mail}")
                        return False
                
                self.wait_and_send_keys(xpath, password, timeout=10)
                click_success = True
                break
            except:
                continue

        xpath_options = [
            "/html/body/div[1]/main/div/div[1]/div[1]/div/div[1]/div/div[2]/form/div[4]/div/button",
            "/html/body/div[1]/main/div/div[1]/div[1]/div/div[1]/div/div[3]/form/div[4]/div/button",
            "/html/body/div[1]/main/div/div[1]/div[1]/div/div[1]/div/div[4]/form/div[4]/div/button",
        ]
        
        for xpath in xpath_options:
            try:
                # Kiểm tra flag dừng
                with thread_lock:
                    if not is_running:
                        print(f"Thread bị dừng, bỏ qua account: {mail}")
                        return False
                
                self.wait_and_send_keys(xpath, password, timeout=10)
                click_success = True
                break
            except:
                continue
    def check_add(self):
        if "Nie" in self.wait_and_get_text("/html/body/div[2]/div/div[3]/div/div/div/div[2]").split():
            return False, 'Alias'
        elif "Alias" in self.wait_and_get_text("/html/body/div[2]/div/div[3]/div/div/div/div[2]").split():
            return False, "Alias"
        return True, "Success"
    def add_mail(self, mail):
        self.driver.get("https://ustawienia.poczta.onet.pl/Konto/AlternatywneAdresy")
        self.driver.get("https://ustawienia.poczta.onet.pl/Konto/AlternatywneAdresy")
        self.driver.get("https://ustawienia.poczta.onet.pl/Konto/AlternatywneAdresy")
        xpath_options = [
            "/html/body/div[2]/div/div[2]/div/div/section/div/div[2]/button",
            "/html/body/div[2]/div/div[2]/div/div/section/div/div[3]/button",
            "/html/body/div[2]/div/div[2]/div/div/section/div/div[4]/button",
        ]
        
        for xpath in xpath_options:
            try:
                # Kiểm tra flag dừng
                with thread_lock:
                    if not is_running:
                        print(f"Thread bị dừng, bỏ qua account: {mail}")
                        return False
                
                self.wait_and_click(xpath, timeout=0)
                click_success = True
                break
            except:
                continue
        self.wait_and_send_keys("/html/body/div[2]/div/div[2]/div/div/section/div/form/div[2]/div/div[1]/div/div/div/input", mail)
        self.wait_and_click("/html/body/div[2]/div/div[2]/div/div/section/div/form/div[2]/div/div[2]/div/div[2]/button")
        # Đợi 3 giây để hệ thống xử lý và hiển thị thông tin
        # input("Nhấn Enter để tiếp tục...")  # Giữ lại để xem kết quả
        check_result, message = self.check_add()
        if check_result:
            print("Đã thêm mail thành công:", mail)
            return mail, message
        else:
            print("Thêm mail thất bại:", mail, "- Lỗi:", message)
            return None, message
    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            
    def __del__(self):
        self.close()

    def main(self):
        pass

# https://ustawienia.poczta.onet.pl/Konto/AlternatywneAdresy


@eel.expose
def add_mail_process(data):
    global is_running
    try:
        print("Received data:", data)
        source_mails = data['data']['sourceMails']
        input_mails = data['data']['inputMails']
        config = data['data']['config']
        thread_count = config['threadCount']
        
        # Khởi tạo biến đếm
        processed = 0
        success = 0
        failed = 0
        mail_status = {}
        
        # Khởi tạo các instance cho từng luồng
        instances = []
        for i in range(min(thread_count, len(source_mails))):
            instance = main_add_mail(source_mails[i], i)
            instances.append(instance)
            
            # Login với mail nguồn
            instance.login(source_mails[i]['email'], source_mails[i]['password'])
            
            mail_status[source_mails[i]['email']] = {
                'status': 'Running',
                'message': 'Đang xử lý'
            }
            is_running = True
            
            # Cập nhật UI
            eel.updateAddMailProgress({
                'processed': processed,
                'success': success,
                'failed': failed,
                'mailStatus': mail_status
            })

        # Phân chia mail cần add cho các instance
        for i, input_mail in enumerate(input_mails):
            instance_index = i % len(instances)
            instance = instances[instance_index]
            
            try:
                added_mail, message = instance.add_mail(input_mail['email'])
                processed += 1
                
                if added_mail:  # Nếu thêm thành công, added_mail sẽ không phải None
                    success += 1
                    source_mail = source_mails[instance_index]['email']
                    # Chỉ lưu thông tin đầy đủ khi thêm thành công
                    input_mail['full_info'] = f"{input_mail['email']}|{input_mail['password']}|{source_mail}"
                    mail_status[source_mails[instance_index]['email']] = {
                        'status': 'Success',
                        'message': f'Đã add mail {input_mail["email"]}'
                    }
                else:
                    failed += 1
                    # Không lưu full_info khi thất bại
                    if 'full_info' in input_mail:
                        del input_mail['full_info']
                    mail_status[source_mails[instance_index]['email']] = {
                        'status': 'Failed',
                        'message': f'Thất bại - {message}'
                    }
            except Exception as e:
                failed += 1
                mail_status[source_mails[instance_index]['email']] = {
                    'status': 'Error',
                    'message': str(e)
                }

            # Cập nhật tiến trình về JavaScript
            eel.updateAddMailProgress({
                'processed': processed,
                'success': success,
                'failed': failed,
                'mailStatus': mail_status,
                'results': input_mails  # Trả về danh sách mail đã được add kèm mail nguồn
            })

        return {
            'success': True,
            'mailStatus': mail_status,
            'results': input_mails
        }
        
    except Exception as e:
        print(f"Error in add_mail_process: {str(e)}")
        return {
            'success': False,
            'message': str(e)
        }
#     try:
#         print("Received data:", data)
#         source_mails = data['data']['sourceMails']
#         input_mails = data['data']['inputMails']
#         config = data['data']['config']
        
#         # Khởi tạo biến đếm
#         processed = 0
#         success = 0
#         failed = 0
#         mail_status = {}

#         # Giả lập xử lý để test
#         for mail in source_mails:
#             processed += 1
#             # Giả định xử lý thành công
#             success += 1
#             mail_status[mail['email']] = {
#                 'success': True,
#                 'message': 'Thành công'
#             }
            
#             # Cập nhật tiến trình về JavaScript
#             eel.updateAddMailProgress({
#                 'processed': processed,
#                 'success': success,
#                 'failed': failed,
#                 'mailStatus': mail_status
#             })
#             time.sleep(1)  # Giả lập delay

#         return {
#             'success': True,
#             'mailStatus': mail_status
#         }
#     except Exception as e:
#         print(f"Error in run_add_mail: {str(e)}")
#         return {
#             'success': False,
#             'message': str(e)
#         }