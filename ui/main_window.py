# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import platform

# Core
from core.config_manager import ConfigManager
from core.pdf_service import PDFService
from core.excel_handler import ExcelHandler

# UI
from ui.tabs.general_tab import GeneralTab
from ui.tabs.coordinate_tab import CoordinateTab
from ui.tabs.custom_tab import CustomFieldTab

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng dụng In Lá Phái Quy Y - v2.0 (MVC)")
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        
        # 1. Services
        self.config_manager = ConfigManager()
        self.pdf_service = PDFService()
        
        # 2. Variables
        self.excel_var = tk.StringVar()
        self.output_var = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Desktop", "QuyY_Output"))
        self.count_var = tk.StringVar(value="0 bản ghi")
        self.status_var = tk.StringVar(value="Sẵn sàng")
        self.export_mode_var = tk.StringVar(value="multiple")
        
        # 3. Build UI
        self._build_menu()
        self._build_layout()
        
        # 4. Xử lý khi đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def _build_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Cấu hình", menu=file_menu)
        file_menu.add_command(label="Lưu Cấu Hình", command=self.save_config)
        file_menu.add_command(label="Mở Cấu Hình...", command=self.load_config)
        file_menu.add_separator()
        file_menu.add_command(label="Reset Mặc Định", command=self.reset_config)
        file_menu.add_separator()
        file_menu.add_command(label="Thoát", command=self.on_closing)
    
    def on_closing(self):
        """Xử lý khi thoát app - hỏi lưu nếu có thay đổi chưa lưu"""
        if self.config_manager.is_dirty():
            result = messagebox.askyesnocancel(
                "Lưu cấu hình?",
                "Bạn có thay đổi chưa lưu.\nBạn có muốn lưu cấu hình trước khi thoát?"
            )
            if result is True:  # Yes - Lưu và thoát
                try:
                    self.config_manager.save()
                except Exception as e:
                    messagebox.showerror("Lỗi lưu", str(e))
                    return  # Không thoát nếu lưu thất bại
                self.root.destroy()
            elif result is False:  # No - Thoát không lưu
                self.root.destroy()
            # Cancel - Không làm gì, ở lại app
        else:
            self.root.destroy()
        
    def _build_layout(self):
        # Header
        header = tk.Frame(self.root, bg="#2c3e50", height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="ỨNG DỤNG IN LÁ PHÁI QUY Y", font=("Arial", 16, "bold"), bg="#2c3e50", fg="white").pack(pady=15)
        
        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tabs
        self.tab_general = GeneralTab(
            self.notebook, 
            self.excel_var, 
            self.output_var, 
            self.count_var, 
            self.export_mode_var,
            on_excel_selected_callback=self.on_excel_selected,
            on_export_callback=self.on_export,
            on_print_callback=self.on_print
        )
        self.tab_coord = CoordinateTab(self.notebook, self.config_manager, self.status_var)
        self.tab_custom = CustomFieldTab(self.notebook, self.config_manager, self.status_var)
        
        self.notebook.add(self.tab_general, text="📁 Chính")
        self.notebook.add(self.tab_coord, text="📐 Tọa Độ")
        self.notebook.add(self.tab_custom, text="✏️ Custom Fields")
        
        # Status & Progress
        status_frame = tk.Frame(self.root, bg="#ecf0f1", height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.progress_bar = ttk.Progressbar(self.root, mode='determinate')
        self.progress_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=0, pady=0)
        
        tk.Label(status_frame, textvariable=self.status_var, bg="#ecf0f1", anchor=tk.W, padx=10).pack(fill=tk.BOTH)

    # --- Actions ---
    
    def on_excel_selected(self, filepath):
        self.excel_var.set(filepath)
        try:
            count, _ = ExcelHandler.read_file(filepath)
            self.count_var.set(f"{count} bản ghi")
            self.status_var.set("Đã load file Excel")
        except Exception as e:
            self.count_var.set("ERROR")
            messagebox.showerror("Lỗi đọc file", str(e))

    def on_export(self):
        excel_path = self.excel_var.get()
        output_dir = self.output_var.get()
        if not excel_path or not output_dir:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn file Excel và thư mục lưu.")
            return

        if not messagebox.askyesno("Xác nhận", "Bắt đầu xuất PDF?"):
            return
            
        try:
            _, df = ExcelHandler.read_file(excel_path)
            mode = self.export_mode_var.get()
            
            self.lock_ui()
            self.status_var.set("Đang xuất PDF...")
            self.progress_bar['value'] = 0
            
            self.pdf_service.run_batch_export(
                df, 
                output_dir, 
                self.config_manager, 
                mode, 
                progress_callback=self.update_progress,
                completion_callback=self.on_process_finished
            )
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def on_print(self):
        excel_path = self.excel_var.get()
        if not excel_path:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn file Excel!")
            return
        
        if not messagebox.askyesno("Xác nhận", "Bắt đầu in trực tiếp?"):
            return
            
        try:
            _, df = ExcelHandler.read_file(excel_path)
            mode = self.export_mode_var.get()
            
            self.lock_ui()
            self.status_var.set("Đang tạo PDF và in...")
            self.progress_bar['value'] = 0
            
            self.pdf_service.run_print_job(
                df, 
                self.config_manager, 
                mode, 
                progress_callback=self.update_progress,
                completion_callback=self.on_process_finished
            )
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def update_progress(self, current, total):
        # Thread safe update
        percent = (current / total) * 100
        self.root.after(0, lambda: self._update_bar(percent, f"Đang xử lý: {current}/{total}"))
        
    def _update_bar(self, val, text):
        self.progress_bar['value'] = val
        self.status_var.set(text)

    def on_process_finished(self, result):
        self.root.after(0, lambda: self._finish_ui(result))
        
    def _finish_ui(self, result):
        self.unlock_ui()
        self.progress_bar['value'] = 0
        if result['error'] > 0:
            msg = f"{result['message']}\n\nChi tiết lỗi:\n" + "\n".join(result['errors'][:5])
            if len(result['errors']) > 5:
                msg += f"\n... và {len(result['errors']) - 5} lỗi khác"
            messagebox.showwarning("Hoàn thành có lỗi", msg)
        else:
            messagebox.showinfo("Thành công", result['message'])
            
            # Open folder only if export
            if result.get('type') == 'export':
                self.pdf_service.open_output_folder(self.output_var.get())
            
        self.status_var.set(result['message'])

    def lock_ui(self):
        self.tab_general.lock_ui()
        
    def unlock_ui(self):
        self.tab_general.unlock_ui()

    def save_config(self):
        try:
            self.config_manager.save()
            messagebox.showinfo("Thành công", "Đã lưu cấu hình")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
            
    def load_config(self):
        f = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if f:
            try:
                self.config_manager.load_from_file(f)
                self.tab_coord.refresh()
                self.tab_custom.refresh()
                messagebox.showinfo("Thành công", "Đã load cấu hình")
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
                
    def reset_config(self):
        if messagebox.askyesno("Reset", "Bạn có chắc muốn reset cấu hình mặc định?"):
            self.config_manager.reset_to_defaults()
            self.tab_coord.refresh()
            self.tab_custom.refresh()
