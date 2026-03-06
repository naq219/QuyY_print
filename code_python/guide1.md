Tuyệt vời. Đây là tài liệu hướng dẫn tái cấu trúc (Refactoring Guide) chi tiết dành cho Developer. Tài liệu này tập trung vào chiến lược, cấu trúc và quy trình chuyển đổi code hiện tại (God Object `app.py`) sang mô hình MVC/Service-oriented mà không bị "ngập" trong code mới.

-----

# REFACTORING GUIDE: QUY Y PRINTER APP (v2.0)

**Mục tiêu:** Chuyển đổi ứng dụng từ cấu trúc đơn khối (Monolithic Script) sang kiến trúc MVC (Model-View-Controller) phân tầng.
**Nguyên tắc:** Tách biệt hoàn toàn Logic xử lý (Core) và Giao diện (UI).

## 1\. Cấu Trúc Thư Mục Mới (Target Structure)

Developer cần tạo cấu trúc thư mục như sau và di chuyển code tương ứng:

```text
QuyY_App/
├── main.py                  # Entry Point (Khởi tạo Controller & Main Window)
├── config.py                # Giữ lại các hằng số mặc định (CONSTANTS)
├── assets/                  # (Optional) Icon, images
│
├── core/                    # [MODEL/SERVICE LAYER] - Xử lý logic, không chứa Tkinter
│   ├── __init__.py
│   ├── config_manager.py    # Class quản lý Load/Save JSON (Tách từ app.py)
│   ├── excel_handler.py     # Xử lý Pandas, lọc dữ liệu (Tách từ app.py)
│   ├── data_processor.py    # Logic chuyển đổi Excel Row -> PDF Data (Hàm _prepare_data cũ)
│   ├── pdf_service.py       # Wrapper quản lý tiến trình in/xuất PDF (Threading)
│   └── lunar_converter.py   # (File cũ giữ nguyên)
│   └── pdf_generator.py     # (File cũ di chuyển vào đây)
│
└── ui/                      # [VIEW LAYER] - Chỉ hiển thị, không xử lý logic nghiệp vụ
    ├── __init__.py
    ├── main_window.py       # Khung chính, Menu, Status bar
    ├── components/          # Các thành phần nhỏ tái sử dụng
    │   ├── __init__.py
    │   └── dialogs.py       # (File cũ di chuyển vào đây)
    └── tabs/                # Các màn hình chức năng
        ├── __init__.py
        ├── general_tab.py   # Tab "Chính"
        ├── coordinate_tab.py# Tab "Tọa Độ"
        └── custom_tab.py    # Tab "Custom Fields"
```

-----

## 2\. Lộ Trình Thực Hiện (Step-by-Step Implementation)

### Giai đoạn 1: Xây dựng Core (Backend)

*Mục tiêu: Đảm bảo logic chạy được mà không cần bật giao diện.*

#### 1.1. `core/config_manager.py`

  * **Nguồn:** Code từ `_load_config`, `_save_config`, `_reset_default` trong `app.py`.
  * **Nhiệm vụ:**
      * Tạo class `ConfigManager`.
      * Lưu trữ `field_positions`, `custom_fields`, `excel_mapping` dưới dạng thuộc tính của class.
      * Method `load()`, `save()`, `get_field(name)`, `update_field(...)`.
      * **Lưu ý:** Loại bỏ toàn bộ `tk.StringVar` hoặc `messagebox`. Nếu lỗi, hãy `raise Exception` để tầng UI bắt.

#### 1.2. `core/data_processor.py`

  * **Nguồn:** Hàm `_prepare_data` trong `app.py`.
  * **Nhiệm vụ:**
      * Import `LunarConverter`.
      * Viết hàm `process_row(row_data) -> dict`.
      * Input là 1 dòng Excel (pandas Series), Output là dict chuẩn để in PDF.
      * Logic chuyển đổi ngày âm/dương nằm gói gọn tại đây.

#### 1.3. `core/excel_handler.py`

  * **Nguồn:** Code từ `_load_excel_preview` trong `app.py`.
  * **Nhiệm vụ:**
      * Method `read_file(path) -> DataFrame`.
      * Thực hiện việc lọc bản ghi trống (`dropna`) tại đây.
      * Trả về tổng số bản ghi và DataFrame sạch.

#### 1.4. `core/pdf_service.py`

  * **Nguồn:** Code từ `_do_export_pdf`, `_do_print_direct` và việc gọi `PDFGenerator`.
  * **Nhiệm vụ:**
      * Class `PDFService`.
      * Import `PDFGenerator`.
      * Method `export_batch(df, output_dir, config, callback_func)`.
      * **Quan trọng:** Xử lý **Threading** tại đây. UI sẽ gọi hàm này, hàm này tạo thread chạy ngầm, và gọi `callback_func(current, total)` để báo ngược lại cho UI cập nhật thanh Progress Bar.

-----

### Giai đoạn 2: Tách nhỏ UI (View)

*Mục tiêu: Chia nhỏ file `app.py` khổng lồ thành các Class quản lý từng tab.*

#### 2.1. `ui/tabs/coordinate_tab.py` & `ui/tabs/custom_tab.py`

  * **Nguồn:** `_build_coord_tab`, `_build_custom_tab`, và các hàm xử lý Treeview (`_on_field_double_click`, v.v.).
  * **Yêu cầu:**
      * Kế thừa `tk.Frame`.
      * Constructor nhận `parent` và `config_manager`.
      * Khi người dùng sửa Treeview -\> Gọi `config_manager.update_field(...)`.
      * Không chứa code save file JSON (việc đó là của nút Save chung hoặc gọi về Controller).

