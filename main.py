

import json
import time
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
from threading import Thread
import base64
import os
import hashlib
from pathlib import Path
from dotenv import load_dotenv, set_key, find_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/tasks',
    'https://www.googleapis.com/auth/calendar'
]

# Version
APP_VERSION = "v2.3.3"
APP_DATE = "2025-12-31"


def get_credentials():
    creds = None
    try:
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    except Exception:
        pass

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Support both dev and bundled exe paths for credentials
            if getattr(sys, 'frozen', False):
                # Running as compiled exe - check bundled location first
                base_path = sys._MEIPASS
                cred_path = os.path.join(base_path, 'credentials.json')
                if not os.path.exists(cred_path):
                    # Fallback to current directory
                    cred_path = 'credentials.json'
            else:
                # Running as script
                cred_path = 'credentials.json'
            
            flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())

    return creds

def get_tasks_service(creds):
    return build('tasks', 'v1', credentials=creds)

def get_calendar_service(creds):
    return build('calendar', 'v3', credentials=creds)

def list_tasks(service, tasklist_id='@default', log_callback=None):
    """Lấy TẤT CẢ tasks từ Google Tasks (bao gồm cả completed và hidden)"""
    all_tasks = []
    page_token = None
    log = log_callback if log_callback else print
    
    while True:
        try:
            result = service.tasks().list(
                tasklist=tasklist_id,
                showCompleted=True,
                showHidden=True,
                maxResults=100,  # Lấy tối đa mỗi lần
                pageToken=page_token
            ).execute()
            
            tasks = result.get('items', [])
            all_tasks.extend(tasks)
            
            # Lấy page token để lấy tiếp trang sau
            page_token = result.get('nextPageToken')
            if not page_token:
                break  # Hết tasks rồi
                
        except Exception as e:
            log(f"❌ Lỗi khi lấy tasks: {e}")
            break
    
    log(f"📊 Đã tải {len(all_tasks)} tasks từ Google Tasks API")
    return all_tasks

def get_existing_tasks_dict(service, tasklist_id='@default', log_callback=None):
    """Lấy tất cả tasks hiện có và cache thành dict để tra cứu nhanh"""
    tasks = list_tasks(service, tasklist_id, log_callback)
    log = log_callback if log_callback else print
    # Trả về dict với key là "title|date" để kiểm tra chính xác
    tasks_dict = {}
    for task in tasks:
        title = task.get('title')
        if not title:
            continue
        # Lấy ngày due, format: 2025-12-31T23:59:59.000Z -> 2025-12-31
        due = task.get('due', '')
        date = due[:10] if due else 'NO_DATE'
        key = f"{title}|{date}"
        tasks_dict[key] = task
    log(f"✓ Đã tạo dictionary với {len(tasks_dict)} tasks duy nhất")
    return tasks_dict

def is_task_added(existing_tasks_dict, title, date):
    """Kiểm tra task đã tồn tại từ dict đã cache (so sánh cả title và date)"""
    key = f"{title}|{date}"
    exists = key in existing_tasks_dict
    # Debug: in ra để kiểm tra (chỉ in khi tìm thấy)
    if exists:
        print(f"[DEBUG] Task đã tồn tại: {key}")
    return exists

def add_task(service, title, due_date, note=None, tasklist_id='@default'):
    task_body = {
        'title': title,
        'due': due_date + 'T23:59:59.000Z',
    }
    if note:
        task_body['notes'] = note
    try:
        service.tasks().insert(tasklist=tasklist_id, body=task_body).execute()
        print(f"[OK] Đã thêm task: {title} | {due_date}")
        return True
    except Exception as e:
        print(f"[ERR] Lỗi khi thêm task {title}: {e}")
        return False

def remove_duplicate_tasks(service, tasklist_id='@default', log_callback=None):
    """Xóa các task trùng lặp (cùng title và due date), giữ lại task cũ nhất"""
    log = log_callback if log_callback else print
    try:
        log("\n🔍 Bắt đầu quét tasks trùng lặp...")
        tasks = list_tasks(service, tasklist_id, log_callback)
        
        if len(tasks) == 0:
            log("⚠ Không có tasks nào để kiểm tra")
            return 0
        
        # Nhóm tasks theo key "title|date"
        log("🔄 Đang phân tích và nhóm tasks...")
        task_groups = {}
        for task in tasks:
            title = task.get('title')
            if not title:
                continue
            due = task.get('due', '')
            date = due[:10] if due else 'NO_DATE'
            key = f"{title}|{date}"
            
            if key not in task_groups:
                task_groups[key] = []
            task_groups[key].append(task)
        
        log(f"✓ Đã phân tích thành {len(task_groups)} nhóm tasks")
        
        # Xóa các task trùng (giữ lại task đầu tiên - task cũ nhất)
        deleted_count = 0
        duplicate_groups = 0
        
        log("\n🗑️ Bắt đầu xóa tasks trùng lặp...")
        for key, group in task_groups.items():
            if len(group) > 1:
                duplicate_groups += 1
                # Rút ngắn title nếu quá dài
                display_title = key.split('|')[0]
                if len(display_title) > 40:
                    display_title = display_title[:37] + "..."
                log(f"\n⚠ Tìm thấy {len(group)} tasks trùng:")
                log(f"   📌 {display_title}")
                log(f"   📅 Ngày: {key.split('|')[1]}")
                
                # Giữ lại task đầu tiên, xóa các task còn lại
                for idx, task in enumerate(group[1:], 1):
                    task_id = task.get('id')
                    try:
                        service.tasks().delete(tasklist=tasklist_id, task=task_id).execute()
                        log(f"   ✓ Đã xóa task trùng #{idx}")
                        deleted_count += 1
                    except Exception as e:
                        log(f"   ✗ Lỗi xóa task #{idx}: {e}")
        
        log("\n" + "="*60)
        if duplicate_groups == 0:
            log("✅ Không tìm thấy tasks trùng lặp!")
        else:
            log(f"✅ Hoàn thành! Tìm thấy {duplicate_groups} nhóm trùng")
            log(f"✅ Đã xóa thành công {deleted_count}/{deleted_count} tasks trùng lặp")
        log("="*60)
        return deleted_count
    except Exception as e:
        log(f"\n❌ Lỗi khi xóa tasks trùng: {e}")
        import traceback
        log(traceback.format_exc())
        return 0

