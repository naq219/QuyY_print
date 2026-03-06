# 📋 TÀI LIỆU DỰ ÁN QUY Y PRINT

> **Phiên bản**: v2.1  
> **Ngày cập nhật**: 14/02/2026  
> **Trạng thái**: ✅ Production  
> **Liên hệ hỗ trợ**: Trung Quảng An – 0983.838.619

---

## MỤC LỤC

1. [Tổng Quan Dự Án](#1-tổng-quan-dự-án)
2. [Kiến Trúc Hệ Thống](#2-kiến-trúc-hệ-thống)
3. [Chi Tiết Module](#3-chi-tiết-module)
4. [Giao Diện Người Dùng](#4-giao-diện-người-dùng)
5. [Cấu Hình & Cấu Trúc Dữ Liệu](#5-cấu-hình--cấu-trúc-dữ-liệu)
6. [Hướng Dẫn Sử Dụng](#6-hướng-dẫn-sử-dụng)
7. [Triển Khai & Build](#7-triển-khai--build)
8. [Bảo Trì & Xử Lý Sự Cố](#8-bảo-trì--xử-lý-sự-cố)
9. [Lịch Sử Phiên Bản](#9-lịch-sử-phiên-bản)
10. [Lộ Trình Phát Triển](#10-lộ-trình-phát-triển)

---

## 1. TỔNG QUAN DỰ ÁN

### 1.1 Mô Tả

**QUY Y PRINT** là ứng dụng desktop chuyên dụng được phát triển để tự động hóa quy trình in **lá phái quy y** (giấy chứng nhận quy y Tam Bảo) cho các Phật tử. Ứng dụng đọc dữ liệu từ file Excel chứa thông tin cá nhân, tự động chuyển đổi ngày dương lịch sang âm lịch, tính Phật lịch, và xuất PDF hoặc in trực tiếp ra máy in với tọa độ được canh chỉnh chính xác trên phôi mẫu.

### 1.2 Mục Tiêu

| Mục tiêu | Mô tả |
|-----------|--------|
| **Tự động hóa** | Loại bỏ thao tác thủ công khi ghi chép thông tin lên lá phái |
| **Chính xác** | Chuyển đổi âm lịch/Phật lịch tự động, giảm sai sót |
| **Linh hoạt** | Hỗ trợ nhiều cấu hình (tọa độ, font, custom fields) cho nhiều loại phôi mẫu |
| **Tiện dụng** | In hàng loạt, xem trước (preview) trước khi in |
| **Đơn giản** | Giao diện trực quan, phù hợp người dùng không chuyên IT |

### 1.3 Đối Tượng Sử Dụng

- Các chùa, tự viện tổ chức lễ quy y
- Ban tổ chức lễ quy y cần in lá phái hàng loạt

### 1.4 Công Nghệ Sử Dụng

| Thành phần | Công nghệ | Phiên bản |
|------------|-----------|-----------|
| Ngôn ngữ chính | Python | ≥ 3.8 |
| Giao diện (GUI) | Tkinter + ttk | Built-in |
| Tạo PDF | ReportLab | ≥ 4.0.0 |
| Xử lý Excel | Pandas + OpenPyXL | ≥ 2.0.0 / ≥ 3.1.0 |
| Xử lý hình ảnh | Pillow (PIL) | ≥ 10.0.0 |
| Chọn ngày | tkcalendar | ≥ 1.6.1 |
| Build EXE | PyInstaller | ≥ 6.0.0 |

### 1.5 Yêu Cầu Hệ Thống

- **OS**: Windows 7/8/10/11 (64-bit)
- **RAM**: Tối thiểu 2GB
- **Dung lượng**: ~50MB (bao gồm file EXE và tài nguyên)
- **Máy in**: Bất kỳ máy in nào được Windows nhận diện

---

## 2. KIẾN TRÚC HỆ THỐNG

### 2.1 Sơ Đồ Kiến Trúc Tổng Thể

```
┌─────────────────────────────────────────────────────────────────┐
│                          main.py (Entry Point)                   │
│   ConfigChooser → Resource Init → MainWindow                    │
└───────────────────────┬─────────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
┌───────▼────────┐            ┌─────────▼──────────┐
│   UI Layer     │            │    Core Layer       │
│                │            │                     │
│ ┌────────────┐ │  sử dụng  │ ┌─────────────────┐ │
│ │ MainWindow │ │───────────►│ │ ConfigManager   │ │
│ └────────────┘ │            │ ├─────────────────┤ │
│ ┌────────────┐ │            │ │ PDFService      │ │
│ │ Tabs (5)   │ │            │ ├─────────────────┤ │
│ │ - General  │ │            │ │ PDFGenerator    │ │
│ │ - Coord    │ │            │ ├─────────────────┤ │
│ │ - Custom   │ │            │ │ ExcelHandler    │ │
│ │ - Settings │ │            │ ├─────────────────┤ │
│ │ - Guide    │ │            │ │ DataProcessor   │ │
│ └────────────┘ │            │ ├─────────────────┤ │
│ ┌────────────┐ │            │ │ LunarConverter  │ │
│ │ Components │ │            │ ├─────────────────┤ │
│ │ - Preview  │ │            │ │ PrinterManager  │ │
│ │ - Dialogs  │ │            │ ├─────────────────┤ │
│ │ - Toast    │ │            │ │ ResourceManager │ │
│ └────────────┘ │            │ ├─────────────────┤ │
│                │            │ │ Utils           │ │
└────────────────┘            │ └─────────────────┘ │
                              └─────────────────────┘
```

### 2.2 Cấu Trúc Thư Mục

```
QuyY_print/
│
├── main.py                          # Entry point - Khởi động ứng dụng
├── config.py                        # Cấu hình mặc định (tọa độ, font, mapping)
├── config.json                      # File cấu hình runtime (user tùy chỉnh)
├── info.quyy                        # Metadata app (lưu lịch sử config đã mở)
│
├── core/                            # === TẦNG LOGIC NGHIỆP VỤ ===
│   ├── __init__.py
│   ├── config_manager.py            # Quản lý cấu hình (load/save/import/export)
│   ├── data_processor.py            # Xử lý dữ liệu Excel → format PDF
│   ├── excel_handler.py             # Đọc & validate file Excel
│   ├── lunar_converter.py           # Chuyển đổi Dương lịch → Âm lịch
│   ├── pdf_generator.py             # Tạo PDF bằng ReportLab
│   ├── pdf_service.py               # Điều phối xuất/in PDF (threading)
│   ├── printer_manager.py           # Quản lý máy in Windows
│   ├── resource_manager.py          # Quản lý tài nguyên (font, phôi mẫu)
│   └── utils.py                     # Tiện ích (Unicode→VNI, slugify, ...)
│
├── ui/                              # === TẦNG GIAO DIỆN ===
│   ├── __init__.py
│   ├── config_chooser.py            # Màn hình khởi động chọn cấu hình
│   ├── main_window.py               # Cửa sổ chính (tabbed interface)
│   ├── tabs/                        # Các tab giao diện
│   │   ├── general_tab.py           #   Tab Chung (chọn file, ngày, in)
│   │   ├── coordinate_tab.py        #   Tab Tọa Độ (chỉnh vị trí field)
│   │   ├── custom_tab.py            #   Tab Custom Fields
│   │   ├── settings_tab.py          #   Tab Cài Đặt
│   │   └── guide_tab.py             #   Tab Hướng Dẫn
│   └── components/                  # UI components tái sử dụng
│       ├── print_preview.py         #   Cửa sổ xem trước & in
│       ├── dialogs.py               #   Dialog tùy chỉnh
│       └── toast.py                 #   Thông báo toast
│
├── docs/                            # === TÀI LIỆU ===
│   ├── PROJECT_DOCUMENTATION.md     # Tài liệu dự án (file này)
│   ├── BAT_DAU_NHANH.md             # Hướng dẫn bắt đầu nhanh
│   ├── CHANGELOG.md                 # Lịch sử thay đổi
│   ├── DIEU_CHINH_TOA_DO.md         # Hướng dẫn điều chỉnh tọa độ
│   ├── EXCEL_FORMAT.md              # Định dạng file Excel
│   ├── PROJECT_OVERVIEW.md          # Tổng quan dự án (cũ)
│   ├── START_HERE.md                # Tài liệu bắt đầu
│   ├── guide_convert_VNI.py         # Script tham khảo chuyển đổi VNI
│   └── sample_data.xlsx             # Dữ liệu mẫu
│
├── phoimau.jpg                      # Ảnh phôi mẫu lá phái
├── quyyfont.ttf                     # Font VNI tùy chỉnh
├── arial.ttf                        # Font Arial backup
├── icon.ico                         # Icon ứng dụng
│
├── requirements.txt                 # Danh sách dependencies Python
├── QuyYPrinter.spec                 # Cấu hình PyInstaller
├── build.bat                        # Script build EXE (Windows)
├── build.sh                         # Script build EXE (Linux/Mac)
├── README.md                        # README gốc
│
├── build/                           # Thư mục build tạm (PyInstaller)
└── dist/                            # Thư mục output EXE
    └── QuyYPrinter_v2.1.exe         # File thực thi cuối cùng
```

### 2.3 Luồng Hoạt Động Chính

```
[Khởi động ứng dụng]
        │
        ▼
┌─────────────────────┐
│ 1. ConfigChooser     │ ──→ Mở config có sẵn (.json)
│    (Chọn cấu hình)  │ ──→ HOẶC tạo config mới (mặc định)
│                      │ ──→ HOẶC thoát app
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ 2. ResourceManager   │ Extract phoimau.jpg, quyyfont.ttf
│    (Khởi tạo)       │ vào thư mục exe (nếu chạy từ .exe)
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ 3. MainWindow        │ Hiển thị giao diện 5 tabs
│    (Giao diện chính) │
└─────────┬───────────┘
          │
          ▼
┌──────────────────────────────────────────────────────┐
│ 4. Tab Chung (General)                                │
│    a. Chọn file Excel → ExcelHandler đọc & validate  │
│    b. Chọn thư mục output                            │
│    c. Chọn ngày quy y → LunarConverter chuyển âm lịch │
│    d. Chọn máy in (tự set default trong Windows)      │
│    e. Nhấn [Xuất PDF] hoặc [In Trực Tiếp]            │
└─────────┬────────────────────────────────────────────┘
          ▼
┌──────────────────────────────────────────────────────┐
│ 5. PDFService (chạy trong thread riêng)               │
│    a. DataProcessor xử lý từng dòng Excel             │
│    b. PDFGenerator tạo PDF (text ở tọa độ cấu hình)  │
│    c. Xuất ra file HOẶC gửi đến máy in               │
│    d. Cập nhật progress bar                           │
└──────────────────────────────────────────────────────┘
```

---

## 3. CHI TIẾT MODULE

### 3.1 Tầng Core (`core/`)

#### 3.1.1 `config_manager.py` – Quản Lý Cấu Hình

**Class**: `ConfigManager`

| Thuộc tính | Mô tả |
|------------|--------|
| `field_positions` | Tọa độ các trường dữ liệu từ Excel (pháp danh, họ tên, năm sinh, địa chỉ) |
| `custom_fields` | Các trường tùy chỉnh với giá trị cố định (ngày DL, ÂL, Phật lịch, ...) |
| `excel_mapping` | Ánh xạ tên field PDF ↔ tên cột Excel |
| `selected_date` | Ngày quy y được chọn |
| `use_vni_font` | Bật/tắt chuyển đổi Unicode → VNI |
| `export_mode` | Chế độ xuất: `"single"` (gộp) hoặc `"multiple"` (riêng lẻ) |

**Chức năng chính:**
- **Load/Save** cấu hình từ file JSON
- **Import/Export** cấu hình để backup/chia sẻ
- **CRUD** custom fields (thêm/sửa/xóa)
- **Dirty tracking** – theo dõi thay đổi chưa lưu
- **Tự động cập nhật** các trường ngày/tháng/năm (DL + ÂL + Phật lịch) khi chọn ngày quy y

#### 3.1.2 `excel_handler.py` – Đọc Excel

**Class**: `ExcelHandler`

| Phương thức | Mô tả |
|-------------|--------|
| `read_file(filepath)` | Đọc file Excel, trả về `(count, DataFrame)` |
| `validate_excel(df)` | Validate dữ liệu: kiểm tra cột bắt buộc, format năm sinh, độ dài text |
| `format_validation_message(warnings)` | Format thông báo cảnh báo để hiển thị cho user |

**Các cột Excel bắt buộc:**

| Tên cột | Ý nghĩa | Bắt buộc |
|---------|---------|----------|
| `hovaten` | Họ và tên | ✅ Bắt buộc |
| `phapdanh` | Pháp danh | ❌ Tùy chọn |
| `namsinh` | Năm sinh (4 chữ số) | ❌ Tùy chọn |
| `diachithuongtru_short` | Địa chỉ thường trú | ❌ Tùy chọn |

#### 3.1.3 `data_processor.py` – Xử Lý Dữ Liệu

**Class**: `DataProcessor`

- Chuyển đổi mỗi dòng Excel (pandas `Series`) thành `dict` phù hợp cho PDF
- Xử lý edge cases: giá trị null, text quá dài (tối đa 50 ký tự cho tên, 100 cho địa chỉ), năm sinh không hợp lệ
- Cung cấp error report chi tiết theo từng dòng

#### 3.1.4 `lunar_converter.py` – Chuyển Đổi Âm Lịch

**Class**: `LunarConverter`

| Phương thức | Mô tả |
|-------------|--------|
| `convert_date(date_str)` | Chuyển chuỗi `"YYYY-MM-DD"` → dict gồm ngày/tháng/năm ÂL, tên Can Chi, Phật lịch |
| `solar_to_lunar(dd, mm, yy)` | Thuật toán chuyển đổi lịch Việt Nam (timezone +7) |
| `get_can_chi(year)` | Tính tên Can Chi cho năm bất kỳ |

**Công thức Phật lịch:** `Phật lịch = Năm dương lịch + 544`

**Bảng Can Chi:** Hỗ trợ từ năm 2015 trở đi, kèm thuật toán tính Can Chi động cho bất kỳ năm nào.

#### 3.1.5 `pdf_generator.py` – Tạo PDF

**Class**: `PDFGenerator`

| Phương thức | Mô tả |
|-------------|--------|
| `create_single_pdf(data, output_path, ...)` | Tạo 1 file PDF cho 1 bản ghi |
| `create_merged_pdf(data_list, output_path, ...)` | Tạo 1 file PDF chứa nhiều trang (mỗi trang 1 bản ghi) |

**Thông số PDF:**
- Khổ giấy: **A4 Landscape** (297mm × 210mm)
- Font: VNI custom (`quyyfont.ttf`)
- Hệ tọa độ: Gốc tọa độ **góc trên bên trái** (mm), tự động chuyển đổi sang hệ ReportLab (gốc dưới-trái)
- Hỗ trợ căn lề: Left (L), Center (C), Right (R)

#### 3.1.6 `pdf_service.py` – Dịch Vụ Xuất/In PDF

**Class**: `PDFService`

| Phương thức | Mô tả |
|-------------|--------|
| `run_batch_export(df, output_dir, config_manager, mode, ...)` | Xuất PDF hàng loạt (chạy trong thread riêng) |
| `run_print_job(df, config_manager, mode, ...)` | Tạo PDF tạm → in → xóa tạm (thread riêng) |
| `print_file(pdf_path, printer_name)` | In file PDF qua SumatraPDF hoặc lệnh hệ thống |

**Chế độ xuất:**
- `"multiple"`: Mỗi bản ghi tạo 1 file PDF riêng (đặt tên: `laphai_{index}_{total}_{slug_name}.pdf`)
- `"single"`: Tất cả bản ghi gộp vào 1 file PDF duy nhất

**Xử lý file lock**: Tự động thêm hậu tố `_1`, `_2`,... nếu file đang bị mở bởi ứng dụng khác.

#### 3.1.7 `printer_manager.py` – Quản Lý Máy In

**Class**: `PrinterManager`

| Phương thức | Mô tả |
|-------------|--------|
| `get_printers()` | Lấy danh sách máy in từ Windows (ưu tiên `win32print`, fallback PowerShell) |
| `get_default_printer()` | Lấy tên máy in mặc định |
| `set_default_printer(printer_name)` | Set máy in mặc định trong Windows (tắt tự động quản lý nếu cần) |

#### 3.1.8 `resource_manager.py` – Quản Lý Tài Nguyên

**Chức năng chính:**
- Xác định thư mục app (khác nhau khi chạy từ source vs. EXE)
- Auto-extract tài nguyên từ PyInstaller bundle (`_MEIPASS`) ra thư mục EXE
- Cung cấp đường dẫn an toàn đến: `phoimau.jpg`, `quyyfont.ttf`, `config.json`

#### 3.1.9 `utils.py` – Tiện Ích

| Hàm | Mô tả |
|-----|--------|
| `convert_unicode_to_vni(text)` | Chuyển Unicode Composited → VNI-Windows encoding (134 ký tự) |
| `slugify(text)` | Bỏ dấu tiếng Việt, chuyển lowercase, thay khoảng trắng bằng gạch ngang |
| `get_safe_print_filename(index, total, name)` | Tạo tên file an toàn cho PDF output |

---

### 3.2 Tầng UI (`ui/`)

#### 3.2.1 `config_chooser.py` – Màn Hình Khởi Động

Hiển thị khi bắt đầu ứng dụng, cho phép:
1. **Mở cấu hình có sẵn** (file `.json`) – mở đúng thư mục lần trước
2. **Tạo mới cấu hình** (dùng giá trị mặc định)
3. **Thoát** ứng dụng

Lưu lịch sử đường dẫn config vào file `info.quyy`.

#### 3.2.2 `main_window.py` – Cửa Sổ Chính

**Class**: `MainWindow` | Kích thước: 900×750px

**Tính năng:**
- Giao diện tab-based gồm 5 tab
- Menu bar: Cấu hình (Lưu / Load / Reset / Import / Export)
- Progress bar cho quá trình xuất/in
- Status bar hiển thị trạng thái
- Hỏi lưu khi chuyển tab hoặc thoát nếu có thay đổi chưa lưu

#### 3.2.3 Tab Chung (`general_tab.py`)

Giao diện chính để thao tác:
- Chọn file Excel + xem số lượng bản ghi
- Chọn thư mục output
- Chọn ngày quy y (DatePicker) + hiển thị thông tin âm lịch
- Chọn máy in (dropdown, tự set default khi chọn)
- Checkbox bật/tắt VNI font
- Nút **Xuất PDF** và **In Trực Tiếp**

#### 3.2.4 Tab Tọa Độ (`coordinate_tab.py`)

Trình chỉnh sửa tọa độ trực quan:
- **Canvas preview**: Hiển thị ảnh phôi mẫu (`phoimau.jpg`) + vị trí text
- **Click chọn** field trên canvas (Ctrl+Click chọn nhiều)
- **Phím mũi tên** di chuyển chính xác (1px = 0.4mm)
- **Ctrl+A**: Chọn tất cả, **Escape**: Bỏ chọn
- **Bảng Treeview**: Hiển thị & chỉnh sửa x, y, size bằng số
- Nút **In thử** 1 trang mẫu để kiểm tra tọa độ
- Nút **Đổi phôi mẫu**: Thay ảnh nền phôi mẫu

#### 3.2.5 Tab Custom Fields (`custom_tab.py`)

Quản lý các trường tùy chỉnh:
- Bảng hiển thị: Tên, Giá trị, X, Y, Size, Align
- Nút **Thêm** / **Sửa** / **Xóa** field
- Double-click để sửa nhanh
- Dialog nhập liệu đầy đủ

#### 3.2.6 Tab Cài Đặt (`settings_tab.py`)

- **Chế độ xuất PDF**: Nhiều file (riêng lẻ) hoặc Một file (gộp trang)
- **Cấu hình font**: Bật/tắt chuyển đổi Unicode → VNI
- **Thông tin PDF**: Khổ giấy A4, hướng Landscape

#### 3.2.7 Tab Hướng Dẫn (`guide_tab.py`)

Hướng dẫn sử dụng tích hợp trong app, scrollable, gồm 6 phần:
1. Chuẩn bị file Excel
2. Chọn file và ngày quy y
3. Chỉnh sửa tọa độ
4. Thêm Custom Fields
5. Xuất PDF / In trực tiếp
6. Lưu cấu hình

#### 3.2.8 Components

| Component | File | Mô tả |
|-----------|------|--------|
| `PrintPreviewWindow` | `print_preview.py` | Cửa sổ preview từng lá phái, navigation (prev/next), in từng trang hoặc lưu PDF |
| `CustomFieldDialog` | `dialogs.py` | Dialog thêm/sửa custom field (6 trường: tên, giá trị, x, y, size, align) |
| `ToastNotification` | `toast.py` | Thông báo auto-hide (success/info/warning/error) |

---

## 4. GIAO DIỆN NGƯỜI DÙNG

### 4.1 Luồng Giao Diện

```
┌─────────────────────┐       ┌──────────────────────────────────┐
│  Config Chooser      │       │         Main Window (Tabs)       │
│                      │       │                                  │
│  [Mở File Có Sẵn]   │──┐    │  ┌──────┬────────┬───────┬───┐  │
│  [Tạo Mới]          │──┼───►│  │Chung │Tọa Độ │Custom│...│  │
│  [Thoát]             │  │    │  └──────┴────────┴───────┴───┘  │
└─────────────────────┘  │    │                                  │
                          │    │  [Xuất PDF] → Chọn thư mục      │
                          │    │  [In Trực Tiếp] → Preview       │
                          │    └──────────────┬───────────────────┘
                          │                   │
                          │    ┌──────────────▼───────────────────┐
                          │    │    Print Preview Window           │
                          │    │                                   │
                          │    │  [◄ Prev] 1/50 [Next ►]          │
                          │    │  ┌─────────────────────────────┐ │
                          │    │  │    Preview Canvas            │ │
                          │    │  │    (phôi mẫu + text)        │ │
                          │    │  └─────────────────────────────┘ │
                          │    │  [🖨️ In Trang Này] [💾 Lưu PDF] │
                          │    └──────────────────────────────────┘
                          │
                          └─► Thoát ứng dụng
```

### 4.2 Định Dạng Text Trên Lá Phái

| Trường | Font Size | Bold | Italic | Align | Nguồn dữ liệu |
|--------|-----------|------|--------|-------|---------------|
| Pháp danh | 18 | ❌ | ✅ | Left | Excel (`phapdanh`) |
| Họ tên | 18 | ❌ | ✅ | Left | Excel (`hovaten`) |
| Năm sinh | 12 | ❌ | ✅ | Left | Excel (`namsinh`) |
| Địa chỉ | 12 | ✅ | ✅ | Left | Excel (`diachithuongtru_short`) |
| Ngày DL | 11 | ❌ | ✅ | Center | Tự động từ ngày quy y |
| Tháng DL | 11 | ❌ | ✅ | Center | Tự động từ ngày quy y |
| Năm DL | 11 | ❌ | ✅ | Center | Tự động từ ngày quy y |
| Ngày ÂL | 11 | ❌ | ✅ | Center | Tự động chuyển đổi |
| Tháng ÂL | 11 | ❌ | ✅ | Center | Tự động chuyển đổi |
| Năm ÂL (Can Chi) | 11 | ✅ | ✅ | Center | Tự động chuyển đổi |
| Phật lịch | 11 | ✅ | ✅ | Center | = Năm DL + 544 |

---

## 5. CẤU HÌNH & CẤU TRÚC DỮ LIỆU

### 5.1 File Cấu Hình (`config.json`)

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
  "custom_fields": {
    "pl":           { "value": "",     "x": 175.2, "y": 188.0, "size": 12, ... },
    "ngay_duong":   { "value": "16",   "x": 235.6, "y": 178.0, "size": 11, ... },
    "thang_duong":  { "value": "12",   "x": 260.0, "y": 177.6, "size": 11, ... },
    "nam_duong":    { "value": "2025", "x": 277.0, "y": 177.6, "size": 11, ... },
    "ngay_am":      { "value": "27",   "x": 236.0, "y": 182.4, "size": 11, ... },
    "thang_am":     { "value": "10",   "x": 259.6, "y": 182.4, "size": 11, ... },
    "nam_am":       { "value": "Ất Tỵ","x": 278.2, "y": 183.2, "size": 11, ... },
    "phat_lich":    { "value": "2569", "x": 211.4, "y": 178.0, "size": 11, ... }
  },
  "selected_date": "2025-12-16",
  "use_vni_font": true,
  "export_mode": "single"
}
```

### 5.2 Hệ Tọa Độ

- **Đơn vị**: Millimeter (mm)
- **Gốc tọa độ**: Góc **trên bên trái** của trang A4
- **X**: Khoảng cách từ cạnh trái (0 → 297mm)
- **Y**: Khoảng cách từ cạnh trên (0 → 210mm)
- **Hướng giấy**: Landscape (A4 xoay ngang: 297mm × 210mm)

> ⚠️ ReportLab sử dụng gốc tọa độ ở góc **dưới bên trái**. Phép chuyển đổi: `y_reportlab = page_height - (y_config × mm)`

### 5.3 File Metadata (`info.quyy`)

```json
{
  "last_config_dir": "C:\\Users\\Admin\\Downloads",
  "last_config_file": "C:/Users/Admin/Downloads/config.json"
}
```

Lưu đường dẫn config đã mở lần trước để mở đúng thư mục khi user mở file.

---

## 6. HƯỚNG DẪN SỬ DỤNG

### 6.1 Cài Đặt

#### Cách 1: Chạy file EXE (Người dùng cuối)

1. Tải file `QuyYPrinter_v2.1.exe` từ thư mục `dist/`
2. Đặt các file sau **cùng thư mục** với file EXE:
   - `phoimau.jpg` – Ảnh phôi mẫu lá phái
   - `quyyfont.ttf` – Font chữ VNI
3. Double-click vào file EXE để chạy

> 💡 Khi chạy lần đầu từ EXE, các file `phoimau.jpg` và `quyyfont.ttf` sẽ được tự động extract từ bundle (nếu đã được nhúng lúc build).

#### Cách 2: Chạy từ Source Code (Nhà phát triển)

```bash
# 1. Clone/tải mã nguồn
cd QuyY_print

# 2. Cài đặt dependencies
python -m pip install -r requirements.txt

# 3. Chạy ứng dụng
python main.py
```

### 6.2 Quy Trình Sử Dụng

#### Bước 1: Chuẩn Bị File Excel

Tạo file Excel (`.xlsx`) với các cột sau ở dòng đầu tiên (header):

| Cột | Mô tả | Ví dụ |
|-----|--------|-------|
| `hovaten` | Họ và tên đầy đủ | Nguyễn Văn An |
| `phapdanh` | Pháp danh (để trống nếu chưa có) | Tâm Minh |
| `namsinh` | Năm sinh (4 chữ số) | 1990 |
| `diachithuongtru_short` | Địa chỉ ngắn gọn | P.10, Q. Gò Vấp, TP.HCM |

> 📎 File mẫu: `docs/sample_data.xlsx`

#### Bước 2: Khởi Động Ứng Dụng

1. Mở ứng dụng → Màn hình **Chọn Cấu Hình** xuất hiện
2. Chọn **"Mở File Cấu Hình Có Sẵn"** (nếu đã có config) hoặc **"Tạo Mới Cấu Hình"**

#### Bước 3: Thao Tác Trong Tab Chung

1. **Chọn file Excel**: Click "📂 Chọn File" → chọn file Excel
2. **Chọn thư mục output**: Click "📁 Chọn Thư Mục" (nếu xuất PDF)
3. **Chọn Ngày Quy Y**: Chọn ngày từ DatePicker → hệ thống tự động tính ngày ÂL + Phật lịch
4. **Chọn máy in**: Từ dropdown (hệ thống tự set default khi chọn)

#### Bước 4: Xuất Hoặc In

- **📄 Xuất PDF**: Tạo file PDF vào thư mục đã chọn
- **🖨️ In Trực Tiếp**: Mở cửa sổ Preview → xem trước → in từng trang hoặc tất cả

#### Bước 5: Lưu Cấu Hình (Nếu Cần)

Menu **Cấu hình** → **Lưu** (hoặc **Lưu thành...** cho file mới)

### 6.3 Chỉnh Sửa Tọa Độ

1. Chuyển sang tab **"Tọa Độ"**
2. **Click vào text** trên canvas để chọn field (đổi thành màu xanh)
3. **Dùng phím mũi tên** ←↑→↓ để di chuyển chính xác
4. Hoặc **double-click vào bảng** bên phải để sửa tọa độ bằng số
5. Nhấn **"In Thử"** để in 1 trang mẫu kiểm tra
6. Sau khi hài lòng, nhấn **"Lưu Cấu Hình"**

> 💡 **Mẹo**: Dùng `Ctrl+A` để chọn tất cả field và di chuyển đồng loạt.

---

## 7. TRIỂN KHAI & BUILD

### 7.1 Build File EXE

#### Tự động (khuyến nghị):

```cmd
build.bat
```

#### Thủ công:

```cmd
pip install -r requirements.txt
pyinstaller --onefile --windowed --name "QuyYPrinter" ^
  --icon "icon.ico" ^
  --add-data "phoimau.jpg;." ^
  --add-data "quyyfont.ttf;." ^
  main.py
```

#### Sử dụng spec file:

```cmd
pyinstaller QuyYPrinter.spec
```

### 7.2 Output

```
dist/
├── QuyYPrinter_v2.1.exe      # File thực thi (single file)
├── phoimau.jpg                # Phôi mẫu (auto-extract khi chạy)
└── quyyfont.ttf               # Font (auto-extract khi chạy)
```

### 7.3 Phân Phối

Để phân phối cho người dùng cuối:
1. Copy file `QuyYPrinter_v2.1.exe` 
2. Đảm bảo có `phoimau.jpg` và `quyyfont.ttf` cùng thư mục (hoặc đã được nhúng vào EXE)
3. Tùy chọn: Kèm file `config.json` mẫu nếu muốn cung cấp cấu hình sẵn
4. Tùy chọn: Kèm file `sample_data.xlsx` làm dữ liệu mẫu

---

## 8. BẢO TRÌ & XỬ LÝ SỰ CỐ

### 8.1 Các Lỗi Thường Gặp

| Lỗi | Nguyên nhân | Giải pháp |
|-----|-------------|-----------|
| "Không thể load font" | File `quyyfont.ttf` không tồn tại | Đặt file font cùng thư mục EXE |
| "Không thể đọc file Excel" | File sai định dạng hoặc đang mở | Đóng file Excel, kiểm tra định dạng `.xlsx` |
| Tọa độ sai lệch | Config không khớp phôi mẫu | Dùng tab Tọa Độ để chỉnh, in thử trước |
| Font tiếng Việt lỗi | Chưa bật VNI hoặc font không đúng | Kiểm tra checkbox VNI trong Cài Đặt |
| Máy in không hiện | Windows chưa cài driver | Cài driver máy in, khởi động lại app |
| File PDF bị lock | File đang mở trong ứng dụng khác | Đóng file PDF, app sẽ tự tạo file mới (`_1`, `_2`...) |

### 8.2 Cấu Trúc Log

Ứng dụng ghi log ra console (stdout) với format:
```
[ModuleName] Message
```
Ví dụ:
```
[Main] Config: path=C:\config.json, is_new=False
[ResourceManager] Extracted: phoimau.jpg -> C:\phoimau.jpg
[PrinterManager] Đã set máy in mặc định: HP LaserJet
```

### 8.3 Backup & Restore Cấu Hình

- **Backup**: Menu Cấu hình → Export → Lưu file `.json`
- **Restore**: Menu Cấu hình → Import → Chọn file `.json` đã backup
- **Reset**: Menu Cấu hình → Reset Mặc Định → Khôi phục giá trị gốc từ `config.py`

---

## 9. LỊCH SỬ PHIÊN BẢN

### v2.1 (Hiện tại – 02/2026)
- ✅ Prompt hỏi lưu khi chuyển tab hoặc thoát (tránh mất dữ liệu)
- ✅ Set máy in mặc định trong Windows khi chọn từ dropdown
- ✅ Hỗ trợ đa cấu hình thông qua Config Chooser
- ✅ Import/Export cấu hình
- ✅ Cửa sổ Print Preview với navigation và in từng trang

### v2.0 (01/2026)
- ✅ Refactor kiến trúc: Tách `core/` và `ui/` riêng biệt
- ✅ Tab-based UI (5 tabs)
- ✅ Trình chỉnh tọa độ trực quan (Canvas preview + phím mũi tên)
- ✅ Custom Fields CRUD
- ✅ Config Manager (JSON-based)
- ✅ Toast notifications
- ✅ Dirty tracking (theo dõi thay đổi chưa lưu)

### v1.0 (12/2025)
- ✅ Ứng dụng đầu tiên (monolithic `app.py`)
- ✅ Đọc Excel, chuyển âm lịch, tạo PDF, in trực tiếp
- ✅ GUI cơ bản với Tkinter
- ✅ Hỗ trợ font VNI Unicode

---

## 10. LỘ TRÌNH PHÁT TRIỂN

### Ngắn hạn (Q1 2026)
- [ ] Hỗ trợ nhập dữ liệu từ nhiều định dạng Excel header (case-insensitive)
- [ ] Drag & drop file Excel
- [ ] Undo/Redo cho chỉnh sửa tọa độ

### Trung hạn (Q2–Q3 2026)
- [ ] Hỗ trợ nhiều template phôi mẫu
- [ ] Export sang Word/Image
- [ ] Batch printing với queue
- [ ] Auto-update kiểm tra phiên bản mới

### Dài hạn (2027+)
- [ ] Web version
- [ ] Cloud storage integration
- [ ] Multi-language support
- [ ] Database backend thay thế Excel

---

> 📞 **Liên hệ hỗ trợ kỹ thuật**: Trung Quảng An – 0983.838.619  
> 📄 **License**: MIT License – Miễn phí sử dụng và chỉnh sửa
