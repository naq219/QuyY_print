# Rules: Năm sinh / Ngày sinh format

## Quy tắc lưu trữ
- **DB field**: `ngay_sinh TEXT` (nullable)
- **Lưu dạng text gốc**: "1990", "02/1990", hoặc "01/02/1990"
- **KHÔNG** lưu dạng ISO `yyyy-mm-dd` nữa
- **KHÔNG** dùng DatePicker component — dùng InputText

## Quy tắc nhập liệu
1. **Chỉ năm**: `1990` → lưu "1990"
2. **Tháng/năm**: `02/1990` → lưu "02/1990"
3. **Đầy đủ**: `01/02/1990` → lưu "01/02/1990"
4. **Auto-pad**: `1/2/1990` → `01/02/1990`
5. **Separator normalize**: Chấp nhận `-`, `.` hoặc `/` → tự đổi thành `/`
6. **Year shorthand**: `90` → `1990` (thêm "19")
7. **Validation**: Năm 1900-2030, tháng 1-12, ngày 1-31
8. **Không bắt buộc**: Có thể để trống

## Excel import
- Cột "Năm sinh" phải là **text**, KHÔNG được format date trong Excel
- Đọc file với `{ raw: true }` để không bị Excel tự convert
- File mẫu: force tất cả cells thành string type (`ws[addr].t = 's'`)

## Nhắc nhở sinh nhật
- **Chỉ hoạt động khi có đầy đủ dd/mm/yyyy** (3 phần khi split '/') 
- Nếu chỉ có năm ("1990") → KHÔNG hiện nhắc nhở sinh nhật
- Parse bằng `split('/')` → `parseInt()`, KHÔNG dùng `new Date()`

## Hiển thị
- Hiện nguyên text gốc từ DB (không cần convert)
- Label hiển thị: "Năm sinh" (không phải "Ngày sinh")
