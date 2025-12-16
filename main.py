# -*- coding: utf-8 -*-
"""
Ứng dụng in lá phái quy y - Entry Point (Refactored)
"""

import tkinter as tk
from tkinter import ttk
import time


def show_splash_screen():
    """Hiển thị splash screen trong 1.5 giây rồi đóng hoàn toàn"""
    splash = tk.Tk()
    splash.overrideredirect(True)  # Bỏ title bar
    
    # Kích thước và vị trí giữa màn hình
    width = 400
    height = 200
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    splash.geometry(f"{width}x{height}+{x}+{y}")
    
    # Background
    splash.configure(bg="#2c3e50")
    
    # Main frame
    frame = tk.Frame(splash, bg="#2c3e50")
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Title
    tk.Label(
        frame,
        text="☸️ QUY Y PRINT",
        font=("Arial", 24, "bold"),
        bg="#2c3e50",
        fg="#ecf0f1"
    ).pack(pady=(20, 5))
    
    # Subtitle
    tk.Label(
        frame,
        text="Ứng Dụng In Lá Phái Quy Y",
        font=("Arial", 12),
        bg="#2c3e50",
        fg="#bdc3c7"
    ).pack(pady=(0, 20))
    
    # Status label
    tk.Label(
        frame,
        text="Đang khởi tạo...",
        font=("Arial", 10),
        bg="#2c3e50",
        fg="#3498db"
    ).pack(pady=(10, 5))
    
    # Progress bar
    style = ttk.Style()
    style.configure("Splash.Horizontal.TProgressbar", 
                   troughcolor='#34495e', 
                   background='#3498db')
    
    progress = ttk.Progressbar(
        frame,
        style="Splash.Horizontal.TProgressbar",
        mode='indeterminate',
        length=300
    )
    progress.pack(pady=(5, 10))
    progress.start(10)
    
    # Version
    tk.Label(
        frame,
        text="v2.0",
        font=("Arial", 8),
        bg="#2c3e50",
        fg="#7f8c8d"
    ).pack(side=tk.BOTTOM)
    
    # Hiển thị và chờ 1.5 giây
    splash.update()
    time.sleep(1.5)
    
    # Đóng hoàn toàn splash
    progress.stop()
    splash.destroy()


def main():
    """Hàm main - khởi động ứng dụng"""
    # Hiển thị splash screen trước (độc lập)
    show_splash_screen()
    
    # Sau khi splash đóng, bắt đầu load main app từ đầu
    print("[Main] Đang khởi tạo resources...")
    
    from core.resource_manager import ensure_all_resources
    extracted = ensure_all_resources()
    for name, path in extracted:
        print(f"  - {name}: {path}")
    
    from ui.main_window import MainWindow
    
    # Tạo main window mới hoàn toàn
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
