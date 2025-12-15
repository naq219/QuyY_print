# -*- coding: utf-8 -*-
"""
Ứng dụng in lá phái quy y - Entry Point (Refactored)
"""

import tkinter as tk
from ui.main_window import MainWindow


def main():
    """Hàm main - khởi động ứng dụng"""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
