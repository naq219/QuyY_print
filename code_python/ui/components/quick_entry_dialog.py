# -*- coding: utf-8 -*-
"""
Quick Entry Dialog - Nhập nhanh thông tin để in/xuất PDF
Không cần file Excel, nhập trực tiếp từ bàn phím
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import tempfile
from datetime import datetime

try:
    from tkcalendar import DateEntry
    HAS_TKCALENDAR = True
except ImportError:
    HAS_TKCALENDAR = False

from core.lunar_converter import LunarConverter
from ui.components.toast import ToastNotification


class PlaceholderEntry(tk.Entry):
    """Entry widget với placeholder text (mờ khi chưa nhập)"""
    
    def __init__(self, master=None, placeholder="", placeholder_color="#999999", **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = placeholder_color
        self.default_fg = self.cget("fg") or "#000000"
        
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        
        self._show_placeholder()
    
    def _show_placeholder(self):
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(fg=self.placeholder_color)
            self._is_placeholder = True
    
    def _on_focus_in(self, event):
        if hasattr(self, '_is_placeholder') and self._is_placeholder:
            self.delete(0, tk.END)
            self.config(fg=self.default_fg)
            self._is_placeholder = False
    
    def _on_focus_out(self, event):
        if not self.get():
            self._show_placeholder()
    
    def get_value(self):
        """Lấy giá trị thực (trả về '' nếu đang hiển thị placeholder)"""
        if hasattr(self, '_is_placeholder') and self._is_placeholder:
            return ""
        return self.get().strip()
    
    def clear(self):
        """Xóa nội dung và hiện lại placeholder"""
        self.delete(0, tk.END)
        self.config(fg=self.default_fg)
        self._is_placeholder = False
        self._show_placeholder()


class QuickEntryDialog(tk.Toplevel):
    """Dialog nhập nhanh thông tin để in lá phái quy y"""
    
    def __init__(self, parent, config_manager, pdf_service, get_printer_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.config_manager = config_manager
        self.pdf_service = pdf_service
        self.get_printer = get_printer_callback
        
        self.title("✍️ Nhập Nhanh Thông Tin")
        
        # Kích thước và vị trí giữa màn hình
        width = 580
        height = 650
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.resizable(False, False)
        
        # Modal dialog
        self.transient(parent)
        self.grab_set()
        
        # Date variable (cho ngày quy y trong dialog)
        self.date_var = tk.StringVar()
        self.lunar_info_var = tk.StringVar(value="Chưa chọn ngày")
        
        self._build_ui()
        
        # Focus vào trường họ tên
        self.after(100, lambda: self.entry_ho_ten.focus_set())
    
    def _build_ui(self):
        # === Header ===
        header = tk.Frame(self, bg="#8e44ad", height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header, 
            text="✍️  NHẬP NHANH THÔNG TIN", 
            font=("Arial", 14, "bold"), 
            bg="#8e44ad", fg="white"
        ).pack(pady=(12, 2))
        
        tk.Label(
            header,
            text="Nhập thông tin trực tiếp để in/xuất PDF nhanh",
            font=("Arial", 9),
            bg="#8e44ad", fg="#dcd6f7"
        ).pack()
        
        # === Form ===
        form_frame = tk.Frame(self, padx=25, pady=15)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- Họ tên (bắt buộc) ---
        lbl_frame = tk.Frame(form_frame)
        lbl_frame.pack(fill=tk.X, pady=(0, 2))
        tk.Label(lbl_frame, text="Họ và Tên", font=("Arial", 11, "bold"), fg="#2c3e50").pack(side=tk.LEFT)
        tk.Label(lbl_frame, text=" *", font=("Arial", 11, "bold"), fg="#e74c3c").pack(side=tk.LEFT)
        
        self.entry_ho_ten = PlaceholderEntry(
            form_frame, 
            placeholder="Nguyễn Văn A",
            font=("Arial", 12), 
            fg="#2c3e50"
        )
        self.entry_ho_ten.pack(fill=tk.X, pady=(0, 10), ipady=4)
        
        # --- Pháp danh ---
        tk.Label(form_frame, text="Pháp Danh", font=("Arial", 11, "bold"), fg="#2c3e50").pack(anchor=tk.W, pady=(0, 2))
        
        self.entry_phap_danh = PlaceholderEntry(
            form_frame, 
            placeholder="Thích Minh...",
            font=("Arial", 12), 
            fg="#2c3e50"
        )
        self.entry_phap_danh.pack(fill=tk.X, pady=(0, 10), ipady=4)
        
        # --- Năm sinh + Địa chỉ (cùng hàng) ---
        row_frame = tk.Frame(form_frame)
        row_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Năm sinh (bên trái, nhỏ hơn)
        ns_frame = tk.Frame(row_frame)
        ns_frame.pack(side=tk.LEFT, padx=(0, 15))
        tk.Label(ns_frame, text="Năm Sinh", font=("Arial", 11, "bold"), fg="#2c3e50").pack(anchor=tk.W, pady=(0, 2))
        self.entry_nam_sinh = PlaceholderEntry(
            ns_frame,
            placeholder="1990",
            font=("Arial", 12),
            fg="#2c3e50",
            width=10
        )
        self.entry_nam_sinh.pack(ipady=4)
        
        # Địa chỉ (bên phải, lớn hơn)
        dc_frame = tk.Frame(row_frame)
        dc_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(dc_frame, text="Địa chỉ", font=("Arial", 11, "bold"), fg="#2c3e50").pack(anchor=tk.W, pady=(0, 2))
        self.entry_dia_chi = PlaceholderEntry(
            dc_frame,
            placeholder="123 Đường ABC, Quận...",
            font=("Arial", 12),
            fg="#2c3e50"
        )
        self.entry_dia_chi.pack(fill=tk.X, ipady=4)
        
        # --- Separator ---
        sep = tk.Frame(form_frame, bg="#ddd", height=1)
        sep.pack(fill=tk.X, pady=(5, 10))
        
        # --- Ngày Quy Y ---
        date_label_frame = tk.Frame(form_frame)
        date_label_frame.pack(fill=tk.X, pady=(0, 2))
        tk.Label(date_label_frame, text="Ngày Quy Y", font=("Arial", 11, "bold"), fg="#2c3e50").pack(side=tk.LEFT)
        tk.Label(date_label_frame, text=" *", font=("Arial", 11, "bold"), fg="#e74c3c").pack(side=tk.LEFT)
        
        date_frame = tk.Frame(form_frame)
        date_frame.pack(fill=tk.X)
        
        if HAS_TKCALENDAR:
            self.date_entry = DateEntry(
                date_frame,
                width=15,
                background='#8e44ad',
                foreground='white',
                borderwidth=2,
                date_pattern='dd/MM/yyyy',
                font=("Arial", 11)
            )
            self.date_entry.pack(side=tk.LEFT, padx=(0, 10))
            self.date_entry.bind("<<DateEntrySelected>>", self._on_date_selected)
            self.date_entry.delete(0, tk.END)
        else:
            tk.Label(date_frame, text="(YYYY-MM-DD):", font=("Arial", 9), fg="#7f8c8d").pack(side=tk.LEFT)
            self.date_entry = tk.Entry(date_frame, textvariable=self.date_var, font=("Arial", 11), width=12)
            self.date_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        tk.Button(
            date_frame, text="Áp dụng", command=self._apply_date,
            bg="#8e44ad", fg="white", font=("Arial", 10, "bold"),
            cursor="hand2", relief="flat", padx=10
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(
            date_frame, text="Xóa ngày", command=self._clear_date,
            bg="#95a5a6", fg="white", font=("Arial", 9),
            cursor="hand2", relief="flat", padx=8
        ).pack(side=tk.LEFT)
        
        # --- Âm lịch (editable) ---
        lunar_frame = tk.Frame(form_frame, bg="#f0ebf8", padx=10, pady=8)
        lunar_frame.pack(fill=tk.X, pady=(8, 0))
        
        # Row 1: Ngày âm lịch
        lunar_row1 = tk.Frame(lunar_frame, bg="#f0ebf8")
        lunar_row1.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(lunar_row1, text="🌙 Âm lịch:", font=("Arial", 10, "bold"), fg="#6c3483", bg="#f0ebf8").pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(lunar_row1, text="Ngày", font=("Arial", 9), fg="#6c3483", bg="#f0ebf8").pack(side=tk.LEFT)
        self.entry_ngay_am = tk.Entry(lunar_row1, font=("Arial", 10), width=4, justify="center")
        self.entry_ngay_am.pack(side=tk.LEFT, padx=(3, 5))
        
        tk.Label(lunar_row1, text="Tháng", font=("Arial", 9), fg="#6c3483", bg="#f0ebf8").pack(side=tk.LEFT)
        self.entry_thang_am = tk.Entry(lunar_row1, font=("Arial", 10), width=4, justify="center")
        self.entry_thang_am.pack(side=tk.LEFT, padx=(3, 5))
        
        tk.Label(lunar_row1, text="Năm", font=("Arial", 9), fg="#6c3483", bg="#f0ebf8").pack(side=tk.LEFT)
        self.entry_nam_am = tk.Entry(lunar_row1, font=("Arial", 10), width=10, justify="center")
        self.entry_nam_am.pack(side=tk.LEFT, padx=(3, 0))
        
        # Row 2: Phật lịch
        lunar_row2 = tk.Frame(lunar_frame, bg="#f0ebf8")
        lunar_row2.pack(fill=tk.X)
        
        tk.Label(lunar_row2, text="☸️ Phật lịch:", font=("Arial", 10, "bold"), fg="#6c3483", bg="#f0ebf8").pack(side=tk.LEFT, padx=(0, 8))
        self.entry_phat_lich = tk.Entry(lunar_row2, font=("Arial", 10), width=8, justify="center")
        self.entry_phat_lich.pack(side=tk.LEFT, padx=(3, 0))
        
        tk.Label(lunar_row2, text="(tự điền khi chọn ngày dương, có thể chỉnh sửa)", font=("Arial", 8), fg="#999", bg="#f0ebf8").pack(side=tk.LEFT, padx=(10, 0))
        
        # === Action Buttons ===
        action_frame = tk.Frame(self, bg="#f5f5f5", padx=25, pady=15)
        action_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Row 1: Export + Print
        btn_row1 = tk.Frame(action_frame, bg="#f5f5f5")
        btn_row1.pack(fill=tk.X, pady=(0, 8))
        
        tk.Button(
            btn_row1, text="📄  Xuất PDF", command=self._on_export,
            bg="#27ae60", fg="white", font=("Arial", 12, "bold"),
            cursor="hand2", relief="flat", height=2
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Button(
            btn_row1, text="🖨️  In Trực Tiếp", command=self._on_print,
            bg="#e74c3c", fg="white", font=("Arial", 12, "bold"),
            cursor="hand2", relief="flat", height=2
        ).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Row 2: Clear + Close
        btn_row2 = tk.Frame(action_frame, bg="#f5f5f5")
        btn_row2.pack(fill=tk.X)
        
        tk.Button(
            btn_row2, text="🔄  Xóa Form", command=self._clear_form,
            bg="#f39c12", fg="white", font=("Arial", 10, "bold"),
            cursor="hand2", relief="flat", padx=15
        ).pack(side=tk.LEFT)
        
        tk.Button(
            btn_row2, text="❌  Đóng", command=self.destroy,
            bg="#7f8c8d", fg="white", font=("Arial", 10),
            cursor="hand2", relief="flat", padx=15
        ).pack(side=tk.RIGHT)
    
    # ==================== DATE HANDLING ====================
    
    def _on_date_selected(self, event=None):
        if HAS_TKCALENDAR:
            date_obj = self.date_entry.get_date()
            date_str = date_obj.strftime("%Y-%m-%d")
            self._update_lunar_display(date_str)
    
    def _apply_date(self):
        if HAS_TKCALENDAR:
            try:
                date_obj = self.date_entry.get_date()
                date_str = date_obj.strftime("%Y-%m-%d")
            except:
                messagebox.showwarning("Lỗi", "Vui lòng chọn ngày hợp lệ!", parent=self)
                return
        else:
            date_str = self.date_var.get().strip()
            if not date_str:
                messagebox.showwarning("Lỗi", "Vui lòng nhập ngày (YYYY-MM-DD)!", parent=self)
                return
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Lỗi", "Định dạng ngày không hợp lệ!\nVui lòng nhập: YYYY-MM-DD", parent=self)
                return
        
        self._update_lunar_display(date_str)
    
    def _clear_date(self):
        if HAS_TKCALENDAR:
            self.date_entry.delete(0, tk.END)
        else:
            self.date_var.set("")
        # Xóa các ô âm lịch
        self.entry_ngay_am.delete(0, tk.END)
        self.entry_thang_am.delete(0, tk.END)
        self.entry_nam_am.delete(0, tk.END)
        self.entry_phat_lich.delete(0, tk.END)
    
    def _update_lunar_display(self, date_str):
        """Tự động điền âm lịch và Phật lịch từ ngày dương"""
        try:
            date_info = LunarConverter.convert_date(date_str)
            
            # Auto-fill entries
            self.entry_ngay_am.delete(0, tk.END)
            self.entry_ngay_am.insert(0, str(date_info['lunar_day']))
            
            self.entry_thang_am.delete(0, tk.END)
            self.entry_thang_am.insert(0, str(date_info['lunar_month']))
            
            self.entry_nam_am.delete(0, tk.END)
            self.entry_nam_am.insert(0, str(date_info['lunar_year_name']))
            
            self.entry_phat_lich.delete(0, tk.END)
            self.entry_phat_lich.insert(0, str(date_info['buddhist_year']))
            
        except Exception as e:
            print(f"[QuickEntry] Lỗi convert ngày: {e}")
    
    def _get_selected_date_str(self):
        """Lấy ngày quy y đã chọn, trả về chuỗi YYYY-MM-DD hoặc None"""
        if HAS_TKCALENDAR:
            try:
                val = self.date_entry.get()
                if val:
                    date_obj = self.date_entry.get_date()
                    return date_obj.strftime("%Y-%m-%d")
            except:
                pass
            return None
        else:
            val = self.date_var.get().strip()
            if val:
                try:
                    datetime.strptime(val, "%Y-%m-%d")
                    return val
                except:
                    pass
            return None
    
    # ==================== FORM HANDLING ====================
    
    def _clear_form(self):
        """Xóa toàn bộ form"""
        self.entry_ho_ten.clear()
        self.entry_phap_danh.clear()
        self.entry_nam_sinh.clear()
        self.entry_dia_chi.clear()
        self._clear_date()
        self.entry_ho_ten.focus_set()
    
    def _get_lunar_values_from_entries(self):
        """Lấy giá trị âm lịch/Phật lịch từ các ô nhập"""
        return {
            "ngay_am": self.entry_ngay_am.get().strip(),
            "thang_am": self.entry_thang_am.get().strip(),
            "nam_am": self.entry_nam_am.get().strip(),
            "phat_lich": self.entry_phat_lich.get().strip()
        }
    
    def _validate_form(self):
        """Validate form, trả về (data_dict, date_str) hoặc None nếu lỗi"""
        ho_ten = self.entry_ho_ten.get_value()
        if not ho_ten:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập Họ và Tên!", parent=self)
            self.entry_ho_ten.focus_set()
            return None
        
        date_str = self._get_selected_date_str()
        if not date_str:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn Ngày Quy Y!", parent=self)
            return None
        
        phap_danh = self.entry_phap_danh.get_value()
        nam_sinh = self.entry_nam_sinh.get_value()
        dia_chi = self.entry_dia_chi.get_value()
        
        # Validate năm sinh nếu có
        if nam_sinh:
            if not nam_sinh.isdigit() or len(nam_sinh) != 4:
                messagebox.showwarning("Lỗi", "Năm sinh phải là 4 chữ số (ví dụ: 1990)!", parent=self)
                self.entry_nam_sinh.focus_set()
                return None
        
        data = {
            "phap_danh": phap_danh,
            "ho_ten": ho_ten,
            "sinh_nam": nam_sinh,
            "dia_chi": dia_chi
        }
        
        return data, date_str
    
    def _prepare_config_with_date(self, date_str):
        """Set ngày quy y vào config tạm để tạo PDF, trả về backup cũ"""
        import copy
        old_date = self.config_manager.get_selected_date()
        # Backup custom_fields values trước khi ghi đè
        old_custom_values = {}
        for key in ["ngay_am", "thang_am", "nam_am", "phat_lich", "ngay_duong", "thang_duong", "nam_duong"]:
            if key in self.config_manager.custom_fields:
                old_custom_values[key] = self.config_manager.custom_fields[key].get("value", "")
        
        # Set ngày dương → auto update custom_fields
        self.config_manager.set_selected_date(date_str)
        
        # Ghi đè bằng giá trị user đã chỉnh sửa trong dialog
        lunar_vals = self._get_lunar_values_from_entries()
        for key, val in lunar_vals.items():
            if key in self.config_manager.custom_fields:
                self.config_manager.custom_fields[key]["value"] = val
        
        return old_date, old_custom_values
    
    def _restore_config_date(self, old_state):
        """Khôi phục lại ngày quy y cũ trong config"""
        old_date, old_custom_values = old_state
        self.config_manager.set_selected_date(old_date)
        # Khôi phục custom_fields values
        for key, val in old_custom_values.items():
            if key in self.config_manager.custom_fields:
                self.config_manager.custom_fields[key]["value"] = val
    
    # ==================== EXPORT / PRINT ====================
    
    def _on_export(self):
        """Xuất PDF từ dữ liệu nhập tay"""
        result = self._validate_form()
        if not result:
            return
        
        data, date_str = result
        
        # Hỏi nơi lưu file
        ho_ten_safe = "".join(c for c in data["ho_ten"] if c.isalnum() or c in (' ', '_')).strip()
        if not ho_ten_safe:
            ho_ten_safe = "quy_y"
        
        filepath = filedialog.asksaveasfilename(
            title="Lưu file PDF",
            initialfile=f"{ho_ten_safe}.pdf",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            parent=self
        )
        
        if not filepath:
            return
        
        try:
            # Set ngày quy y tạm
            old_state = self._prepare_config_with_date(date_str)
            
            try:
                # Tạo PDF
                self.pdf_service.generator.register_font()
                self.pdf_service.generator.create_single_pdf(
                    data,
                    filepath,
                    field_positions=self.config_manager.field_positions,
                    custom_fields=self.config_manager.custom_fields,
                    use_vni=getattr(self.config_manager, "use_vni_font", True),
                    use_background=getattr(self.config_manager, "use_background_image", False)
                )
                
                messagebox.showinfo(
                    "Thành công", 
                    f"✅ Đã xuất PDF thành công!\n\n📄 {os.path.basename(filepath)}\n📁 {os.path.dirname(filepath)}",
                    parent=self
                )
                
                # Mở thư mục chứa file
                self.pdf_service.open_output_folder(os.path.dirname(filepath))
                
            finally:
                # Luôn khôi phục ngày cũ
                self._restore_config_date(old_state)
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất PDF:\n{str(e)}", parent=self)
    
    def _on_print(self):
        """In trực tiếp từ dữ liệu nhập tay"""
        result = self._validate_form()
        if not result:
            return
        
        data, date_str = result
        
        if not messagebox.askyesno("Xác nhận in", 
            f"Bạn có muốn in lá phái cho:\n\n"
            f"👤 {data['ho_ten']}\n"
            f"{'📿 ' + data['phap_danh'] if data['phap_danh'] else ''}\n\n"
            f"Ngày quy y: {date_str}",
            parent=self
        ):
            return
        
        try:
            # Set ngày quy y tạm
            old_state = self._prepare_config_with_date(date_str)
            
            try:
                # Tạo temp PDF
                temp_dir = tempfile.mkdtemp()
                temp_path = os.path.join(temp_dir, "quick_print.pdf")
                
                self.pdf_service.generator.register_font()
                self.pdf_service.generator.create_single_pdf(
                    data,
                    temp_path,
                    field_positions=self.config_manager.field_positions,
                    custom_fields=self.config_manager.custom_fields,
                    use_vni=getattr(self.config_manager, "use_vni_font", True),
                    use_background=getattr(self.config_manager, "use_background_image", False)
                )
                
                # Lấy tên máy in
                printer_name = None
                if self.get_printer:
                    printer_name = self.get_printer()
                
                # Gửi in
                self.pdf_service.print_file(temp_path, printer_name)
                
                messagebox.showinfo(
                    "Đã gửi in",
                    f"✅ Đã gửi lệnh in thành công!\n\n"
                    f"👤 {data['ho_ten']}\n"
                    f"🖨️ {printer_name or 'Máy in mặc định'}",
                    parent=self
                )
                
            finally:
                self._restore_config_date(old_state)
                # Cleanup temp
                try:
                    import shutil
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except:
                    pass
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể in:\n{str(e)}", parent=self)
