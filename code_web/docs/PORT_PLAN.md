# 📋 KẾ HOẠCH PORT SANG WEB - QUY Y PRINT

> **Ngày tạo:** 2026-03-06  
> **Trạng thái:** Đang triển khai  
> **Mục tiêu:** Port toàn bộ ứng dụng in lá phái quy y từ Python/Tkinter sang Web (Nuxt 4 + PrimeVue + Cloudflare Pages)

---

## 1. TỔNG QUAN KIẾN TRÚC

### 1.1 Bản Desktop (Python) - Hiện tại

```
main.py → ConfigChooser → MainWindow
                            ├── GeneralTab (chọn Excel, ngày, in/xuất)
                            ├── CoordinateTab (canvas chỉnh tọa độ)
                            ├── CustomFieldTab (thêm/sửa/xóa custom field)
                            ├── SettingsTab (cài đặt font, máy in)
                            └── GuideTab (hướng dẫn)
```

### 1.2 Bản Web (Nuxt) - Mới (ALL-IN-ONE page)

```
app/
├── pages/
│   └── index.vue           → Trang duy nhất: Excel + Ngày + Canvas + In [✅]
├── composables/
│   ├── useVniConverter.ts   → Convert Unicode ↔ VNI [✅]
│   ├── useLunarConverter.ts → Chuyển đổi Dương → Âm lịch [✅]
│   ├── useConfigManager.ts  → Quản lý config (localStorage) [✅]
│   ├── useDataProcessor.ts  → Excel handler + Data processor [✅]
│   └── useLayout.ts         → Layout management [✅]
├── layouts/                 → Sidebar + Topbar [✅]
└── tests/                   → Test composables [✅]
```

---

## 2. MAPPING MODULE: PYTHON → JAVASCRIPT

### 2.1 Core Modules

| # | Python Module | Dòng | JS Module | Thư viện | Trạng thái |
|---|---|---|---|---|---|
| 1 | `core/utils.py` | 86 | `composables/useVniConverter.ts` | Thuần JS | ✅ Xong |
| 2 | `core/lunar_converter.py` | 271 | `composables/useLunarConverter.ts` | Thuần JS (port math) | ✅ Xong |
| 3 | `core/config_manager.py` | 292 | `composables/useConfigManager.ts` | localStorage | ✅ Xong |
| 4 | `core/excel_handler.py` | 159 | `composables/useDataProcessor.ts` | **SheetJS (xlsx)** | ✅ Xong |
| 5 | `core/data_processor.py` | 132 | `composables/useDataProcessor.ts` | Thuần JS | ✅ Xong |
| 6 | `core/pdf_generator.py` | 186 | Nhúng trong `pages/index.vue` | **pdf-lib + fontkit** | ✅ Xong |
| 7 | `core/pdf_service.py` | 305 | Nhúng trong `pages/index.vue` | pdf-lib | ✅ Xong |
| 8 | `core/printer_manager.py` | 133 | ❌ Bỏ | `window.print()` | N/A |
| 9 | `core/resource_manager.py` | 117 | ❌ Bỏ | Static files (`public/`) | N/A |
| 10 | `config.py` | 129 | Nhúng vào `useConfigManager.ts` | Thuần JS | ✅ Xong |

### 2.2 UI Modules

| # | Python UI | Dòng | Vue Page/Component | Trạng thái |
|---|---|---|---|---|
| 1 | `ui/config_chooser.py` | 213 | ❌ Bỏ (web không cần) | N/A |
| 2 | `ui/main_window.py` | 411 | `layouts/` + router | ✅ Xong |
| 3 | `ui/tabs/general_tab.py` | ~400 | `pages/print.vue` | ⬜ Chưa |
| 4 | `ui/tabs/coordinate_tab.py` | 623 | `pages/index.vue` (canvas) | ✅ Xong |
| 5 | `ui/tabs/custom_tab.py` | ~120 | Nhập vào `pages/coordinate.vue` | ⬜ Chưa |
| 6 | `ui/tabs/settings_tab.py` | ~150 | `pages/settings.vue` | ⬜ Chưa |
| 7 | `ui/tabs/guide_tab.py` | ~130 | `pages/guide.vue` | ⬜ Chưa |
| 8 | `ui/components/print_preview.py` | ~330 | Nhập vào `pages/print.vue` | ⬜ Chưa |
| 9 | `ui/components/quick_entry_dialog.py` | ~600 | Dialog PrimeVue | ⬜ Chưa |
| 10 | `ui/components/toast.py` | ~60 | PrimeVue `useToast()` | ✅ Xong |
| 11 | `ui/components/dialogs.py` | ~90 | PrimeVue Dialog | ✅ Xong |

