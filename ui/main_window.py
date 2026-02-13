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
from ui.tabs.settings_tab import SettingsTab
from ui.tabs.guide_tab import GuideTab

class MainWindow:
    def __init__(self, root, config_path=None):
        self.root = root
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        
        # 1. Services - nhận config_path từ config chooser
        self.config_manager = ConfigManager(config_path=config_path)
        self.pdf_service = PDFService()
        
        # Cập nhật title hiển thị tên file config
        self._update_title()
        
        # 2. Variables
        self.excel_var = tk.StringVar()
        self.output_var = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Desktop", "QuyY_Output"))
        self.count_var = tk.StringVar(value="0 bản ghi")
        self.status_var = tk.StringVar(value="Sẵn sàng")
        
        # Load export_mode từ config (mặc định "single")
        self.export_mode_var = tk.StringVar(value=self.config_manager.export_mode)
        
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
    
    def _update_title(self):
        """Cập nhật title cửa sổ hiển thị tên file config"""
        base_title = "Ứng dụng In Lá Phái Quy Y - v2.0"
        if self.config_manager.config_path:
            config_name = os.path.basename(self.config_manager.config_path)
            self.root.title(f"{base_title} - [{config_name}]")
        else:
            self.root.title(f"{base_title} - [Cấu hình mới *]")
    
    def on_closing(self):
        """Xử lý khi thoát app - hỏi lưu nếu có thay đổi chưa lưu"""
        if self.config_manager.is_dirty() or self.config_manager.is_new_config:
            result = messagebox.askyesnocancel(
                "Lưu cấu hình?",
                "Bạn có thay đổi chưa lưu.\nBạn có muốn lưu cấu hình trước khi thoát?"
            )
            if result is True:  # Yes - Lưu và thoát
                if self._do_save():
                    self.root.destroy()
                # Nếu lưu thất bại hoặc user cancel save-as, ở lại app
            elif result is False:  # No - Thoát không lưu
                self.root.destroy()
            # Cancel - Không làm gì, ở lại app
        else:
            self.root.destroy()
        
    def _build_layout(self):
        # Header
        header = tk.Frame(self.root, bg="#2c3e50", height=75)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="ỨNG DỤNG IN LÁ PHÁI QUY Y", font=("Arial", 16, "bold"), bg="#2c3e50", fg="white").pack(pady=(12, 2))
        tk.Label(header, text="📞 0983.838.619", font=("Arial", 9), bg="#2c3e50", fg="#bdc3c7").pack(pady=(0, 8))
        
        # Style cho Notebook tabs - to hơn và dễ nhìn hơn
        style = ttk.Style()
        style.configure('TNotebook.Tab', 
                       font=('Arial', 11, 'bold'),
                       padding=[15, 8])  # [horizontal, vertical]
        style.map('TNotebook.Tab',
                 background=[('selected', '#3498db')],
                 foreground=[('selected', '#2c3e50')])
        
        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tabs
        self.tab_general = GeneralTab(
            self.notebook,
            self.config_manager,
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
        self.tab_settings = SettingsTab(self.notebook, self.config_manager, self.export_mode_var, self.status_var)
        self.tab_guide = GuideTab(self.notebook)
        
        # Tab names với spacing đẹp hơn
        self.notebook.add(self.tab_general, text="  📁 Chính  ")
        self.notebook.add(self.tab_coord, text="  📐 Tọa Độ  ")
        self.notebook.add(self.tab_custom, text="  ✏️ Custom Fields  ")
        self.notebook.add(self.tab_settings, text="  ⚙️ Cài đặt  ")
        self.notebook.add(self.tab_guide, text="  📖 Hướng dẫn  ")
        
        # Track tab hiện tại để kiểm tra dirty khi chuyển tab
        self._previous_tab = None
        
        # Bind event để refresh khi chuyển tab
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        
        # Refresh sau khi UI được build hoàn toàn
        self.root.after(100, self._initial_refresh)
        
        # Footer - Contact info
        footer_frame = tk.Frame(self.root, bg="#34495e", height=35)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)
        
        tk.Label(
            footer_frame, 
            text="📞 Liên hệ: Trung Quảng An 0983.838.619", 
            font=("Arial", 10, "bold"), 
            bg="#34495e", 
            fg="#ecf0f1"
        ).pack(side=tk.RIGHT, padx=15, pady=8)
        
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
            count, df = ExcelHandler.read_file(filepath)
            self.count_var.set(f"{count} bản ghi")
            self.status_var.set("Đã load file Excel")
            
            # Clear ngày quy y khi chọn file Excel mới
            self.config_manager.set_selected_date(None)
            # Cập nhật UI của tab chính nếu có
            if hasattr(self, 'tab_general') and hasattr(self.tab_general, '_clear_date_ui'):
                self.tab_general._clear_date_ui()
            
            # Validate Excel file
            warnings = ExcelHandler.validate_excel(df)
            if warnings['has_warnings']:
                warning_msg = ExcelHandler.format_validation_message(warnings)
                messagebox.showwarning("Cảnh báo dữ liệu", warning_msg)
                self.status_var.set(f"Đã load - {warnings['summary']}")
            
        except Exception as e:
            self.count_var.set("ERROR")
            messagebox.showerror("Lỗi đọc file", str(e))

    def on_export(self):
        excel_path = self.excel_var.get()
        output_dir = self.output_var.get()
        if not excel_path or not output_dir:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn file Excel và thư mục lưu.")
            return
        
        # Kiểm tra đã chọn ngày quy y chưa
        if not self.config_manager.is_date_selected():
            messagebox.showwarning("Chưa chọn ngày", "Vui lòng chọn Ngày Quy Y trước khi xuất PDF!\n\nVào tab 'Chính' > phần 'Ngày Quy Y' để chọn ngày.")
            return

        if not messagebox.askyesno("Xác nhận", "Bắt đầu xuất PDF?"):
            return
            
        try:
            _, df = ExcelHandler.read_file(excel_path)
            mode = self.export_mode_var.get()
            
            # Validate trước khi xuất
            warnings = ExcelHandler.validate_excel(df)
            if warnings['has_warnings']:
                warning_msg = ExcelHandler.format_validation_message(warnings)
                if not messagebox.askyesno("Cảnh báo dữ liệu", 
                    warning_msg + "\n\nBạn có muốn tiếp tục xuất PDF không?"):
                    return
            
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
            self.unlock_ui()
            messagebox.showerror("Lỗi", str(e))

    def on_print(self):
        excel_path = self.excel_var.get()
        if not excel_path:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn file Excel!")
            return
        
        # Kiểm tra đã chọn ngày quy y chưa
        if not self.config_manager.is_date_selected():
            messagebox.showwarning("Chưa chọn ngày", "Vui lòng chọn Ngày Quy Y trước khi in!\n\nVào tab 'Chính' > phần 'Ngày Quy Y' để chọn ngày.")
            return
            
        try:
            _, df = ExcelHandler.read_file(excel_path)
            
            # Validate trước khi in
            warnings = ExcelHandler.validate_excel(df)
            if warnings['has_warnings']:
                warning_msg = ExcelHandler.format_validation_message(warnings)
                if not messagebox.askyesno("Cảnh báo dữ liệu", 
                    warning_msg + "\n\nBạn có muốn tiếp tục in không?"):
                    return
            
            # Lấy máy in được chọn từ tab Chính
            selected_printer = self.tab_general.get_selected_printer() if hasattr(self.tab_general, 'get_selected_printer') else None
            
            # Mở cửa sổ preview thay vì in batch
            from ui.components.print_preview import PrintPreviewWindow
            PrintPreviewWindow(self.root, df, self.config_manager, self.pdf_service, selected_printer)
            
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

    def _do_save(self):
        """Thực hiện lưu config. Nếu config mới -> hỏi save-as.
        Returns: True nếu lưu thành công, False nếu thất bại/cancel
        """
        try:
            self.config_manager.save()
            self._update_title()
            return True
        except Exception as e:
            if str(e) == "NEED_SAVE_AS":
                # Config mới, cần hỏi user chọn nơi lưu
                return self._save_as_config()
            else:
                messagebox.showerror("Lỗi lưu", str(e))
                return False
    
    def _save_as_config(self):
        """Hỏi user chọn thư mục và tên file để lưu config mới.
        Returns: True nếu lưu thành công, False nếu cancel
        """
        filepath = filedialog.asksaveasfilename(
            title="Lưu file cấu hình",
            defaultextension=".json",
            initialfile="config.json",
            filetypes=[("JSON Config", "*.json"), ("Tất cả file", "*.*")]
        )
        if not filepath:
            return False  # User cancel
        
        try:
            self.config_manager.set_config_path(filepath)
            self.config_manager.save()
            self._update_title()
            # Lưu lại thư mục cho lần mở sau
            from ui.config_chooser import ConfigChooser
            ConfigChooser.save_last_config_path(filepath)
            messagebox.showinfo("Thành công", f"Đã lưu cấu hình:\n{filepath}")
            return True
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
            return False
    
    def save_config(self):
        if self._do_save():
            if self.config_manager.config_path:
                messagebox.showinfo("Thành công", f"Đã lưu cấu hình:\n{self.config_manager.config_path}")
            
    def load_config(self):
        f = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if f:
            try:
                self.config_manager.load_from_file(f)
                self.tab_coord.refresh()
                self.tab_custom.refresh()
                self._update_title()
                messagebox.showinfo("Thành công", "Đã load cấu hình")
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
                
    def reset_config(self):
        if messagebox.askyesno("Reset", "Bạn có chắc muốn reset cấu hình mặc định?"):
            self.config_manager.reset_to_defaults()
            self.tab_coord.refresh()
            self.tab_custom.refresh()

    def _on_tab_changed(self, event):
        """Refresh tab khi người dùng chuyển sang tab khác + hỏi lưu nếu cần"""
        try:
            selected_tab = self.notebook.select()
            tab_text = self.notebook.tab(selected_tab, "text")
            
            # Kiểm tra nếu đang rời tab Toạ Độ hoặc Custom Fields mà có thay đổi chưa lưu
            if self._previous_tab and self.config_manager.is_dirty():
                if "Tọa Độ" in self._previous_tab or "Custom" in self._previous_tab:
                    result = messagebox.askyesno(
                        "Lưu cấu hình?",
                        f"Bạn có thay đổi chưa lưu ở tab {self._previous_tab.strip()}.\n" 
                        f"Bạn có muốn lưu cấu hình không?",
                        icon="question"
                    )
                    if result:
                        self._do_save()
                    else:
                        # Không lưu → reload config từ file để huỷ thay đổi
                        if self.config_manager.config_path:
                            self.config_manager.load()
                        self.config_manager.clear_dirty()
                        self.tab_coord.refresh()
                        self.tab_custom.refresh()
            
            # Cập nhật tab hiện tại
            self._previous_tab = tab_text
            
            # Refresh tab đích
            if "Tọa Độ" in tab_text:
                self.tab_coord.refresh()
            elif "Custom" in tab_text:
                self.tab_custom.refresh()
        except Exception as e:
            print(f"[MainWindow] Error on tab changed: {e}")

    def _initial_refresh(self):
        """Refresh tất cả tabs sau khi UI được build hoàn toàn"""
        try:
            self.tab_coord.refresh()
            self.tab_custom.refresh()
            print("[MainWindow] Initial refresh completed")
        except Exception as e:
            print(f"[MainWindow] Error initial refresh: {e}")