def get_study_calendar_id(service):
    calendars = service.calendarList().list().execute().get('items', [])
    for cal in calendars:
        if cal.get('summary') == 'Study' or cal.get('summary') == 'Studys':  # tên lịch
            return cal.get('id')
    
    # Nếu không tìm thấy, trả về primary calendar (lịch mặc định)
    print("[WARN] Không tìm thấy calendar tên 'Study', sẽ sử dụng lịch mặc định")
    return 'primary'


def get_existing_events_dict(service, calendar_id, start_date=None, end_date=None):
    """Lấy tất cả events trong khoảng thời gian và cache thành dict"""
    # Nếu không có ngày bắt đầu/kết thúc, lấy từ đầu năm đến cuối năm
    if not start_date:
        start_date = f"{datetime.now().year}-01-01"
    if not end_date:
        end_date = f"{datetime.now().year}-12-31"
    
    start_datetime = f"{start_date}T00:00:00+07:00"
    end_datetime = f"{end_date}T23:59:59+07:00"

    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=start_datetime,
        timeMax=end_datetime,
        singleEvents=True,
        orderBy='startTime',
        maxResults=2500  # Lấy nhiều events
    ).execute()

    events = events_result.get('items', [])
    # Tạo dict với key là "title|date" để kiểm tra chính xác
    events_dict = {}
    for event in events:
        title = event.get('summary', '')
        start = event.get('start', {})
        date = start.get('date') or start.get('dateTime', '')[:10]
        key = f"{title}|{date}"
        events_dict[key] = event
    
    return events_dict

def is_event_added(existing_events_dict, title, date):
    """Kiểm tra event đã tồn tại từ dict đã cache"""
    key = f"{title}|{date}"
    return key in existing_events_dict

def add_event(service, title, date, url, calendar_id):
    event_body = {
        'summary': title,
        'description': f'Sự kiện lấy từ UTH: {url}',
        'start': {
            'date': date,
            'timeZone': 'Asia/Ho_Chi_Minh',
        },
        'end': {
            'date': date,
            'timeZone': 'Asia/Ho_Chi_Minh',
        }
    }
    try:
        result = service.events().insert(calendarId=calendar_id, body=event_body).execute()
        print(f"[OK] Đã thêm sự kiện: {title} | {date} | Link: {result.get('htmlLink')}")
        return True
    except Exception as e:
        print(f"[ERR] Lỗi khi thêm sự kiện {title}: {e}")
        return False



def get_machine_key():
    """Tạo key duy nhất dựa trên máy tính"""
    try:
        # Sử dụng tên máy + username làm seed
        machine_info = f"{os.environ.get('COMPUTERNAME', 'default')}{os.environ.get('USERNAME', 'user')}"
        key = hashlib.sha256(machine_info.encode()).digest()
        return base64.urlsafe_b64encode(key)
    except:
        # Fallback key nếu không lấy được thông tin máy
        return base64.urlsafe_b64encode(b'uth_default_key_2025')

def encrypt_data(data):
    """Mã hóa dữ liệu với XOR cipher + base64"""
    try:
        key = get_machine_key()
        # Convert data to bytes
        data_bytes = data.encode('utf-8')
        # XOR encryption
        encrypted = bytearray()
        for i, byte in enumerate(data_bytes):
            encrypted.append(byte ^ key[i % len(key)])
        # Base64 encode
        encoded = base64.b64encode(bytes(encrypted)).decode('utf-8')
        return encoded
    except Exception as e:
        print(f"[ERR] Lỗi mã hóa: {e}")
        return None

def decrypt_data(data):
    """Giải mã dữ liệu"""
    try:
        key = get_machine_key()
        # Base64 decode
        decoded = base64.b64decode(data.encode('utf-8'))
        # XOR decryption
        decrypted = bytearray()
        for i, byte in enumerate(decoded):
            decrypted.append(byte ^ key[i % len(key)])
        return bytes(decrypted).decode('utf-8')
    except Exception as e:
        print(f"[ERR] Lỗi giải mã: {e}")
        return None

def save_uth_login(mssv, password, filename=".env"):
    """Lưu thông tin đăng nhập đã mã hóa vào .env"""
    try:
        encrypted_mssv = encrypt_data(mssv)
        encrypted_pass = encrypt_data(password)
        
        if encrypted_mssv and encrypted_pass:
            # Tạo file .env nếu chưa có
            env_path = Path(filename)
            if not env_path.exists():
                env_path.touch()
                try:
                    os.chmod(env_path, 0o600)  # rw------- chỉ owner
                except:
                    pass
            
            # Lưu vào .env
            set_key(env_path, "UTH_MSSV_ENCRYPTED", encrypted_mssv)
            set_key(env_path, "UTH_PASSWORD_ENCRYPTED", encrypted_pass)
            set_key(env_path, "CREDENTIAL_VERSION", "1.3")
            
            print(f"[OK] Đã lưu thông tin đăng nhập vào .env (mã hóa)")
            return True
    except Exception as e:
        print(f"[ERR] Lỗi lưu thông tin đăng nhập: {e}")
    return False

def load_uth_login(filename=".env"):
    """Đọc thông tin đăng nhập từ .env"""
    try:
        env_path = Path(filename)
        if not env_path.exists():
            return None, None
        
        # Load .env file
        load_dotenv(env_path)
        
        encrypted_mssv = os.getenv("UTH_MSSV_ENCRYPTED", "")
        encrypted_pass = os.getenv("UTH_PASSWORD_ENCRYPTED", "")
        
        if not encrypted_mssv or not encrypted_pass:
            return None, None
            
        mssv = decrypt_data(encrypted_mssv)
        password = decrypt_data(encrypted_pass)
        
        if mssv and password:
            return mssv, password
    except Exception as e:
        print(f"[ERR] Lỗi đọc file đăng nhập: {e}")
    return None, None


