import imaplib
import email
import re
import eel
import threading
import time
from email.header import decode_header
from email.utils import parsedate_to_datetime
from concurrent.futures import ThreadPoolExecutor

# Biến lưu trạng thái tài khoản
completed_accounts = set()
completed_accounts_lock = threading.Lock()
processed_accounts = set()
processed_accounts_lock = threading.Lock()

def is_account_completed(mailadd):
    with completed_accounts_lock:
        return mailadd in completed_accounts

def mark_account_completed(mailadd):
    with completed_accounts_lock:
        completed_accounts.add(mailadd)
    with processed_accounts_lock:
        processed_accounts.add(mailadd)
    print(f"[INFO] ✅ Account {mailadd} đã hoàn tất!")

def mark_account_processed(mailadd):
    with processed_accounts_lock:
        processed_accounts.add(mailadd)

class ReadOneMail:
    def __init__(self, mail_data):
        self.mail_data = mail_data
        self.mail = imaplib.IMAP4_SSL("imap.poczta.onet.pl", 993)

    def decode_mime_words(self, s):
        decoded_fragments = decode_header(s)
        return ''.join(
            fragment.decode(charset or 'utf-8') if isinstance(fragment, bytes) else fragment
            for fragment, charset in decoded_fragments
        )

    def process_mail(self, msg, body_text, body_html):
        mailadd = self.mail_data["mailadd"]
        if is_account_completed(mailadd):
            return True

        to_addr = msg.get("To", "").lower()
        mailadd_lower = mailadd.lower()
        if mailadd_lower not in to_addr:
            return False

        from_raw = msg.get("From", "Unknown")
        from_name_match = re.match(r'"?([^"<]+)"?\s*(<[^>]+>)?', from_raw)
        from_name = from_name_match.group(1).strip() if from_name_match else from_raw

        date_raw = msg.get("Date", "")
        try:
            dt = parsedate_to_datetime(date_raw)
            date_str = dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            date_str = date_raw

        subject_raw = msg.get("Subject", "")
        subject = self.decode_mime_words(subject_raw)

        match = re.search(
            r'https://www\.facebook\.com/login/recover/cancel/\?n=(\d+)&amp;id=(\d+)',
            body_html
        )
        if not match:
            match = re.search(
                r'https://www\.facebook\.com/login/recover/cancel/\?n=(\d+)&id=(\d+)',
                body_text
            )

        if match:
            n_val = match.group(1)
            id_val = match.group(2)
            
            try:
                eel.updateReadMailResult(
                    mailadd,
                    from_name,
                    date_str,
                    subject,
                    id_val,
                    n_val,
                    "✅ Đã tìm thấy code"
                )
            except Exception as e:
                print(f"[ERROR] Lỗi cập nhật UI khi tìm code: {e}")

            mark_account_completed(mailadd)
            return True

        return False

    def read_mail(self):
        mailadd = self.mail_data["mailadd"]
        if is_account_completed(mailadd):
            return

        print(f"[INFO] Bắt đầu đọc mail cho: {self.mail_data['mail']} -> {mailadd}")

        try:
            self.mail.login(self.mail_data['mail'], self.mail_data['pass'])
        except imaplib.IMAP4.error as e:
            print(f"[ERROR] Đăng nhập thất bại cho {self.mail_data['mail']}: {e}")
            try:
                eel.updateReadMailResult(
                    mailadd,
                    self.mail_data['mail'],
                    time.strftime("%Y-%m-%d %H:%M"),
                    "Lỗi đăng nhập",
                    "N/A",
                    "N/A",
                    f"❌ Lỗi đăng nhập: {e}"
                )
            except:
                pass
            mark_account_processed(mailadd)
            return

        try:
            self.mail.select('"Spo&AUI-eczno&AVs-ci"')
        except:
            try:
                self.mail.select("INBOX")
            except:
                try:
                    eel.updateReadMailResult(
                        mailadd,
                        self.mail_data['mail'],
                        time.strftime("%Y-%m-%d %H:%M"),
                        "Lỗi folder",
                        "N/A",
                        "N/A",
                        "❌ Không thể chọn thư mục mail"
                    )
                except:
                    pass
                mark_account_processed(mailadd)
                return

        status, data = self.mail.search(None, "ALL")
        if status != "OK":
            try:
                eel.updateReadMailResult(
                    mailadd,
                    self.mail_data['mail'],
                    time.strftime("%Y-%m-%d %H:%M"),
                    "Lỗi tìm mail",
                    "N/A",
                    "N/A",
                    "❌ Không thể tìm thấy mail"
                )
            except:
                pass
            mark_account_processed(mailadd)
            return

        mail_ids = data[0].split()
        mail_ids = mail_ids[-50:]  # Chỉ lấy 50 mail mới nhất
        
        found_code = False
        for i, mail_id in enumerate(reversed(mail_ids)):
            if is_account_completed(mailadd):
                found_code = True
                break

            try:
                status, msg_data = self.mail.fetch(mail_id, "(RFC822)")
                if status != "OK":
                    continue

                msg = email.message_from_bytes(msg_data[0][1])
                body_text = ""
                body_html = ""

                if msg.is_multipart():
                    for part in msg.walk():
                        ctype = part.get_content_type()
                        if ctype == "text/plain":
                            body_text += part.get_payload(decode=True).decode(
                                part.get_content_charset() or "utf-8", errors="ignore"
                            )
                        elif ctype == "text/html":
                            body_html += part.get_payload(decode=True).decode(
                                part.get_content_charset() or "utf-8", errors="ignore"
                            )
                else:
                    ctype = msg.get_content_type()
                    if ctype == "text/plain":
                        body_text = msg.get_payload(decode=True).decode(
                            msg.get_content_charset() or "utf-8", errors="ignore"
                        )
                    elif ctype == "text/html":
                        body_html = msg.get_payload(decode=True).decode(
                            msg.get_content_charset() or "utf-8", errors="ignore"
                        )

                if self.process_mail(msg, body_text, body_html):
                    found_code = True
                    break

            except Exception as e:
                print(f"[ERROR] Lỗi khi xử lý mail {mail_id} cho {mailadd}: {e}")
                continue

            time.sleep(0.05)

        try:
            self.mail.logout()
        except:
            pass

        # ĐÂY LÀ PHẦN QUAN TRỌNG: Đảm bảo tất cả account đều được update lên treeview
        if not found_code:
            print(f"[INFO] Account {mailadd} không tìm thấy code, đang update lên treeview...")
            try:
                eel.updateReadMailResult(
                    mailadd,
                    self.mail_data['mail'],
                    time.strftime("%Y-%m-%d %H:%M"),
                    "Đã check xong",
                    "N/A",
                    "N/A",
                    "❌ Không tìm thấy code"
                )
                print(f"[SUCCESS] Đã update account {mailadd} (không có code) lên treeview")
            except Exception as e:
                print(f"[ERROR] Lỗi cập nhật UI cho mail không có code {mailadd}: {e}")
            print(f"[WARNING] Không tìm thấy code cho {mailadd}")
        
        mark_account_processed(mailadd)
        print(f"[DEBUG] Account {mailadd} đã được mark processed")

