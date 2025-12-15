# -*- coding: utf-8 -*-
"""
Ứng dụng in lá phái quy y - Entry Point
"""

import tkinter as tk
from app import QuyYPrinterApp


def main():
    """Hàm main - khởi động ứng dụng"""
    root = tk.Tk()
    app = QuyYPrinterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
