# -*- coding: utf-8 -*-
"""
Ứng dụng in lá phái quy y - Entry Point (Refactored)
"""

import tkinter as tk
from ui.main_window import MainWindow
from core.resource_manager import ensure_all_resources


def main():
    """Hàm main - khởi động ứng dụng"""
    # Extract các file resource cần thiết (phoimau.jpg, quyyfont.ttf)
    # Nếu chạy lần đầu từ exe, các file sẽ được tạo ra ở thư mục exe
    print("[Main] Đang khởi tạo resources...")
    extracted = ensure_all_resources()
    for name, path in extracted:
        print(f"  - {name}: {path}")
    
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()

