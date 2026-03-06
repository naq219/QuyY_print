# QUY Y PRINTER - TỔNG QUAN DỰ ÁN

## 📋 Mô tả
Ứng dụng desktop tự động in lá phái quy y từ danh sách Excel với các tính năng:
- Chuyển đổi âm lịch tự động
- Xuất PDF hàng loạt
- In trực tiếp ra máy in
- Giao diện đơn giản, dễ sử dụng

## 🗂️ Cấu trúc dự án

```
quy_y_printer/
│
├── 📄 main.py                      # File chính - GUI Tkinter
├── 📄 config.py                    # Cấu hình tọa độ các trường
├── 📄 lunar_converter.py           # Module chuyển đổi âm lịch
├── 📄 pdf_generator.py             # Module tạo PDF với ReportLab
├── 📄 test.py                      # Test suite
│
├── 📁 fonts/                       # Thư mục chứa font
│   ├── quyyfont.ttf               # Font VNI-Commerce (cần thêm)
│   └── README.txt                 # Hướng dẫn
│
├── 📄 requirements.txt             # Python dependencies
├── 📄 QuyYPrinter.spec            # PyInstaller spec file
│
├── 📄 build.bat                    # Script build exe (Windows)
├── 📄 build.sh                     # Script build exe (Linux/Mac)
│
├── 📄 README.md                    # Hướng dẫn đầy đủ
├── 📄 HUONG_DAN_NHANH.txt         # Hướng dẫn nhanh
├── 📄 DIEU_CHINH_TOA_DO.md        # Hướng dẫn điều chỉnh tọa độ
├── 📄 CHANGELOG.md                 # Lịch sử thay đổi
├── 📄 PROJECT_OVERVIEW.md          # File này
│
└── 📄 sample_data.xlsx             # File Excel mẫu
```

## 🔧 Công nghệ sử dụng

### Backend
- **Python 3.8+**: Ngôn ngữ chính
- **ReportLab**: Tạo PDF với font Unicode
- **Pandas**: Xử lý dữ liệu Excel
- **OpenPyXL**: Đọc file Excel

### Frontend
- **Tkinter**: GUI (built-in Python)
- **ttk**: Themed widgets

### Build & Deploy
- **PyInstaller**: Build file .exe
- **--onefile**: Single executable
- **--windowed**: Không hiện console

## 📊 Luồng hoạt động

```
[1] User chọn file Excel
         ↓
[2] Ứng dụng đọc và validate dữ liệu
         ↓
[3] User chọn: "Xuất PDF" hoặc "In trực tiếp"
         ↓
[4] Với mỗi bản ghi:
    a. Đọc thông tin từ Excel
    b. Chuyển ngày dương → âm lịch
    c. Tính Phật lịch
    d. Tạo PDF với text ở tọa độ đã cấu hình
         ↓
[5] Hiển thị kết quả + mở thư mục output
```

## 🎨 Định dạng text

| Trường | Font Size | Bold | Italic | Align |
|--------|-----------|------|--------|-------|
| Pháp danh | 18 | ❌ | ✅ | Left |
| Họ tên | 18 | ❌ | ✅ | Left |
| Năm sinh | 12 | ❌ | ✅ | Left |
| Địa chỉ | 12 | ✅ | ✅ | Left |
| Ngày DL | 11 | ❌ | ✅ | Center |
| Tháng DL | 11 | ❌ | ✅ | Center |
| Năm DL | 11 | ❌ | ✅ | Center |
| Ngày ÂL | 11 | ❌ | ✅ | Center |
| Tháng ÂL | 11 | ❌ | ✅ | Center |
| Năm ÂL | 11 | ✅ | ✅ | Center |
| Phật lịch | 11 | ✅ | ✅ | Center |

## 📍 Tọa độ mặc định

Tọa độ tính theo mm trên khổ A4 (210mm x 297mm):

```python
FIELD_POSITIONS = {
    "phap_danh": {"x": 85, "y": 147},    # Pháp danh
    "ho_ten": {"x": 85, "y": 147},       # Họ tên (nếu không có pháp danh)
    "sinh_nam": {"x": 85, "y": 157},     # Năm sinh
    "dia_chi": {"x": 85, "y": 165},      # Địa chỉ
    "ngay_duong": {"x": 110, "y": 198},  # Ngày DL
    "thang_duong": {"x": 130, "y": 198}, # Tháng DL
    "nam_duong": {"x": 155, "y": 198},   # Năm DL
    "ngay_am": {"x": 110, "y": 206},     # Ngày ÂL
    "thang_am": {"x": 130, "y": 206},    # Tháng ÂL
    "nam_am": {"x": 155, "y": 206},      # Năm ÂL
    "phat_lich": {"x": 155, "y": 214}    # Phật lịch
}
```

**Lưu ý**: Đây là tọa độ ước lượng ban đầu, cần điều chỉnh theo template thực tế.

## 🧪 Testing

Chạy test suite:
```bash
python test.py
```

Test coverage:
- ✅ Chuyển đổi âm lịch
- ✅ Tạo PDF đơn lẻ
- ✅ Đọc file Excel
- ✅ Tạo PDF hàng loạt

## 📦 Build & Deploy

### Build trên Windows:
```cmd
build.bat
```

### Build trên Linux/Mac:
```bash
chmod +x build.sh
./build.sh
```

### Build thủ công:
```bash
pyinstaller QuyYPrinter.spec
```

File output: `dist/QuyYPrinter.exe` (Windows) hoặc `dist/QuyYPrinter` (Linux/Mac)

## 🔐 Dependencies

```
reportlab>=4.0.0    # PDF generation
pandas>=2.0.0       # Excel processing
openpyxl>=3.1.0     # Excel file format
pillow>=10.0.0      # Image processing
pyinstaller>=6.0.0  # Build executable
```

## 🐛 Known Issues

1. **Font warning**: Nếu không có file `quyyfont.ttf`, sẽ dùng Helvetica (không hỗ trợ tiếng Việt tốt)
2. **Tọa độ**: Cần điều chỉnh thủ công cho chính xác
3. **Header row**: Dòng đầu Excel bị skip (mặc định là header)

## 🚀 Roadmap

### Version 1.1.0 (Q1 2026)
- [ ] GUI điều chỉnh tọa độ drag-and-drop
- [ ] Preview PDF real-time
- [ ] Undo/Redo cho điều chỉnh tọa độ
- [ ] Save/Load cấu hình

### Version 1.2.0 (Q2 2026)
- [ ] Hỗ trợ nhiều template
- [ ] Template marketplace
- [ ] Export sang Word/Image
- [ ] Batch printing với queue

### Version 2.0.0 (Q3 2026)
- [ ] Cloud storage integration
- [ ] Multi-language support
- [ ] Database backend
- [ ] Web version

## 👥 Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng:
1. Fork repository
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## 📝 License

MIT License - Free to use and modify.

## 📧 Liên hệ

Nếu có câu hỏi hoặc gặp vấn đề, vui lòng tạo issue trên GitHub hoặc liên hệ trực tiếp.

---

**Version**: 1.0.0  
**Last Updated**: 2025-12-15  
**Status**: ✅ Production Ready
