# -*- coding: utf-8 -*-
"""
Print Preview Window - Cửa sổ xem trước và in từng lá phái
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os
import tempfile

from core.data_processor import DataProcessor
from core.resource_manager import get_app_dir, get_phoimau_path

# Constants - Scale giống CoordinateTab
A4_WIDTH_MM = 297
A4_HEIGHT_MM = 210
SCALE = 2.5
CANVAS_WIDTH = int(A4_WIDTH_MM * SCALE)
CANVAS_HEIGHT = int(A4_HEIGHT_MM * SCALE)


class PrintPreviewWindow(tk.Toplevel):
    """Cửa sổ preview và in lá phái"""
    
    def __init__(self, parent, df, config_manager, pdf_service):
        super().__init__(parent)
        self.df = df
        self.config_manager = config_manager
        self.pdf_service = pdf_service
        
        self.current_index = 0
        self.total_records = len(df)
        self.processed_data = []  # Cache processed data
        
        # Window setup
        self.title("Preview Lá Phái Quy Y")
        self.geometry("1100x700")
        self.resizable(True, True)
        
        # Preload data
        self._preprocess_data()
        
        # Build UI
        self._build_ui()
        
        # Load first record
        if self.total_records > 0:
            self._load_record(0)
        
        # Modal-like behavior
        self.transient(parent)
        self.grab_set()
        
    def _preprocess_data(self):
        """Xử lý trước tất cả dữ liệu"""
        for idx, row in self.df.iterrows():
            try:
                data = DataProcessor.process_row(row)
                name = row.get('hovaten', f'Record {idx}')
                self.processed_data.append({
                    'name': str(name),
                    'data': data,
                    'row_index': idx
                })
            except Exception as e:
                print(f"Error processing row {idx}: {e}")
                
    def _build_ui(self):
        # Main container
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - List
        left_frame = tk.Frame(main_frame, width=200)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        tk.Label(left_frame, text="Danh Sách", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        # Listbox with scrollbar
        list_frame = tk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Arial", 10))
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        # Populate listbox
        for i, item in enumerate(self.processed_data):
            self.listbox.insert(tk.END, f"{i+1}. {item['name']}")
            
        self.listbox.bind('<<ListboxSelect>>', self.on_list_select)
        
        # Right panel - Preview
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Canvas
        canvas_frame = tk.Frame(right_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT,
                                bg="#e0e0e0", relief="sunken", borderwidth=1)
        self.canvas.pack(anchor=tk.CENTER)
        
        self._load_background()
        
        # Navigation frame
        nav_frame = tk.Frame(right_frame)
        nav_frame.pack(fill=tk.X, pady=(10, 5))
        
        self.btn_prev = tk.Button(nav_frame, text="◀ Trước", command=self.on_prev,
                                   font=("Arial", 10), width=10)
        self.btn_prev.pack(side=tk.LEFT)
        
        self.lbl_position = tk.Label(nav_frame, text="0 / 0", font=("Arial", 12, "bold"))
        self.lbl_position.pack(side=tk.LEFT, expand=True)
        
        self.btn_next = tk.Button(nav_frame, text="Sau ▶", command=self.on_next,
                                   font=("Arial", 10), width=10)
        self.btn_next.pack(side=tk.RIGHT)
        
        # Action frame
        action_frame = tk.Frame(right_frame)
        action_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.btn_print = tk.Button(action_frame, text="🖨️ In Trang Này", command=self.on_print_current,
                                    font=("Arial", 11, "bold"), bg="#27ae60", fg="white", height=2)
        self.btn_print.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.btn_save = tk.Button(action_frame, text="💾 Lưu PDF", command=self.on_save_pdf,
                                   font=("Arial", 11, "bold"), bg="#3498db", fg="white", height=2)
        self.btn_save.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
    def _load_background(self):
        """Load ảnh phoimau làm background"""
        self.tk_bg_image = None
        
        # Tìm phoimau
        app_dir = get_app_dir()
        found_bg = None
        for ext in [".png", ".jpg", ".jpeg"]:
            path = os.path.join(app_dir, f"phoimau{ext}")
            if os.path.exists(path):
                found_bg = path
                break
                
        if found_bg:
            try:
                img = Image.open(found_bg)
                img = img.resize((CANVAS_WIDTH, CANVAS_HEIGHT), Image.Resampling.LANCZOS)
                self.tk_bg_image = ImageTk.PhotoImage(img)
                self.canvas.create_image(0, 0, image=self.tk_bg_image, anchor=tk.NW, tags="bg")
            except Exception as e:
                print(f"Error loading bg: {e}")
        else:
            self.canvas.create_text(CANVAS_WIDTH//2, CANVAS_HEIGHT//2,
                                     text="Không tìm thấy ảnh phoimau", fill="#999")
                                     
    def _load_record(self, index):
        """Load và hiển thị record tại index"""
        if index < 0 or index >= self.total_records:
            return
            
        self.current_index = index
        self._render_preview()
        self._update_navigation()
        
        # Sync listbox selection
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(index)
        self.listbox.see(index)
        
    def _render_preview(self):
        """Vẽ text lên canvas theo config"""
        self.canvas.delete("field")
        
        if self.current_index >= len(self.processed_data):
            return
            
        record = self.processed_data[self.current_index]
        data = record['data']
        
        # Draw standard fields
        for name, conf in self.config_manager.field_positions.items():
            if name in data and data[name]:
                self._draw_field(name, str(data[name]), conf, is_custom=False)
                
        # Draw custom fields
        for name, conf in self.config_manager.custom_fields.items():
            value = conf.get("value", "")
            if value:
                self._draw_field(name, str(value), conf, is_custom=True)
                
    def _draw_field(self, name, text, conf, is_custom=False):
        """Vẽ một field lên canvas"""
        x_mm = conf.get("x", 0)
        y_mm = conf.get("y", 0)
        size = conf.get("size", 12)
        align = conf.get("align", "L")
        
        x_px = x_mm * SCALE
        y_px = y_mm * SCALE
        
        anchor = tk.SW
        if align == "C": anchor = tk.S
        elif align == "R": anchor = tk.SE
        
        self.canvas.create_text(
            x_px, y_px,
            text=text,
            font=("Arial", int(size * 0.8), "bold" if is_custom else "normal"),
            fill="blue" if not is_custom else "red",
            anchor=anchor,
            tags="field"
        )
        
    def _update_navigation(self):
        """Cập nhật trạng thái navigation"""
        self.lbl_position.config(text=f"{self.current_index + 1} / {self.total_records}")
        self.btn_prev.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if self.current_index < self.total_records - 1 else tk.DISABLED)
        
    def on_prev(self):
        if self.current_index > 0:
            self._load_record(self.current_index - 1)
            
    def on_next(self):
        if self.current_index < self.total_records - 1:
            self._load_record(self.current_index + 1)
            
    def on_list_select(self, event):
        selection = self.listbox.curselection()
        if selection:
            self._load_record(selection[0])
            
    def on_print_current(self):
        """In record hiện tại"""
        if self.current_index >= len(self.processed_data):
            return
            
        record = self.processed_data[self.current_index]
        
        try:
            # Tạo temp PDF
            temp_dir = tempfile.mkdtemp()
            # Use simple ASCII name for temp file to avoid print errors
            import time
            safe_name = f"print_job_{int(time.time()*1000)}"
            temp_path = os.path.join(temp_dir, f"{safe_name}.pdf")
            
            # Generate PDF
            from core.pdf_generator import PDFGenerator
            generator = PDFGenerator()
            generator.create_single_pdf(
                record['data'],
                temp_path,
                field_positions=self.config_manager.field_positions,
                custom_fields=self.config_manager.custom_fields
            )
            
            # Print
            self.pdf_service.print_file(temp_path)
            messagebox.showinfo("Thành công", f"Đã gửi lệnh in cho: {record['name']}")
            
        except Exception as e:
            messagebox.showerror("Lỗi in", str(e))
            
    def on_save_pdf(self):
        """Lưu PDF record hiện tại"""
        if self.current_index >= len(self.processed_data):
            return
            
        record = self.processed_data[self.current_index]
        safe_name = "".join(c for c in record['name'] if c.isalnum() or c in (' ', '_')).strip()
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=f"{safe_name}.pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if not filepath:
            return
            
        try:
            from core.pdf_generator import PDFGenerator
            generator = PDFGenerator()
            generator.create_single_pdf(
                record['data'],
                filepath,
                field_positions=self.config_manager.field_positions,
                custom_fields=self.config_manager.custom_fields
            )
            messagebox.showinfo("Thành công", f"Đã lưu: {filepath}")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
