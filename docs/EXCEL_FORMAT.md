# 📊 ĐỊNH DẠNG FILE EXCEL

## Yêu cầu chung

File Excel (.xlsx hoặc .xls) cần có các cột sau:

| Tên cột | Kiểu dữ liệu | Bắt buộc | Ghi chú |
|---------|--------------|----------|---------|
| `hovaten` | Text | ✅ | Họ và tên đầy đủ |
| `phapdanh` | Text | ❌ | Pháp danh (để trống nếu không có) |
| `namsinh` | Number/Text | ✅ | Năm sinh (VD: 1990, 1995) |
| `diachithuongtru_short` | Text | ✅ | Địa chỉ rút gọn |
| `dauthoigian` | Date/DateTime | ✅ | Ngày quy y |

## Chi tiết từng cột

### 1. `hovaten` - Họ và tên
- **Bắt buộc**: ✅ Có
- **Kiểu**: Text
- **Độ dài**: Không giới hạn (khuyến nghị < 50 ký tự)
- **Ví dụ**: 
  - `Nguyễn Văn A`
  - `Trần Thị Bích Ngọc`
  - `Lê Hoàng Nam`

**Lưu ý**: 
- Nếu có `phapdanh` thì sẽ in pháp danh, không in họ tên
- Nếu không có `phapdanh` thì in họ tên

---

### 2. `phapdanh` - Pháp danh
- **Bắt buộc**: ❌ Không (có thể để trống)
- **Kiểu**: Text
- **Độ dài**: Không giới hạn (khuyến nghị < 50 ký tự)
- **Ví dụ**: 
  - `Thích Thiện Tâm`
  - `Thích Minh Đức`
  - (để trống nếu không có)

**Lưu ý**: 
- Nếu có pháp danh, sẽ ưu tiên in pháp danh thay vì họ tên
- Nếu để trống, sẽ in họ tên thông thường

---

### 3. `namsinh` - Năm sinh
- **Bắt buộc**: ✅ Có
- **Kiểu**: Number hoặc Text
- **Format**: YYYY (4 số)
- **Ví dụ**: 
  - `1990`
  - `1985`
  - `2000`

**Lưu ý**: 
- Chỉ cần năm, không cần ngày/tháng
- Có thể nhập dạng số hoặc text
- Không format thành date trong Excel

---

### 4. `diachithuongtru_short` - Địa chỉ
- **Bắt buộc**: ✅ Có
- **Kiểu**: Text
- **Độ dài**: Không giới hạn (khuyến nghị < 100 ký tự)
- **Ví dụ**: 
  - `Phường Vinh Tân, TP Vinh, Nghệ An`
  - `Xã Thượng Sơn, Đô Lương, Nghệ An`
  - `Hà Nội`

**Lưu ý**: 
- Có thể viết đầy đủ hoặc rút gọn tùy ý
- Địa chỉ quá dài có thể bị cắt khi in

---

### 5. `dauthoigian` - Ngày quy y
- **Bắt buộc**: ✅ Có
- **Kiểu**: Date hoặc DateTime hoặc Text
- **Format hỗ trợ**: 
  - `YYYY-MM-DD` (2025-05-02)
  - `YYYY-MM-DD HH:MM:SS` (2025-05-02 19:00:07)
  - Date format của Excel

**Ví dụ**: 
  - `2025-05-02`
  - `2025-12-15`
  - `2025-05-02 19:00:07`

**Lưu ý**: 
- Ứng dụng tự động chuyển sang âm lịch
- Phật lịch = Năm dương lịch + 544
- Nếu có giờ phút giây, chỉ lấy phần ngày

---

## Template Excel mẫu

### Dòng header (dòng đầu tiên):
```
hovaten | phapdanh | namsinh | diachithuongtru_short | dauthoigian
```

### Dòng dữ liệu mẫu:
```
Nguyễn Văn A |  | 1990 | Hà Nội | 2025-05-02
Trần Thị B | Thích Thiện Tâm | 1985 | TP.HCM | 2025-05-03
Lê Văn C |  | 2000 | Nghệ An | 2025-05-04 10:30:00
```