---

## 3. CHI TIẾT TỪNG MODULE CẦN PORT

### 3.1 ⬜ `useLunarConverter.ts` — Chuyển đổi Dương → Âm lịch

**Nguồn:** `core/lunar_converter.py` (271 dòng)

**Chức năng:**
- `jd_from_date(dd, mm, yy)` → Tính Julian day number
- `get_new_moon_day(k, timezone)` → Tính ngày trăng non (sóc)
- `get_sun_longitude(jdn, timezone)` → Tính kinh độ mặt trời
- `get_lunar_month_11(yy, timezone)` → Tìm tháng 11 âm lịch
- `get_leap_month_offset(a11, timezone)` → Tính tháng nhuận
- `solar_to_lunar(dd, mm, yy, timezone)` → Chuyển dương → âm
- `get_can_chi(year)` → Tính tên Can Chi (Ất Tỵ, Bính Ngọ...)
- `convert_date(date_str)` → API chính: nhận "YYYY-MM-DD", trả về dict

**Output của `convert_date()`:**
```typescript
interface LunarResult {
  solar_day: number      // Ngày dương
  solar_month: number    // Tháng dương
  solar_year: number     // Năm dương 
  lunar_day: number      // Ngày âm
  lunar_month: number    // Tháng âm
  lunar_year: number     // Năm âm (số)
  lunar_year_name: string // "Ất Tỵ", "Bính Ngọ"...
  buddhist_year: number  // Phật lịch = dương + 544
}
```

**Lưu ý port:**
- Toàn bộ logic là tính toán math thuần → port thẳng sang JS
- `math.sin()` → `Math.sin()`, `math.cos()` → `Math.cos()`
- `int()` → `Math.floor()` hoặc `Math.trunc()`
- Bảng Can Chi có sẵn, công thức tính cho năm bất kỳ: `(year - 4) % 10` và `(year - 4) % 12`
- Timezone mặc định = 7 (Việt Nam)

---

### 3.2 ⬜ `useConfigManager.ts` — Quản lý cấu hình

**Nguồn:** `core/config_manager.py` (292 dòng) + `config.py` (129 dòng)

**Dữ liệu config cần lưu:**
```typescript
interface AppConfig {
  // Tọa độ 4 trường chính từ Excel
  field_positions: Record<string, FieldPosition>
  
  // Mapping Excel column → field name
  excel_mapping: Record<string, string>
  
  // Custom fields (ngày tháng, giá trị cố định)
  custom_fields: Record<string, CustomField>
  
  // Cài đặt
  use_vni_font: boolean     // Dùng font VNI hay Unicode
  export_mode: 'single' | 'multiple'  // 1 file PDF hay nhiều file
  use_background_image: boolean  // In có ảnh nền
}

interface FieldPosition {
  x: number      // mm từ trái
  y: number      // mm từ trên
  size: number   // font size
  bold: boolean
  italic: boolean
  align: 'L' | 'C' | 'R'
}

interface CustomField extends FieldPosition {
  value: string  // Giá trị hiển thị
}
```

**Giá trị mặc định (từ `config.py`):**

| Field | X (mm) | Y (mm) | Size | Align |
|---|---|---|---|---|
| `phap_danh` | 196.6 | 139.0 | 18 | L |
| `ho_ten` | 196.6 | 129.4 | 18 | L |
| `sinh_nam` | 197.0 | 147.0 | 12 | L |
| `dia_chi` | 197.4 | 154.2 | 12 | L |

**Custom fields mặc định (ngày tháng):**

| Field | X | Y | Size | Align | Mô tả |
|---|---|---|---|---|---|
| `phat_lich` | 206.0 | 178.0 | 12 | L | Phật lịch |
| `ngay_duong` | 235.2 | 178.4 | 11 | C | Ngày dương |
| `thang_duong` | 259.6 | 178.0 | 11 | C | Tháng dương |
| `nam_duong` | 276.6 | 178.0 | 11 | C | Năm dương |
| `ngay_am` | 235.6 | 182.8 | 11 | C | Ngày âm |
| `thang_am` | 259.2 | 182.8 | 11 | C | Tháng âm |
| `nam_am` | 277.8 | 183.6 | 11 | C | Năm Can Chi |

**Excel mapping mặc định:**

| Field PDF | Cột Excel |
|---|---|
| `ho_ten` | `hovaten` |
| `phap_danh` | `phapdanh` |
| `nam_sinh` | `namsinh` |
| `dia_chi` | `diachithuongtru_short` |

