# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk

class SettingsTab(tk.Frame):
    """Tab Cài đặt - Chứa các tùy chọn xuất PDF và font"""
    
    def __init__(self, parent, config_manager, mode_var, status_var):
        super().__init__(parent)
        self.config_manager = config_manager
        self.mode_var = mode_var
        self.status_var = status_var
        
        # VNI font variable
        self.use_vni_var = tk.BooleanVar(value=getattr(self.config_manager, "use_vni_font", True))
        self.use_vni_var.trace("w", self._on_vni_change)
        
        self._build_ui()
        
    def _build_ui(self):
        content_frame = tk.Frame(self, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(
            content_frame, 
            text="⚙️ Cài Đặt Ứng Dụng", 
            font=("Arial", 16, "bold"),
            fg="#2c3e50"
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # 1. Chế độ xuất PDF
        self._build_section(content_frame, "📄 Chế Độ Xuất PDF")
        
        tk.Radiobutton(
            self.last_section, 
            text="📄 Nhiều file PDF (riêng lẻ) - Mỗi người một file", 
            variable=self.mode_var, 
            value="multiple",
            font=("Arial", 10)
        ).pack(anchor=tk.W, pady=2)
        
        tk.Radiobutton(
            self.last_section, 
            text="📚 Một file PDF (gộp trang) - Tất cả trong 1 file", 
            variable=self.mode_var, 
            value="single",
            font=("Arial", 10)
        ).pack(anchor=tk.W, pady=2)
        
        # Explain
        tk.Label(
            self.last_section,
            text="• Chọn 'Nhiều file' nếu muốn quản lý từng file riêng\n• Chọn 'Một file' nếu muốn in liên tục hoặc gửi email 1 lần",
            font=("Arial", 9),
            fg="#7f8c8d",
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=(10, 0))
        
        # 2. Cấu hình Font
        self._build_section(content_frame, "🔤 Cấu Hình Font")
        
        tk.Checkbutton(
            self.last_section, 
            text="Chuyển đổi Unicode sang VNI (dùng cho font VNI-Times, VNI-Ariston...)", 
            variable=self.use_vni_var,
            font=("Arial", 10)
        ).pack(anchor=tk.W)
        
        # Explain
        tk.Label(
            self.last_section,
            text="• Bật nếu bạn sử dụng font VNI (phổ biến trong in ấn cổ)\n• Tắt nếu sử dụng font Unicode thông thường",
            font=("Arial", 9),
            fg="#7f8c8d",
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=(10, 0))
        
        # 3. Thông tin PDF
        self._build_section(content_frame, "📐 Thông Tin PDF")
        
        info_items = [
            "• Khổ giấy: A4 (297mm x 210mm)",
            "• Hướng: NGANG (Landscape)",
            "• Tọa độ gốc: Góc trên bên trái",
            "• Chỉnh sửa tọa độ: Tab 'Tọa Độ'",
            "• Thêm field tùy chỉnh: Tab 'Custom Fields'"
        ]
        
        for item in info_items:
            tk.Label(
                self.last_section,
                text=item,
                font=("Arial", 10),
                fg="#34495e",
                justify=tk.LEFT
            ).pack(anchor=tk.W, pady=1)

    def _build_section(self, parent, title):
        self.last_section = tk.LabelFrame(parent, text=title, font=("Arial", 11, "bold"), padx=15, pady=15)
        self.last_section.pack(fill=tk.X, pady=(0, 15))
    
    def _on_vni_change(self, *args):
        self.config_manager.use_vni_font = self.use_vni_var.get()
        self.config_manager.mark_dirty()
        self.status_var.set("*Đã thay đổi cấu hình font - Chưa lưu*")
