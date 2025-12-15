# -*- coding: utf-8 -*-
"""
Ứng dụng in lá phái quy y
GUI với Tkinter - Phiên bản có điều chỉnh tọa độ và custom fields
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import threading
import json
import copy
import pandas as pd
from pdf_generator import PDFGenerator
from config import FIELD_POSITIONS, CUSTOM_FIELDS, EXCEL_FIELD_MAPPING
import platform

# File lưu cấu hình
CONFIG_FILE = "field_config.json"


class QuyYPrinterApp:
    """Ứng dụng in lá phái quy y với điều chỉnh tọa độ"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng dụng In Lá Phái Quy Y - v2.0")
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        
        # Variables
        self.excel_path = tk.StringVar()
        self.output_dir = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Desktop", "QuyY_Output"))
        self.record_count = tk.StringVar(value="0 bản ghi")
        self.status_text = tk.StringVar(value="Sẵn sàng")
        
        # Export mode: "multiple" = nhiều file, "single" = 1 file nhiều trang
        self.export_mode = tk.StringVar(value="multiple")
        
        # Field positions (editable copy)
        self.field_positions = copy.deepcopy(FIELD_POSITIONS)
        self.custom_fields = copy.deepcopy(CUSTOM_FIELDS)
        self.excel_mapping = copy.deepcopy(EXCEL_FIELD_MAPPING)
        
        # Load saved config if exists
        self._load_config()
        
        # PDF Generator
        self.pdf_generator = PDFGenerator()
        
        # Build GUI
        self._build_gui()
        
        # Populate field table
        self._refresh_field_table()
        self._refresh_custom_table()
        
    def _build_gui(self):
        """Xây dựng giao diện"""
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="ỨNG DỤNG IN LÁ PHÁI QUY Y - v2.0",
            font=("Arial", 16, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=15)
        
        # Main content with Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Main (file selection & actions)
        main_tab = tk.Frame(self.notebook)
        self.notebook.add(main_tab, text="📁 Chính")
        self._build_main_tab(main_tab)
        
        # Tab 2: Coordinate adjustment
        coord_tab = tk.Frame(self.notebook)
        self.notebook.add(coord_tab, text="📐 Tọa Độ")
        self._build_coord_tab(coord_tab)
        
        # Tab 3: Custom fields
        custom_tab = tk.Frame(self.notebook)
        self.notebook.add(custom_tab, text="✏️ Custom Fields")
        self._build_custom_tab(custom_tab)
        
        # Status bar
        status_frame = tk.Frame(self.root, bg="#ecf0f1", height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        tk.Label(
            status_frame,
            textvariable=self.status_text,
            font=("Arial", 9),
            bg="#ecf0f1",
            anchor=tk.W,
            padx=10
        ).pack(fill=tk.BOTH)
    
    def _build_main_tab(self, parent):
        """Tab chính: chọn file và thao tác"""
        content_frame = tk.Frame(parent, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # File Excel selection
        excel_frame = tk.LabelFrame(content_frame, text="1. Chọn File Excel", font=("Arial", 11, "bold"), padx=10, pady=10)
        excel_frame.pack(fill=tk.X, pady=(0, 15))
        
        excel_path_frame = tk.Frame(excel_frame)
        excel_path_frame.pack(fill=tk.X)
        
        tk.Entry(
            excel_path_frame,
            textvariable=self.excel_path,
            font=("Arial", 10),
            state="readonly"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Button(
            excel_path_frame,
            text="Chọn File",
            command=self._browse_excel,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            cursor="hand2"
        ).pack(side=tk.RIGHT)
        
        # Record count
        tk.Label(
            excel_frame,
            textvariable=self.record_count,
            font=("Arial", 10),
            fg="#27ae60"
        ).pack(anchor=tk.W, pady=(10, 0))
        
        # Output directory
        output_frame = tk.LabelFrame(content_frame, text="2. Thư Mục Lưu PDF", font=("Arial", 11, "bold"), padx=10, pady=10)
        output_frame.pack(fill=tk.X, pady=(0, 15))
        
        output_path_frame = tk.Frame(output_frame)
        output_path_frame.pack(fill=tk.X)
        
        tk.Entry(
            output_path_frame,
            textvariable=self.output_dir,
            font=("Arial", 10)
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Button(
            output_path_frame,
            text="Chọn Thư Mục",
            command=self._browse_output,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            cursor="hand2"
        ).pack(side=tk.RIGHT)
        
        # Export mode options
        export_mode_frame = tk.LabelFrame(content_frame, text="3. Chế Độ Xuất PDF", font=("Arial", 11, "bold"), padx=10, pady=10)
        export_mode_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Radiobutton(
            export_mode_frame,
            text="📄 Nhiều file PDF (mỗi bản ghi một file riêng)",
            variable=self.export_mode,
            value="multiple",
            font=("Arial", 10)
        ).pack(anchor=tk.W)
        
        tk.Radiobutton(
            export_mode_frame,
            text="📚 Một file PDF (tất cả bản ghi trong một file, mỗi bản ghi một trang)",
            variable=self.export_mode,
            value="single",
            font=("Arial", 10)
        ).pack(anchor=tk.W)
        
        # Info box
        info_frame = tk.LabelFrame(content_frame, text="📋 Thông tin", font=("Arial", 11, "bold"), padx=10, pady=10)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        info_text = """• PDF được tạo theo hướng NGANG (landscape)
• Chuyển sang tab "Tọa Độ" để điều chỉnh vị trí các trường
• Chuyển sang tab "Custom Fields" để thêm trường tùy chỉnh"""
        
        tk.Label(
            info_frame,
            text=info_text,
            font=("Arial", 10),
            justify=tk.LEFT,
            anchor=tk.W
        ).pack(anchor=tk.W, pady=5)
        
        # Action buttons
        action_frame = tk.Frame(content_frame)
        action_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Button(
            action_frame,
            text="📄 Xuất PDF",
            command=self._export_pdf,
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2,
            cursor="hand2"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Button(
            action_frame,
            text="🖨️ In Trực Tiếp",
            command=self._print_direct,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2,
            cursor="hand2"
        ).pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # Progress bar
        progress_frame = tk.Frame(content_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.pack(fill=tk.X)
    
    def _build_coord_tab(self, parent):
        """Tab điều chỉnh tọa độ"""
        content_frame = tk.Frame(parent, padx=10, pady=10)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        tk.Label(
            content_frame,
            text="Double-click vào ô để chỉnh sửa giá trị. Nhấn Enter để xác nhận.",
            font=("Arial", 10),
            fg="#7f8c8d"
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Treeview for field positions
        columns = ("Field", "X (mm)", "Y (mm)", "Size", "Bold", "Italic", "Align")
        self.field_tree = ttk.Treeview(content_frame, columns=columns, show="headings", height=12)
        
        # Column headers
        for col in columns:
            self.field_tree.heading(col, text=col)
            width = 100 if col == "Field" else 70
            self.field_tree.column(col, width=width, anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=self.field_tree.yview)
        self.field_tree.configure(yscrollcommand=scrollbar.set)
        
        self.field_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click for editing
        self.field_tree.bind("<Double-1>", self._on_field_double_click)
        
        # Buttons frame
        btn_frame = tk.Frame(parent, padx=10, pady=10)
        btn_frame.pack(fill=tk.X)
        
        tk.Button(
            btn_frame,
            text="💾 Lưu Cấu Hình",
            command=self._save_config,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="📂 Load Cấu Hình",
            command=self._load_config_dialog,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🔄 Reset Mặc Định",
            command=self._reset_default,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15
        ).pack(side=tk.LEFT, padx=5)
    
    def _build_custom_tab(self, parent):
        """Tab custom fields"""
        content_frame = tk.Frame(parent, padx=10, pady=10)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        tk.Label(
            content_frame,
            text="Thêm các trường tùy chỉnh với giá trị cố định (ví dụ: user = naq)",
            font=("Arial", 10),
            fg="#7f8c8d"
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Treeview for custom fields
        columns = ("Tên Field", "Giá Trị", "X (mm)", "Y (mm)", "Size", "Align")
        self.custom_tree = ttk.Treeview(content_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.custom_tree.heading(col, text=col)
            width = 100 if col in ("Tên Field", "Giá Trị") else 70
            self.custom_tree.column(col, width=width, anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=self.custom_tree.yview)
        self.custom_tree.configure(yscrollcommand=scrollbar.set)
        
        self.custom_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click for editing
        self.custom_tree.bind("<Double-1>", self._on_custom_double_click)
        
        # Add/Edit/Delete buttons
        btn_frame = tk.Frame(parent, padx=10, pady=10)
        btn_frame.pack(fill=tk.X)
        
        tk.Button(
            btn_frame,
            text="➕ Thêm Field",
            command=self._add_custom_field,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="✏️ Sửa Field",
            command=self._edit_custom_field,
            bg="#f39c12",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🗑️ Xóa Field",
            command=self._delete_custom_field,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="💾 Lưu Cấu Hình",
            command=self._save_config,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15
        ).pack(side=tk.RIGHT, padx=5)
    
    def _refresh_field_table(self):
        """Refresh field positions table"""
        # Clear existing
        for item in self.field_tree.get_children():
            self.field_tree.delete(item)
        
        # Add fields
        for field_name, field_config in self.field_positions.items():
            self.field_tree.insert("", tk.END, iid=field_name, values=(
                field_name,
                field_config.get("x", 0),
                field_config.get("y", 0),
                field_config.get("size", 12),
                "✓" if field_config.get("bold", False) else "",
                "✓" if field_config.get("italic", False) else "",
                field_config.get("align", "L")
            ))
    
    def _refresh_custom_table(self):
        """Refresh custom fields table"""
        # Clear existing
        for item in self.custom_tree.get_children():
            self.custom_tree.delete(item)
        
        # Add custom fields
        for field_name, field_config in self.custom_fields.items():
            self.custom_tree.insert("", tk.END, iid=field_name, values=(
                field_name,
                field_config.get("value", ""),
                field_config.get("x", 0),
                field_config.get("y", 0),
                field_config.get("size", 12),
                field_config.get("align", "L")
            ))
    
    def _on_field_double_click(self, event):
        """Handle double-click on field tree"""
        item = self.field_tree.selection()
        if not item:
            return
        
        field_name = item[0]
        column = self.field_tree.identify_column(event.x)
        col_index = int(column[1:]) - 1
        
        if col_index == 0:  # Field name - not editable
            return
        
        # Get current value
        values = self.field_tree.item(field_name, "values")
        current_value = values[col_index]
        
        # Column names
        col_names = ["Field", "x", "y", "size", "bold", "italic", "align"]
        col_key = col_names[col_index]
        
        if col_key in ("bold", "italic"):
            # Toggle boolean
            new_value = not self.field_positions[field_name].get(col_key, False)
            self.field_positions[field_name][col_key] = new_value
        elif col_key == "align":
            # Cycle through L, C, R
            aligns = ["L", "C", "R"]
            current = self.field_positions[field_name].get("align", "L")
            idx = aligns.index(current) if current in aligns else 0
            new_value = aligns[(idx + 1) % 3]
            self.field_positions[field_name]["align"] = new_value
        else:
            # Prompt for new value
            new_value = simpledialog.askfloat(
                "Chỉnh sửa",
                f"Nhập giá trị mới cho {col_key} của {field_name}:",
                initialvalue=float(current_value) if current_value else 0
            )
            if new_value is not None:
                if col_key == "size":
                    self.field_positions[field_name][col_key] = int(new_value)
                else:
                    self.field_positions[field_name][col_key] = new_value
        
        self._refresh_field_table()
        self.status_text.set(f"Đã cập nhật {field_name}.{col_key}")
    
    def _on_custom_double_click(self, event):
        """Handle double-click on custom field tree"""
        item = self.custom_tree.selection()
        if not item:
            return
        
        field_name = item[0]
        column = self.custom_tree.identify_column(event.x)
        col_index = int(column[1:]) - 1
        
        if col_index == 0:  # Field name - not editable directly
            return
        
        # Get current value
        values = self.custom_tree.item(field_name, "values")
        current_value = values[col_index]
        
        # Column keys
        col_keys = ["name", "value", "x", "y", "size", "align"]
        col_key = col_keys[col_index]
        
        if col_key == "align":
            # Cycle through L, C, R
            aligns = ["L", "C", "R"]
            current = self.custom_fields[field_name].get("align", "L")
            idx = aligns.index(current) if current in aligns else 0
            new_value = aligns[(idx + 1) % 3]
            self.custom_fields[field_name]["align"] = new_value
        elif col_key == "value":
            new_value = simpledialog.askstring(
                "Chỉnh sửa",
                f"Nhập giá trị mới cho {field_name}:",
                initialvalue=current_value
            )
            if new_value is not None:
                self.custom_fields[field_name]["value"] = new_value
        else:
            new_value = simpledialog.askfloat(
                "Chỉnh sửa",
                f"Nhập giá trị mới cho {col_key} của {field_name}:",
                initialvalue=float(current_value) if current_value else 0
            )
            if new_value is not None:
                if col_key == "size":
                    self.custom_fields[field_name][col_key] = int(new_value)
                else:
                    self.custom_fields[field_name][col_key] = new_value
        
        self._refresh_custom_table()
        self.status_text.set(f"Đã cập nhật custom field: {field_name}")
    
    def _add_custom_field(self):
        """Add a new custom field"""
        # Dialog to get field info
        dialog = CustomFieldDialog(self.root, "Thêm Custom Field")
        if dialog.result:
            name, value, x, y, size, align = dialog.result
            if name in self.custom_fields:
                messagebox.showwarning("Cảnh báo", f"Field '{name}' đã tồn tại!")
                return
            
            self.custom_fields[name] = {
                "value": value,
                "x": float(x),
                "y": float(y),
                "size": int(size),
                "bold": False,
                "italic": False,
                "align": align
            }
            self._refresh_custom_table()
            self.status_text.set(f"Đã thêm custom field: {name}")
    
    def _edit_custom_field(self):
        """Edit selected custom field"""
        item = self.custom_tree.selection()
        if not item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn field cần sửa!")
            return
        
        field_name = item[0]
        field_config = self.custom_fields[field_name]
        
        dialog = CustomFieldDialog(
            self.root,
            "Sửa Custom Field",
            initial=(
                field_name,
                field_config.get("value", ""),
                field_config.get("x", 0),
                field_config.get("y", 0),
                field_config.get("size", 12),
                field_config.get("align", "L")
            )
        )
        
        if dialog.result:
            name, value, x, y, size, align = dialog.result
            
            # If name changed, delete old and create new
            if name != field_name:
                del self.custom_fields[field_name]
            
            self.custom_fields[name] = {
                "value": value,
                "x": float(x),
                "y": float(y),
                "size": int(size),
                "bold": False,
                "italic": False,
                "align": align
            }
            self._refresh_custom_table()
            self.status_text.set(f"Đã cập nhật custom field: {name}")
    
    def _delete_custom_field(self):
        """Delete selected custom field"""
        item = self.custom_tree.selection()
        if not item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn field cần xóa!")
            return
        
        field_name = item[0]
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa field '{field_name}'?"):
            del self.custom_fields[field_name]
            self._refresh_custom_table()
            self.status_text.set(f"Đã xóa custom field: {field_name}")
    
    def _save_config(self):
        """Save configuration to JSON file"""
        config = {
            "field_positions": self.field_positions,
            "custom_fields": self.custom_fields,
            "excel_mapping": self.excel_mapping
        }
        
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Thành công", f"Đã lưu cấu hình vào {CONFIG_FILE}")
            self.status_text.set(f"Đã lưu cấu hình: {CONFIG_FILE}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu cấu hình:\n{str(e)}")
    
    def _load_config(self):
        """Load configuration from JSON file"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                if "field_positions" in config:
                    self.field_positions = config["field_positions"]
                if "custom_fields" in config:
                    self.custom_fields = config["custom_fields"]
                if "excel_mapping" in config:
                    self.excel_mapping = config["excel_mapping"]
                
                return True
            except Exception as e:
                print(f"Lỗi khi load config: {e}")
        return False
    
    def _load_config_dialog(self):
        """Load configuration from file dialog"""
        filename = filedialog.askopenfilename(
            title="Chọn file cấu hình",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                if "field_positions" in config:
                    self.field_positions = config["field_positions"]
                if "custom_fields" in config:
                    self.custom_fields = config["custom_fields"]
                if "excel_mapping" in config:
                    self.excel_mapping = config["excel_mapping"]
                
                self._refresh_field_table()
                self._refresh_custom_table()
                messagebox.showinfo("Thành công", f"Đã load cấu hình từ {filename}")
                self.status_text.set(f"Đã load cấu hình: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể load cấu hình:\n{str(e)}")
    
    def _reset_default(self):
        """Reset to default configuration"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn reset về mặc định?\nTất cả thay đổi sẽ bị mất!"):
            self.field_positions = copy.deepcopy(FIELD_POSITIONS)
            self.custom_fields = copy.deepcopy(CUSTOM_FIELDS)
            self.excel_mapping = copy.deepcopy(EXCEL_FIELD_MAPPING)
            self._refresh_field_table()
            self._refresh_custom_table()
            self.status_text.set("Đã reset về cấu hình mặc định")
    
    def _browse_excel(self):
        """Chọn file Excel"""
        filename = filedialog.askopenfilename(
            title="Chọn file Excel",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        if filename:
            self.excel_path.set(filename)
            self._load_excel_preview(filename)
    
    def _load_excel_preview(self, filepath):
        """Load và hiển thị thông tin preview từ Excel"""
        try:
            df = pd.read_excel(filepath)
            # Lọc bỏ dòng header
            df = df[df['hovaten'].notna()]
            count = len(df)
            self.record_count.set(f"{count} bản ghi")
            self.status_text.set(f"Đã load file: {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc file Excel:\n{str(e)}")
            self.record_count.set("0 bản ghi")
    
    def _browse_output(self):
        """Chọn thư mục output"""
        dirname = filedialog.askdirectory(title="Chọn thư mục lưu PDF")
        if dirname:
            self.output_dir.set(dirname)
    
    def _export_pdf(self):
        """Xuất PDF hàng loạt"""
        if not self.excel_path.get():
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file Excel!")
            return
        
        if not self.output_dir.get():
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn thư mục lưu PDF!")
            return
        
        # Confirm
        if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xuất tất cả PDF?"):
            return
        
        # Chạy trong thread riêng để không block GUI
        thread = threading.Thread(target=self._do_export_pdf)
        thread.daemon = True
        thread.start()
    
    def _do_export_pdf(self):
        """Thực hiện xuất PDF (chạy trong thread riêng)"""
        try:
            self.status_text.set("Đang xuất PDF...")
            self.progress['value'] = 0
            
            def progress_callback(current, total):
                progress_percent = (current / total) * 100
                self.progress['value'] = progress_percent
                self.status_text.set(f"Đang xử lý: {current}/{total}")
                self.root.update_idletasks()
            
            export_mode = self.export_mode.get()
            
            if export_mode == "single":
                # Tạo 1 file PDF với nhiều trang
                success, error, errors = self._create_merged_pdf_with_config(
                    self.excel_path.get(),
                    self.output_dir.get(),
                    progress_callback
                )
                
                # Hiển thị kết quả
                message = f"Hoàn thành!\n\nĐã tạo 1 file PDF với {success} trang"
                if error > 0:
                    message += f"\nLỗi: {error} bản ghi"
                if errors:
                    message += f"\n\nChi tiết lỗi:\n" + "\n".join(errors[:5])
                    if len(errors) > 5:
                        message += f"\n... và {len(errors) - 5} lỗi khác"
                
                messagebox.showinfo("Kết quả", message)
                self.status_text.set(f"Hoàn thành: 1 file PDF với {success} trang")
            else:
                # Tạo nhiều file PDF
                success, error, errors = self._create_batch_pdf_with_config(
                    self.excel_path.get(),
                    self.output_dir.get(),
                    progress_callback
                )
                
                # Hiển thị kết quả
                message = f"Hoàn thành!\n\nThành công: {success} file\nLỗi: {error} file"
                if errors:
                    message += f"\n\nChi tiết lỗi:\n" + "\n".join(errors[:5])
                    if len(errors) > 5:
                        message += f"\n... và {len(errors) - 5} lỗi khác"
                
                messagebox.showinfo("Kết quả", message)
                self.status_text.set(f"Hoàn thành: {success} file thành công, {error} file lỗi")
            
            # Mở thư mục output
            if success > 0:
                if platform.system() == 'Windows':
                    os.startfile(self.output_dir.get())
                elif platform.system() == 'Darwin':  # macOS
                    os.system(f'open "{self.output_dir.get()}"')
                else:  # Linux
                    os.system(f'xdg-open "{self.output_dir.get()}"')
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi:\n{str(e)}")
            self.status_text.set("Lỗi khi xuất PDF")
        finally:
            self.progress['value'] = 0
    
    def _create_batch_pdf_with_config(self, excel_path, output_dir, progress_callback=None):
        """Create batch PDF with custom configuration"""
        from lunar_converter import LunarConverter
        
        # Đọc Excel
        df = pd.read_excel(excel_path)
        df = df[df['hovaten'].notna()]
        
        success_count = 0
        error_count = 0
        errors = []
        total = len(df)
        
        os.makedirs(output_dir, exist_ok=True)
        
        for idx, row in df.iterrows():
            try:
                # Chuẩn bị dữ liệu
                data = self._prepare_data(row)
                
                # Tạo tên file
                ho_ten = str(row.get('hovaten', f'person_{idx}')).strip()
                safe_filename = "".join(c for c in ho_ten if c.isalnum() or c in (' ', '_')).strip()
                output_path = os.path.join(output_dir, f"{safe_filename}_{idx}.pdf")
                
                # Tạo PDF với custom config
                self.pdf_generator.create_single_pdf(
                    data, 
                    output_path, 
                    field_positions=self.field_positions,
                    custom_fields=self.custom_fields
                )
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f"Dòng {idx}: {str(e)}")
            
            if progress_callback:
                progress_callback(idx + 1, total)
        
        return success_count, error_count, errors
    
    def _create_merged_pdf_with_config(self, excel_path, output_dir, progress_callback=None):
        """Create single PDF with multiple pages from Excel data"""
        from lunar_converter import LunarConverter
        
        # Đọc Excel
        df = pd.read_excel(excel_path)
        df = df[df['hovaten'].notna()]
        
        success_count = 0
        error_count = 0
        errors = []
        data_list = []
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Chuẩn bị dữ liệu cho tất cả bản ghi
        for idx, row in df.iterrows():
            try:
                data = self._prepare_data(row)
                data_list.append(data)
            except Exception as e:
                error_count += 1
                errors.append(f"Dòng {idx}: {str(e)}")
        
        if data_list:
            try:
                # Tạo tên file PDF merged
                output_path = os.path.join(output_dir, "QuyY_TatCa.pdf")
                
                # Tạo PDF với nhiều trang
                page_count = self.pdf_generator.create_merged_pdf(
                    data_list,
                    output_path,
                    field_positions=self.field_positions,
                    custom_fields=self.custom_fields,
                    progress_callback=progress_callback
                )
                success_count = page_count
            except Exception as e:
                error_count += len(data_list)
                errors.append(f"Lỗi tạo PDF: {str(e)}")
        
        return success_count, error_count, errors
    
    def _prepare_data(self, row):
        """Prepare data from Excel row"""
        from lunar_converter import LunarConverter
        
        phap_danh = row.get('phapdanh')
        ho_ten = row.get('hovaten', '')
        nam_sinh = row.get('namsinh', '')
        dia_chi = row.get('diachithuongtru_short', '')
        ngay_quy_y = row.get('dauthoigian', '')
        
        if pd.isna(phap_danh) or str(phap_danh).strip() == '':
            phap_danh = ""
        
        if ngay_quy_y and not pd.isna(ngay_quy_y):
            date_info = LunarConverter.convert_date(str(ngay_quy_y))
        else:
            date_info = {
                'solar_day': '', 'solar_month': '', 'solar_year': '',
                'lunar_day': '', 'lunar_month': '', 'lunar_year': '',
                'buddhist_year': ''
            }
        
        return {
            "phap_danh": phap_danh,
            "ho_ten": ho_ten if not phap_danh else "",
            "sinh_nam": str(nam_sinh) if not pd.isna(nam_sinh) else "",
            "dia_chi": str(dia_chi) if not pd.isna(dia_chi) else "",
            "ngay_duong": str(date_info['solar_day']) if date_info['solar_day'] else "",
            "thang_duong": str(date_info['solar_month']) if date_info['solar_month'] else "",
            "nam_duong": str(date_info['solar_year']) if date_info['solar_year'] else "",
            "ngay_am": str(date_info['lunar_day']) if date_info['lunar_day'] else "",
            "thang_am": str(date_info['lunar_month']) if date_info['lunar_month'] else "",
            "nam_am": str(date_info['lunar_year']) if date_info['lunar_year'] else "",
            "phat_lich": str(date_info['buddhist_year']) if date_info['buddhist_year'] else ""
        }
    
    def _print_direct(self):
        """In trực tiếp ra máy in"""
        if not self.excel_path.get():
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file Excel!")
            return
        
        # Tạo PDF tạm trong temp folder
        import tempfile
        temp_dir = tempfile.mkdtemp()
        
        # Confirm
        if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn in tất cả?"):
            return
        
        # Chạy trong thread riêng
        thread = threading.Thread(target=self._do_print_direct, args=(temp_dir,))
        thread.daemon = True
        thread.start()
    
    def _do_print_direct(self, temp_dir):
        """Thực hiện in trực tiếp (chạy trong thread riêng)"""
        try:
            self.status_text.set("Đang tạo PDF và in...")
            self.progress['value'] = 0
            
            def progress_callback(current, total):
                progress_percent = (current / total) * 100
                self.progress['value'] = progress_percent
                self.status_text.set(f"Đang in: {current}/{total}")
                self.root.update_idletasks()
            
            # Tạo PDF
            success, error, errors = self._create_batch_pdf_with_config(
                self.excel_path.get(),
                temp_dir,
                progress_callback
            )
            
            # In từng file PDF
            if success > 0:
                import glob
                pdf_files = glob.glob(os.path.join(temp_dir, "*.pdf"))
                
                for pdf_file in pdf_files:
                    self._print_pdf_file(pdf_file)
                
                messagebox.showinfo("Hoàn thành", f"Đã gửi {len(pdf_files)} file đến máy in!")
            else:
                messagebox.showwarning("Cảnh báo", "Không có file nào được tạo!")
            
            self.status_text.set(f"Hoàn thành in: {success} file")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi in:\n{str(e)}")
            self.status_text.set("Lỗi khi in")
        finally:
            self.progress['value'] = 0
            # Xóa temp folder
            import shutil
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
    
    def _print_pdf_file(self, pdf_path):
        """In một file PDF"""
        system = platform.system()
        
        try:
            if system == 'Windows':
                import win32api
                import win32print
                
                printer_name = win32print.GetDefaultPrinter()
                win32api.ShellExecute(
                    0,
                    "print",
                    pdf_path,
                    f'/d:"{printer_name}"',
                    ".",
                    0
                )
            elif system == 'Darwin':  # macOS
                os.system(f'lpr "{pdf_path}"')
            else:  # Linux
                os.system(f'lp "{pdf_path}"')
        except Exception as e:
            print(f"Lỗi khi in file {pdf_path}: {e}")


class CustomFieldDialog(simpledialog.Dialog):
    """Dialog for adding/editing custom field"""
    
    def __init__(self, parent, title, initial=None):
        self.initial = initial
        self.result = None
        super().__init__(parent, title)
    
    def body(self, master):
        # Name
        tk.Label(master, text="Tên Field:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_entry = tk.Entry(master, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Value
        tk.Label(master, text="Giá trị:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.value_entry = tk.Entry(master, width=30)
        self.value_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # X
        tk.Label(master, text="X (mm):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.x_entry = tk.Entry(master, width=30)
        self.x_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Y
        tk.Label(master, text="Y (mm):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.y_entry = tk.Entry(master, width=30)
        self.y_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Size
        tk.Label(master, text="Cỡ chữ:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.size_entry = tk.Entry(master, width=30)
        self.size_entry.grid(row=4, column=1, padx=5, pady=5)
        
        # Align
        tk.Label(master, text="Căn lề:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.align_var = tk.StringVar(value="L")
        align_frame = tk.Frame(master)
        align_frame.grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        tk.Radiobutton(align_frame, text="Trái", variable=self.align_var, value="L").pack(side=tk.LEFT)
        tk.Radiobutton(align_frame, text="Giữa", variable=self.align_var, value="C").pack(side=tk.LEFT)
        tk.Radiobutton(align_frame, text="Phải", variable=self.align_var, value="R").pack(side=tk.LEFT)
        
        # Set initial values if editing
        if self.initial:
            name, value, x, y, size, align = self.initial
            self.name_entry.insert(0, name)
            self.value_entry.insert(0, value)
            self.x_entry.insert(0, str(x))
            self.y_entry.insert(0, str(y))
            self.size_entry.insert(0, str(size))
            self.align_var.set(align)
        else:
            # Defaults
            self.x_entry.insert(0, "50")
            self.y_entry.insert(0, "100")
            self.size_entry.insert(0, "12")
        
        return self.name_entry
    
    def apply(self):
        try:
            name = self.name_entry.get().strip()
            value = self.value_entry.get().strip()
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
            size = int(self.size_entry.get())
            align = self.align_var.get()
            
            if not name:
                messagebox.showerror("Lỗi", "Tên field không được để trống!")
                return
            
            self.result = (name, value, x, y, size, align)
        except ValueError as e:
            messagebox.showerror("Lỗi", f"Giá trị không hợp lệ: {e}")


def main():
    """Hàm main"""
    root = tk.Tk()
    app = QuyYPrinterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
