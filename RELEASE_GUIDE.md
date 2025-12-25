# 📦 Hướng Dẫn Release UTH SyncTask

## 🎯 Checklist Trước Khi Release

### 1. Code & Testing
- [ ] Test đầy đủ các tính năng
- [ ] Kiểm tra icon hiển thị trong exe
- [ ] Test trên máy sạch (không có Python)
- [ ] Xác nhận không có lỗi trong log

### 2. Documentation
- [ ] Cập nhật version trong `main.py`
- [ ] Cập nhật `CHANGELOG.md` với các thay đổi
- [ ] Cập nhật version badge trong `README.md`
- [ ] Kiểm tra `README_PORTABLE.md` đầy đủ

### 3. Build
- [ ] Build exe thành công
- [ ] Test exe trên máy sạch
- [ ] File size hợp lý (~50-70MB)
- [ ] Icon hiển thị đúng

---

## 🔨 Build Release Version

### Bước 1: Clean Build
```powershell
# Xóa build cũ
Remove-Item -Recurse -Force build, dist
Remove-Item -Force *.spec

# Build mới
pyinstaller --noconsole --onefile --name UTH_SyncTask --icon="img/uth_synctask_logo.ico" --add-data "img;img" --add-data "credentials.json;." main.py
```

### Bước 2: Test Executable
```powershell
# Chạy thử
.\dist\UTH_SyncTask.exe

# Kiểm tra:
# - Icon hiển thị đúng
# - Logo trong header hiển thị
# - Đăng nhập Google thành công
# - Crawl và sync hoạt động
```

### Bước 3: Prepare Release Files
```powershell
# Tạo thư mục release
New-Item -ItemType Directory -Force -Path release

# Copy file exe
Copy-Item dist\UTH_SyncTask.exe release\

# Copy credentials template (nếu có)
# User sẽ tự tạo credentials.json của họ
```

---

## 📤 Release lên GitHub

### Option 1: Sử Dụng GitHub Web Interface

#### Bước 1: Commit & Push Code
```powershell
git add .
git commit -m "Release v2.3.1"
git push origin main
```

#### Bước 2: Tạo Release trên GitHub
1. Vào repository trên GitHub
2. Click tab **Releases** → **Create a new release**
3. **Tag version**: `v2.3.1`
4. **Release title**: `UTH SyncTask v2.3.1`
5. **Description**: Copy nội dung từ CHANGELOG.md

```markdown
## UTH SyncTask v2.3.1

### 🔧 Sửa Lỗi & Cải Tiến
- **Icon hiển thị trong exe**: Sửa đường dẫn icon và logo khi build với PyInstaller
  - Sử dụng `sys._MEIPASS` để load đúng đường dẫn khi chạy exe
  - Icon taskbar và title bar hiển thị chính xác
  - Logo PNG trong header hiển thị đúng
- **Lịch mặc định**: Tự động thêm vào lịch mặc định (primary) nếu không tìm thấy calendar "Study"
  - Không còn bỏ qua events khi không tìm thấy lịch Study
  - Log rõ ràng khi sử dụng lịch mặc định

### 📥 Tải Về
- **Windows Portable**: `UTH_SyncTask.exe` - Không cần cài Python
- **Source Code**: Clone repository và chạy `python main.py`

### 📚 Hướng Dẫn
- [Hướng dẫn sử dụng Portable](README_PORTABLE.md)
- [Hướng dẫn cài đặt từ Source](README.md)

### ⚙️ Yêu Cầu
- Windows 10/11
- Chrome/Edge Browser
- ChromeDriver (cùng version với browser)
- Google Account với Calendar & Tasks API enabled
```

6. **Upload file**: Kéo thả `UTH_SyncTask.exe` vào mục **Attach binaries**
7. Click **Publish release**

### Option 2: Sử Dụng GitHub CLI

```powershell
# Cài GitHub CLI (nếu chưa có)
# https://cli.github.com/

# Login
gh auth login

# Tạo release với file đính kèm
gh release create v2.3.1 `
  dist\UTH_SyncTask.exe `
  --title "UTH SyncTask v2.3.1" `
  --notes-file release_notes.md