@eel.expose
def start_read_mail(data):
    try:
        accounts = data.get("accounts", [])
        thread_count = data.get("thread_count", 5)

        if not accounts:
            print("⚠ Không có tài khoản để đọc!")
            eel.setButtonStatus("error")()
            return False

        with completed_accounts_lock:
            completed_accounts.clear()
        with processed_accounts_lock:
            processed_accounts.clear()

        # Debug: In ra tất cả accounts trước khi xử lý
        print(f"[DEBUG] Danh sách {len(accounts)} accounts cần xử lý:")
        for i, acc in enumerate(accounts, 1):
            print(f"  {i}. {acc['mail']} -> {acc['mailadd']}")

        print(f"[INFO] Bắt đầu đọc {len(accounts)} accounts với {thread_count} threads")

        # Tạo danh sách để theo dõi các account đã được xử lý
        all_mailaddrs = {acc["mailadd"] for acc in accounts}
        print(f"[DEBUG] Unique mailaddrs cần xử lý: {all_mailaddrs}")

        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            executor.map(lambda acc: ReadOneMail(acc).read_mail(), accounts)

        # Đợi một chút để đảm bảo tất cả threads đã hoàn thành
        time.sleep(1)

        # Debug: In ra trạng thái sau khi xử lý
        with completed_accounts_lock:
            print(f"[DEBUG] Completed accounts: {completed_accounts}")
        with processed_accounts_lock:
            print(f"[DEBUG] Processed accounts: {processed_accounts}")

        # Kiểm tra và update những account chưa được xử lý (nếu có)
        with processed_accounts_lock:
            unprocessed_accounts = all_mailaddrs - processed_accounts

        if unprocessed_accounts:
            print(f"[WARNING] Có {len(unprocessed_accounts)} accounts chưa được xử lý: {unprocessed_accounts}")
            for mailadd in unprocessed_accounts:
                try:
                    # Tìm account data tương ứng
                    account_data = next((acc for acc in accounts if acc["mailadd"] == mailadd), None)
                    if account_data:
                        print(f"[INFO] Đang update account chưa xử lý: {mailadd}")
                        eel.updateReadMailResult(
                            mailadd,
                            account_data['mail'],
                            time.strftime("%Y-%m-%d %H:%M"),
                            "Chưa xử lý",
                            "N/A",
                            "N/A",
                            "⚠️ Account chưa được xử lý"
                        )
                    else:
                        print(f"[ERROR] Không tìm thấy account data cho {mailadd}")
                except Exception as e:
                    print(f"[ERROR] Lỗi update account chưa xử lý {mailadd}: {e}")

        # Thêm debug cho những account có code nhưng chưa được update
        missing_from_treeview = []
        for acc in accounts:
            mailadd = acc["mailadd"]
            # Nếu account này đã completed nhưng không có trong treeview
            if mailadd in completed_accounts:
                # Kiểm tra xem có được update không bằng cách thử update lại
                try:
                    print(f"[INFO] Account {mailadd} đã có code, đảm bảo được update lên treeview")
                except:
                    missing_from_treeview.append(mailadd)

        print(f"✅ Hoàn tất đọc mail! Đã lấy được code cho {len(completed_accounts)}/{len(accounts)} accounts")
        print(f"[DEBUG] Số unique mailaddrs: {len(all_mailaddrs)}, Số accounts input: {len(accounts)}")
        eel.setButtonStatus("done")()
        return True

    except Exception as e:
        print(f"[ERROR] Lỗi trong start_read_mail: {e}")
        eel.setButtonStatus("error")()
        return False