# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from datetime import datetime

# Try to import tkcalendar for better date picker
try:
    from tkcalendar import DateEntry
    HAS_TKCALENDAR = True
except ImportError:
    HAS_TKCALENDAR = False

from core.lunar_converter import LunarConverter
from ui.components.toast import ToastNotification

class GeneralTab(tk.Frame):
    def __init__(self, parent, config_manager, excel_var, output_var, count_var, mode_var, on_excel_selected_callback, on_export_callback, on_print_callback):
        super().__init__(parent)
        self.config_manager = config_manager
        self.excel_var = excel_var
        self.output_var = output_var
        self.count_var = count_var
        self.mode_var = mode_var
        
        self.on_excel_selected = on_excel_selected_callback
        self.on_export = on_export_callback
        self.on_print = on_print_callback
        
        self.use_vni_var = tk.BooleanVar(value=getattr(self.config_manager, "use_vni_font", True))
        self.use_vni_var.trace("w", self._on_vni_change)
        
        # Date variables
        self.date_var = tk.StringVar()
        self.lunar_info_var = tk.StringVar(value="Chưa chọn ngày")
        
        self._build_ui()
        self._load_saved_date()
        
    def _build_ui(self):
        content_frame = tk.Frame(self, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 1. Excel
        self._build_section(content_frame, "1. Chọn File Excel")
        excel_frame = tk.Frame(self.last_section)
        excel_frame.pack(fill=tk.X)
        
        tk.Entry(excel_frame, textvariable=self.excel_var, state="readonly", font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Button(excel_frame, text="Chọn File", command=self._browse_excel, bg="#3498db", fg="white", font=("Arial", 10, "bold")).pack(side=tk.RIGHT)
        
        tk.Label(self.last_section, textvariable=self.count_var, font=("Arial", 10), fg="#27ae60").pack(anchor=tk.W, pady=(10, 0))
        
        # 2. Output
        self._build_section(content_frame, "2. Thư Mục Lưu PDF")
        out_frame = tk.Frame(self.last_section)
        out_frame.pack(fill=tk.X)
        
        tk.Entry(out_frame, textvariable=self.output_var, font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Button(out_frame, text="Chọn Thư Mục", command=self._browse_output, bg="#3498db", fg="white", font=("Arial", 10, "bold")).pack(side=tk.RIGHT)
        
        # 3. Ngày Quy Y 📅
        self._build_section(content_frame, "3. Ngày Quy Y 📅")
        date_frame = tk.Frame(self.last_section)
        date_frame.pack(fill=tk.X)
        
        tk.Label(date_frame, text="Chọn ngày (Dương lịch):", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        if HAS_TKCALENDAR:
            # Use DateEntry if tkcalendar is available
            self.date_entry = DateEntry(
                date_frame,
                width=15,
                background='#3498db',
                foreground='white',
                borderwidth=2,
                date_pattern='yyyy-mm-dd',
                font=("Arial", 10)
            )
            self.date_entry.pack(side=tk.LEFT, padx=(0, 10))
            self.date_entry.bind("<<DateEntrySelected>>", self._on_date_selected)
            # Clear initial date
            self.date_entry.delete(0, tk.END)
        else:
            # Fallback to Entry with format hint
            tk.Label(date_frame, text="(YYYY-MM-DD):", font=("Arial", 9), fg="#7f8c8d").pack(side=tk.LEFT)
            self.date_entry = tk.Entry(date_frame, textvariable=self.date_var, font=("Arial", 10), width=12)
            self.date_entry.pack(side=tk.LEFT, padx=(5, 10))
            self.date_var.trace("w", self._on_date_text_change)
        
        tk.Button(date_frame, text="Áp dụng", command=self._apply_date, bg="#9b59b6", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(date_frame, text="Xóa", command=self._clear_date, bg="#95a5a6", fg="white", font=("Arial", 10)).pack(side=tk.LEFT)
        
        # Lunar calendar display
        lunar_frame = tk.Frame(self.last_section, bg="#f8f9fa", padx=10, pady=8)
        lunar_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Label(lunar_frame, textvariable=self.lunar_info_var, font=("Arial", 10, "bold"), 
                 fg="#2c3e50", bg="#f8f9fa", justify=tk.LEFT, anchor=tk.W).pack(fill=tk.X)
        
        # Actions
        action_frame = tk.Frame(content_frame)
        action_frame.pack(fill=tk.X, pady=(15, 15))
        
        self.btn_export = tk.Button(action_frame, text="📄 Xuất PDF", command=self.on_export, bg="#27ae60", fg="white", font=("Arial", 12, "bold"), height=2)
        self.btn_export.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.btn_print = tk.Button(action_frame, text="🖨️ In Trực Tiếp", command=self.on_print, bg="#e74c3c", fg="white", font=("Arial", 12, "bold"), height=2)
        self.btn_print.pack(side=tk.RIGHT, fill=tk.X, expand=True)

    def _build_section(self, parent, title):
        self.last_section = tk.LabelFrame(parent, text=title, font=("Arial", 11, "bold"), padx=10, pady=10)
        self.last_section.pack(fill=tk.X, pady=(0, 15))

    def _load_saved_date(self):
        """Load ngày đã lưu từ config"""
        saved_date = self.config_manager.get_selected_date()
        if saved_date:
            if HAS_TKCALENDAR:
                try:
                    date_obj = datetime.strptime(saved_date, "%Y-%m-%d")
                    self.date_entry.set_date(date_obj)
                except:
                    pass
            else:
                self.date_var.set(saved_date)
            self._update_lunar_display(saved_date)

    def _on_date_selected(self, event=None):
        """Callback khi chọn ngày từ DateEntry (tkcalendar)"""
        if HAS_TKCALENDAR:
            date_obj = self.date_entry.get_date()
            date_str = date_obj.strftime("%Y-%m-%d")
            self._apply_date_value(date_str)

    def _on_date_text_change(self, *args):
        """Callback khi nhập ngày bằng text (fallback)"""
        # Don't auto-apply, wait for "Áp dụng" button
        pass

    def _apply_date(self):
        """Áp dụng ngày được chọn"""
        if HAS_TKCALENDAR:
            try:
                date_obj = self.date_entry.get_date()
                date_str = date_obj.strftime("%Y-%m-%d")
            except:
                messagebox.showwarning("Lỗi", "Vui lòng chọn ngày hợp lệ!")
                return
        else:
            date_str = self.date_var.get().strip()
            if not date_str:
                messagebox.showwarning("Lỗi", "Vui lòng nhập ngày (định dạng YYYY-MM-DD)!")
                return
            # Validate format
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Lỗi", "Định dạng ngày không hợp lệ!\nVui lòng nhập theo định dạng: YYYY-MM-DD (ví dụ: 2025-12-16)")
                return
        
        self._apply_date_value(date_str)

    def _apply_date_value(self, date_str):
        """Áp dụng giá trị ngày và cập nhật config"""
        try:
            self.config_manager.set_selected_date(date_str)
            self._update_lunar_display(date_str)
            ToastNotification.success(self, f"Đã chọn ngày quy y: {date_str}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể convert ngày: {str(e)}")

    def _update_lunar_display(self, date_str):
        """Cập nhật hiển thị âm lịch và Phật lịch"""
        try:
            date_info = LunarConverter.convert_date(date_str)
            
            solar_text = f"Dương lịch: {date_info['solar_day']}/{date_info['solar_month']}/{date_info['solar_year']}"
            lunar_text = f"Âm lịch: {date_info['lunar_day']}/{date_info['lunar_month']} năm {date_info['lunar_year_name']}"
            buddhist_text = f"Phật lịch: {date_info['buddhist_year']}"
            
            self.lunar_info_var.set(f"✅ {solar_text}  |  🌙 {lunar_text}  |  ☸️ {buddhist_text}")
        except Exception as e:
            self.lunar_info_var.set(f"❌ Lỗi convert: {str(e)}")

    def _clear_date(self):
        """Xóa ngày đã chọn"""
        self.config_manager.set_selected_date(None)
        self.lunar_info_var.set("Chưa chọn ngày")
        if HAS_TKCALENDAR:
            self.date_entry.delete(0, tk.END)
        else:
            self.date_var.set("")
        ToastNotification.info(self, "Đã xóa ngày quy y")

    def _browse_excel(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")])
        if filename:
            self.on_excel_selected(filename)
            
    def _browse_output(self):
        dirname = filedialog.askdirectory()
        if dirname:
            self.output_var.set(dirname)

    def lock_ui(self):
        self.btn_export.config(state="disabled")
        self.btn_print.config(state="disabled")
        
    def unlock_ui(self):
        self.btn_export.config(state="normal")
        self.btn_print.config(state="normal")
        
    def _on_vni_change(self, *args):
        self.config_manager.use_vni_font = self.use_vni_var.get()
        self.config_manager.mark_dirty()
