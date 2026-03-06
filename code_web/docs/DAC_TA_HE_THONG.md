# 📖 ĐẶC TẢ HỆ THỐNG - ỨNG DỤNG IN LÁ PHÁI QUY Y

> **Phiên bản gốc:** v2.1 (Python/Tkinter)  
> **Mục đích tài liệu:** Mô tả chi tiết TẤT CẢ luồng hoạt động, tính năng, quy tắc xử lý,  
> edge case và lưu ý nghiệp vụ để chuẩn bị port sang web mà KHÔNG bị sai hoặc thiếu.

---

## MỤC LỤC

1. [Tổng quan hệ thống](#1-tổng-quan-hệ-thống)
2. [Luồng khởi động ứng dụng](#2-luồng-khởi-động-ứng-dụng)
3. [Quản lý cấu hình (Config)](#3-quản-lý-cấu-hình-config)
4. [Luồng chọn ngày quy y + Âm lịch](#4-luồng-chọn-ngày-quy-y--âm-lịch)
5. [Luồng import và xử lý Excel](#5-luồng-import-và-xử-lý-excel)
6. [Luồng tạo và xuất PDF](#6-luồng-tạo-và-xuất-pdf)
7. [Luồng in trực tiếp + Print Preview](#7-luồng-in-trực-tiếp--print-preview)
8. [Nhập nhanh (Quick Entry)](#8-nhập-nhanh-quick-entry)
9. [Chỉnh tọa độ trực quan (Coordinate Tab)](#9-chỉnh-tọa-độ-trực-quan-coordinate-tab)
10. [Custom Fields CRUD](#10-custom-fields-crud)
11. [Cài đặt (Settings)](#11-cài-đặt-settings)
12. [Font VNI và Unicode](#12-font-vni-và-unicode)
13. [Quy tắc tọa độ và render PDF](#13-quy-tắc-tọa-độ-và-render-pdf)
14. [Xử lý lỗi và Edge Cases](#14-xử-lý-lỗi-và-edge-cases)
15. [Dữ liệu mẫu và định dạng Excel](#15-dữ-liệu-mẫu-và-định-dạng-excel)
16. [Bảng tóm tắt validation rules](#16-bảng-tóm-tắt-validation-rules)
17. [Danh sách các dialog/popup](#17-danh-sách-các-dialogpopup)
18. [Luồng dirty state và lưu cấu hình](#18-luồng-dirty-state-và-lưu-cấu-hình)
19. [Quản lý máy in (Desktop only)](#19-quản-lý-máy-in-desktop-only)
20. [Thuật toán chuyển đổi Dương → Âm lịch](#20-thuật-toán-chuyển-đổi-dương--âm-lịch)

---

## 1. TỔNG QUAN HỆ THỐNG

### 1.1 Mục đích
Ứng dụng in **Lá Phái Quy Y** (giấy chứng nhận quy y Tam Bảo trong Phật giáo).  
Mỗi lá phái chứa thông tin: họ tên, pháp danh, năm sinh, địa chỉ, ngày quy y (dương/âm/Phật lịch).

### 1.2 Đầu vào
- **File Excel** chứa danh sách người quy y (hàng loạt)
- **Nhập tay** từng người (Quick Entry)
- **Ngày dương lịch** → tự tính ngày âm + Phật lịch
- **File phôi mẫu** (ảnh .jpg background lá phái)
- **File font VNI** (quyyfont.ttf)

### 1.3 Đầu ra
- **File PDF** (đơn lẻ hoặc gộp nhiều trang)
- **In trực tiếp** ra máy in

### 1.4 Giao diện chính
Ứng dụng có **5 tab**:

| Tab | Tên | Chức năng |
|-----|-----|-----------|
| 1 | **📁 Chính** | Chọn Excel, chọn ngày, chọn máy in, xuất PDF/in |
| 2 | **📐 Tọa Độ** | Canvas kéo thả chỉnh vị trí các trường trên phôi |
| 3 | **✏️ Custom Fields** | Thêm/sửa/xóa các trường tùy chỉnh |
| 4 | **⚙️ Cài đặt** | Font VNI, chế độ xuất, ảnh nền |
| 5 | **📖 Hướng dẫn** | Hướng dẫn sử dụng |

---

## 2. LUỒNG KHỞI ĐỘNG ỨNG DỤNG

### 2.1 Trình tự khởi động

```
[Mở app]
  ↓
[Config Chooser] — Màn hình chọn cấu hình
  ├── "📂 Mở File Cấu Hình Có Sẵn" → hộp thoại chọn file .json
  ├── "✨ Tạo Mới Cấu Hình" → mở app với config mặc định (chưa lưu)
  └── "❌ Thoát" → đóng app
  ↓
[Ensure Resources] — Kiểm tra + extract phoimau.jpg, quyyfont.ttf
  ↓
[MainWindow] — Cửa sổ chính với 5 tab
```

### 2.2 Config Chooser - Chi tiết

- **Lưu lịch sử**: Ghi nhớ thư mục config lần trước vào file `info.quyy` (JSON)
- **Khi mở file**: Hộp thoại chọn file mở đúng thư mục lần trước
- **Khi tạo mới**: `config_path = None`, `is_new_config = True`, title hiện `[Cấu hình mới *]`
- **Khi user đóng cửa sổ**: `result = None` → `sys.exit(0)` → thoát app

### 2.3 Ensure Resources

Khi chạy dạng .exe (PyInstaller):
- File `phoimau.jpg` và `quyyfont.ttf` được bundle trong `_MEIPASS`
- Khi khởi động, copy ra thư mục exe nếu chưa có
- Khi chạy dev: dùng file trực tiếp trong project

---

## 3. QUẢN LÝ CẤU HÌNH (CONFIG)

### 3.1 Cấu trúc config.json

```json
{
  "field_positions": {
    "phap_danh": { "x": 199.0, "y": 139.4, "size": 18, "bold": false, "italic": true, "align": "L" },
    "ho_ten":    { "x": 199.8, "y": 128.2, "size": 18, "bold": false, "italic": true, "align": "L" },
    "sinh_nam":  { "x": 199.4, "y": 147.0, "size": 12, "bold": false, "italic": true, "align": "L" },
    "dia_chi":   { "x": 199.8, "y": 154.2, "size": 12, "bold": true,  "italic": true, "align": "L" }
  },
  "excel_mapping": {
    "ho_ten": "hovaten",
    "phap_danh": "phapdanh",
    "nam_sinh": "namsinh",
    "dia_chi": "diachithuongtru_short"
  },
  "custom_fields": { ... },
  "use_vni_font": true,
  "export_mode": "single",
  "use_background_image": false
}
```

### 3.2 Hai loại trường

**A. Field Positions (4 trường chính)** — Dữ liệu lấy từ Excel:
- `phap_danh` → cột `phapdanh`
- `ho_ten` → cột `hovaten`  
- `sinh_nam` → cột `namsinh`
- `dia_chi` → cột `diachithuongtru_short`

**B. Custom Fields (7 trường ngày tháng + tùy chỉnh)** — Giá trị cố định (cùng giá trị cho tất cả lá phái trong lần in):
- `phat_lich` — Năm Phật lịch (= dương + 544)
- `ngay_duong`, `thang_duong`, `nam_duong` — Ngày/Tháng/Năm dương lịch
- `ngay_am`, `thang_am` — Ngày/Tháng âm lịch
- `nam_am` — Tên Can Chi (ví dụ: "Ất Tỵ")
- (+ bất kỳ trường nào user thêm đều là custom field)

### 3.3 Thuộc tính mỗi trường

| Thuộc tính | Kiểu | Mặc định | Mô tả |
|------------|------|----------|-------|
| `x` | float | - | Tọa độ ngang (mm) tính từ mép trái |
| `y` | float | - | Tọa độ dọc (mm) tính từ mép trên |
| `size` | int | 12 | Cỡ chữ (pt) |
| `bold` | bool | false | In đậm |
| `italic` | bool | false | In nghiêng |
| `align` | "L"/"C"/"R" | "L" | Căn lề: Left, Center, Right |
| `value` | string | "" | (Chỉ custom fields) Giá trị cố định hiển thị |

### 3.4 Excel Mapping

Dùng để ánh xạ tên trường PDF → tên cột Excel:
```
PDF field "ho_ten" ← Excel column "hovaten"
PDF field "phap_danh" ← Excel column "phapdanh"
PDF field "nam_sinh" ← Excel column "namsinh"
PDF field "dia_chi" ← Excel column "diachithuongtru_short"
```

**LƯU Ý:** Mapping này có thể tùy chỉnh nếu file Excel có tên cột khác.

### 3.5 Giá trị mặc định (Default positions)

| Field | X (mm) | Y (mm) | Size | Align | Bold | Italic |
|-------|--------|--------|------|-------|------|--------|
| phap_danh | 196.6 | 139.0 | 18 | L | ❌ | ✅ |
| ho_ten | 196.6 | 129.4 | 18 | L | ❌ | ✅ |
| sinh_nam | 197.0 | 147.0 | 12 | L | ❌ | ✅ |
| dia_chi | 197.4 | 154.2 | 12 | L | ✅ | ✅ |

| Custom Field | X | Y | Size | Align | Mô tả |
|---|---|---|---|---|---|
| phat_lich | 206.0 | 178.0 | 12 | L | Phật lịch |
| ngay_duong | 235.2 | 178.4 | 11 | C | Ngày dương |
| thang_duong | 259.6 | 178.0 | 11 | C | Tháng dương |
| nam_duong | 276.6 | 178.0 | 11 | C | Năm dương |
| ngay_am | 235.6 | 182.8 | 11 | C | Ngày âm |
| thang_am | 259.2 | 182.8 | 11 | C | Tháng âm |
| nam_am | 277.8 | 183.6 | 11 | C | Năm Can Chi |

### 3.6 Lưu/Load config

- **Lưu**: Ghi config.json (trừ `selected_date` — không lưu ngày đã chọn)
- **Load**: Đọc config.json, merge với defaults nếu thiếu key
- **Import**: Load file config từ vị trí bất kỳ, cập nhật config_path
- **Export**: Xuất config ra file JSON bất kỳ (backup/share)
- **Reset**: Khôi phục `field_positions` về mặc định, xóa `custom_fields`, giữ file path

---

## 4. LUỒNG CHỌN NGÀY QUY Y + ÂM LỊCH

### 4.1 Luồng hoạt động

```
[User chọn ngày dương lịch] (DatePicker hoặc nhập YYYY-MM-DD)
  ↓ nhấn "Áp dụng"
[LunarConverter.convert_date(date_str)]
  ↓ tính toán
[Tự động điền các ô:]
  • Ngày âm: 27
  • Tháng âm: 10
  • Năm âm: Ất Tỵ
  • Phật lịch: 2569
  ↓ đồng thời
[Cập nhật custom_fields trong ConfigManager:]
  • custom_fields["ngay_duong"]["value"] = "16"
  • custom_fields["thang_duong"]["value"] = "12"
  • custom_fields["nam_duong"]["value"] = "2025"
  • custom_fields["ngay_am"]["value"] = "27"
  • custom_fields["thang_am"]["value"] = "10"
  • custom_fields["nam_am"]["value"] = "Ất Tỵ"
  • custom_fields["phat_lich"]["value"] = "2569"
```

### 4.2 Quy tắc quan trọng

1. **Ngày quy y là BẮT BUỘC** trước khi xuất PDF hoặc in
2. **Khi chọn file Excel mới → tự động XÓA ngày đã chọn** (buộc user chọn lại)
3. **Ngày quy y KHÔNG lưu vào config** — mỗi lần mở app phải chọn lại
4. **Giá trị âm lịch có thể CHỈNH SỬA BẰNG TAY** sau khi tự điền (user nhấn "✔ Lưu âm lịch" để đồng bộ)
5. **Phật lịch = năm dương + 544**
6. **Tên Can Chi** tính theo công thức: `Can[(year-4)%10] + Chi[(year-4)%12]`

### 4.3 Công thức tính

```
Input: "2025-12-16" (dương lịch)
  → solar_day=16, solar_month=12, solar_year=2025
  → [thuật toán âm lịch] → lunar_day=27, lunar_month=10, lunar_year=2025
  → Can Chi năm 2025: index_can=(2025-4)%10=1 → "Ất", index_chi=(2025-4)%12=5 → "Tỵ" → "Ất Tỵ"
  → Buddhist year = 2025 + 544 = 2569
```

### 4.4 Button "Xóa" ngày
- Xóa `selected_date = None`
- Xóa tất cả giá trị trong các custom fields ngày tháng (set "")
- Xóa nội dung các ô nhập trên UI

---

## 5. LUỒNG IMPORT VÀ XỬ LÝ EXCEL

### 5.1 Đọc file Excel

```
[User click "Chọn File"]
  ↓
[File dialog: *.xlsx, *.xls]
  ↓ chọn file
[ExcelHandler.read_file(path)]
  ↓
  1. Đọc bằng pandas.read_excel()
  2. Lọc bỏ dòng có hovaten = NaN
  3. Return: (count, DataFrame)
  ↓ đồng thời
[Hiển thị số bản ghi: "X bản ghi"]
[XÓA ngày quy y đã chọn trước đó]
  ↓
[ExcelHandler.validate_excel(df)]
  ↓ nếu có warnings
[Hiện hộp thoại cảnh báo]
```

### 5.2 Validation khi đọc

**Kiểm tra header (cột):**
- Các cột bắt buộc: `hovaten`, `phapdanh`, `namsinh`, `diachithuongtru_short`
- Nếu thiếu cột → cảnh báo nhưng vẫn cho tiếp tục

**Kiểm tra từng dòng:**

| Trường | Quy tắc | Hành động khi lỗi |
|--------|---------|-------------------|
| hovaten | Bắt buộc, != "", max 50 ký tự | Cảnh báo "Thiếu họ tên" |
| phapdanh | Optional, max 50 ký tự | Cảnh báo nếu quá dài |
| namsinh | Must match `/^\d{4}$/`, xử lý float "1990.0" → "1990" | Cảnh báo "Năm sinh không hợp lệ" |
| diachithuongtru_short | Optional, max 100 ký tự | Cảnh báo nếu quá dài |

**Hiển thị cảnh báo:** Tối đa 10 dòng lỗi, nếu nhiều hơn hiện "... và X dòng khác".

### 5.3 Xử lý dữ liệu (DataProcessor)

Mỗi dòng Excel được xử lý thành dict:

```python
{
  "phap_danh": "Tâm Minh",     # hoặc "" nếu trống
  "ho_ten": "Nguyễn Văn An",   # hoặc "[LỖI: Thiếu họ tên - Dòng X]"
  "sinh_nam": "1990",           # hoặc "[1990?]" nếu ko hợp lệ
  "dia_chi": "TP.HCM",         # hoặc "" nếu trống
  "_has_error": False,
  "_error_details": [],
  "_row_index": 2               # Số dòng Excel (bắt đầu từ 2)
}
```

**Quy tắc xử lý chi tiết:**

1. **Họ tên rỗng** → `"[LỖI: Thiếu họ tên - Dòng X]"` (vẫn in nhưng hiện text lỗi)
2. **Quá dài (>50 ký tự)** → Cắt bớt + `"..."` (ví dụ: `"Nguyễn Văn..."`)
3. **Năm sinh có dấu chấm** → Cắt phần sau `.` (Excel format float: `"1990.0"` → `"1990"`)
4. **Năm sinh không hợp lệ** → `"[1990?]"` (hiển thị kèm dấu `?`)
5. **Địa chỉ max 100 ký tự** (gấp đôi so với các trường khác)
6. **Trim khoảng trắng** đầu/cuối tất cả các trường
7. **Dòng có lỗi vẫn tạo PDF** — không skip, chỉ đánh dấu `_has_error = True`

---

## 6. LUỒNG TẠO VÀ XUẤT PDF

### 6.1 Hai chế độ xuất

| Chế độ | Giá trị | Mô tả | Output |
|--------|---------|-------|--------|
| Nhiều file | `"multiple"` | Mỗi người 1 file PDF riêng | `Nguyễn Văn A.pdf`, `Trần Thị B.pdf`... |
| Một file | `"single"` | Tất cả gộp trong 1 file | `QuyY_TatCa.pdf` (nhiều trang) |

### 6.2 Luồng xuất PDF

```
[User click "📄 Xuất PDF"]
  ↓ kiểm tra
  ├── Chưa chọn Excel → Cảnh báo "Vui lòng chọn file Excel"
  ├── Chưa chọn ngày → Cảnh báo "Vui lòng chọn Ngày Quy Y"
  └── OK
  ↓
[validate Excel data → cảnh báo nếu có lỗi → user quyết "Tiếp tục?"]
  ↓
[Hộp thoại xác nhận "Bắt đầu xuất PDF?"]
  ↓ Yes
[LOCK UI (disable buttons)]
[Progress bar bắt đầu]
  ↓ chạy background thread
[PDFService.run_batch_export()]
  ├── mode="single":
  │     1. Process tất cả rows → data_list
  │     2. Progress: 0→50% (processing data)
  │     3. generator.create_merged_pdf() → 1 file nhiều trang
  │     4. Progress: 50→100% (generating PDF)
  │
  └── mode="multiple":
        1. Loop từng row:
        2. Process row → data
        3. Tên file: sanitize(hovaten) + ".pdf"
        4. generator.create_single_pdf() → 1 file/person
        5. Progress: 0→100% (per record)
  ↓
[Completion callback]
[UNLOCK UI]
  ├── Không lỗi → "Thành công" + mở thư mục output
  └── Có lỗi → "Hoàn thành có lỗi" + chi tiết (tối đa 5)
```

### 6.3 Xử lý file bị lock

Khi file PDF đang mở bởi app khác (Acrobat, Chrome...):
1. Thử ghi vào file gốc → fail (PermissionError)
2. Tự động thêm suffix: `file.pdf` → `file_1.pdf` → `file_2.pdf`
3. Tối đa 100 attempts
4. Fallback cuối: dùng timestamp `file_1678234567.pdf`
5. Thông báo: "File gốc đang được mở, đã lưu sang: file_1.pdf"

### 6.4 Tên file output

**Mode multiple:**
- Export: `hovaten_sanitized.pdf` (giữ ký tự alpha, số, space, underscore)
- Print temp: `job_{index}_{timestamp}.pdf` (ASCII only, tránh lỗi OS)
- Nếu tên rỗng: `record_{index}.pdf`

**Mode single:**
- `QuyY_TatCa.pdf`

### 6.5 Render PDF - Chi tiết kỹ thuật

**Khổ giấy:** A4 Landscape = 297mm × 210mm = 841.89pt × 595.28pt

**Tọa độ:**
- Gốc tọa độ config: **góc trên bên trái** (x tăng sang phải, y tăng xuống dưới)
- Gốc tọa độ PDF (ReportLab): **góc dưới bên trái** (y tăng lên trên)
- Chuyển đổi: `y_pdf = page_height - (y_mm * mm_to_pt)`
- `1 mm = 2.8346 pt`

**Thứ tự render trên mỗi trang:**
1. Vẽ ảnh nền (nếu `use_background_image = true`)
2. Vẽ 4 trường chính (field_positions) — data từ Excel
3. Vẽ tất cả custom fields — giá trị cố định

**Align xử lý:**
- `"L"` (Left): `drawString(x, y, text)` — text bắt đầu từ x
- `"C"` (Center): `drawCentredString(x, y, text)` — text có tâm tại x
- `"R"` (Right): `drawRightString(x, y, text)` — text kết thúc tại x

**Font:**
- Đăng ký 1 font duy nhất: `quyyfont.ttf` với tên `"QuyYFont"`
- Tất cả text đều dùng font này
- Nếu `use_vni_font = true` → text qua `convert_unicode_to_vni()` trước khi vẽ

---

## 7. LUỒNG IN TRỰC TIẾP + PRINT PREVIEW

### 7.1 Luồng khi click "🖨️ In Trực Tiếp"

```
[User click "In Trực Tiếp"]
  ↓ kiểm tra
  ├── Chưa chọn Excel → Cảnh báo
  ├── Chưa chọn ngày → Cảnh báo
  └── OK
  ↓
[validate Excel → cảnh báo nếu lỗi]
  ↓
[MỞ CỬA SỔ PRINT PREVIEW] (thay vì in batch ngay)
```

### 7.2 Print Preview Window

**Layout:**
```
┌──────────┬───────────────────────────────────────┐
│          │                                       │
│ Danh     │          Canvas Preview               │
│ sách     │    (phôi mẫu + text field)            │
│          │                                       │
│ 1. An    │                                       │
│ 2. Bình  │                                       │
│ 3. Cường │                                       │
│          ├───────────────────────────────────────┤
│          │ [◀ Trước]   2 / 50   [Sau ▶]         │
│          │ [🖨️ In Trang Này] [💾 Lưu PDF]       │
└──────────┴───────────────────────────────────────┘
```

**Tính năng:**
1. **Sidebar danh sách**: Listbox hiện tất cả tên, click để nhảy đến
2. **Canvas preview**: Hiện phôi mẫu + text field tại vị trí đúng
3. **Navigation**: Nút Trước/Sau, hiện "2 / 50"
4. **In trang hiện tại**: Tạo temp PDF → gửi lệnh in → xóa temp
5. **Lưu PDF trang hiện tại**: Hộp thoại save file

**Preview render:**
- Standard fields → màu xanh (blue)
- Custom fields → màu đỏ (red), in đậm
- Scale: `SCALE = 2.5` → `canvas = 297*2.5 x 210*2.5 = 742 x 525 px`
- Font hiển thị canvas: `display_size = int(size * 0.8)` (nhỏ hơn thực tế một chút)
- Y offset: thêm font descent để baseline khớp PDF

**Modal behavior:** Cửa sổ preview là modal (grab_set) — không thao tác được cửa sổ chính khi preview mở.

---

## 8. NHẬP NHANH (QUICK ENTRY)

### 8.1 Mục đích
In lá phái cho **1 người duy nhất** mà không cần tạo file Excel.

### 8.2 Giao diện

```
┌─────────────────────────────────────┐
│    ✍️  NHẬP NHANH THÔNG TIN        │
│    Nhập thông tin trực tiếp...      │
├─────────────────────────────────────┤
│ Họ và Tên *  [___placeholder___]    │
│ Pháp Danh    [___placeholder___]    │
│ Năm Sinh [____] Địa chỉ [________] │
│─────────────────────────────────────│
│ Ngày Quy Y * [DatePicker] [Áp dụng]│
│ 🌙 Âm lịch: Ngày[__] Tháng[__]    │
│              Năm [_________]        │
│ ☸️ Phật lịch: [________]            │
├─────────────────────────────────────┤
│ [📄 Xuất PDF]    [🖨️ In Trực Tiếp] │
│ [🔄 Xóa Form]           [❌ Đóng]  │
└─────────────────────────────────────┘
```

### 8.3 Placeholder Entry
- Khi chưa nhập: hiện text mờ (placeholder) ví dụ "Nguyễn Văn A"
- Khi focus vào: xóa placeholder, chuyển màu chữ bình thường
- Khi focus ra mà rỗng: hiện lại placeholder
- `get_value()`: trả về "" nếu đang hiện placeholder

### 8.4 Luồng xử lý

```
[User điền form + chọn ngày + nhấn "Xuất PDF" hoặc "In"]
  ↓ validate
  ├── Họ tên rỗng → "Vui lòng nhập Họ và Tên!"
  ├── Ngày rỗng → "Vui lòng chọn Ngày Quy Y!"
  ├── Năm sinh != 4 chữ số → "Năm sinh phải là 4 chữ số!"
  └── OK
  ↓
[_prepare_config_with_date(date_str)]
  1. Backup old_date + old_custom_values
  2. set_selected_date(date_str) → auto fill ngày dương/âm/phật lịch
  3. Ghi đè bằng giá trị user đã chỉnh sửa tay trong dialog
  ↓
[Tạo PDF / In]
  ↓
[_restore_config_date(old_state)]  ← LUÔN LUÔN khôi phục, kể cả khi lỗi
```

### 8.5 Lưu ý quan trọng

- **BACKUP CONFIG TRƯỚC KHI IN**: Quick entry set ngày tạm vào config → phải restore lại sau
- **Giá trị âm lịch user chỉnh tay**: Sau khi set_selected_date auto fill → ghi đè bằng giá trị user nhập
- **Không ảnh hưởng config chính**: Ngày quy y ở tab Chính vẫn giữ nguyên
- **Modal dialog**: Không thao tác được cửa sổ chính khi Quick Entry mở
- **Xóa Form**: Xóa tất cả input + reset placeholder, focus vào ô họ tên

---

## 9. CHỈNH TỌA ĐỘ TRỰC QUAN (COORDINATE TAB)

### 9.1 Canvas preview

- **Kích thước**: A4 landscape scale × 2.5 → 742 × 525 px
- **Background**: Ảnh phôi mẫu `phoimau.jpg` (resize fit canvas)
- **Hiển thị**: Tất cả field (cả standard + custom) với text + bounding box

### 9.2 Tương tác chuột

- **Click**: Chọn field gần nhất (trong bán kính 20px)
- **Double-click**: Mở dialog chỉnh sửa field
- **Drag**: Kéo field đã chọn di chuyển
- **Click vào vùng trống**: Bỏ chọn

### 9.3 Tương tác phím

- **Ctrl+A**: Chọn tất cả fields
- **Arrow keys**: Di chuyển field đã chọn (bước = 0.4mm mỗi lần nhấn)
- **Nếu chọn nhiều field**: Di chuyển đồng loạt

### 9.4 Bảng thuộc tính

- Bảng bên phải hiện danh sách fields: Tên, X, Y, Size, Align
- Click vào hàng = chọn field tương ứng
- Nút chỉnh sửa = mở dialog
- Tọa độ auto cập nhật real-time khi kéo/di chuyển

### 9.5 Khi thay đổi tọa độ

- Cập nhật `field_positions` hoặc `custom_fields` trong ConfigManager
- Đánh dấu `dirty = true`
- Chưa auto-save — chỉ lưu khi user nhấn "Lưu Cấu Hình"

---

## 10. CUSTOM FIELDS CRUD

### 10.1 Giao diện

Bảng TreeView:
| Tên Field | Giá Trị | X (mm) | Y (mm) | Size | Align |
|-----------|---------|--------|--------|------|-------|

Nút: [➕ Thêm] [✏️ Sửa] [🗑️ Xóa]

### 10.2 Dialog thêm/sửa

Fields: Tên Field, Giá trị, X (mm), Y (mm), Cỡ chữ, Căn lề (L/C/R)
- Default X=50, Y=100, Size=12, Align=L

### 10.3 Validation

- Tên field không được trống
- Tên field không được trùng (khi thêm mới hoặc đổi tên)
- X, Y phải là float
- Size phải là int
- Khi đổi tên: xóa key cũ, tạo key mới

### 10.4 Double-click = Edit

Click đúp vào dòng trong bảng → mở dialog sửa

---

## 11. CÀI ĐẶT (SETTINGS)

### 11.1 Chế độ xuất PDF
- Radio button: "Nhiều file riêng lẻ" / "Một file gộp trang"
- Thay đổi → `config_manager.export_mode` + dirty

### 11.2 Cấu hình Font
- Checkbox: "Chuyển đổi Unicode sang VNI"
- Bật = dùng font VNI (phổ biến trong in ấn cổ)
- Tắt = dùng font Unicode thông thường
- Thay đổi → `config_manager.use_vni_font` + dirty

### 11.3 Ảnh nền (Phôi mẫu)
- Checkbox: "In kèm ảnh nền (phôi mẫu) trong PDF"
- Tắt = chỉ in chữ (khi phôi đã in sẵn trên giấy)
- Bật = in cả ảnh nền + chữ (in trên giấy trắng)
- Thay đổi → `config_manager.use_background_image` + dirty

### 11.4 Thông tin PDF (read-only)
- Khổ giấy: A4 (297mm × 210mm)
- Hướng: NGANG (Landscape)
- Tọa độ gốc: Góc trên bên trái

---

## 12. FONT VNI VÀ UNICODE

### 12.1 Tại sao dùng VNI?

Font `quyyfont.ttf` (VNI-Ariston / kiểu thư pháp) dùng **bảng mã VNI Windows** chứ không phải Unicode.  
Nếu truyền text Unicode thẳng vào font VNI → ký tự sai.  
Phải convert: `"Nguyễn"` → `"Nguyeãn"` trước khi render.

### 12.2 Bảng chuyển đổi

134 ký tự Unicode → VNI (ví dụ trích):
```
À → AØ    Á → AÙ    Â → AÂ    Ã → AÕ
à → aø    á → aù    ă → aê    â → aâ
Đ → Ñ     đ → ñ     Ơ → Ô     ơ → ô
Ư → Ö     ư → ö     ...
```

### 12.3 Thuật toán convert

```
1. Normalize text về NFC (dựng sẵn)
2. Loop từng ký tự:
   - Nếu có trong bảng map → thay thế (có thể 1-to-many: "À" → "AØ")
   - Nếu không → giữ nguyên
3. Join kết quả
```

### 12.4 Khi nào convert?

- `use_vni_font = true` → convert text trước khi `drawText`/`drawString`
- `use_vni_font = false` → truyền text Unicode thẳng vào font
- Convert áp dụng cho **CẢ** standard fields lẫn custom fields

---

## 13. QUY TẮC TỌA ĐỘ VÀ RENDER PDF

### 13.1 Hệ tọa độ

```
(0,0) ─────────────────────── (297, 0)
  │                              │
  │          A4 Landscape        │
  │         297mm × 210mm        │
  │                              │
  │    x tăng →                  │
  │    y tăng ↓                  │
  │                              │
(0, 210) ──────────────────── (297, 210)
```

- **Config lưu**: (x_mm, y_mm) → mốc tính từ **góc trên bên trái**
- **PDF render**: chuyển sang gốc dưới trái: `y_pdf = 595.28 - (y_mm × 2.8346)`
- **Canvas preview**: `x_px = x_mm × SCALE`, `y_px = y_mm × SCALE`

### 13.2 Ảnh nền (Background)

- File: `phoimau.jpg` (hoặc .png)
- Tìm trong thư mục app: `phoimau.jpg` → `phoimau.jpeg` → `phoimau.png`
- Render PDF: `drawImage(path, 0, 0, width=page_width, height=page_height)`
- Render canvas: resize về kích thước canvas (742 × 525)
- Phải vẽ ảnh nền TRƯỚC chữ

### 13.3 Font size và hiển thị

- Config lưu `size` theo đơn vị **point** (pt)
- Canvas preview: `display_size = int(size × 0.8)` (nhỏ hơn thực tế)
- PDF: sử dụng `size` nguyên bản

---

## 14. XỬ LÝ LỖI VÀ EDGE CASES

### 14.1 File Excel

| Tình huống | Xử lý |
|------------|-------|
| File không tồn tại | `FileNotFoundError` → hiện lỗi |
| File đang mở bởi Excel | Vẫn đọc được (pandas lock read) |
| File sai format (.csv, .docx) | `Exception` → hiện lỗi |
| File rỗng (không có dòng data) | `count = 0`, UI hiện "0 bản ghi" |
| Thiếu cột bắt buộc | Cảnh báo nhưng vẫn cho tiếp tục |
| Ký tự Unicode trong tên file | OK trên tất cả OS |

### 14.2 PDF xuất

| Tình huống | Xử lý |
|------------|-------|
| File PDF đang mở | Tự thêm suffix `_1`, `_2`... |
| Thư mục output không tồn tại | Tự tạo `os.makedirs(exist_ok=True)` |
| Font file không tìm thấy | Warning log, vẫn tạo PDF (có thể lỗi) |
| Phôi mẫu không tìm thấy | Skip ảnh nền, chỉ vẽ chữ |
| Ký tự Unicode không hỗ trợ | Font fallback handling |
| Data quá dài tràn bề ngang | Vẫn vẽ, có thể bị cắt ở lề |

### 14.3 In ấn

| Tình huống | Xử lý |
|------------|-------|
| Không có máy in | Hiện "(Không có máy in)" |
| Win32 API lỗi | Fallback: `os.startfile("print")` |
| Startfile lỗi | Fallback: mở file để user in thủ công |
| Temp file lỗi tên Unicode | Dùng tên ASCII `job_{index}_{timestamp}` |

### 14.4 Config

| Tình huống | Xử lý |
|------------|-------|
| File config rỗng | Dùng defaults |
| File config bị JSON lỗi | Dùng defaults + log error |
| Field mới thêm thiếu trong file cũ | Merge: giữ giá trị cũ + thêm defaults |
| Config mới chưa save → thoát app | Hỏi "Lưu trước khi thoát?" |
| Config mới chưa có path → save | Hiện "Save As" dialog |

---

## 15. DỮ LIỆU MẪU VÀ ĐỊNH DẠNG EXCEL

### 15.1 Cấu trúc file Excel

| Cột | Tên cột | Bắt buộc | Kiểu | Max length |
|-----|---------|----------|------|------------|
| A | `hovaten` | ✅ | text | 50 |
| B | `phapdanh` | ❌ | text | 50 |
| C | `namsinh` | ✅ | number/text | 4 digits |
| D | `diachithuongtru_short` | ✅ | text | 100 |

### 15.2 Ví dụ data

```
hovaten               | phapdanh      | namsinh | diachithuongtru_short
─────────────────────────────────────────────────────────────────────
Nguyễn Văn An         | Tâm Minh      | 1990    | P.10, Q.Gò Vấp, TP.HCM
Trần Thị Bình Ngọc    | Diệu Hạnh     | 1985    | H.Đức Phổ, Quảng Ngãi
Lê Văn Cường          |               | 2001    | X.An Phú, H.Củ Chi, TP.HCM
Phạm Thị Dung         | Thiện Tâm     | 1995.0  | Hà Nội
```

### 15.3 Xử lý edge case trong data

- `1995.0` (Excel number format) → `"1995"` (bỏ `.0`)
- `hovaten = NaN` → **skip dòng này** (không đếm, không in)
- Dòng header → tự động nhận dạng qua pandas
- Các cột phụ (gioitinh, sodienthoai...) → **bỏ qua**

---

## 16. BẢNG TÓM TẮT VALIDATION RULES

### 16.1 Trước khi xuất PDF / in

| Kiểm tra | Bắt buộc? | Message |
|----------|-----------|---------|
| Đã chọn file Excel | ✅ | "Vui lòng chọn file Excel!" |
| Đã chọn thư mục output (xuất) | ✅ | "Vui lòng chọn file Excel và thư mục lưu" |
| Đã chọn ngày quy y | ✅ | "Vui lòng chọn Ngày Quy Y trước khi xuất/in!" |
| Excel data hợp lệ | ⚠️ | Cảnh báo, user chọn "Tiếp tục?" |
| Xác nhận xuất | ✅ | "Bắt đầu xuất PDF?" |

### 16.2 Quick Entry

| Kiểm tra | Bắt buộc? | Message |
|----------|-----------|---------|
| Họ tên | ✅ | "Vui lòng nhập Họ và Tên!" |
| Ngày quy y | ✅ | "Vui lòng chọn Ngày Quy Y!" |
| Năm sinh (nếu có) | ⚠️ | "Năm sinh phải là 4 chữ số!" |
| Pháp danh | ❌ | Để trống OK |
| Địa chỉ | ❌ | Để trống OK |

### 16.3 Custom Field Dialog

| Kiểm tra | Bắt buộc? | Message |
|----------|-----------|---------|
| Tên field | ✅ | "Tên field không được để trống!" |
| Tên field unique | ✅ | "Field 'X' đã tồn tại!" |
| X, Y | ✅ | "Giá trị không hợp lệ" (phải là số) |
| Size | ✅ | "Giá trị không hợp lệ" (phải là số nguyên) |

---

## 17. DANH SÁCH CÁC DIALOG / POPUP

| # | Loại | Trigger | Nội dung | Buttons |
|---|------|---------|----------|---------|
| 1 | Config Chooser | Khởi động app | Mở/Tạo mới/Thoát | 3 buttons |
| 2 | File dialog | Chọn Excel | Filter: *.xlsx, *.xls | Open/Cancel |
| 3 | Folder dialog | Chọn thư mục output | Browse folder | Select/Cancel |
| 4 | Warning | Excel có lỗi (đọc) | Chi tiết lỗi | OK |
| 5 | Warning | Trước xuất/in, Excel có lỗi | Chi tiết + "Tiếp tục?" | Yes/No |
| 6 | Confirm | Xuất PDF | "Bắt đầu xuất PDF?" | Yes/No |
| 7 | Info | Xuất xong, không lỗi | "Thành công" | OK |
| 8 | Warning | Xuất xong, có lỗi | Chi tiết lỗi (max 5) | OK |
| 9 | Print Preview | In trực tiếp | Cửa sổ preview modal | Custom |
| 10 | Quick Entry | Nhập nhanh | Form modal | Custom |
| 11 | Custom Field | Thêm/sửa field | Form dialog | OK/Cancel |
| 12 | Confirm | Xóa custom field | "Xóa field X?" | Yes/No |
| 13 | Confirm | Reset config | "Bạn có chắc?" | Yes/No |
| 14 | Yes/No/Cancel | Thoát app (dirty) | "Lưu trước khi thoát?" | Yes/No/Cancel |
| 15 | Yes/No | Chuyển tab (dirty) | "Lưu thay đổi?" | Yes/No |
| 16 | Save As | Config mới lần đầu | Save file dialog | Save/Cancel |
| 17 | Toast | Nhiều nơi | Thông báo tự ẩn (3s) | Tự ẩn |

---

## 18. LUỒNG DIRTY STATE VÀ LƯU CẤU HÌNH

### 18.1 Khi nào dirty = true?

- Thay đổi tọa độ field (drag, phím mũi tên)
- Thay đổi thuộc tính field (size, align, value)
- Thêm/sửa/xóa custom field
- Thay đổi setting: VNI toggle, export mode, background image

### 18.2 Khi chuyển tab

```
[User click tab khác]
  ↓ kiểm tra
  if (đang rời tab "Tọa Độ" hoặc "Custom Fields") AND (dirty == true):
    ↓
    [Hỏi: "Bạn có thay đổi chưa lưu. Lưu không?"]
      ├── Yes → save config → clear dirty
      └── No → RELOAD config từ file → clear dirty → refresh UI
                (Hủy bỏ tất cả thay đổi chưa lưu!)
```

### 18.3 Khi thoát app

```
[User đóng window]
  ↓
  if (dirty == true) OR (is_new_config == true):
    ↓
    [Hỏi: "Lưu trước khi thoát?"]
      ├── Yes → save (nếu new → save_as dialog)
      │         ├── Save thành công → thoát
      │         └── Cancel save_as → KHÔNG thoát
      ├── No → thoát không lưu
      └── Cancel → KHÔNG thoát (ở lại app)
```

### 18.4 Title bar

- Có file config: `"Ứng dụng... - [config.json]"`
- Config mới chưa lưu: `"Ứng dụng... - [Cấu hình mới *]"`

---

## 19. QUẢN LÝ MÁY IN (DESKTOP ONLY)

### 19.1 Load danh sách máy in

Chạy background thread để không block UI:
1. Ưu tiên `win32print.EnumPrinters()` (nếu có pywin32)
2. Fallback: PowerShell `Get-Printer`
3. Lấy máy in mặc định: `win32print.GetDefaultPrinter()` hoặc PowerShell
4. Hiển thị trong Combobox dropdown

### 19.2 Khi user chọn máy in

→ **Set luôn làm máy in mặc định Windows** (background thread)
- Win32: `win32print.SetDefaultPrinter(name)`
- Fallback: PowerShell `WScript.Network.SetDefaultPrinter()`
- Kết quả: Toast "🖨️ Đã đặt 'Tên máy in' làm mặc định"

### 19.3 Lưu ý khi port web

Web **KHÔNG** thể:
- Liệt kê máy in
- Set máy in mặc định
- In thẳng ra máy in

Web CHỈ có thể:
- Tạo PDF → `window.print()` → user chọn máy in trong browser dialog
- Hoặc: download PDF → user mở + in thủ công

---

## 20. THUẬT TOÁN CHUYỂN ĐỔI DƯƠNG → ÂM LỊCH

### 20.1 Tổng quan

Thuật toán tính lịch Việt Nam, dựa trên:
- Julian Day Number
- Tính ngày Trăng Non (New Moon Day)
- Kinh độ Mặt Trời (Sun Longitude)
- Xác định tháng nhuận

### 20.2 Các hàm

1. **`jd_from_date(dd, mm, yy)`** → Julian Day Number
   - Chuyển ngày dương lịch sang số ngày Julian

2. **`get_new_moon_day(k, timezone=7)`** → JD ngày trăng non thứ k
   - Tính toán thiên văn (sin, cos)
   - k đếm từ năm 1900
   - timezone mặc định = 7 (Việt Nam, GMT+7)

3. **`get_sun_longitude(jdn, timezone=7)`** → int 0-11
   - Kinh độ mặt trời tại JD, chia thành 12 cung

4. **`get_lunar_month_11(yy, timezone=7)`** → JD bắt đầu tháng 11 âm lịch

5. **`get_leap_month_offset(a11, timezone=7)`** → offset tháng nhuận

6. **`solar_to_lunar(dd, mm, yy, timezone=7)`** → `(ngày_âm, tháng_âm, năm_âm, leap_flag)`
   - Hàm chính: chuyển dương → âm lịch
   - `leap_flag = 1` nếu tháng nhuận

7. **`get_can_chi(year)`** → "Ất Tỵ"
   - Bảng sẵn 2015-2040
   - Công thức chung: `Can[(year-4)%10]` + `Chi[(year-4)%12]`
   - Can = ["Giáp","Ất","Bính","Đinh","Mậu","Kỷ","Canh","Tân","Nhâm","Quý"]
   - Chi = ["Tý","Sửu","Dần","Mão","Thìn","Tỵ","Ngọ","Mùi","Thân","Dậu","Tuất","Hợi"]

8. **`convert_date(date_str)`** → API chính
   - Input: "YYYY-MM-DD" hoặc datetime
   - Nếu chứa space: lấy phần trước space (xử lý "2025-12-16 19:00:07")
   - Output:
     ```
     solar_day, solar_month, solar_year,
     lunar_day, lunar_month, lunar_year,
     lunar_year_name,   # Can Chi
     buddhist_year      # = solar_year + 544
     ```

### 20.3 Lưu ý port

- Tất cả là thuật toán toán học thuần → port thẳng sang JS
- `int()` trong Python: truncate toward zero → dùng `Math.trunc()` trong JS (KHÔNG phải `Math.floor()` vì behavior khác với số âm)
- `//` (integer division) → `Math.trunc(a/b)` trong JS
- `math.sin`, `math.cos` → `Math.sin`, `Math.cos`
- Hằng số PI: `3.14159265358979323846` → `Math.PI`
- Timezone luôn = 7, hardcode OK

### 20.4 Test cases

```
Input: "2025-05-02"
Expected: solar=2/5/2025, lunar=5/4/2025(Ất Tỵ), buddhist=2569

Input: "2025-12-15"
Expected: solar=15/12/2025, lunar=25/10/2025(Ất Tỵ), buddhist=2569

Input: "2024-01-01"
Expected: solar=1/1/2024, lunar=20/11/2023(Quý Mão), buddhist=2568
```

---

## PHỤ LỤC A: UTILS HỖ TRỢ

### A.1 Slugify

```python
def slugify(text):
    # "Nguyễn Văn A" → "nguyen-van-a"
    # Replace đ→d, remove diacritics, lowercase, non-alnum→dash
```

### A.2 Safe print filename

```python
def get_safe_print_filename(index, total, name):
    # → "laphai_1_50_nguyen-van-a.pdf"
```

---

## PHỤ LỤC B: TOAST NOTIFICATION

- **Success** (xanh lá): `✅ message` — 3 giây
- **Info** (xanh dương): `ℹ️ message` — 3 giây
- **Warning** (vàng cam): `⚠️ message` — 3 giây
- **Error** (đỏ): `❌ message` — **5 giây** (lâu hơn)
- Vị trí: top hoặc bottom
- Tự ẩn, không cần user click

---

## PHỤ LỤC C: CONSTANTS

```
A4_WIDTH  = 297 mm
A4_HEIGHT = 210 mm
PDF_ORIENTATION = "landscape"
FONT_NAME = "QuyYFont"
FONT_FILE = "quyyfont.ttf"
BG_FILE   = "phoimau.jpg"
MAX_FIELD_LENGTH = 50 (ký tự)
MAX_ADDR_LENGTH  = 100 (ký tự)
CANVAS_SCALE     = 2.5
1 mm = 2.8346 pt
```
