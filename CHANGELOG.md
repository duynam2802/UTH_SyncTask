# 📝 Nhật Ký Phiên Bản - UTH Calendar & Task Manager

## [v2.3.2] - 2025-12-25

### 🔧 Sửa Lỗi & Cải Tiến
- **Kiểm tra task đã hoàn thành**: Không thêm lại task đã tồn tại (kể cả đã hoàn thành)
  - Thêm `showCompleted=True` và `showHidden=True` vào API call
  - Tránh trùng lặp task trong Google Tasks

---

## [v2.3.1] - 2025-12-25

### 🔧 Sửa Lỗi & Cải Tiến
- **Icon hiển thị trong exe**: Sửa đường dẫn icon và logo khi build với PyInstaller
  - Sử dụng `sys._MEIPASS` để load đúng đường dẫn khi chạy exe
  - Icon taskbar và title bar hiển thị chính xác
  - Logo PNG trong header hiển thị đúng
- **Lịch mặc định**: Tự động thêm vào lịch mặc định (primary) nếu không tìm thấy calendar "Study"
  - Không còn bỏ qua events khi không tìm thấy lịch Study
  - Log rõ ràng khi sử dụng lịch mặc định

---

## [v2.3.0] - 2025-12-25

### ✨ Tính Năng Mới
- **Quản lý .env**: Lưu credentials trong `.env` file thay vì `.uth_credentials`
- **Python-dotenv**: Tích hợp thư viện python-dotenv để quản lý environment variables
- **Nâng cấp mã hóa**: XOR cipher + machine-specific key (thay vì Base64 đơn giản)
- **Template .env**: Thêm file `.env.example` hướng dẫn cấu hình
- **Tài liệu bảo mật**: Tạo SECURITY.md với hướng dẫn chi tiết về backup và bảo vệ token

### 🔒 Bảo Mật
- **Machine-specific encryption**: Credentials chỉ giải mã được trên máy đã mã hóa
- **File permissions**: Tự động set chmod 600 cho .env (Linux/Mac)
- **Gitignore hoàn chỉnh**: Bảo vệ toàn diện .env, credentials.json, token.json
- **XOR Cipher**: Mã hóa mạnh hơn với key dựa trên COMPUTERNAME + USERNAME

### 🎨 Cải Tiến Giao Diện  
- **Bo góc mềm mại hơn**: Tăng radius button từ 8px → 15px
- **Vẽ button mượt mà**: Thêm `style="pieslice"` cho arc, loại bỏ outline cứng
- **Button responsive**: Button tự động vẽ lại khi thay đổi kích thước trong grid
- **Logo hiển thị dài hơn**: Tăng kích thước logo từ 100x50px → 150x50px
- **Version display**: Hiển thị version + date ở góc phải header

### 📚 Tài Liệu
- **README.md**: Viết lại hoàn toàn với structure chuyên nghiệp
- **SECURITY.md**: Hướng dẫn backup, restore, và bảo vệ credentials
- **CHANGELOG.md**: Nhật ký phiên bản chi tiết
- **.env.example**: Template với instructions đầy đủ

### 🔧 Sửa Lỗi
- Sửa lỗi bo góc phải của button không hiển thị đúng
- Cải thiện render góc bo tròn cho mượt mà hơn
- Fix XOR decryption với machine key

---

## [v2.2.0] - 2025-12-20

### ✨ Tính Năng Mới
- **Giao diện hiện đại**: UI mới với màu chủ đạo #018486 (màu UTH)
- **Bo góc tròn**: Tất cả component đều có góc bo tròn mềm mại
- **Button tùy chỉnh**: RoundedButton với hover effect
- **3 tùy chọn linh hoạt**:
  - Chạy ẩn trình duyệt
  - Thêm vào Google Tasks
  - Thêm vào Google Calendar

### 🎨 Giao Diện
- Logo UTH hiển thị trong header
- Layout 2 cột: Login/Options và Nhật ký
- Thanh trạng thái với emoji động
- Button BẮT ĐẦU (xanh) và DỪNG (đỏ)

---

## [v1.1.0] - 2025-12-15

### ✨ Tính Năng Mới
- **Crawl tự động từ UTH**: Lấy dữ liệu deadline từ hệ thống UTH
- **Đồng bộ Google Calendar**: Tự động thêm sự kiện vào lịch "Study"
- **Đồng bộ Google Tasks**: Tạo task với deadline
- **Kiểm tra trùng lặp**: Tránh thêm sự kiện/task đã tồn tại

### 🔒 Bảo Mật
- Lưu thông tin đăng nhập trong file `uth_login.json`
- OAuth2 cho Google API (token.json)

---

## [v1.0.0] - 2025-12-10

### 🎉 Phiên Bản Đầu Tiên
- **Chức năng cơ bản**: Crawl deadline từ UTH
- **Selenium WebDriver**: Tự động đăng nhập và lấy dữ liệu
- **Google API Integration**: Kết nối với Calendar và Tasks API
- **Command-line interface**: Chạy qua terminal

---



---

## 📌 Ghi Chú

### Yêu Cầu Hệ Thống
- Python 3.8+
- Chrome WebDriver
- Kết nối Internet
- Google Account với Calendar & Tasks API enabled

### Dependencies
```
selenium
google-auth
google-auth-oauthlib
google-api-python-client
pillow
```

---

**💡 Tip**: Để xem phiên bản hiện tại trong app, nhấn vào "About" trong menu (coming soon!)
