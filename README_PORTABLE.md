# 🚀 UTH SyncTask - Hướng Dẫn Sử Dụng (Portable Version)

![Version](https://img.shields.io/badge/version-v2.3.2-018486?style=for-the-badge)

**Phiên bản portable - Chạy trực tiếp không cần cài Python**

---

## 📦 Tải Về

### Option 1: Tải từ GitHub Releases
1. Truy cập [Releases Page](https://github.com/YOUR_USERNAME/calendar_and_task_add_deadline/releases)
2. Tải file `UTH_SyncTask.exe` từ phiên bản mới nhất
3. Giải nén và chạy

### Option 2: Build Từ Source
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/calendar_and_task_add_deadline.git
cd calendar_and_task_add_deadline

# Cài đặt dependencies
pip install -r requirements.txt

# Build exe
pyinstaller --noconsole --onefile --name UTH_SyncTask --icon="img/uth_synctask_logo.ico" --add-data "img;img" --add-data "credentials.json;." main.py
```

---

## ⚙️ Cài Đặt & Cấu Hình

### 1️⃣ Chuẩn Bị
- ✅ Windows 10/11
- ✅ Chrome hoặc Edge browser (cùng version với ChromeDriver)
- ✅ Google Account với Calendar & Tasks đã bật

### 2️⃣ Tải ChromeDriver
**Quan trọng**: Version ChromeDriver phải khớp với Chrome/Edge của bạn

```bash
# Kiểm tra Chrome version
chrome://version

# Tải ChromeDriver tại:
https://googlechromelabs.github.io/chrome-for-testing/
# hoặc cho Edge:
https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
```

**Cách cài đặt:**
1. Tải file `chromedriver.exe` phù hợp với version Chrome
2. Đặt vào thư mục cùng với `UTH_SyncTask.exe`
3. Hoặc thêm vào PATH của Windows

### 3️⃣ Tạo Google API Credentials

#### Bước 1: Tạo Project
1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo project mới hoặc chọn project có sẵn
3. Đặt tên: `UTH-Calendar-Sync` (hoặc tên tùy ý)

#### Bước 2: Bật APIs
1. Vào **APIs & Services** → **Enable APIs and Services**
2. Tìm và bật:
   - **Google Calendar API**
   - **Google Tasks API**

#### Bước 3: Tạo OAuth Credentials
1. Vào **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth Client ID**
3. Chọn **Application type**: Desktop app
4. Đặt tên: `UTH SyncTask Desktop`
5. Click **Create**

#### Bước 4: Tải credentials.json
1. Sau khi tạo, click icon **Download** bên cạnh OAuth Client
2. Đổi tên file thành `credentials.json`
3. **Đặt file `credentials.json` cùng thư mục với `UTH_SyncTask.exe`**

---

## 🎯 Sử Dụng

### Lần Đầu Chạy
1. **Đảm bảo có:**
   - `UTH_SyncTask.exe`
   - `credentials.json` (từ Google Cloud Console)
   - `chromedriver.exe` (hoặc trong PATH)

2. **Chạy ứng dụng:**
   - Double-click `UTH_SyncTask.exe`

3. **Xác thực Google (lần đầu):**
   - Trình duyệt sẽ tự động mở
   - Đăng nhập Google Account
   - Cho phép quyền truy cập Calendar & Tasks
   - File `token.json` sẽ được tạo tự động

4. **Nhập thông tin UTH:**
   - Username UTH (VD: 2021010101)
   - Password UTH
   - Chọn "Lưu thông tin đăng nhập" nếu muốn

5. **Bấm "Bắt đầu đồng bộ"**

### Lần Chạy Sau
- Chỉ cần double-click `UTH_SyncTask.exe` và bấm "Bắt đầu đồng bộ"
- Không cần đăng nhập lại Google hay nhập lại mật khẩu UTH

---

## 🔧 Cấu Hình Nâng Cao

### Tùy Chọn Đồng Bộ
- ☑️ **Thêm vào Calendar**: Tạo events trong lịch "Study"
- ☑️ **Thêm vào Tasks**: Tạo tasks với deadline
- ☑️ **Chạy ẩn trình duyệt**: Không hiển thị Chrome khi crawl

### Lịch Mặc Định
- Ứng dụng tìm calendar tên **"Study"** để thêm events
- Nếu không tìm thấy → tự động thêm vào **lịch mặc định**
- Bạn có thể tạo calendar "Study" trên Google Calendar để tách biệt

---

## 📁 Cấu Trúc Thư Mục

```
📦 UTH_SyncTask/
├── 📄 UTH_SyncTask.exe       # File chạy chính
├── 📄 credentials.json        # Google API credentials (bắt buộc)
├── 📄 chromedriver.exe        # WebDriver cho Chrome
├── 📄 token.json             # Tự tạo sau lần xác thực đầu
├── 📄 .env                   # Lưu thông tin đăng nhập (tự tạo)
└── 📂 img/                   # Thư mục chứa logo (đã build vào exe)
```

---

## ❓ Xử Lý Sự Cố

### ❌ Lỗi "ChromeDriver not found"
**Nguyên nhân**: Không tìm thấy chromedriver.exe

**Giải pháp**:
```bash
# Option 1: Đặt vào cùng thư mục exe
UTH_SyncTask/
├── UTH_SyncTask.exe
└── chromedriver.exe

# Option 2: Thêm vào PATH
setx PATH "%PATH%;C:\path\to\chromedriver"
```

### ❌ Lỗi "This version of ChromeDriver only supports Chrome version X"
**Nguyên nhân**: Sai version ChromeDriver

**Giải pháp**:
1. Kiểm tra Chrome version: `chrome://version`
2. Tải ChromeDriver đúng version tại: https://googlechromelabs.github.io/chrome-for-testing/
3. Thay file `chromedriver.exe` cũ

### ❌ Lỗi "credentials.json not found"
**Nguyên nhân**: Chưa có hoặc sai vị trí credentials.json

**Giải pháp**:
- Tạo credentials.json từ [Google Cloud Console](#3️⃣-tạo-google-api-credentials)
- Đặt cùng thư mục với `UTH_SyncTask.exe`

### ❌ Icon không hiển thị
**Giải pháp**:
- Thư mục `img/` đã được build sẵn vào exe
- Nếu vẫn lỗi, kiểm tra log hoặc build lại từ source

### ❌ Không thể lưu thông tin đăng nhập
**Nguyên nhân**: Lỗi quyền ghi file

**Giải pháp**:
- Chạy ứng dụng với quyền Administrator
- Đặt ứng dụng ở nơi có quyền ghi (VD: Documents, Desktop)

---

## 🔒 Bảo Mật

### Lưu Trữ Thông Tin
- **credentials.json**: Thông tin OAuth từ Google (public)
- **token.json**: Token xác thực Google (private)
- **.env**: Username/Password UTH được mã hóa XOR + machine-specific key

### ⚠️ Lưu Ý Quan Trọng
- ❌ **KHÔNG** chia sẻ `token.json` và `.env`
- ✅ File `.env` chỉ giải mã được trên máy đã mã hóa
- ✅ Nếu chuyển máy mới, cần nhập lại thông tin đăng nhập
- ✅ Backup định kỳ `token.json` nếu không muốn xác thực lại

---

## 📊 So Sánh Versions

| Tính Năng | Portable (exe) | Source Code |
|-----------|---------------|-------------|
| Cài Python | ❌ Không cần | ✅ Cần Python 3.8+ |
| Cài Packages | ❌ Không cần | ✅ Cần pip install |
| Kích thước | ~50-70 MB | ~5 MB |
| Tốc độ khởi động | Nhanh | Chậm hơn một chút |
| Cập nhật | Tải exe mới | git pull |
| Customize | Giới hạn | Tự do chỉnh sửa |

---

## 🆘 Hỗ Trợ

**Gặp vấn đề?** Mở issue tại: [GitHub Issues](https://github.com/YOUR_USERNAME/calendar_and_task_add_deadline/issues)

**Cung cấp thông tin:**
- 💻 Windows version
- 🌐 Chrome/Edge version
- 📝 Nội dung log trong ứng dụng
- 📸 Screenshot lỗi (nếu có)

---

## 📜 License

MIT License - Xem [LICENSE](LICENSE) để biết thêm chi tiết

---

## 🎓 Credits

Developed for **University of Transport Ho Chi Minh City (UTH)**

**Latest**: v2.3.2 (2025-12-25)