**Lưu trữ web:** `localStorage` thay cho file JSON
- Key: `quyy_config` → JSON string
- Export/Import: Download/Upload file `.json`
- `set_selected_date()`: Khi chọn ngày, tự gọi `LunarConverter` để fill các custom fields ngày tháng

---

### 3.3 ⬜ `useExcelHandler.ts` — Đọc file Excel

**Nguồn:** `core/excel_handler.py` (159 dòng)

**Thư viện:** `xlsx` (SheetJS) — đã có trong dependencies

**Chức năng:**
1. **`readFile(file: File)`** — Đọc file Excel từ `<input type="file">`
   - Python dùng `pandas.read_excel()` → JS dùng `XLSX.read()`
   - Lọc bỏ dòng NaN ở cột `hovaten`
   - Return: `{ count, data: object[] }`

2. **`validateExcel(data)`** — Kiểm tra dữ liệu
   - Kiểm tra cột bắt buộc: `hovaten`, `phapdanh`, `namsinh`, `diachithuongtru_short`
   - Kiểm tra từng dòng: họ tên rỗng, năm sinh 4 chữ số, độ dài tối đa 50 ký tự
   - Return: `{ has_warnings, missing_columns, row_warnings, summary }`

**Lưu ý port:**
- `pd.isna(value)` → `value === null || value === undefined || value === ''`
- `pd.read_excel()` → `XLSX.read(buffer, { type: 'array' })` + `XLSX.utils.sheet_to_json()`
- Đọc file: `FileReader.readAsArrayBuffer(file)` → Promise
- Không cần `import re` → dùng RegExp JS `/^\d{4}$/`

---

### 3.4 ⬜ `useDataProcessor.ts` — Xử lý dữ liệu

**Nguồn:** `core/data_processor.py` (132 dòng)

**Chức năng:**
1. **`processRow(row, index)`** — Xử lý 1 dòng Excel
   - Clean & validate `hovaten` (bắt buộc, max 50 ký tự)
   - Clean & validate `phapdanh` (optional, max 50)
   - Clean & validate `namsinh` (4 chữ số, xử lý float `1990.0` → `1990`)
   - Clean & validate `diachithuongtru_short` (optional, max 100)
   - Return: `{ phap_danh, ho_ten, sinh_nam, dia_chi, _has_error, _error_details }`

2. **`processDataFrame(data)`** — Xử lý toàn bộ mảng
   - Gọi `processRow()` cho từng dòng
   - Đếm lỗi, tạo summary
   - Return: `{ dataList, errorCount, errorSummary }`

**Quy tắc xử lý:**
- Họ tên thiếu → `"[LỖI: Thiếu họ tên - Dòng X]"`
- Quá dài → cắt bớt + `"..."`
- Năm sinh có `.` → lấy phần trước dấu `.` (Excel format float)
- Năm sinh không hợp lệ → `"[1990?]"` (vẫn in nhưng đánh dấu)

---

### 3.5 🔄 `usePdfGenerator.ts` — Tạo PDF

**Nguồn:** `core/pdf_generator.py` (186 dòng) + `core/pdf_service.py` (305 dòng)

**Thư viện:** `pdf-lib` + `@pdf-lib/fontkit` — đã cài sẵn

**Chức năng chính:**

1. **`createSinglePdf(data, config)`** — Tạo 1 trang PDF
   - Tạo page A4 Landscape (841.89 × 595.28 pt)
   - Vẽ ảnh nền (phôi mẫu) nếu bật
   - Embed font VNI (`quyyfont.ttf`)
   - Vẽ các field chuẩn: `field_positions` (data từ Excel)
   - Vẽ các custom field: `custom_fields` (ngày tháng, giá trị cố định)
   - Convert text Unicode → VNI nếu bật `use_vni_font`

2. **`createMergedPdf(dataList, config)`** — Tạo PDF nhiều trang
   - Loop `dataList`, mỗi item → 1 page
   - Progress callback
   - Return: PDF bytes

3. **`createMultiplePdf(dataList, config)`** — Tạo nhiều file PDF riêng
   - Web: tạo ZIP chứa nhiều file, hoặc download lần lượt

**Mapping tọa độ:**
```
Python (ReportLab): x_pt = x_mm * mm,  y_pt = page_height - (y_mm * mm)
JS (pdf-lib):       x_pt = x_mm * 2.8346,  y_pt = page_height - (y_mm * 2.8346)
```

**Align mapping:**
```
Python: drawString (L), drawCentredString (C), drawRightString (R)
JS:     drawText(x, y)  → x -= 0 (L), x -= width/2 (C), x -= width (R)
```

