# -*- coding: utf-8 -*-
"""
Dialog classes cho ứng dụng in lá phái quy y
"""

import tkinter as tk
from tkinter import simpledialog, messagebox


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
