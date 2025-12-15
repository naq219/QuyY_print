# -*- coding: utf-8 -*-
"""
Ứng dụng in lá phái quy y
GUI với Tkinter
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import pandas as pd
from pdf_generator import PDFGenerator
from config import FIELD_POSITIONS
import platform


class QuyYPrinterApp:
    """Ứng dụng in lá phái quy y"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng dụng In Lá Phái Quy Y")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Variables
        self.excel_path = tk.StringVar()
        self.output_dir = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Desktop", "QuyY_Output"))
        self.record_count = tk.StringVar(value="0 bản ghi")
        self.status_text = tk.StringVar(value="Sẵn sàng")
        
        # PDF Generator
        self.pdf_generator = PDFGenerator()
        
        # Build GUI
        self._build_gui()
        
    def _build_gui(self):
        """Xây dựng giao diện"""
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="ỨNG DỤNG IN LÁ PHÁI QUY Y",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=20)
        
        # Main content
        content_frame = tk.Frame(self.root, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # File Excel selection
        excel_frame = tk.LabelFrame(content_frame, text="1. Chọn File Excel", font=("Arial", 11, "bold"), padx=10, pady=10)
        excel_frame.pack(fill=tk.X, pady=(0, 15))
        
        excel_path_frame = tk.Frame(excel_frame)
        excel_path_frame.pack(fill=tk.X)
        
        tk.Entry(
            excel_path_frame,
            textvariable=self.excel_path,
            font=("Arial", 10),
            state="readonly"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Button(
            excel_path_frame,
            text="Chọn File",
            command=self._browse_excel,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            cursor="hand2"
        ).pack(side=tk.RIGHT)
        
        # Record count
        tk.Label(
            excel_frame,
            textvariable=self.record_count,
            font=("Arial", 10),
            fg="#27ae60"
        ).pack(anchor=tk.W, pady=(10, 0))
        
        # Output directory
        output_frame = tk.LabelFrame(content_frame, text="2. Thư Mục Lưu PDF", font=("Arial", 11, "bold"), padx=10, pady=10)
        output_frame.pack(fill=tk.X, pady=(0, 15))
        
        output_path_frame = tk.Frame(output_frame)
        output_path_frame.pack(fill=tk.X)
        
        tk.Entry(
            output_path_frame,
            textvariable=self.output_dir,
            font=("Arial", 10)
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Button(
            output_path_frame,
            text="Chọn Thư Mục",
            command=self._browse_output,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            cursor="hand2"
        ).pack(side=tk.RIGHT)
        
        # Coordinate adjustment (for future feature)
        coord_frame = tk.LabelFrame(content_frame, text="3. Điều Chỉnh Tọa Độ (Tính năng tương lai)", 
                                     font=("Arial", 11, "bold"), padx=10, pady=10)
        coord_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        tk.Label(
            coord_frame,
            text="Tính năng điều chỉnh tọa độ sẽ được cập nhật trong phiên bản sau.",
            font=("Arial", 9),
            fg="#95a5a6"
        ).pack(pady=10)
        
        # Action buttons
        action_frame = tk.Frame(content_frame)
        action_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Button(
            action_frame,
            text="📄 Xuất PDF",
            command=self._export_pdf,
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2,
            cursor="hand2"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Button(
            action_frame,
            text="🖨️ In Trực Tiếp",
            command=self._print_direct,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2,
            cursor="hand2"
        ).pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # Progress bar
        progress_frame = tk.Frame(content_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.pack(fill=tk.X)
        
        # Status bar
        status_frame = tk.Frame(self.root, bg="#ecf0f1", height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        tk.Label(
            status_frame,
            textvariable=self.status_text,
            font=("Arial", 9),
            bg="#ecf0f1",
            anchor=tk.W,
            padx=10
        ).pack(fill=tk.BOTH)
    
    def _browse_excel(self):
        """Chọn file Excel"""
        filename = filedialog.askopenfilename(
            title="Chọn file Excel",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        if filename:
            self.excel_path.set(filename)
            self._load_excel_preview(filename)
    
    def _load_excel_preview(self, filepath):
        """Load và hiển thị thông tin preview từ Excel"""
        try:
            df = pd.read_excel(filepath)
            # Lọc bỏ dòng header
            df = df[df['hovaten'].notna()]
            count = len(df)
            self.record_count.set(f"{count} bản ghi")
            self.status_text.set(f"Đã load file: {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc file Excel:\n{str(e)}")
            self.record_count.set("0 bản ghi")
    
    def _browse_output(self):
        """Chọn thư mục output"""
        dirname = filedialog.askdirectory(title="Chọn thư mục lưu PDF")
        if dirname:
            self.output_dir.set(dirname)
    
    def _export_pdf(self):
        """Xuất PDF hàng loạt"""
        if not self.excel_path.get():
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file Excel!")
            return
        
        if not self.output_dir.get():
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn thư mục lưu PDF!")
            return
        
        # Confirm
        if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xuất tất cả PDF?"):
            return
        
        # Chạy trong thread riêng để không block GUI
        thread = threading.Thread(target=self._do_export_pdf)
        thread.daemon = True
        thread.start()
    
    def _do_export_pdf(self):
        """Thực hiện xuất PDF (chạy trong thread riêng)"""
        try:
            self.status_text.set("Đang xuất PDF...")
            self.progress['value'] = 0
            
            def progress_callback(current, total):
                progress_percent = (current / total) * 100
                self.progress['value'] = progress_percent
                self.status_text.set(f"Đang xử lý: {current}/{total}")
                self.root.update_idletasks()
            
            success, error, errors = self.pdf_generator.create_batch_pdf(
                self.excel_path.get(),
                self.output_dir.get(),
                progress_callback
            )
            
            # Hiển thị kết quả
            message = f"Hoàn thành!\n\nThành công: {success} file\nLỗi: {error} file"
            if errors:
                message += f"\n\nChi tiết lỗi:\n" + "\n".join(errors[:5])
                if len(errors) > 5:
                    message += f"\n... và {len(errors) - 5} lỗi khác"
            
            messagebox.showinfo("Kết quả", message)
            self.status_text.set(f"Hoàn thành: {success} file thành công, {error} file lỗi")
            
            # Mở thư mục output
            if success > 0:
                if platform.system() == 'Windows':
                    os.startfile(self.output_dir.get())
                elif platform.system() == 'Darwin':  # macOS
                    os.system(f'open "{self.output_dir.get()}"')
                else:  # Linux
                    os.system(f'xdg-open "{self.output_dir.get()}"')
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi:\n{str(e)}")
            self.status_text.set("Lỗi khi xuất PDF")
        finally:
            self.progress['value'] = 0
    
    def _print_direct(self):
        """In trực tiếp ra máy in"""
        if not self.excel_path.get():
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file Excel!")
            return
        
        # Tạo PDF tạm trong temp folder
        import tempfile
        temp_dir = tempfile.mkdtemp()
        
        # Confirm
        if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn in tất cả?"):
            return
        
        # Chạy trong thread riêng
        thread = threading.Thread(target=self._do_print_direct, args=(temp_dir,))
        thread.daemon = True
        thread.start()
    
    def _do_print_direct(self, temp_dir):
        """Thực hiện in trực tiếp (chạy trong thread riêng)"""
        try:
            self.status_text.set("Đang tạo PDF và in...")
            self.progress['value'] = 0
            
            def progress_callback(current, total):
                progress_percent = (current / total) * 100
                self.progress['value'] = progress_percent
                self.status_text.set(f"Đang in: {current}/{total}")
                self.root.update_idletasks()
            
            # Tạo PDF
            success, error, errors = self.pdf_generator.create_batch_pdf(
                self.excel_path.get(),
                temp_dir,
                progress_callback
            )
            
            # In từng file PDF
            if success > 0:
                import glob
                pdf_files = glob.glob(os.path.join(temp_dir, "*.pdf"))
                
                for pdf_file in pdf_files:
                    self._print_pdf_file(pdf_file)
                
                messagebox.showinfo("Hoàn thành", f"Đã gửi {len(pdf_files)} file đến máy in!")
            else:
                messagebox.showwarning("Cảnh báo", "Không có file nào được tạo!")
            
            self.status_text.set(f"Hoàn thành in: {success} file")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi in:\n{str(e)}")
            self.status_text.set("Lỗi khi in")
        finally:
            self.progress['value'] = 0
            # Xóa temp folder
            import shutil
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
    
    def _print_pdf_file(self, pdf_path):
        """
        In một file PDF
        
        Args:
            pdf_path: đường dẫn đến file PDF
        """
        system = platform.system()
        
        try:
            if system == 'Windows':
                # Windows: sử dụng ShellExecute với verb "print"
                import win32api
                import win32print
                
                printer_name = win32print.GetDefaultPrinter()
                win32api.ShellExecute(
                    0,
                    "print",
                    pdf_path,
                    f'/d:"{printer_name}"',
                    ".",
                    0
                )
            elif system == 'Darwin':  # macOS
                os.system(f'lpr "{pdf_path}"')
            else:  # Linux
                os.system(f'lp "{pdf_path}"')
        except Exception as e:
            print(f"Lỗi khi in file {pdf_path}: {e}")


def main():
    """Hàm main"""
    root = tk.Tk()
    app = QuyYPrinterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
