# 📦 Hướng Dẫn Build File .EXE

## Chuẩn Bị

### 1. Cài Đặt PyInstaller
```bash
pip install pyinstaller
```

### 2. Kiểm Tra Dependencies
```bash
pip install -r requirements.txt
```

## Build File .EXE

### Cách 1: Build với file spec (Khuyến nghị)
```bash
pyinstaller build_exe.spec
```

### Cách 2: Build trực tiếp với command line
```bash
pyinstaller --noconsole --onefile --name UTHSyncTask --icon="img/uth_synctask_logo.ico" --add-data "img;img" --add-data "credentials.json;." main.py

```

## Sau Khi Build

### Vị Trí File
File .exe sẽ nằm trong thư mục:
```
dist/UTH_Calendar_Task_Manager.exe
```

### File Cần Đi Kèm
Khi chạy trên máy khác, bạn cần đưa theo các file sau (đặt cùng thư mục với .exe):

1. **credentials.json** - File OAuth từ Google Cloud Console
2. **.env** (optional) - File lưu thông tin đăng nhập
3. **token.json** (auto-generated) - Tạo tự động lần đầu

### Cấu Trúc Thư Mục Deploy
```
📁 UTH_Calendar_Task_Manager/
├── 📄 UTH_Calendar_Task_Manager.exe
├── 📄 credentials.json
├── 📄 .env (optional)
└── 📄 token.json (auto-generated)
```

## Yêu Cầu Trên Máy Đích
- **Google Chrome** phiên bản mới nhất
- **ChromeDriver** (app sẽ tự tải nếu có internet)
- Không cần Python (đã embed trong .exe)

## Xử Lý Lỗi Build

### Lỗi: "Failed to execute script"
Build lại với console=True để xem lỗi chi tiết.

### Lỗi: "Module not found"
Thêm vào hiddenimports trong build_exe.spec

### Logo không hiển thị
Kiểm tra đường dẫn trong datas của spec file.