**Lưu ý:**
- Font VNI: text phải qua `convertUnicodeToVni()` trước khi drawText
- Background image: canvas → toDataURL('image/jpeg') → embedJpg()
- Một phần đã implement trong `index.vue` → cần tách thành composable riêng

---

### 3.6 ⬜ Trang In Hàng Loạt (`pages/print.vue`)

**Nguồn:** `ui/tabs/general_tab.py` (~400 dòng)

**Luồng hoạt động:**
```
1. Chọn ngày dương lịch (DatePicker)
   ↓ auto
2. Tính ngày âm + Phật lịch (LunarConverter)
   ↓ auto fill
3. Hiển thị: ngày/tháng/năm dương, ngày/tháng/năm âm Can Chi, Phật lịch
   ↓
4. Upload file Excel (FileUpload PrimeVue)
   ↓
5. Validate + hiển thị danh sách (DataTable)
   ↓
6. Chọn chế độ: 1 file nhiều trang / nhiều file
   ↓
7. Click "Tạo PDF" / "In Ngay"
   ↓
8. Progress bar + kết quả
```

**UI Components (PrimeVue):**
- `DatePicker` → chọn ngày quy y
- `FileUpload` → upload Excel
- `DataTable` → preview dữ liệu
- `ProgressBar` → tiến trình tạo PDF
- `Button` → Xuất PDF, In ngay
- `Dialog` → Cảnh báo validation
- `Toast` → Thông báo kết quả

---

### 3.7 ⬜ Quick Entry Dialog

**Nguồn:** `ui/components/quick_entry_dialog.py` (~600 dòng)

**Chức năng:** Nhập nhanh dữ liệu 1 người (không cần Excel)
- Form: Họ tên, Pháp danh, Năm sinh, Địa chỉ
- Preview trước khi in
- Nút: In ngay, Tạo PDF

---

### 3.8 ⬜ Custom Field Manager

**Nguồn:** `ui/tabs/custom_tab.py` (~120 dòng)

**Chức năng:**
- Danh sách custom fields (DataTable)
- Thêm field mới (name, value, x, y, size, align)
- Sửa field (double-click)
- Xóa field
- Đồng bộ với canvas coordinate

---

