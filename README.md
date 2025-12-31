
# 🎓 UTH Calendar & Task Manager

<div align="center">

![Version](https://img.shields.io/badge/version-v2.3.3-018486?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

**Tự động đồng bộ deadline từ hệ thống UTH vào Google Calendar & Tasks**

[Tính Năng](#-tính-năng) • [Cài Đặt](#-cài-đặt) • [Sử Dụng](#-sử-dụng) • [Changelog](CHANGELOG.md)

</div>

---

## 📋 Giới Thiệu

**UTH Calendar & Task Manager** là công cụ tự động thu thập thông tin deadline/sự kiện từ hệ thống học tập trực tuyến của **Đại học Giao thông Vận tải TP.HCM (UTH)** và đồng bộ lên Google Calendar & Google Tasks.

### ✨ Highlights
- 🎨 **Giao diện hiện đại**: UI đẹp mắt với màu chủ đạo UTH (#018486)
- 🔒 **Bảo mật cao cấp**: Mã hóa XOR + machine-specific key, lưu trong .env
- ⚡ **Tự động hóa hoàn toàn**: Crawl và đồng bộ chỉ với 1 click
- 🔄 **Tránh trùng lặp**: Kiểm tra thông minh trước khi thêm (title + date)
- 🧹 **Dọn dẹp tự động**: Xóa tasks trùng lặp với 1 click
- 🎛️ **Linh hoạt**: Tùy chọn chạy ẩn, chỉ thêm Calendar hoặc Tasks
- 📝 **Quản lý .env**: Credentials được lưu an toàn trong .env file

---

## 🚀 Tính Năng

### 🎯 Chức Năng Chính
- ✅ **Tự động đăng nhập UTH**: Sử dụng Selenium WebDriver
- ✅ **Crawl deadline thông minh**: Lấy toàn bộ sự kiện từ calendar môn học
- ✅ **Đồng bộ Google Calendar**: Thêm vào lịch "Study" tự động
- ✅ **Đồng bộ Google Tasks**: Tạo task với deadline rõ ràng
- ✅ **Kiểm tra trùng lặp thông minh**: So sánh cả title và ngày deadline
- ✅ **Dọn dẹp tasks trùng**: Tự động quét và xóa tasks trùng lặp với 1 click
- ✅ **Pagination thông minh**: Lấy toàn bộ tasks từ Google API (không bỏ sót)
- ✅ **Lưu thông tin đăng nhập**: Mã hóa XOR + machine-specific key trong .env
- ✅ **Quản lý credentials**: Sử dụng python-dotenv cho .env file

### 🎨 Giao Diện
- 🖼️ Logo UTH hiển thị đẹp mắt
- 🎨 Bo góc mềm mại cho tất cả component
- 🔘 Button với hover effect chuyên nghiệp
- 📝 Nhật ký real-time với emoji động và logs chi tiết
- 📊 Thanh trạng thái hiển thị tiến trình
- 🌈 Color scheme đồng nhất với UTH branding
- 🧹 Button dọn dẹp tasks trùng với màu vàng cam nổi bật

### ⚙️ Tùy Chọn
- 👁️ **Chạy ẩn trình duyệt**: Headless mode (Chrome)
- 📅 **Thêm vào Google Calendar**: Bật/tắt đồng bộ Calendar
- ✅ **Thêm vào Google Tasks**: Bật/tắt đồng bộ Tasks
- 💾 **Lưu thông tin đăng nhập**: Tự động điền lần sau
- 🧹 **Dọn dẹp tasks trùng**: Xóa tasks trùng lặp (cùng tên + ngày)

---

## 💻 Yêu Cầu Hệ Thống

### Phần Mềm
- **Python**: 3.8 trở lên
- **Google Chrome**: Phiên bản mới nhất
- **ChromeDriver**: Tương thích với Chrome đã cài
- **Internet**: Kết nối ổn định

### Dependencies
```bash
selenium>=4.0.0
google-auth>=2.0.0
google-auth-oauthlib>=0.5.0
google-api-python-client>=2.0.0
pillow>=9.0.0
python-dotenv>=1.0.0
```

---

## 📦 Cài Đặt

### Bước 1: Clone Repository
```bash
git clone https://github.com/duynam2802/UTH_SyncTask
cd UTH_SyncTask
```

### Bước 2: Cài Đặt Dependencies
```bash
pip install -r requirements.txt
```

Hoặc cài thủ công:
```bash
pip install selenium google-auth google-auth-oauthlib google-api-python-client pillow
```

### Bước 3: Tải ChromeDriver
1. Kiểm tra phiên bản Chrome: `chrome://version`
2. Tải ChromeDriver tương ứng: [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)
3. Đặt `chromedriver.exe` vào thư mục hệ thống hoặc cùng thư mục với `main.py`

### Bước 4: Cấu Hình Google API

#### 4.1. Tạo Project Google Cloud
1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo project mới hoặc chọn project có sẵn
3. Vào **APIs & Services** → **Enable APIs and Services**
4. Tìm và bật:
   - ✅ Google Calendar API
   - ✅ Google Tasks API

#### 4.2. Tạo OAuth Credentials
1. Vào **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Chọn **Application type**: Desktop app
4. Đặt tên (VD: "UTH Calendar Manager")
5. Download file JSON và đổi tên thành `credentials.json`
6. Đặt file `credentials.json` vào thư mục gốc của project

### Bước 5: Tạo Lịch "Study" (Optional)
1. Mở [Google Calendar](https://calendar.google.com)
2. Bên trái click **+** → **Create new calendar**
3. Đặt tên: **Study** hoặc **Studys**
4. Save

> **Lưu ý**: Nếu không tạo lịch "Study", sự kiện sẽ được thêm vào lịch mặc định.

---

## 🎮 Sử Dụng

### Khởi Chạy Ứng Dụng
```bash
python main.py
```

### Lần Đầu Sử Dụng

#### 1️⃣ **Xác thực Google API**
- Lần đầu chạy sẽ mở trình duyệt để đăng nhập Google
- Chọn tài khoản và cho phép truy cập Calendar & Tasks
- Token sẽ được lưu vào `token.json`

#### 2️⃣ **Nhập Thông Tin UTH**
- **MSSV**: Mã số sinh viên của bạn
- **Mật khẩu**: Password đăng nhập hệ thống UTH
- ✅ Tick "💾 Lưu thông tin đăng nhập" để lưu

#### 3️⃣ **Chọn Tùy Chọn**
- ☑️ **Chạy ẩn trình duyệt**: Chạy Chrome ở chế độ headless
- ☑️ **Thêm vào Google Tasks**: Tạo task với deadline
- ☑️ **Thêm vào Google Calendar**: Thêm event vào lịch

#### 4️⃣ **Bắt Đầu**
- Click nút **BẮT ĐẦU** (màu xanh)
- Theo dõi tiến trình trong panel **Nhật ký**
- Click **DỪNG** (màu đỏ) nếu cần dừng giữa chừng

### Nhật Ký Hoạt Động
App sẽ hiển thị real-time:
- 🚀 Bắt đầu quá trình
- 🌐 Mở trình duyệt và đăng nhập
- 📚 Danh sách môn học tìm thấy
- 📅 Các deadline được phát hiện
- ✅ Kết quả thêm vào Calendar/Tasks
- ⏱️ Thời gian hoàn thành

---

## 📁 Cấu Trúc Thư Mục

```
calendar_and_task_add_deadline/
├── 📄 main.py                          # File chính chạy ứng dụng
├── 📄 .env                             # Environment variables (credentials encrypted)
├── 📄 .env.example                     # Template file cho .env
├── 📄 credentials.json                 # Google OAuth credentials
├── 📄 token.json                       # Token xác thực (auto-generated)
├── 📄 README.md                        # Tài liệu này
├── 📄 CHANGELOG.md                     # Nhật ký phiên bản
├── 📄 SECURITY.md                      # Hướng dẫn bảo mật
├── 📄 requirements.txt                 # Dependencies
├── 📄 .gitignore                       # Git ignore rules
├── 📄 calendar_and_task_add_deadline.spec  # PyInstaller spec
├── 📂 img/
│   └── 🖼️ ut-logo.png                 # Logo UTH
└── 📂 build/                           # Build outputs (nếu có)
```

---

## 🔐 Bảo Mật

### Thông Tin Được Mã Hóa
- **MSSV & Password**: Mã hóa XOR + machine-specific key trong `.env`
- **Google Token**: Lưu trong `token.json`
- **Machine-specific**: Credentials chỉ giải mã được trên máy đã mã hóa


---

## 🐛 Xử Lý Lỗi

### Lỗi Thường Gặp

#### 1. `ChromeDriver not found`
**Nguyên nhân**: Chưa cài hoặc sai version ChromeDriver  
**Giải pháp**: 
```bash
# Kiểm tra Chrome version
chrome://version

# Tải ChromeDriver tương ứng và đặt vào PATH
```

#### 2. `File credentials.json not found`
**Nguyên nhân**: Chưa cấu hình Google API  
**Giải pháp**: Làm theo [Bước 4: Cấu Hình Google API](#bước-4-cấu-hình-google-api)

#### 3. `Login failed - MSSV/Password incorrect`
**Nguyên nhân**: Sai thông tin đăng nhập UTH  
**Giải pháp**: Kiểm tra lại MSSV và password

#### 4. `Calendar 'Study' not found`
**Nguyên nhân**: Chưa tạo lịch Study  
**Giải pháp**: Tạo lịch "Study" hoặc sửa code để dùng lịch mặc định

#### 5. `Token expired`
**Nguyên nhân**: Token Google hết hạn  
**Giải pháp**: 
```bash
# Xóa token và xác thực lại
del token.json
python main.py
```

---

## 🔧 Tùy Chỉnh

### Thay Đổi Tên Lịch
Sửa trong `main.py`:
```python
def get_study_calendar_id(service):
    calendars = service.calendarList().list().execute().get('items', [])
    for cal in calendars:
        if cal.get('summary') == 'Study':  # ← Đổi tên ở đây
            return cal.get('id')
```

### Thay Đổi Màu Sắc
Sửa trong `CalendarTaskApp.__init__()`:
```python
self.colors = {
    'primary': '#018486',      # Màu chủ đạo
    'primary_dark': '#016668', # Màu hover
    # ... thêm màu tùy chỉnh
}
```

### Build Executable
```bash
# Cài PyInstaller
pip install pyinstaller

# Build file .exe
pyinstaller calendar_and_task_add_deadline.spec

# File .exe sẽ ở: dist/calendar_and_task_add_deadline.exe
```

---

## 📅 Tự Động Chạy

### Windows Task Scheduler

#### 1. Tạo file `run_uth_manager.bat`:
```batch
@echo off
cd /main.py
pause
```

#### 2. Tạo Task Scheduler:
1. Win + R → `taskschd.msc`
2. **Create Task** → Đặt tên "UTH Calendar Sync"
3. **Triggers** → New → Chọn thời gian (VD: 8:00 AM daily)
4. **Actions** → New → Browse to `run_uth_manager.bat`
5. OK và nhập password Windows

### Linux/Mac Cron Job
```bash
# Mở crontab
crontab -e

# Thêm dòng (chạy 8:00 AM mỗi ngày)
0 8 * * * cd /path/to/project && python3 main.py >> /tmp/uth_manager.log 2>&1
```

---

## 🤝 Đóng Góp

Contributions are welcome! 

### Cách Đóng Góp
1. Fork repo
2. Tạo branch: `git checkout -b feature/AmazingFeature`
3. Commit: `git commit -m 'Add some AmazingFeature'`
4. Push: `git push origin feature/AmazingFeature`
5. Mở Pull Request

### Báo Lỗi
Mở [Issue](https://github.com/duynam2802/UTH_SyncTask/issues) với:
- 🐛 Mô tả lỗi chi tiết
- 📸 Screenshot (nếu có)
- 💻 Môi trường (OS, Python version, Chrome version)
- 📋 Log lỗi

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 👨‍💻 Tác Giả

**Duy & AI**
- 📧 Email: duynd2971@gmai.com
- 🐙 GitHub: [@duynam2802](https://github.com/duynam2802)

---

## 🙏 Credits

- [Google Calendar API](https://developers.google.com/calendar)
- [Google Tasks API](https://developers.google.com/tasks)
- [Selenium WebDriver](https://www.selenium.dev/)
- [Pillow](https://python-pillow.org/)

---

## 📊 Changelog

Xem chi tiết các phiên bản tại [CHANGELOG.md](CHANGELOG.md)

**Latest**: v2.3.2 (2025-12-25)
- 🔧 Kiểm tra task đã hoàn thành: Không thêm lại task đã tồn tại (kể cả đã hoàn thành)
- ✨ Tránh trùng lặp task trong Google Tasks
- 📝 .env.example template
- 🎨 Bo góc mềm mại button (radius 15px)
- 🖼️ Logo hiển thị dài hơn (150x50px)

---

<div align="center">

**⭐ Nếu thấy hữu ích, đừng quên star repo nhé! ⭐**

Made with ❤️ for UTH Students

</div>

