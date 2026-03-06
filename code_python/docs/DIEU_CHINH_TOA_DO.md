# HƯỚNG DẪN ĐIỀU CHỈNH TỌA ĐỘ CHI TIẾT

## Giới thiệu
Tọa độ các trường text được cấu hình trong file `config.py`. Bạn có thể dễ dàng điều chỉnh để phù hợp với template của mình.

## Hệ tọa độ

- **Gốc tọa độ (0,0)**: Góc TRÊN BÊN TRÁI của trang A4
- **Trục X**: Từ TRÁI sang PHẢI (đơn vị: mm)
- **Trục Y**: Từ TRÊN xuống DƯỚI (đơn vị: mm)
- **Kích thước A4**: 210mm (rộng) x 297mm (cao)

```
(0,0) ────────────────────────────> X (210mm)
  │
  │    ┌──────────────────────┐
  │    │                      │
  │    │     Trang A4         │
  │    │                      │
  │    │                      │
  │    │                      │
  │    └──────────────────────┘
  ↓
  Y
(297mm)
```

## Cấu trúc cấu hình

Mỗi trường trong `FIELD_POSITIONS` có cấu trúc:

```python
"ten_truong": {
    "x": 85,           # Tọa độ X (mm từ trái)
    "y": 147,          # Tọa độ Y (mm từ trên)
    "size": 18,        # Cỡ chữ
    "bold": False,     # In đậm (True/False)
    "italic": True,    # In nghiêng (True/False)
    "align": "L"       # Căn chỉnh: L=Left, C=Center, R=Right
}
```

## Các trường cần điều chỉnh

### 1. Pháp danh / Họ tên
```python
"phap_danh": {
    "x": 85,      # Thử thay đổi từ 80-100
    "y": 147,     # Thử thay đổi từ 140-155
    "size": 18,
    "bold": False,
    "italic": True,
    "align": "L"
}
```

### 2. Năm sinh
```python
"sinh_nam": {
    "x": 85,
    "y": 157,     # Khoảng cách ~10mm từ họ tên
    "size": 12,
    "bold": False,
    "italic": True,
    "align": "L"
}
```

### 3. Địa chỉ
```python
"dia_chi": {
    "x": 85,
    "y": 165,     # Khoảng cách ~8mm từ năm sinh
    "size": 12,
    "bold": True,    # In đậm
    "italic": True,
    "align": "L"
}
```

### 4. Ngày Dương lịch
```python
"ngay_duong": {
    "x": 110,     # Vị trí cột "ngày"
    "y": 198,
    "size": 11,
    "bold": False,
    "italic": True,
    "align": "C"  # Căn giữa
}
```

### 5. Tháng Dương lịch
```python
"thang_duong": {
    "x": 130,     # Vị trí cột "tháng" (cách ngày ~20mm)
    "y": 198,
    "size": 11,
    "bold": False,
    "italic": True,
    "align": "C"
}
```

### 6. Năm Dương lịch
```python
"nam_duong": {
    "x": 155,     # Vị trí cột "năm" (cách tháng ~25mm)
    "y": 198,
    "size": 11,
    "bold": False,
    "italic": True,
    "align": "C"
}
```

### 7-9. Ngày/Tháng/Năm Âm lịch
```python
"ngay_am": {"x": 110, "y": 206, ...},   # Cùng X với ngày dương
"thang_am": {"x": 130, "y": 206, ...},  # Cùng X với tháng dương
"nam_am": {
    "x": 155,
    "y": 206,
    "size": 11,
    "bold": True,    # In đậm
    "italic": True,
    "align": "C"
}
```

### 10. Phật lịch
```python
"phat_lich": {
    "x": 155,     # Cùng X với năm âm
    "y": 214,     # Cách năm âm ~8mm
    "size": 11,
    "bold": True,    # In đậm
    "italic": True,
    "align": "C"
}
```

## Quy trình điều chỉnh

### Bước 1: Xác định vị trí cần chỉnh
1. In thử 1 file PDF
2. So sánh với template mẫu
3. Xác định trường nào cần dịch chuyển

### Bước 2: Tính toán độ lệch
- Nếu text **quá TRÁI** → Tăng giá trị X
- Nếu text **quá PHẢI** → Giảm giá trị X
- Nếu text **quá CAO** → Tăng giá trị Y
- Nếu text **quá THẤP** → Giảm giá trị Y

**Mẹo**: Mỗi lần điều chỉnh 2-5mm để dễ kiểm soát

### Bước 3: Sửa config.py
1. Mở file `config.py`
2. Tìm trường cần sửa trong `FIELD_POSITIONS`
3. Thay đổi giá trị `x` hoặc `y`
4. Lưu file

### Bước 4: Test lại
1. Chạy lại ứng dụng
2. Xuất PDF thử với 1-2 bản ghi
3. Kiểm tra kết quả
4. Lặp lại cho đến khi đúng

## Ví dụ điều chỉnh

### Ví dụ 1: Họ tên quá trái, muốn dịch sang phải 10mm
```python
# TRƯỚC
"ho_ten": {"x": 85, "y": 147, ...}

# SAU
"ho_ten": {"x": 95, "y": 147, ...}  # 85 + 10 = 95
```

### Ví dụ 2: Ngày tháng quá cao, muốn hạ xuống 5mm
```python
# TRƯỚC
"ngay_duong": {"x": 110, "y": 198, ...}

# SAU
"ngay_duong": {"x": 110, "y": 203, ...}  # 198 + 5 = 203
```

### Ví dụ 3: Điều chỉnh toàn bộ dòng ngày tháng
```python
# Điều chỉnh cả 3 trường cùng lúc để giữ căn chỉnh
"ngay_duong": {"x": 110, "y": 200, ...},
"thang_duong": {"x": 130, "y": 200, ...},  # Cùng Y
"nam_duong": {"x": 155, "y": 200, ...},    # Cùng Y
```

## Mẹo và Lưu ý

### 1. Đo chính xác từ template
- Dùng ruler tool trong Photoshop/GIMP
- Hoặc in template và dùng thước đo

### 2. Backup trước khi sửa
```bash
cp config.py config.py.backup
```

### 3. Test với in thật
- Test trên màn hình có thể khác in thật
- In thử vài trang để kiểm tra

### 4. Căn chỉnh theo cột
- Các trường cùng cột nên có cùng X
- Ví dụ: ngày/tháng/năm dương và âm

### 5. Khoảng cách giữa các dòng
- Thường là 8-10mm cho text bình thường
- Có thể tăng/giảm tùy design

## Công cụ hỗ trợ (Tương lai)

Trong phiên bản tương lai, chúng tôi sẽ thêm:
- GUI drag-and-drop để điều chỉnh tọa độ trực quan
- Preview real-time
- Tool đo tọa độ từ ảnh template

## Troubleshooting

### Text bị cắt
- Kiểm tra size chữ có quá lớn không
- Kiểm tra X không vượt quá 200mm
- Kiểm tra Y không vượt quá 290mm

### Text không hiển thị
- Kiểm tra font đã được load chưa
- Kiểm tra tọa độ có nằm ngoài trang không
- Kiểm tra dữ liệu có rỗng không

### Căn chỉnh không đều
- Sử dụng `align: "C"` cho text ngắn
- Sử dụng `align: "L"` cho text dài

## Liên hệ

Nếu cần hỗ trợ thêm, vui lòng liên hệ hoặc tạo issue.
