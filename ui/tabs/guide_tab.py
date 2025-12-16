# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk

class GuideTab(tk.Frame):
    """Tab Hướng dẫn sử dụng"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self._build_ui()
        
    def _build_ui(self):
        # Scrollable frame
        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, padx=20, pady=20)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # Content
        self._build_content(scrollable_frame)
    
    def _build_content(self, parent):
        # Title
        tk.Label(
            parent, 
            text="📖 Hướng Dẫn Sử Dụng", 
            font=("Arial", 18, "bold"),
            fg="#2c3e50"
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Section 1
        self._build_guide_section(parent, "1️⃣ Chuẩn bị File Excel", [
            "• File Excel cần có các cột sau:",
            "   - hovaten: Họ và tên",
            "   - phapdanh: Pháp danh (có thể để trống)",
            "   - namsinh: Năm sinh",
            "   - diachithuongtru_short: Địa chỉ (ngắn gọn)",
            "",
            "• Lưu ý: Tên cột phải viết thường, không dấu"
        ])
        
        # Section 2
        self._build_guide_section(parent, "2️⃣ Chọn File và Ngày Quy Y", [
            "• Bước 1: Click 'Chọn File' để chọn file Excel",
            "• Bước 2: Chọn thư mục lưu PDF",
            "• Bước 3: Chọn Ngày Quy Y từ lịch",
            "• Bước 4: Nhấn 'Áp dụng' để xác nhận ngày",
            "",
            "⚠️ BẮT BUỘC: Phải chọn Ngày Quy Y trước khi xuất/in PDF!"
        ])
        
        # Section 3
        self._build_guide_section(parent, "3️⃣ Chỉnh Sửa Tọa Độ", [
            "• Vào tab 'Tọa Độ' để điều chỉnh vị trí các field",
            "• Kéo thả trực tiếp trên preview",
            "• Hoặc double-click vào bảng để sửa số liệu",
            "• Dùng phím mũi tên để di chuyển chính xác",
            "• Nhấn Escape để bỏ chọn field"
        ])
        
        # Section 4
        self._build_guide_section(parent, "4️⃣ Thêm Custom Fields", [
            "• Vào tab 'Custom Fields' để thêm field tùy chỉnh",
            "• Click '➕ Thêm Field' để tạo mới",
            "• Nhập tên, giá trị và tọa độ",
            "• Double-click để sửa field đã tạo"
        ])
        
        # Section 5
        self._build_guide_section(parent, "5️⃣ Xuất PDF / In Trực Tiếp", [
            "• 📄 Xuất PDF: Tạo file PDF vào thư mục đã chọn",
            "• 🖨️ In Trực Tiếp: Mở cửa sổ preview và in",
            "",
            "Chế độ xuất (cài đặt trong tab 'Cài đặt'):",
            "• Nhiều file: Mỗi người 1 file PDF riêng",
            "• Một file: Tất cả gộp thành 1 file PDF"
        ])
        
        # Section 6
        self._build_guide_section(parent, "6️⃣ Lưu Cấu Hình", [
            "• Menu 'Cấu hình' > 'Lưu Cấu Hình' để lưu",
            "• Cấu hình sẽ được tự động load khi mở app",
            "• Có thể export/import cấu hình để backup"
        ])
        
        # Footer
        tk.Label(
            parent,
            text="─" * 50,
            fg="#bdc3c7"
        ).pack(anchor=tk.W, pady=(20, 10))
        
        tk.Label(
            parent,
            text="✨ Chúc bạn sử dụng hiệu quả! ✨",
            font=("Arial", 12, "italic"),
            fg="#27ae60"
        ).pack(anchor=tk.CENTER)

    def _build_guide_section(self, parent, title, items):
        section = tk.LabelFrame(parent, text=title, font=("Arial", 12, "bold"), padx=15, pady=10, fg="#2980b9")
        section.pack(fill=tk.X, pady=(0, 15))
        
        for item in items:
            if item == "":
                tk.Label(section, text="").pack()  # Empty line
            else:
                tk.Label(
                    section,
                    text=item,
                    font=("Arial", 10),
                    fg="#34495e",
                    justify=tk.LEFT,
                    anchor=tk.W
                ).pack(anchor=tk.W, pady=1)
