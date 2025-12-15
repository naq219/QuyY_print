# Changelog

Tất cả các thay đổi quan trọng của dự án sẽ được ghi lại trong file này.

## [1.0.0] - 2025-12-15

### Tính năng mới
- ✨ Đọc dữ liệu từ file Excel (.xlsx, .xls)
- ✨ Chuyển đổi tự động Dương lịch sang Âm lịch
- ✨ Tự động tính Phật lịch (năm dương lịch + 544)
- ✨ Xuất PDF hàng loạt
- ✨ In trực tiếp ra máy in
- ✨ Giao diện GUI với Tkinter
- ✨ Hỗ trợ font Unicode tiếng Việt (VNI-Commerce)
- ✨ Progress bar hiển thị tiến độ
- ✨ Cấu hình tọa độ linh hoạt trong config.py

### Format text
- Họ tên, Pháp danh: Size 18, italic
- Năm sinh: Size 12, italic
- Địa chỉ: Size 12, bold + italic
- Ngày tháng (DL, ÂL): Size 11, italic
- Năm ÂL, Phật lịch: Size 11, bold + italic

### Tính năng kỹ thuật
- Python 3.8+
- ReportLab cho PDF generation
- Pandas cho xử lý Excel
- Thuật toán chuyển đổi lịch Việt Nam chính xác
- Build exe bằng PyInstaller

### Hạn chế hiện tại
- Tọa độ cần điều chỉnh thủ công trong config.py
- Chưa có preview PDF trước khi in
- Chưa hỗ trợ nhiều template

### Kế hoạch tương lai (v1.1.0)
- [ ] GUI điều chỉnh tọa độ drag-and-drop
- [ ] Preview PDF real-time
- [ ] Hỗ trợ nhiều template
- [ ] Export sang Word, Image
- [ ] Lưu cấu hình tọa độ cho nhiều template

---

## [Unreleased]

### Đang phát triển
- GUI điều chỉnh tọa độ
- Preview PDF

### Cân nhắc
- Multi-language support
- Cloud storage integration
- Template marketplace
