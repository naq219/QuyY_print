# -*- coding: utf-8 -*-
"""
Ứng dụng in lá phái quy y - Entry Point (Refactored)
"""

import tkinter as tk
import sys


def main():
    """Hàm main - khởi động ứng dụng"""
    
    # 1. Hiển thị màn hình chọn cấu hình (thay vì splash screen)
    from ui.config_chooser import ConfigChooser
    chooser = ConfigChooser()
    result = chooser.run()
    
    # Nếu user đóng cửa sổ -> thoát app
    if result is None:
        print("[Main] User đã thoát.")
        sys.exit(0)
    
    config_path, is_new = result
    print(f"[Main] Config: path={config_path}, is_new={is_new}")
    
    # 2. Load resources
    print("[Main] Đang khởi tạo resources...")
    from core.resource_manager import ensure_all_resources
    extracted = ensure_all_resources()
    for name, path in extracted:
        print(f"  - {name}: {path}")
    
    # 3. Khởi tạo main window với config đã chọn
    from ui.main_window import MainWindow
    
    root = tk.Tk()
    app = MainWindow(root, config_path=config_path)
    root.mainloop()


if __name__ == "__main__":
    main()