## 4. CẤU TRÚC FILE CONFIG.JSON

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
    "phat_lich":    { "value": "2569", "x": 211.4, "y": 178.0, "size": 11, "align": "C" },
    "ngay_duong":   { "value": "16",   "x": 235.6, "y": 178.0, "size": 11, "align": "C" },
    "thang_duong":  { "value": "12",   "x": 260.0, "y": 177.6, "size": 11, "align": "C" },
    "nam_duong":    { "value": "2025", "x": 277.0, "y": 177.6, "size": 11, "align": "C" },
    "ngay_am":      { "value": "27",   "x": 236.0, "y": 182.4, "size": 11, "align": "C" },
    "thang_am":     { "value": "10",   "x": 259.6, "y": 182.4, "size": 11, "align": "C" },
    "nam_am":       { "value": "Ất Tỵ","x": 278.2, "y": 183.2, "size": 11, "align": "C" }
  },
  "use_vni_font": true,
  "export_mode": "single",
  "use_background_image": false
}
```

---

## 5. THỨ TỰ TRIỂN KHAI

### Phase 1: Nền tảng ✅ XONG
- [x] Setup Nuxt 4 + PrimeVue + TailwindCSS
- [x] Layout: Sidebar + Topbar
- [x] Canvas chỉnh tọa độ trực quan (drag & drop, phím mũi tên)
- [x] VNI font loading (FontFace API) + Unicode→VNI converter
- [x] PDF preview cơ bản (pdf-lib)
- [x] Static files: phoimau.jpg, quyyfont.ttf

### Phase 2: Core Logic ✅ XONG
- [x] Port `LunarConverter` sang JS (+ tests)
- [x] Port `ConfigManager` sang JS (localStorage + SSR safe)
- [x] Port `ExcelHandler` sang JS (SheetJS) 
- [x] Port `DataProcessor` sang JS (+ tests)
- [x] PDF Generator nhúng trong index.vue

### Phase 3: Trang In Ấn ✅ XONG (gộp vào index.vue)
- [x] Trang chọn ngày (auto tính âm lịch + Phật lịch)
- [x] Upload + validate Excel
- [x] Preview canvas với dữ liệu demo/thực
- [x] Tạo PDF gộp (1 file nhiều trang)
- [x] Download PDF / In trực tiếp
- [x] Record navigation (Trước/Sau)
- [x] Nhập nhanh (expandable)

### Phase 4: Quản lý Config ✅ XONG
- [x] Chỉnh tọa độ fields (drag, phím mũi tên, dialog)
- [x] Export config JSON
- [x] Settings (VNI toggle, background image)
- [x] Reset to defaults
- [ ] Import config JSON (upload)

### Phase 5: Nâng cao ⬜
- [ ] Cải thiện UX/UI
- [ ] Hướng dẫn sử dụng
- [ ] Template system (chọn phôi mẫu khác nhau)
- [ ] Deploy Cloudflare Pages

---

## 6. SO SÁNH KỸ THUẬT

| Vấn đề | Desktop (Python) | Web (JS) |
|---|---|---|
| **Đọc Excel** | `pandas.read_excel()` | `XLSX.read()` (SheetJS) |
| **Tạo PDF** | `reportlab` Canvas | `pdf-lib` PDFDocument |
| **Font VNI** | RegisterFont TTF + VNI convert | FontFace API + pdf-lib embedFont |
| **Lưu config** | File `config.json` trên ổ cứng | `localStorage` trên trình duyệt |
| **Chọn ngày** | `tkcalendar.DateEntry` | PrimeVue `DatePicker` |
| **In trực tiếp** | `win32api.ShellExecute("print")` | `window.open(blob).print()` |
| **Chọn máy in** | `win32print.EnumPrinters()` | ❌ Không thể (browser security) |
| **Progress bar** | `ttk.Progressbar` | PrimeVue `ProgressBar` |
| **Canvas** | Tkinter Canvas (click, phím mũi tên) | HTML5 Canvas (+ drag & drop!) |
| **File dialog** | `tkinter.filedialog` | `<input type="file">` |
| **Xuất file** | `os.path.join()` + ghi file | `Blob` + `URL.createObjectURL()` |

---

## 7. NHỮNG THAY ĐỔI QUAN TRỌNG KHI PORT

### 7.1 Không cần nữa (Desktop-only)
- ❌ `printer_manager.py` — Web dùng `window.print()`
- ❌ `resource_manager.py` — Web dùng `public/` folder
- ❌ `config_chooser.py` — Web không cần chọn file config khi khởi động
- ❌ PyInstaller build (`.spec`, `build.bat`)
- ❌ `win32api`, `win32print` — Windows API

### 7.2 Thay đổi behavior
- **In ấn:** Desktop in thẳng ra máy in → Web tạo PDF rồi `window.print()` (user chọn máy in trong browser dialog)
- **Lưu config:** File JSON trên ổ cứng → `localStorage` (mất khi xóa cache browser, cần có export/import)
- **Xuất nhiều file:** Desktop ghi thẳng ra thư mục → Web phải zip lại hoặc download lần lượt
- **File lock:** Desktop xử lý file bị lock (`_get_available_filepath`) → Web không cần (Blob tạo mới mỗi lần)

### 7.3 PDF: ReportLab → pdf-lib

| ReportLab | pdf-lib |
|---|---|
| `canvas.Canvas(path, pagesize)` | `PDFDocument.create()` + `addPage([w, h])` |
| `c.drawString(x, y, text)` | `page.drawText(text, { x, y })` |
| `c.drawCentredString(x, y, text)` | Tính `x -= width/2` rồi `drawText` |
| `c.drawRightString(x, y, text)` | Tính `x -= width` rồi `drawText` |
| `c.setFont(name, size)` | `embedFont(bytes)` lúc đầu, truyền vào `drawText` |
| `c.drawImage(path, ...)` | `embedJpg(bytes)` + `page.drawImage(img, {...})` |
| `c.showPage()` | `pdfDoc.addPage(...)` |
| `c.save()` | `await pdfDoc.save()` → Uint8Array |
| Tọa độ Y: `page_height - y_mm * mm` | Giống nhau |

---

## 8. FILE DỮ LIỆU MẪU

### 8.1 Excel mẫu (`sample_data.xlsx`)

| hovaten | phapdanh | namsinh | diachithuongtru_short |
|---|---|---|---|
| Nguyễn Văn An | Tâm Minh | 1990 | P.10, Q.Gò Vấp, TP.HCM |
| Trần Thị Bình | Diệu Hạnh | 1985 | TT.Đức Phổ, Quảng Ngãi |
| Lê Văn Cường | Thiện Tâm | 2001 | X.An Phú, H.Củ Chi, TP.HCM |

### 8.2 Công thức tính ngày

```
Input: Ngày dương lịch (ví dụ: 2025-12-16)
  ↓ LunarConverter.solar_to_lunar()
Output:
  - Ngày âm: 27
  - Tháng âm: 10
  - Năm âm: Ất Tỵ (Can Chi)
  - Phật lịch: 2569 (= 2025 + 544)
```