class RoundedButton(tk.Canvas):
    """Button với góc bo tròn"""
    def __init__(self, parent, text, command=None, radius=10, padding=10, bg_color="#018486", 
                 fg_color="white", hover_color="#016668", font=("Segoe UI", 10, "bold"), **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.command = command
        self.radius = radius
        self.padding = padding
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_color = hover_color
        self.font = font
        self.text = text
        
        self.config(highlightthickness=0, bg=parent.cget('bg'))
        
        # Calculate size
        self.height = 40
        self.width = 200
        self.config(height=self.height, width=self.width)
        
        self.draw(self.bg_color)
        
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Configure>", self.on_resize)
        
    def on_resize(self, event=None):
        """Vẽ lại khi button thay đổi kích thước"""
        self.width = self.winfo_width()
        self.height = self.winfo_height()
        self.draw(self.bg_color)
        
    def draw(self, color):
        self.delete("all")
        w = self.winfo_width() if self.winfo_width() > 1 else self.width
        h = self.winfo_height() if self.winfo_height() > 1 else self.height
        r = self.radius
        
        # Draw rounded rectangle with smooth corners
        self.create_arc(0, 0, 2*r, 2*r, start=90, extent=90, fill=color, outline=color, style="pieslice")
        self.create_arc(w-2*r, 0, w, 2*r, start=0, extent=90, fill=color, outline=color, style="pieslice")
        self.create_arc(0, h-2*r, 2*r, h, start=180, extent=90, fill=color, outline=color, style="pieslice")
        self.create_arc(w-2*r, h-2*r, w, h, start=270, extent=90, fill=color, outline=color, style="pieslice")
        
        self.create_rectangle(r, 0, w-r, h, fill=color, outline="")
        self.create_rectangle(0, r, w, h-r, fill=color, outline="")
        
        # Draw text
        self.create_text(w/2, h/2, text=self.text, fill=self.fg_color, font=self.font)
        
    def on_click(self, event):
        if self.command and str(self.cget('state')) != 'disabled':
            self.command()
            
    def on_enter(self, event):
        if str(self.cget('state')) != 'disabled':
            self.draw(self.hover_color)
            
    def on_leave(self, event):
        if str(self.cget('state')) != 'disabled':
            self.draw(self.bg_color)
            
    def config_colors(self, bg_color=None, state=None):
        if bg_color:
            self.bg_color = bg_color
        if state:
            self.config(state=state)
        self.draw(self.bg_color)


class RoundedEntry(tk.Canvas):
    """Entry với góc bo tròn"""
    def __init__(self, parent, radius=8, bg_color="#ffffff", border_color="#d1d5db",
                 font=("Segoe UI", 9), show=None, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.radius = radius
        self.bg_color = bg_color
        self.border_color = border_color
        self.show = show
        
        self.config(highlightthickness=0, bg=parent.cget('bg'), height=32)
        
        # Create entry widget
        self.entry = tk.Entry(self, font=font, relief="flat", bd=0, bg=bg_color)
        if show:
            self.entry.config(show=show)
        
        self.bind("<Configure>", self.on_resize)
        
    def on_resize(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        r = self.radius
        
        if w < 2*r or h < 2*r:
            return
        
        # Draw border
        self.create_arc(0, 0, 2*r, 2*r, start=90, extent=90, fill=self.border_color, outline=self.border_color)
        self.create_arc(w-2*r, 0, w, 2*r, start=0, extent=90, fill=self.border_color, outline=self.border_color)
        self.create_arc(0, h-2*r, 2*r, h, start=180, extent=90, fill=self.border_color, outline=self.border_color)
        self.create_arc(w-2*r, h-2*r, w, h, start=270, extent=90, fill=self.border_color, outline=self.border_color)
        self.create_rectangle(r, 0, w-r, h, fill=self.border_color, outline=self.border_color)
        self.create_rectangle(0, r, w, h-r, fill=self.border_color, outline=self.border_color)
        
        # Draw background
        offset = 2
        self.create_arc(offset, offset, 2*r-offset, 2*r-offset, start=90, extent=90, fill=self.bg_color, outline=self.bg_color)
        self.create_arc(w-2*r+offset, offset, w-offset, 2*r-offset, start=0, extent=90, fill=self.bg_color, outline=self.bg_color)
        self.create_arc(offset, h-2*r+offset, 2*r-offset, h-offset, start=180, extent=90, fill=self.bg_color, outline=self.bg_color)
        self.create_arc(w-2*r+offset, h-2*r+offset, w-offset, h-offset, start=270, extent=90, fill=self.bg_color, outline=self.bg_color)
        self.create_rectangle(r, offset, w-r, h-offset, fill=self.bg_color, outline=self.bg_color)
        self.create_rectangle(offset, r, w-offset, h-r, fill=self.bg_color, outline=self.bg_color)
        
        # Position entry
        self.entry.place(x=10, y=5, width=w-20, height=h-10)
    
    def get(self):
        return self.entry.get()
    
    def insert(self, index, string):
        self.entry.insert(index, string)


class RoundedFrame(tk.Canvas):
    """Frame với góc bo tròn"""
    def __init__(self, parent, radius=15, bg_color="#ffffff", border_color="#e0e0e0", 
                 border_width=1, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.radius = radius
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_width = border_width
        
        self.config(highlightthickness=0, bg=parent.cget('bg'))
        
        self.bind("<Configure>", self.on_resize)
        
    def on_resize(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        r = self.radius
        
        if w < 2*r or h < 2*r:
            return
            
        # Draw border
        if self.border_width > 0:
            self.create_arc(0, 0, 2*r, 2*r, start=90, extent=90, 
                          fill=self.border_color, outline=self.border_color, width=self.border_width)
            self.create_arc(w-2*r, 0, w, 2*r, start=0, extent=90, 
                          fill=self.border_color, outline=self.border_color, width=self.border_width)
            self.create_arc(0, h-2*r, 2*r, h, start=180, extent=90, 
                          fill=self.border_color, outline=self.border_color, width=self.border_width)
            self.create_arc(w-2*r, h-2*r, w, h, start=270, extent=90, 
                          fill=self.border_color, outline=self.border_color, width=self.border_width)
            
            self.create_rectangle(r, 0, w-r, h, fill=self.border_color, outline=self.border_color)
            self.create_rectangle(0, r, w, h-r, fill=self.border_color, outline=self.border_color)
        
        # Draw background (slightly smaller for border effect)
        offset = self.border_width
        self.create_arc(offset, offset, 2*r-offset, 2*r-offset, start=90, extent=90, 
                      fill=self.bg_color, outline=self.bg_color)
        self.create_arc(w-2*r+offset, offset, w-offset, 2*r-offset, start=0, extent=90, 
                      fill=self.bg_color, outline=self.bg_color)
        self.create_arc(offset, h-2*r+offset, 2*r-offset, h-offset, start=180, extent=90, 
                      fill=self.bg_color, outline=self.bg_color)
        self.create_arc(w-2*r+offset, h-2*r+offset, w-offset, h-offset, start=270, extent=90, 
                      fill=self.bg_color, outline=self.bg_color)
        
        self.create_rectangle(r, offset, w-r, h-offset, fill=self.bg_color, outline=self.bg_color)
        self.create_rectangle(offset, r, w-offset, h-r, fill=self.bg_color, outline=self.bg_color)


class CalendarTaskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UTH Sync Task")
        self.root.geometry("1100x700")
        self.root.resizable(True, True)
        
        # Set icon for window and taskbar
        try:
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                base_path = sys._MEIPASS
            else:
                # Running as script
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            icon_path = os.path.join(base_path, "img", "uth_synctask_logo.ico")
            if os.path.exists(icon_path):
                root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Could not set icon: {e}")
        
        # Set color scheme - Màu chủ đạo #018486
        self.colors = {
            'primary': '#018486',      # Màu chủ đạo trường
            'primary_dark': '#016668', # Màu đậm hơn
            'primary_light': '#E6F7F7', # Màu nhạt
            'success': '#10b981',      # Green
            'warning': '#f59e0b',      # Amber
            'danger': '#ef4444',       # Red
            'dark': '#1f2937',         # Dark gray
            'light': '#ffffff',        # White
            'bg': '#f8f9fa',           # Light bg
            'border': '#e0e0e0',       # Border color
            'text_dark': '#2d3748',    # Dark text
            'text_light': '#718096'    # Light text
        }
        
        # Configure root background
        self.root.configure(bg=self.colors['bg'])
        
        # Variables
        self.is_running = False
        
        # Load logo
        self.logo_image = None
        try:
            from PIL import Image, ImageTk, ImageDraw
            
            # Get correct path for logo
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            logo_path = os.path.join(base_path, "img", "ut-logo.png")
            img = Image.open(logo_path)
            img = img.resize((150, 50), Image.Resampling.LANCZOS)
            self.logo_image = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Không thể load logo: {e}")
        
        # Configure ttk style for rounded widgets
        self.style = ttk.Style()
        self.style.configure('Rounded.TFrame', relief='flat', borderwidth=0)
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Header với logo
        header_frame = RoundedFrame(main_container, radius=12, bg_color=self.colors['light'], 
                                   border_color=self.colors['border'], border_width=1, height=70)
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Logo trên nền trắng
        if self.logo_image:
            logo_label = tk.Label(header_frame, image=self.logo_image, bg=self.colors['light'])
            logo_label.place(x=15, y=10)
        
        # Title
        title_label = tk.Label(header_frame, text="UTH Calendar & Task Manager", 
                               font=("Segoe UI", 15, "bold"), 
                               fg=self.colors['primary'], bg=self.colors['light'])
        title_label.place(x=175, y=13)
        
        # Version label (góc phải)
        version_label = tk.Label(header_frame, text=f"{APP_VERSION} • {APP_DATE}", 
                                font=("Segoe UI", 8), 
                                fg=self.colors['text_light'], bg=self.colors['light'])
        version_label.place(relx=1.0, x=-15, y=15, anchor="ne")
        
        subtitle_label = tk.Label(header_frame, text="Đồng bộ sự kiện UTH với Google Calendar & Tasks", 
                                 font=("Segoe UI", 9), 
                                 fg=self.colors['text_light'], bg=self.colors['light'])
        subtitle_label.place(x=175, y=40)
        
        # Content frame
        content_frame = tk.Frame(main_container, bg=self.colors['bg'])
        content_frame.pack(fill="both", expand=True)
        
        # Left panel - Login và Options (40% chiều rộng)
        left_panel = tk.Frame(content_frame, bg=self.colors['bg'], width=420)
        left_panel.pack(side="left", fill="both", padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Login frame - Gọn gàng hơn với rounded input
        login_container = RoundedFrame(left_panel, radius=12, bg_color=self.colors['light'],
                                      border_color=self.colors['border'], border_width=1, height=150)
        login_container.pack(fill="x", pady=(0, 8))
        login_container.pack_propagate(False)
        
        login_frame = tk.Frame(login_container, bg=self.colors['light'])
        login_frame.place(x=12, y=8, relwidth=1, width=-24, relheight=1, height=16)
        
        tk.Label(login_frame, text="Thông tin đăng nhập", font=("Segoe UI", 9, "bold"),
                bg=self.colors['light'], fg=self.colors['text_dark']).pack(anchor="w", pady=(0,3))
        
        # MSSV row
        mssv_row = tk.Frame(login_frame, bg=self.colors['light'])
        mssv_row.pack(fill="x", pady=2)
        tk.Label(mssv_row, text="MSSV:", font=("Segoe UI", 9), width=10,
                bg=self.colors['light'], fg=self.colors['text_dark'], anchor="w").pack(side="left")
        self.mssv_entry = RoundedEntry(mssv_row, radius=8, bg_color=self.colors['light'],
                                      border_color=self.colors['border'])
        self.mssv_entry.pack(side="left", fill="x", expand=True, padx=(5,0))
        
        # Password row
        pass_row = tk.Frame(login_frame, bg=self.colors['light'])
        pass_row.pack(fill="x", pady=2)
        tk.Label(pass_row, text="Mật khẩu:", font=("Segoe UI", 9), width=10,
                bg=self.colors['light'], fg=self.colors['text_dark'], anchor="w").pack(side="left")
        self.password_entry = RoundedEntry(pass_row, radius=8, bg_color=self.colors['light'],
                                          border_color=self.colors['border'], show="•")
        self.password_entry.pack(side="left", fill="x", expand=True, padx=(5,0))
        
        # Checkbox lưu thông tin đăng nhập
        save_login_row = tk.Frame(login_frame, bg=self.colors['light'])
        save_login_row.pack(fill="x", pady=(5, 0))
        self.save_login_var = tk.BooleanVar(value=False)
        tk.Checkbutton(save_login_row, text="💾 Lưu thông tin đăng nhập ", 
                      variable=self.save_login_var, font=("Segoe UI", 9),
                      bg=self.colors['light'], fg=self.colors['text_dark'], 
                      selectcolor=self.colors['light'],
                      activebackground=self.colors['light']).pack(anchor="w", padx=(90, 0))
        
        # Load saved credentials
        mssv, password = load_uth_login()
        if mssv:
            self.mssv_entry.insert(0, mssv)
            self.password_entry.insert(0, password)
            self.save_login_var.set(True)
        
        # Options frame - Có đầy đủ 3 options
        options_container = RoundedFrame(left_panel, radius=12, bg_color=self.colors['light'],
                                        border_color=self.colors['border'], border_width=1, height=120)
        options_container.pack(fill="x", pady=(0, 8))
        options_container.pack_propagate(False)
        
        options_frame = tk.Frame(options_container, bg=self.colors['light'])
        options_frame.place(x=12, y=8, relwidth=1, width=-24, relheight=1, height=-16)
        
        tk.Label(options_frame, text="Tùy chọn", font=("Segoe UI", 9, "bold"),
                bg=self.colors['light'], fg=self.colors['text_dark']).pack(anchor="w", pady=(0,3))
        
        self.headless_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Chạy ẩn trình duyệt", 
                      variable=self.headless_var, font=("Segoe UI", 9),
                      bg=self.colors['light'], fg=self.colors['text_dark'], 
                      selectcolor=self.colors['light'],
                      activebackground=self.colors['light']).pack(anchor="w", pady=2)
        
        self.add_tasks_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Thêm vào Google Tasks", 
                      variable=self.add_tasks_var, font=("Segoe UI", 9),
                      bg=self.colors['light'], fg=self.colors['text_dark'],
                      selectcolor=self.colors['light'],
                      activebackground=self.colors['light']).pack(anchor="w", pady=2)
        
        self.add_events_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Thêm vào Google Calendar", 
                      variable=self.add_events_var, font=("Segoe UI", 9),
                      bg=self.colors['light'], fg=self.colors['text_dark'],
                      selectcolor=self.colors['light'],
                      activebackground=self.colors['light']).pack(anchor="w", pady=2)
        
        # Control buttons - 3 buttons (2 hàng)
        btn_container = RoundedFrame(
            left_panel,
            radius=12,
            bg_color=self.colors['light'],
            border_color=self.colors['border'],
            border_width=1,
            height=120          # tăng để chứa 2 hàng buttons
        )
        btn_container.pack(fill="x", pady=(0, 8))
        btn_container.pack_propagate(False)

        btn_frame = tk.Frame(btn_container, bg=self.colors['light'])
        btn_frame.place(x=12, y=10, relwidth=1, width=-24, relheight=1, height=-20)

        # Cấu hình grid
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.rowconfigure(0, weight=1)
        btn_frame.rowconfigure(1, weight=1)

        self.start_btn = RoundedButton(
            btn_frame,
            text="BẮT ĐẦU",
            command=self.start_process,
            radius=15,
            bg_color=self.colors['primary'],
            hover_color=self.colors['primary_dark'],
            font=("Segoe UI", 9, "bold")
        )
        self.start_btn.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 6),
            pady=(4, 4)            
        )

        self.stop_btn = RoundedButton(
            btn_frame,
            text="DỪNG",
            command=self.stop_process,
            radius=10,
            bg_color=self.colors['danger'],
            hover_color="#dc2626",
            font=("Segoe UI", 9, "bold")
        )
        self.stop_btn.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(6, 0),
            pady=(4, 4)            
        )
        
        # Button xóa tasks trùng - hàng thứ 2
        self.cleanup_btn = RoundedButton(
            btn_frame,
            text="🧹 DỌN DẸP TASKS TRÙNG",
            command=self.cleanup_duplicate_tasks,
            radius=10,
            bg_color="#f59e0b",  # màu vàng cam
            hover_color="#d97706",
            font=("Segoe UI", 9, "bold")
        )
        self.cleanup_btn.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=0,
            pady=(4, 4)            
        )
        self.stop_btn.config(state="disabled")



        
        # Nhật ký ở left panel 
        log_container = RoundedFrame(left_panel, radius=12, bg_color="#2d3748",
                                    border_color=self.colors['primary'], border_width=2)
        log_container.pack(fill="both", expand=True)
        
        log_frame = tk.Frame(log_container, bg="#2d3748")
        log_frame.place(x=8, y=8, relwidth=1, width=-16, relheight=1, height=-16)
        
        tk.Label(log_frame, text="📝 Nhật ký xử lý", font=("Segoe UI", 9, "bold"),
                bg="#2d3748", fg="#e2e8f0").pack(anchor="w", pady=(0,5))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap="word", 
                                                  font=("Consolas", 8),
                                                  bg="#1e293b", fg="#e2e8f0",
                                                  insertbackground="white",
                                                  relief="flat", borderwidth=0)
        self.log_text.pack(fill="both", expand=True, pady=(3,0))
        
        # Right panel - 2 ô hiển thị sự kiện mới và cũ xếp dọc (60% chiều rộng)
        right_panel = tk.Frame(content_frame, bg=self.colors['bg'])
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Ô trên - Sự kiện mới thêm
        new_events_container = RoundedFrame(right_panel, radius=12, 
                                           bg_color=self.colors['primary_light'],
                                           border_color=self.colors['primary'], border_width=2)
        new_events_container.pack(fill="both", expand=True, pady=(0, 4))
        
        new_frame = tk.Frame(new_events_container, bg=self.colors['primary_light'])
        new_frame.place(x=8, y=8, relwidth=1, width=-16, relheight=1, height=-16)
        
        tk.Label(new_frame, text="➕ Mới thêm", font=("Segoe UI", 9, "bold"),
                bg=self.colors['primary_light'], fg=self.colors['primary']).pack(anchor="w", pady=(0,4))
        
        self.new_text = scrolledtext.ScrolledText(new_frame, wrap="word", 
                                                  font=("Segoe UI", 9),
                                                  bg=self.colors['primary_light'], 
                                                  fg=self.colors['text_dark'],
                                                  relief="flat", borderwidth=0,
                                                  state="disabled")
        self.new_text.pack(fill="both", expand=True)
        
        # Ô dưới - Sự kiện đã tồn tại
        exist_events_container = RoundedFrame(right_panel, radius=12, 
                                             bg_color="#fef3c7",
                                             border_color=self.colors['warning'], border_width=2)
        exist_events_container.pack(fill="both", expand=True, pady=(4, 0))
        
        exist_frame = tk.Frame(exist_events_container, bg="#fef3c7")
        exist_frame.place(x=8, y=8, relwidth=1, width=-16, relheight=1, height=-16)
        
        tk.Label(exist_frame, text="♻️ Đã tồn tại", font=("Segoe UI", 9, "bold"),
                bg="#fef3c7", fg=self.colors['warning']).pack(anchor="w", pady=(0,4))
        
        self.exist_text = scrolledtext.ScrolledText(exist_frame, wrap="word", 
                                                    font=("Segoe UI", 9),
                                                    bg="#fef3c7", 
                                                    fg="#92400e",
                                                    relief="flat", borderwidth=0,
                                                    state="disabled")
        self.exist_text.pack(fill="both", expand=True)
        
        # Status bar
        status_frame = tk.Frame(self.root, bg=self.colors['primary'], height=26)
        status_frame.pack(side="bottom", fill="x")
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="Sẵn sàng", 
                                     font=("Segoe UI", 8),
                                     fg="white", bg=self.colors['primary'], 
                                     anchor="w", padx=12)
        self.status_label.pack(fill="both", expand=True)
        
    def log(self, message):
        """Ghi log vào text widget"""
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.root.update_idletasks()
        
    def add_to_new_list(self, item_type, title, date):
        """Thêm item vào danh sách mới"""
        self.new_text.config(state="normal")
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if item_type == "task":
            icon = "📌"
        else:
            icon = "📅"
            
        self.new_text.insert("end", f"{icon} {title}\n", "title")
        self.new_text.insert("end", f"   📆 {date}  •  ⏰ {timestamp}\n\n", "detail")
        self.new_text.see("end")
        self.new_text.config(state="disabled")
        self.root.update_idletasks()
        
    def add_to_exist_list(self, item_type, title, date):
        """Thêm item vào danh sách đã tồn tại"""
        self.exist_text.config(state="normal")
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if item_type == "task":
            icon = "📌"
        else:
            icon = "📅"
            
        self.exist_text.insert("end", f"{icon} {title}\n", "title")
        self.exist_text.insert("end", f"   📆 {date}  •  ⏰ {timestamp}\n\n", "detail")
        self.exist_text.see("end")
        self.exist_text.config(state="disabled")
        self.root.update_idletasks()
        
    def clear_event_lists(self):
        """Xóa nội dung các cột sự kiện"""
        self.new_text.config(state="normal")
        self.new_text.delete(1.0, "end")
        self.new_text.config(state="disabled")
        
        self.exist_text.config(state="normal")
        self.exist_text.delete(1.0, "end")
        self.exist_text.config(state="disabled")
    
    def set_status(self, status):
        """Cập nhật status bar"""
        self.status_label.config(text=status)
        
    def start_process(self):
        """Bắt đầu quá trình crawl và thêm events/tasks"""
        if self.is_running:
            return
            
        mssv = self.mssv_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not mssv or not password:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập MSSV và mật khẩu!")
            return
        
        # Lưu thông tin đăng nhập nếu checkbox được chọn
        if self.save_login_var.get():
            save_uth_login(mssv, password)
        else:
            # Xóa credentials khỏi .env nếu bỏ chọn
            env_path = Path(".env")
            if env_path.exists():
                try:
                    load_dotenv(env_path)
                    # Xóa các key liên quan
                    set_key(env_path, "UTH_MSSV_ENCRYPTED", "")
                    set_key(env_path, "UTH_PASSWORD_ENCRYPTED", "")
                    print("[OK] Đã xóa thông tin đăng nhập khỏi .env")
                except Exception as e:
                    print(f"[ERR] Không thể xóa credentials: {e}")
        
        self.is_running = True
        self.start_btn.config_colors(bg_color="#9ca3af", state="disabled")
        self.stop_btn.config_colors(bg_color=self.colors['danger'], state="normal")
        self.log_text.delete(1.0, "end")
        self.clear_event_lists()
        
        # Chạy trong thread riêng để không block GUI
        thread = Thread(target=self.run_process, args=(mssv, password), daemon=True)
        thread.start()
        
    def stop_process(self):
        """Dừng quá trình"""
        self.is_running = False
        self.start_btn.config_colors(bg_color=self.colors['primary'], state="normal")
        self.stop_btn.config_colors(bg_color="#9ca3af", state="disabled")
        self.log("⏹ [STOP] Đã dừng quá trình")
        self.set_status("Đã dừng")
    
    def cleanup_duplicate_tasks(self):
        """Dọn dẹp tasks trùng lặp"""
        if self.is_running:
            messagebox.showwarning("Đang chạy", "Vui lòng dừng quá trình trước khi dọn dẹp!")
            return
        
        result = messagebox.askyesno(
            "Xác nhận",
            "Bạn có chắc muốn xóa các tasks trùng lặp?\n\n"
            "⚠️ Lưu ý: Các tasks có cùng tên và ngày deadline sẽ bị xóa,\n"
            "chỉ giữ lại task đầu tiên (task cũ nhất)."
        )
        
        if not result:
            return
        
        self.cleanup_btn.config_colors(bg_color="#9ca3af", state="disabled")
        self.set_status("🧹 Đang dọn dẹp tasks trùng...")
        self.log("\n" + "="*60)
        self.log("🧹 BẮT ĐẦU DỌN DẸP TASKS TRÙNG LẶP")
        self.log("="*60)
        
        # Chạy trong thread riêng
        thread = Thread(target=self._run_cleanup, daemon=True)
        thread.start()
    
    def _run_cleanup(self):
        """Thread worker để dọn dẹp tasks"""
        try:
            self.log("🔑 Đang xác thực với Google...")
            creds = get_credentials()
            tasks_service = get_tasks_service(creds)
            self.log("✓ Đã kết nối Google Tasks\n")
            
            # Truyền self.log làm callback để ghi log vào GUI
            deleted = remove_duplicate_tasks(tasks_service, log_callback=self.log)
            
            self.set_status(f"✅ Đã xóa {deleted} tasks trùng")
            
            if deleted > 0:
                messagebox.showinfo(
                    "Hoàn thành",
                    f"Đã xóa thành công {deleted} tasks trùng lặp!\n\n"
                    "Vui lòng kiểm tra lại Google Tasks."
                )
            else:
                messagebox.showinfo("Hoàn thành", "Không tìm thấy tasks trùng lặp!")
                
        except Exception as e:
            error_msg = f"Lỗi khi dọn dẹp: {str(e)}"
            self.log(f"\n❌ {error_msg}")
            self.set_status("❌ Lỗi khi dọn dẹp")
            messagebox.showerror("Lỗi", error_msg)
            import traceback
            self.log(traceback.format_exc())
        finally:
            self.cleanup_btn.config_colors(bg_color="#f59e0b", state="normal")
        
    def run_process(self, mssv, password):
        """Logic chính để crawl và thêm events/tasks"""
        try:
            self.set_status(f"🚀 Đang khởi động...")
            self.log("=" * 60)
            self.log("🚀 BẮT ĐẦU QUÁ TRÌNH CRAWL SỰ KIỆN TỪ UTH")
            self.log("=" * 60)
            
            # Setup Chrome
            chrome_options = Options()
            if self.headless_var.get():
                chrome_options.add_argument("--headless")
                self.log("✓ Chế độ: Headless (ẩn trình duyệt)")
            else:
                self.log("✓ Chế độ: Hiển thị trình duyệt")
                
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--log-level=3")
            
            self.log("📂 Đang khởi tạo Chrome WebDriver...")
            driver = webdriver.Chrome(options=chrome_options)
            
            sites = [
                ("https://courses.ut.edu.vn", "/login/index.php"),
                ("https://thnn.ut.edu.vn", "/login/index.php"),
            ]
            
            events = []
            
            for base_url, login_path in sites:
                if not self.is_running:
                    break
                    
                self.set_status(f"🌐 Đang đăng nhập vào {base_url}...")
                self.log(f"\n🌐 Đang truy cập: {base_url}")
                
                driver.get(base_url + login_path)
                time.sleep(2)
                driver.find_element(By.ID, "username").send_keys(mssv)
                driver.find_element(By.ID, "password").send_keys(password + Keys.RETURN)
                time.sleep(3)
                
                self.log(f"✓ Đã đăng nhập vào {base_url}")
                
                self.set_status(f"📅 Đang lấy sự kiện từ {base_url}...")
                driver.get(base_url + "/calendar/view.php?view=month")
                time.sleep(5)
                
                days_with_events = driver.find_elements(By.CSS_SELECTOR, "td.hasevent")
                self.log(f"📅 Tìm thấy {len(days_with_events)} ngày có sự kiện")
                
                for day_cell in days_with_events:
                    if not self.is_running:
                        break
                    try:
                        timestamp = int(day_cell.get_attribute("data-day-timestamp"))
                        date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
                        event_items = day_cell.find_elements(By.CSS_SELECTOR, "li[data-region='event-item']")
                        for item in event_items:
                            title = item.find_element(By.CLASS_NAME, "eventname").text.strip()
                            url = item.find_element(By.TAG_NAME, "a").get_attribute("href")
                            events.append({"title": title, "date": date_str, "url": url})
                    except Exception as e:
                        self.log(f"⚠ Lỗi khi xử lý ngày: {e}")
            
            driver.quit()
            self.log(f"\n✓ Đã đóng trình duyệt")
            self.log(f"📊 Tổng số sự kiện lấy được: {len(events)}")
            
            if not self.is_running:
                self.log("\n⚠ Quá trình đã bị dừng bởi người dùng")
                self.start_btn.config_colors(bg_color=self.colors['primary'], state="normal")
                self.stop_btn.config_colors(bg_color="#9ca3af", state="disabled")
                return
            
            if len(events) == 0:
                self.log("\n⚠ Không tìm thấy sự kiện nào!")
                self.set_status("⚠ Không có sự kiện")
                self.start_btn.config_colors(bg_color=self.colors['primary'], state="normal")
                self.stop_btn.config_colors(bg_color="#9ca3af", state="disabled")
                return
            
            # Connect to Google Services
            self.set_status("🔐 Đang kết nối Google Services...")
            self.log("\n🔐 Đang xác thực với Google API...")
            creds = get_credentials()
            
            tasks_service = None
            calendar_service = None
            existing_tasks = {}
            existing_events = {}
            study_calendar_id = None
            
            if self.add_tasks_var.get():
                tasks_service = get_tasks_service(creds)
                self.log("✓ Đã kết nối Google Tasks")
                self.log("📥 Đang tải danh sách tasks hiện có...")
                existing_tasks = get_existing_tasks_dict(tasks_service, log_callback=self.log)
                self.log(f"✓ Đã cache {len(existing_tasks)} tasks để kiểm tra trùng")
            
            if self.add_events_var.get():
                calendar_service = get_calendar_service(creds)
                self.log("✓ Đã kết nối Google Calendar")
                study_calendar_id = get_study_calendar_id(calendar_service)
                if study_calendar_id == 'primary':
                    self.log("⚠ Không tìm thấy calendar 'Study', sẽ thêm vào lịch mặc định")
                else:
                    self.log("✓ Đã tìm thấy calendar 'Study'")
                self.log("📥 Đang tải danh sách events hiện có...")
                existing_events = get_existing_events_dict(calendar_service, study_calendar_id)
                self.log(f"✓ Đã tải {len(existing_events)} events hiện có")
            
            # Process events
            self.log("\n" + "=" * 60)
            self.log("📝 BẮT ĐẦU XỬ LÝ SỰ KIỆN...")
            self.log("=" * 60)
            
            added_tasks = 0
            skipped_tasks = 0
            added_events = 0
            skipped_events = 0
            
            for i, event in enumerate(events):
                if not self.is_running:
                    break
                    
                self.set_status(f"⚙️ Đang xử lý {i+1}/{len(events)}: {event['title'][:30]}...")
                
                # Add Task
                if self.add_tasks_var.get() and tasks_service:
                    if not is_task_added(existing_tasks, event['title'], event['date']):
                        if add_task(tasks_service, event['title'], event['date'], 
                                note=f"Sự kiện từ UTH: {event['url']}"):
                            self.log(f"➕ [MỚI] Task: {event['title']} | {event['date']}")
                            self.add_to_new_list("task", event['title'], event['date'])
                            # Store task info consistently with get_existing_tasks_dict format
                            key = f"{event['title']}|{event['date']}"
                            existing_tasks[key] = {
                                'title': event['title'],
                                'due': event['date'] + 'T23:59:59.000Z'
                            }
                            added_tasks += 1
                    else:
                        self.log(f"⊝ [CŨ] Task: {event['title']} | {event['date']}")
                        self.add_to_exist_list("task", event['title'], event['date'])
                        skipped_tasks += 1
                
                # Add Event
                if self.add_events_var.get() and calendar_service and study_calendar_id:
                    if not is_event_added(existing_events, event['title'], event['date']):
                        if add_event(calendar_service, event['title'], event['date'], 
                                    event['url'], study_calendar_id):
                            self.log(f"➕ [MỚI] Event: {event['title']} | {event['date']}")
                            self.add_to_new_list("event", event['title'], event['date'])
                            # Store event info consistently with get_existing_events_dict format
                            key = f"{event['title']}|{event['date']}"
                            existing_events[key] = {
                                'summary': event['title'],
                                'start': {'date': event['date']}
                            }
                            added_events += 1
                    else:
                        self.log(f"⊝ [CŨ] Event: {event['title']} | {event['date']}")
                        self.add_to_exist_list("event", event['title'], event['date'])
                        skipped_events += 1
            
            # Summary
            self.log("\n" + "=" * 60)
            self.log("✅ HOÀN TẤT!")
            self.log("=" * 60)
            self.log(f"📊 TỔNG KẾT:")
            if self.add_tasks_var.get():
                self.log(f"  📌 Tasks mới thêm: {added_tasks}")
                self.log(f"  📌 Tasks đã tồn tại: {skipped_tasks}")
            if self.add_events_var.get():
                self.log(f"  📅 Events mới thêm: {added_events}")
                self.log(f"  📅 Events đã tồn tại: {skipped_events}")
            self.log("=" * 60)
            
            self.set_status("✓ Hoàn tất!")
            
            # Message box
            total_new = added_tasks + added_events
            total_exist = skipped_tasks + skipped_events
            
            summary_msg = "✅ ĐÃ XỬ LÝ XONG!\n\n"
            summary_msg += "━" * 30 + "\n"
            summary_msg += f"➕ MỚI THÊM: {total_new}\n"
            if self.add_tasks_var.get():
                summary_msg += f"   📌 Tasks: {added_tasks}\n"
            if self.add_events_var.get():
                summary_msg += f"   📅 Events: {added_events}\n"
            summary_msg += "\n"
            summary_msg += f"♻️ ĐÃ TỒN TẠI: {total_exist}\n"
            if self.add_tasks_var.get():
                summary_msg += f"   📌 Tasks: {skipped_tasks}\n"
            if self.add_events_var.get():
                summary_msg += f"   📅 Events: {skipped_events}\n"
            summary_msg += "━" * 30
            
            messagebox.showinfo("Thành công", summary_msg)
            
        except Exception as e:
            self.log(f"\n❌ LỖI: {e}")
            self.set_status(f"❌ Lỗi: {e}")
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi:\n\n{e}")
        
        finally:
            self.is_running = False
            self.start_btn.config_colors(bg_color=self.colors['primary'], state="normal")
            self.stop_btn.config_colors(bg_color="#9ca3af", state="disabled")


def main():
    root = tk.Tk()
    app = CalendarTaskApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

