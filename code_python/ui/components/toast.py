# -*- coding: utf-8 -*-
"""
Toast Notification - Thông báo tự động ẩn sau vài giây
"""

import tkinter as tk


class ToastNotification:
    """Toast notification tự động ẩn sau một khoảng thời gian"""
    
    @staticmethod
    def show(parent, message, duration=3000, bg_color="#27ae60", fg_color="white", position="top"):
        """
        Hiển thị thông báo toast
        
        Args:
            parent: Widget cha
            message: Nội dung thông báo
            duration: Thời gian hiển thị (ms), mặc định 3000ms = 3 giây
            bg_color: Màu nền
            fg_color: Màu chữ
            position: Vị trí ("top" hoặc "bottom")
        """
        # Tạo frame toast
        toast = tk.Frame(parent, bg=bg_color, padx=15, pady=8)
        
        # Label thông báo
        lbl = tk.Label(
            toast, 
            text=message, 
            font=("Arial", 10, "bold"),
            bg=bg_color, 
            fg=fg_color
        )
        lbl.pack()
        
        # Đặt vị trí
        if position == "top":
            toast.place(relx=0.5, y=10, anchor=tk.N)
        else:
            toast.place(relx=0.5, rely=1.0, y=-10, anchor=tk.S)
        
        # Raise to top
        toast.lift()
        
        # Tự động ẩn sau duration ms
        parent.after(duration, lambda: toast.destroy())
        
        return toast
    
    @staticmethod
    def success(parent, message, duration=3000):
        """Thông báo thành công (màu xanh lá)"""
        return ToastNotification.show(parent, f"✅ {message}", duration, bg_color="#27ae60", fg_color="white")
    
    @staticmethod
    def info(parent, message, duration=3000):
        """Thông báo thông tin (màu xanh dương)"""
        return ToastNotification.show(parent, f"ℹ️ {message}", duration, bg_color="#3498db", fg_color="white")
    
    @staticmethod
    def warning(parent, message, duration=3000):
        """Thông báo cảnh báo (màu vàng)"""
        return ToastNotification.show(parent, f"⚠️ {message}", duration, bg_color="#f39c12", fg_color="white")
    
    @staticmethod
    def error(parent, message, duration=5000):
        """Thông báo lỗi (màu đỏ) - hiển thị lâu hơn"""
        return ToastNotification.show(parent, f"❌ {message}", duration, bg_color="#e74c3c", fg_color="white")
