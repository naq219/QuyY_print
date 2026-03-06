# -*- coding: utf-8 -*-
"""
Config Chooser - Màn hình chọn file cấu hình khi khởi động app
"""

import tkinter as tk
from tkinter import ttk, filedialog
import os
import json


# File lưu đường dẫn config lần trước (nằm cùng thư mục app)
def _get_history_path():
    """Lấy đường dẫn file lưu lịch sử config"""
    from core.resource_manager import get_app_dir
    return os.path.join(get_app_dir(), "info.quyy")


class ConfigChooser:
    """Màn hình chọn file cấu hình khi khởi động app
    
    Returns:
        tuple: (config_path, is_new)
            - config_path: đường dẫn file config đã chọn, hoặc None nếu tạo mới
            - is_new: True nếu tạo mới, False nếu mở file có sẵn
        Hoặc None nếu user đóng cửa sổ (thoát app)
    """
    
    def __init__(self):
        self.result = None  # (config_path, is_new) hoặc None
        self._build()
    
    @staticmethod
    def _load_last_config_dir():
        """Đọc thư mục config lần trước từ file lịch sử"""
        try:
            history_path = _get_history_path()
            if os.path.exists(history_path):
                with open(history_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                last_dir = data.get("last_config_dir", "")
                if last_dir and os.path.isdir(last_dir):
                    return last_dir
        except Exception as e:
            print(f"[ConfigChooser] Lỗi đọc lịch sử: {e}")
        return ""
    
    @staticmethod
    def save_last_config_path(config_path):
        """Lưu thư mục của file config vừa dùng (gọi từ bên ngoài cũng được)"""
        if not config_path:
            return
        try:
            history_path = _get_history_path()
            last_dir = os.path.dirname(os.path.abspath(config_path))
            data = {"last_config_dir": last_dir, "last_config_file": config_path}
            with open(history_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ConfigChooser] Lỗi lưu lịch sử: {e}")
    
    def _build(self):
        self.root = tk.Tk()
        self.root.title("QUY Y PRINT - Chọn Cấu Hình")
        
        # Kích thước và vị trí giữa màn hình
        width = 500
        height = 380
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.resizable(False, False)
        self.root.configure(bg="#2c3e50")
        
        # Xử lý đóng cửa sổ = thoát app
        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # === Header ===
        header_frame = tk.Frame(self.root, bg="#2c3e50")
        header_frame.pack(fill=tk.X, padx=30, pady=(25, 5))
        
        tk.Label(
            header_frame,
            text="☸️ QUY Y PRINT",
            font=("Arial", 22, "bold"),
            bg="#2c3e50",
            fg="#ecf0f1"
        ).pack()
        
        tk.Label(
            header_frame,
            text="Ứng Dụng In Lá Phái Quy Y",
            font=("Arial", 11),
            bg="#2c3e50",
            fg="#bdc3c7"
        ).pack(pady=(2, 0))
        
        tk.Label(
            header_frame,
            text="v2.1",
            font=("Arial", 8),
            bg="#2c3e50",
            fg="#7f8c8d"
        ).pack(pady=(2, 0))
        
        # === Separator ===
        sep = tk.Frame(self.root, bg="#3498db", height=2)
        sep.pack(fill=tk.X, padx=40, pady=(15, 15))
        
        # === Tiêu đề chọn cấu hình ===
        tk.Label(
            self.root,
            text="Chọn cấu hình để bắt đầu:",
            font=("Arial", 12, "bold"),
            bg="#2c3e50",
            fg="#ecf0f1"
        ).pack(pady=(5, 15))
        
        # === Buttons ===
        btn_frame = tk.Frame(self.root, bg="#2c3e50")
        btn_frame.pack(fill=tk.X, padx=50)
        
        # Button: Mở file cấu hình có sẵn
        btn_open = tk.Button(
            btn_frame,
            text="📂  Mở File Cấu Hình Có Sẵn",
            font=("Arial", 13, "bold"),
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            activeforeground="white",
            cursor="hand2",
            height=2,
            relief="flat",
            command=self._on_open
        )
        btn_open.pack(fill=tk.X, pady=(0, 12))
        
        # Button: Tạo mới cấu hình
        btn_new = tk.Button(
            btn_frame,
            text="✨  Tạo Mới Cấu Hình",
            font=("Arial", 13, "bold"),
            bg="#27ae60",
            fg="white",
            activebackground="#219a52",
            activeforeground="white",
            cursor="hand2",
            height=2,
            relief="flat",
            command=self._on_new
        )
        btn_new.pack(fill=tk.X, pady=(0, 12))
        
        # Button: Thoát
        btn_exit = tk.Button(
            btn_frame,
            text="❌  Thoát",
            font=("Arial", 11),
            bg="#7f8c8d",
            fg="white",
            activebackground="#6c7a7d",
            activeforeground="white",
            cursor="hand2",
            height=1,
            relief="flat",
            command=self._on_cancel
        )
        btn_exit.pack(fill=tk.X)
        
        # === Footer ===
        tk.Label(
            self.root,
            text="📞 Liên hệ: Trung Quảng An 0983.838.619",
            font=("Arial", 9),
            bg="#2c3e50",
            fg="#7f8c8d"
        ).pack(side=tk.BOTTOM, pady=(0, 10))
    
    def _on_open(self):
        """User chọn mở file cấu hình có sẵn - mở đúng thư mục lần trước"""
        initial_dir = self._load_last_config_dir()
        
        filepath = filedialog.askopenfilename(
            title="Chọn file cấu hình",
            initialdir=initial_dir if initial_dir else None,
            filetypes=[("JSON Config", "*.json"), ("Tất cả file", "*.*")],
            parent=self.root
        )
        if filepath:
            # Lưu lại thư mục lần này
            self.save_last_config_path(filepath)
            self.result = (filepath, False)
            self.root.destroy()
    
    def _on_new(self):
        """User chọn tạo mới cấu hình"""
        self.result = (None, True)
        self.root.destroy()
    
    def _on_cancel(self):
        """User đóng cửa sổ = thoát app"""
        self.result = None
        self.root.destroy()
    
    def run(self):
        """Chạy dialog và trả về kết quả"""
        self.root.mainloop()
        return self.result