```

**File release_notes.md:**
```markdown
## UTH SyncTask v2.3.1

### 🔧 Sửa Lỗi & Cải Tiến
- Icon hiển thị đúng trong exe
- Tự động thêm vào lịch mặc định nếu không tìm thấy "Study"

[Xem chi tiết CHANGELOG](CHANGELOG.md)
```

---

## 📝 Release Notes Template

```markdown
# UTH SyncTask v{VERSION}

## 🎯 Highlights
- [Tính năng nổi bật 1]
- [Tính năng nổi bật 2]

## ✨ Tính Năng Mới
- [Feature 1]
- [Feature 2]

## 🔧 Sửa Lỗi & Cải Tiến
- [Bugfix 1]
- [Improvement 1]

## 📥 Tải Về

### Windows Portable (Recommended)
**File**: `UTH_SyncTask.exe` (XX MB)
- ✅ Không cần cài Python
- ✅ Chạy trực tiếp trên Windows 10/11
- 📖 [Hướng dẫn sử dụng](README_PORTABLE.md)

### Source Code
```bash
git clone https://github.com/YOUR_USERNAME/calendar_and_task_add_deadline.git
cd calendar_and_task_add_deadline
git checkout v{VERSION}
pip install -r requirements.txt
python main.py
```

## ⚙️ Yêu Cầu Hệ Thống
- **OS**: Windows 10/11
- **Browser**: Chrome hoặc Edge (latest)
- **ChromeDriver**: Cùng version với Chrome/Edge
- **Google Account** với:
  - Google Calendar API enabled
  - Google Tasks API enabled

## 🆕 So với phiên bản trước
[So sánh thay đổi chi tiết]

## 📚 Tài Liệu
- 📖 [README.md](README.md) - Hướng dẫn cài đặt từ source
- 🚀 [README_PORTABLE.md](README_PORTABLE.md) - Hướng dẫn dùng file exe
- 📝 [CHANGELOG.md](CHANGELOG.md) - Lịch sử phiên bản
- 🔒 [SECURITY.md](SECURITY.md) - Hướng dẫn bảo mật

## 🐛 Báo Lỗi
Gặp vấn đề? [Mở issue tại đây](https://github.com/YOUR_USERNAME/calendar_and_task_add_deadline/issues)
```

---

## 🔄 Update Existing Release

```powershell
# Xóa release cũ
gh release delete v2.3.1 --yes

# Tạo release mới
gh release create v2.3.1 dist\UTH_SyncTask.exe --title "..." --notes "..."
```

Hoặc trên GitHub Web:
1. Vào Releases
2. Click **Edit** release cần sửa
3. Upload file mới hoặc sửa description
4. **Update release**

---

## 📊 Post-Release Checklist

- [ ] Kiểm tra link download hoạt động
- [ ] Test download và chạy exe từ GitHub
- [ ] Update README.md với link release mới nhất
- [ ] Thông báo release (nếu cần)
- [ ] Monitor issues/feedback từ users

---

## 🎯 Best Practices

### Versioning (Semantic Versioning)
- **Major** (2.x.x): Breaking changes
- **Minor** (x.3.x): Tính năng mới, backwards compatible
- **Patch** (x.x.1): Bugfixes, improvements

### Release Frequency
- **Patch**: Khi có bugfix quan trọng
- **Minor**: Khi có tính năng mới
- **Major**: Khi có thay đổi lớn về architecture hoặc breaking changes

### Backup
```powershell
# Backup version cũ trước khi release
Copy-Item dist\UTH_SyncTask.exe backups\UTH_SyncTask_v2.3.0.exe
```

---

## 🔗 Links Quan Trọng

- **GitHub Releases**: https://github.com/YOUR_USERNAME/calendar_and_task_add_deadline/releases
- **GitHub CLI Docs**: https://cli.github.com/manual/gh_release
- **Semantic Versioning**: https://semver.org/

---

## 📧 Support

Cần hỗ trợ? Contact:
- GitHub Issues
- Email: your-email@example.com