#### 2.2. `ui/tabs/general_tab.py`

  * **Nguồn:** `_build_main_tab`.
  * **Yêu cầu:**
      * Chứa các `Entry` chọn file, nút Export.
      * **Không tự xử lý Export**. Khi nút Export được bấm, nó sẽ kích hoạt một Event hoặc gọi một hàm callback được truyền từ `MainWindow`.
      * Ví dụ: `self.on_export_click(excel_path, output_path, mode)`.

#### 2.3. `ui/main_window.py` (Controller trung tâm)

  * **Nguồn:** Class `QuyYPrinterApp` (phần khung sườn).
  * **Nhiệm vụ:**
      * Khởi tạo `tk.Tk`.
      * Khởi tạo các Core services: `self.cfg = ConfigManager()`, `self.pdf_service = PDFService()`.
      * Tạo Notebook và add các Tab con vào.
      * Truyền `self.cfg` vào các Tab con để chúng hiển thị dữ liệu.
      * **Wiring (Nối dây):**
          * Định nghĩa hàm `handle_export(...)`.
          * Truyền hàm này vào `GeneralTab`.
          * Khi `handle_export` chạy -\> gọi `self.pdf_service.export_batch(...)`.
          * Cung cấp hàm `update_progress_ui` để làm callback cho Service.

-----

## 3\. Quy Tắc Refactoring (Do's and Don'ts)

1.  **Dependency Injection (Tiêm phụ thuộc):**

      * *Don't:* Trong `CoordinateTab`, không được `import ConfigManager` và tạo mới nó.
      * *Do:* Truyền instance của `ConfigManager` đã được tạo ở `main.py` vào `CoordinateTab`.
      * *Tại sao?* Để tất cả các tab đều sửa chung một bộ dữ liệu cấu hình.

2.  **UI không chứa Logic:**

      * *Kiểm tra:* Nếu trong file `ui/` có dòng `import pandas` hay `from lunar_converter`, bạn đang làm sai. UI chỉ nên nhận dữ liệu đã xử lý (List, Dict, String).

3.  **Callback cho Threading:**

      * Logic export chạy rất lâu. Service phải chạy trên Thread riêng.
      * Service không được phép đụng vào `tk.Label` hay `progress_bar`.
      * Service gọi `callback(percent)`. Controller (Main Window) nhận `percent` và dùng `root.after` hoặc `variable.set` để update UI an toàn.

## 4\. Các bước di chuyển code cụ thể (Cheat Sheet)

| Code cũ (app.py) | Vị trí mới đề xuất | Ghi chú |
| :--- | :--- | :--- |
| `FIELD_POSITIONS`, `CONFIG_FILE` | `core/config_manager.py` | Biến thành thuộc tính của class Config |
| `_load_config`, `_save_config` | `core/config_manager.py` | Logic JSON |
| `_prepare_data` | `core/data_processor.py` | Logic nghiệp vụ quan trọng nhất |
| `_load_excel_preview` | `core/excel_handler.py` | Tách logic đọc file |
| `_do_export_pdf`, `thread` | `core/pdf_service.py` | Logic chạy batch job |
| `_build_gui`, `notebook` | `ui/main_window.py` | Khung ứng dụng |
| `_build_coord_tab` | `ui/tabs/coordinate_tab.py` | Tạo class `CoordinateTab(tk.Frame)` |
| `_build_custom_tab` | `ui/tabs/custom_tab.py` | Tạo class `CustomFieldTab(tk.Frame)` |
| `CustomFieldDialog` | `ui/components/dialogs.py` | Giữ nguyên hoặc di chuyển file |

-----

## 5\. Ví dụ mẫu cho Controller (ui/main\_window.py)

Đây là cách bạn nối các phần lại với nhau:

```python
# Pseudo-code minh họa logic Controller
class MainWindow:
    def __init__(self, root):
        self.root = root
        
        # 1. Init Core Services
        self.config_manager = ConfigManager("field_config.json")
        self.pdf_service = PDFService()
        
        # 2. Init UI Components
        self.notebook = ttk.Notebook(root)
        
        # Inject config_manager vào các tab để chúng hiển thị dữ liệu
        self.coord_tab = CoordinateTab(self.notebook, self.config_manager)
        self.general_tab = GeneralTab(self.notebook, on_export=self.start_export_process)
        
        self.notebook.add(self.general_tab, text="Chính")
        self.notebook.add(self.coord_tab, text="Tọa Độ")
        # ...

    def start_export_process(self, file_path, output_dir):
        """Hàm này được gọi từ nút bấm ở GeneralTab"""
        # Lock UI
        self.general_tab.lock_buttons()
        
        # Gọi Service chạy ngầm
        self.pdf_service.run_batch(
            file_path, 
            output_dir, 
            self.config_manager.get_positions(),
            on_progress=self.update_progress_bar,
            on_finish=self.on_export_finished
        )

    def update_progress_bar(self, current, total):
        # Update UI an toàn
        percent = (current / total) * 100
        self.general_tab.progress_var.set(percent)

    def on_export_finished(self, status):
        # Unlock UI và thông báo
        self.general_tab.unlock_buttons()
        messagebox.showinfo("Xong", status)
```