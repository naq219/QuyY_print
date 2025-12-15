# Ứng Dụng In Lá Phái Quy Y

Ứng dụng tự động in lá phái quy y từ danh sách Excel với tính năng chuyển đổi âm lịch tự động.

## Tính năng

- ✅ Đọc dữ liệu từ file Excel
- ✅ Chuyển đổi ngày dương lịch sang âm lịch tự động
- ✅ Tính Phật lịch (năm dương lịch + 544)
- ✅ Xuất PDF hàng loạt
- ✅ In trực tiếp ra máy in
- ✅ Giao diện đơn giản, dễ sử dụng
- ✅ Hỗ trợ font Unicode tiếng Việt

## Yêu cầu hệ thống

- Windows 7/8/10/11 (64-bit)
- Python 3.8+ (nếu chạy từ source code)

## Cài đặt

### Cách 1: Chạy file .exe (Đơn giản nhất)

1. Tải file `QuyYPrinter.exe`
2. Đặt file `quyyfont.ttf` vào thư mục `fonts/`
3. Double-click để chạy

### Cách 2: Chạy từ source code

```bash
# Clone hoặc download source code
cd quy_y_printer

# Cài đặt dependencies
python -m pip install -r requirements.txt

# Chạy ứng dụng
python main.py
```

### Cách 3: Build file .exe

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Build exe bằng PyInstaller
pyinstaller --onefile --windowed --add-data "fonts;fonts" --icon=icon.ico main.py

# File .exe sẽ được tạo trong thư mục dist/
```

## Cấu trúc thư mục

```
quy_y_printer/
│
├── main.py                 # File chính
├── config.py              # Cấu hình tọa độ
├── lunar_converter.py     # Module chuyển âm lịch
├── pdf_generator.py       # Module tạo PDF
├── requirements.txt       # Dependencies
├── README.md             # File này
│
├── fonts/
│   └── quyyfont.ttf      # Font VNI-Commerce (cần thêm)
│
└── dist/                 # Thư mục chứa file .exe (sau khi build)
    └── main.exe
```

## Hướng dẫn sử dụng

### 1. Chuẩn bị file Excel

File Excel cần có các cột sau:

- `hovaten`: Họ và tên
- `phapdanh`: Pháp danh (để trống nếu không có)
- `namsinh`: Năm sinh
- `diachithuongtru_short`: Địa chỉ
- `dauthoigian`: Ngày quy y (định dạng: YYYY-MM-DD hoặc YYYY-MM-DD HH:MM:SS)

### 2. Chạy ứng dụng

1. Mở ứng dụng
2. Chọn file Excel (nút "Chọn File")
3. Chọn thư mục lưu PDF (nút "Chọn Thư Mục")
4. Chọn một trong hai:
   - **Xuất PDF**: Tạo file PDF và lưu vào thư mục
   - **In Trực Tiếp**: Tạo PDF tạm và gửi đến máy in

### 3. Kết quả

- PDF được tạo với tên file: `{họ_tên}_{index}.pdf`
- Chỉ in text, không in ảnh nền (để in lên giấy đã có sẵn hình)

## Điều chỉnh tọa độ

Tọa độ các trường được cấu hình trong file `config.py`:

```python
FIELD_POSITIONS = {
    "phap_danh": {
        "x": 85,      # mm từ trái
        "y": 147,     # mm từ trên
        "size": 18,   # Cỡ chữ
        "bold": False,
        "italic": True,
        "align": "L"  # L: Left, C: Center, R: Right
    },
    # ... các trường khác
}
```

Để điều chỉnh:

1. Mở file `config.py`
2. Sửa giá trị `x`, `y` cho từng trường
3. Lưu và chạy lại ứng dụng
4. Test với 1-2 bản ghi trước khi in hàng loạt

## Format text

- **Họ tên, Pháp danh**: Size 18, italic
- **Năm sinh**: Size 12, italic
- **Địa chỉ**: Size 12, bold + italic
- **Ngày tháng (DL, ÂL)**: Size 11, italic
- **Năm ÂL, Phật lịch**: Size 11, bold + italic

## Lưu ý

1. **Font chữ**: Đặt file `quyyfont.ttf` vào thư mục `fonts/`
2. **Âm lịch**: Được tính tự động bằng thuật toán chuyển đổi lịch Việt Nam
3. **Phật lịch**: Tự động tính = Năm dương lịch + 544
4. **Pháp danh**: Nếu có pháp danh thì in pháp danh, nếu không thì in họ tên

## Troubleshooting

### Lỗi: "Không thể load font"
- Kiểm tra file `quyyfont.ttf` có trong thư mục `fonts/` không
- Đảm bảo đường dẫn đến font đúng

### Lỗi: "Không thể đọc file Excel"
- Kiểm tra định dạng file (.xlsx hoặc .xls)
- Đảm bảo các cột cần thiết có trong file
- Đóng file Excel nếu đang mở

### Tọa độ không chính xác
- Mở file `config.py` và điều chỉnh giá trị `x`, `y`
- Test với 1-2 file trước khi in hàng loạt

## Tính năng tương lai

- [ ] GUI điều chỉnh tọa độ trực tiếp
- [ ] Preview PDF trước khi in
- [ ] Hỗ trợ nhiều template khác nhau
- [ ] Export sang định dạng khác (Word, Image)

## Liên hệ & Hỗ trợ

Nếu gặp vấn đề, vui lòng liên hệ hoặc tạo issue trên GitHub.

## License

MIT License - Free to use and modify.
