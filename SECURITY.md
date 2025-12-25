# 🔐 Hướng Dẫn Bảo Mật Token & Credentials

## 📋 Các File Nhạy Cảm

### 1. `credentials.json` - Google OAuth Credentials
**Mức độ:** 🔴 CỰC KỲ NHẠY CẢM
- Chứa Client ID và Client Secret của Google OAuth
- **KHÔNG BAO GIỜ** commit lên Git
- **KHÔNG** chia sẻ cho ai

**Backup:**
```bash
# Copy với tên khác và lưu ở nơi an toàn
cp credentials.json credentials.backup.json
# Hoặc lưu vào USB/cloud riêng tư
```

---

### 2. `token.json` - Google Access Token
**Mức độ:** 🟠 RẤT NHẠY CẢM
- Chứa access token và refresh token
- Cho phép truy cập Google Calendar & Tasks
- Hết hạn sau một thời gian (auto refresh)
- **KHÔNG** commit lên Git

**Backup:**
```bash
# Backup định kỳ
cp token.json token.backup.json
```

**Khôi phục:** Nếu mất, chỉ cần chạy lại app và xác thực Google lại.

---

### 3. `.uth_credentials` - UTH Login Info
**Mức độ:** 🟡 NHẠY CẢM
- Chứa MSSV và password (đã mã hóa)
- Mã hóa bằng XOR cipher + machine-specific key
- Chỉ giải mã được trên máy tính đã mã hóa

**Đặc điểm:**
- ✅ Mã hóa dựa trên thông tin máy tính
- ✅ Không thể giải mã trên máy khác
- ✅ File ẩn (bắt đầu với dấu `.`)
- ✅ Quyền truy cập hạn chế (chmod 600)

---

## 🛡️ Cách Bảo Vệ

### ✅ Đã Làm (Built-in)
1. **`.gitignore` đầy đủ** - Tất cả file nhạy cảm đã được ignore
2. **Mã hóa credentials** - XOR cipher với machine key
3. **File permissions** - Chmod 600 (chỉ owner đọc/ghi)
4. **Machine-specific encryption** - Không thể copy sang máy khác

### 🔒 Nên Làm Thêm

#### 1. Backup An Toàn
```bash
# Tạo thư mục backup riêng (không trong repo)
mkdir -p ~/uth-backup

# Backup tất cả credentials
cp credentials.json ~/uth-backup/credentials_$(date +%Y%m%d).json
cp token.json ~/uth-backup/token_$(date +%Y%m%d).json
cp .uth_credentials ~/uth-backup/uth_$(date +%Y%m%d).json

# Encrypt thư mục backup (Windows: sử dụng BitLocker)
# Linux/Mac: 
tar -czf - ~/uth-backup | openssl enc -aes-256-cbc -e > uth-backup.tar.gz.enc
```

#### 2. Cloud Backup (Mã hóa)
```bash
# Sử dụng rclone với encryption
rclone copy ~/uth-backup/ mycloud:/encrypted/uth-backup/ --crypt

# Hoặc 7zip với password
7z a -p uth-backup.7z ~/uth-backup/*
```

#### 3. USB Backup
```bash
# Copy vào USB (nên dùng USB mã hóa)
cp -r ~/uth-backup /media/usb/
```

---

## 🚨 Khi Bị Mất Token

### Mất `credentials.json`
1. Vào [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo OAuth credentials mới
3. Download và đổi tên thành `credentials.json`
4. Chạy lại app và xác thực

### Mất `token.json`
1. Xóa file `token.json` (nếu còn)
2. Chạy lại app: `python main.py`
3. Trình duyệt sẽ mở để xác thực lại
4. Token mới sẽ được tạo tự động

### Mất `.uth_credentials`
1. Không thể khôi phục (do machine-specific)
2. Chỉ cần nhập lại MSSV/password trong app
3. Tick "Lưu thông tin đăng nhập" để tạo mới

---

## 🔄 Thu Hồi Quyền Truy Cập

### Thu hồi Google Token
1. Vào [Google Account Permissions](https://myaccount.google.com/permissions)
2. Tìm "UTH Calendar Manager"
3. Click "Remove Access"
4. Xóa `token.json` trên máy

### Đổi Password UTH
1. Đổi password trên hệ thống UTH
2. Xóa `.uth_credentials`
3. Nhập password mới trong app

---

## 📂 Cấu Trúc Lưu Trữ Đề Xuất

```
📁 D:/Secure/
├── 📁 UTH-Backup/
│   ├── 🔒 credentials_20251225.json
│   ├── 🔒 token_20251225.json
│   ├── 🔒 uth_20251225.json
│   └── 📝 backup_log.txt
│
├── 📁 Project/ (Git repo)
│   ├── main.py
│   ├── README.md
│   ├── .gitignore ✅
│   ├── credentials.json ❌ (not in Git)
│   ├── token.json ❌ (not in Git)
│   └── .uth_credentials ❌ (not in Git)
```

---

## ⚠️ Cảnh Báo An Ninh

### ❌ KHÔNG BAO GIỜ:
- ❌ Commit credentials lên Git/GitHub
- ❌ Share credentials qua email/chat
- ❌ Screenshot chứa credentials
- ❌ Paste credentials vào pastebin/gist
- ❌ Upload credentials lên cloud public

### ✅ NÊN:
- ✅ Backup thường xuyên
- ✅ Encrypt backups
- ✅ Sử dụng 2FA cho Google Account
- ✅ Đổi password định kỳ
- ✅ Kiểm tra Git history trước khi push

---

## 🔍 Kiểm Tra Rò Rỉ

### Trước khi commit:
```bash
# Kiểm tra xem có file nhạy cảm không
git status

# Kiểm tra staged files
git diff --cached

# Tìm kiếm credentials trong code
grep -r "credentials" . --exclude-dir=.git
grep -r "token" . --exclude-dir=.git
```

### Nếu đã commit nhầm:
```bash
# Xóa file khỏi Git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch credentials.json" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (CHỈ nếu repo là private và của bạn)
git push origin --force --all
```

---

## 🔐 Nâng Cao: Sử dụng Cryptography

Nếu muốn bảo mật cao hơn, có thể nâng cấp lên Fernet encryption:

```python
# Thêm vào requirements.txt
cryptography>=41.0.0

# Trong code:
from cryptography.fernet import Fernet

def get_fernet_key():
    """Tạo hoặc load Fernet key"""
    key_file = ".uth_key"
    if os.path.exists(key_file):
        with open(key_file, "rb") as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, "wb") as f:
            f.write(key)
        os.chmod(key_file, 0o600)
        return key

def encrypt_data_fernet(data):
    key = get_fernet_key()
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()

def decrypt_data_fernet(data):
    key = get_fernet_key()
    f = Fernet(key)
    return f.decrypt(data.encode()).decode()
```

---

## 📞 Hỗ Trợ

Nếu có vấn đề về bảo mật:
- 📧 Email: your.email@example.com
- 🐙 GitHub Issues: [Create Issue](https://github.com/yourusername/uth-calendar-manager/issues)

---

**🔒 An toàn hơn = Yên tâm hơn!**
