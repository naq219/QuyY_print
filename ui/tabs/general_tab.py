# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

class GeneralTab(tk.Frame):
    def __init__(self, parent, excel_var, output_var, count_var, mode_var, on_excel_selected_callback, on_export_callback, on_print_callback):
        super().__init__(parent)
        self.excel_var = excel_var
        self.output_var = output_var
        self.count_var = count_var
        self.mode_var = mode_var
        
        self.on_excel_selected = on_excel_selected_callback
        self.on_export = on_export_callback
        self.on_print = on_print_callback
        
        self._build_ui()
        
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
        
        # 3. Mode
        self._build_section(content_frame, "3. Chế Độ Xuất PDF")
        tk.Radiobutton(self.last_section, text="📄 Nhiều file PDF (riêng lẻ)", variable=self.mode_var, value="multiple").pack(anchor=tk.W)
        tk.Radiobutton(self.last_section, text="📚 Một file PDF (gộp trang)", variable=self.mode_var, value="single").pack(anchor=tk.W)
        
        # Info
        info_frame = tk.LabelFrame(content_frame, text="📋 Thông tin", font=("Arial", 11, "bold"), padx=10, pady=10)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        tk.Label(info_frame, text="• PDF hướng NGANG (Landscape)\n• Chỉnh tọa độ ở tab 'Tọa Độ'", justify=tk.LEFT).pack(anchor=tk.W)
        
        # Actions
        action_frame = tk.Frame(content_frame)
        action_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.btn_export = tk.Button(action_frame, text="📄 Xuất PDF", command=self.on_export, bg="#27ae60", fg="white", font=("Arial", 12, "bold"), height=2)
        self.btn_export.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.btn_print = tk.Button(action_frame, text="🖨️ In Trực Tiếp", command=self.on_print, bg="#e74c3c", fg="white", font=("Arial", 12, "bold"), height=2)
        self.btn_print.pack(side=tk.RIGHT, fill=tk.X, expand=True)

    def _build_section(self, parent, title):
        self.last_section = tk.LabelFrame(parent, text=title, font=("Arial", 11, "bold"), padx=10, pady=10)
        self.last_section.pack(fill=tk.X, pady=(0, 15))

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
