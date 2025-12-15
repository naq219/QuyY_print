# 🚀 BẮT ĐẦU NHANH - QUY Y PRINTER

## ⚡ Bước 1: Chuẩn bị (2 phút)

### 1.1. Cài đặt Python (nếu chưa có)
- Tải Python 3.8+ từ: https://www.python.org/downloads/
- ✅ Tick vào "Add Python to PATH" khi cài đặt
- Kiểm tra: Mở Command Prompt, gõ `python --version`

### 1.2. Chuẩn bị Font
```
📁 quy_y_printer/
  📁 fonts/
    📄 quyyfont.ttf  ← ĐẶT FILE FONT VÀO ĐÂY
```

### 1.3. Cài đặt Dependencies
Mở Command Prompt tại thư mục `quy_y_printer`:
```cmd
pip install -r requirements.txt
```

⏱️ **Thời gian**: ~2-3 phút tùy tốc độ mạng

---

## 🎯 Bước 2: Chạy ứng dụng (30 giây)

### Windows:
```cmd
python main.py
```

### Linux/Mac:
```bash
python3 main.py
```

✅ Cửa sổ ứng dụng sẽ mở ra!

---

## 📝 Bước 3: Sử dụng (1 phút)

### 3.1. Chọn file Excel
1. Click nút **"Chọn File"**
2. Chọn file Excel có sẵn dữ liệu
3. Số bản ghi sẽ hiển thị bên dưới

### 3.2. Chọn nơi lưu PDF
1. Click nút **"Chọn Thư Mục"**
2. Chọn thư mục để lưu các file PDF

### 3.3. Xuất PDF
1. Click nút **"📄 Xuất PDF"**
2. Đợi progress bar chạy
3. Thư mục chứa PDF sẽ tự động mở

### 3.4. Hoặc in trực tiếp
1. Click nút **"🖨️ In Trực Tiếp"**
2. Các file sẽ được gửi đến máy in mặc định

---

## 🔧 Bước 4: Điều chỉnh tọa độ (nếu cần)

**Vấn đề**: Text không khớp với vị trí trên lá phái?

### 4.1. Test với 1 file trước
- Chỉ chọn 1-2 bản ghi đầu tiên
- Xuất PDF và kiểm tra

### 4.2. Điều chỉnh
1. Mở file `config.py`
2. Tìm `FIELD_POSITIONS`
3. Sửa giá trị `x`, `y` cho từng trường
4. Lưu file và chạy lại

### Ví dụ:
```python
# Text quá TRÁI → Tăng x
"ho_ten": {"x": 95, "y": 147, ...}  # Trước là 85

# Text quá CAO → Tăng y  
"ho_ten": {"x": 85, "y": 152, ...}  # Trước là 147
```

📖 **Chi tiết**: Xem file `DIEU_CHINH_TOA_DO.md`

---

## ✅ Checklist nhanh

```
☐ Python 3.8+ đã cài
☐ File quyyfont.ttf đã đặt vào fonts/
☐ pip install -r requirements.txt đã chạy
☐ File Excel đã chuẩn bị (có đủ các cột cần thiết)
☐ Đã test với 1-2 file trước
☐ Tọa độ đã điều chỉnh chính xác
```

---

## 🎁 Build file .exe (Tùy chọn)

Nếu muốn tạo file .exe để dùng mà không cần Python:

### Windows:
```cmd
build.bat
```

### Linux/Mac:
```bash
./build.sh
```

File .exe sẽ nằm trong thư mục `dist/`

---

## 🆘 Gặp vấn đề?

### Lỗi "No module named..."
```cmd
pip install tên_module --break-system-packages
```

### Lỗi "Cannot read Excel"
- Đóng file Excel nếu đang mở
- Kiểm tra định dạng file (.xlsx hoặc .xls)
- Kiểm tra các cột: hovaten, namsinh, diachithuongtru_short, dauthoigian

### Font không hiển thị tiếng Việt
- Kiểm tra file `quyyfont.ttf` có trong `fonts/` không
- Đảm bảo tên file chính xác (không có khoảng trắng)

### Tọa độ không chính xác
- Xem hướng dẫn trong `DIEU_CHINH_TOA_DO.md`
- Điều chỉnh từng 2-5mm một lần
- Test sau mỗi lần điều chỉnh

---

## 📚 Tài liệu đầy đủ

- 📘 **README.md**: Hướng dẫn đầy đủ
- 📗 **DIEU_CHINH_TOA_DO.md**: Chi tiết về điều chỉnh tọa độ
- 📙 **PROJECT_OVERVIEW.md**: Tổng quan kỹ thuật
- 📕 **CHANGELOG.md**: Lịch sử phiên bản

---

## 🎉 Hoàn thành!

Bây giờ bạn đã sẵn sàng in hàng trăm lá phái quy y một cách tự động! 

**Mẹo**: Luôn test với 1-2 file trước khi in hàng loạt để đảm bảo tọa độ chính xác.

---

**Thời gian tổng cộng**: ~5-10 phút (bao gồm cài đặt)  
**Độ khó**: ⭐⭐ (Dễ - Trung bình)

💡 **Nếu vẫn gặp khó khăn**, hãy xem file `README.md` để được hướng dẫn chi tiết hơn!