---

## Các cột bổ sung (không bắt buộc)

Nếu file Excel có thêm các cột khác, ứng dụng sẽ **bỏ qua** chúng:
- `gioitinh` (giới tính)
- `sodienthoai` (số điện thoại)
- `diachithuongtru` (địa chỉ đầy đủ)
- `nguoigioithieu` (người giới thiệu)
- `ghichu` (ghi chú)
- v.v.

---

## Xử lý dữ liệu

### Dòng header
- Dòng đầu tiên được **tự động bỏ qua** (mặc định là header)
- Đếm số bản ghi từ dòng thứ 2 trở đi

### Dữ liệu rỗng/null
- Nếu `hovaten` rỗng → Bỏ qua dòng này
- Nếu `phapdanh` rỗng → In `hovaten`
- Nếu các trường khác rỗng → Để trống tương ứng

### Khoảng trắng
- Tự động trim khoảng trắng thừa đầu/cuối
- Khoảng trắng giữa các từ được giữ nguyên

---

## Ví dụ file Excel hoàn chỉnh

| hovaten | phapdanh | namsinh | diachithuongtru_short | dauthoigian |
|---------|----------|---------|----------------------|-------------|
| Nguyễn Văn A | | 1990 | Hà Nội | 2025-05-02 |
| Trần Thị Bích | Thích Minh Đức | 1985 | TP Vinh, Nghệ An | 2025-05-03 |
| Lê Hoàng Nam | | 2000 | Đà Nẵng | 2025-05-04 |
| Phạm Thị Lan | Thích Thiện Tâm | 1995 | Hải Phòng | 2025-05-05 |

**Kết quả in**:
1. Lá 1: Nguyễn Văn A, 1990, Hà Nội, DL: 2/5/2025, ÂL: 5/4/2025
2. Lá 2: Thích Minh Đức, 1985, TP Vinh, Nghệ An, DL: 3/5/2025, ÂL: 6/4/2025
3. Lá 3: Lê Hoàng Nam, 2000, Đà Nẵng, DL: 4/5/2025, ÂL: 7/4/2025
4. Lá 4: Thích Thiện Tâm, 1995, Hải Phòng, DL: 5/5/2025, ÂL: 8/4/2025

---

## Lỗi thường gặp

### ❌ "Cannot read Excel file"
**Nguyên nhân**: 
- File đang mở trong Excel
- File bị hỏng
- Không phải format .xlsx/.xls

**Giải pháp**:
- Đóng file Excel
- Kiểm tra lại định dạng file
- Thử save as .xlsx

### ❌ "Column not found"
**Nguyên nhân**: 
- Thiếu một trong các cột bắt buộc
- Tên cột sai chính tả

**Giải pháp**:
- Kiểm tra tên cột: `hovaten`, `namsinh`, `diachithuongtru_short`, `dauthoigian`
- Không có dấu cách, viết liền

### ❌ "Invalid date format"
**Nguyên nhân**: 
- Ngày không đúng format
- Có ký tự đặc biệt

**Giải pháp**:
- Dùng format YYYY-MM-DD
- Hoặc dùng date picker trong Excel

---

## Tips & Tricks

### 💡 Tip 1: Copy từ Google Sheets
- Export Google Sheets → Download as .xlsx
- Hoặc copy-paste vào Excel desktop

### 💡 Tip 2: Validate dữ liệu trước
- Check không có dòng rỗng
- Check format ngày tháng đúng
- Check không có ký tự lạ

### 💡 Tip 3: Backup dữ liệu
- Luôn giữ 1 bản backup
- Tách file lớn thành nhiều file nhỏ nếu cần

### 💡 Tip 4: Test trước
- Test với 3-5 dòng đầu tiên
- Kiểm tra kỹ trước khi in hàng loạt

---

**Lưu ý**: File `sample_data.xlsx` trong project là ví dụ thực tế có thể tham khảo!
