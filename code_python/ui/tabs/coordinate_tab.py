# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
from PIL import Image, ImageTk
import os
import shutil

from core.resource_manager import get_app_dir, get_phoimau_path
from core.resource_manager import get_font_path
from ui.components.toast import ToastNotification

# Constants
A4_WIDTH_MM = 297
A4_HEIGHT_MM = 210
SCALE = 2.5  # Pixels per mm
CANVAS_WIDTH = int(A4_WIDTH_MM * SCALE)
CANVAS_HEIGHT = int(A4_HEIGHT_MM * SCALE)

SAMPLE_DATA = {
    "phap_danh": "Pháp danh",
    "ho_ten": "Họ tên",
    "sinh_nam": "Năm sinh",
    "dia_chi": "Địa chỉ (vd xóm 3, xã Nam Sơn, huyện Nam Sơn, tỉnh Hưng Yên)",
    "ngay_duong": "Ngày DL",
    "thang_duong": "Tháng DL",
    "nam_duong": "Năm DL",
    "ngay_am": "Ngày AL",
    "thang_am": "Tháng AL",
    "nam_am": "Năm AL",
    "phat_lich": "PLịch"
}

class CoordinateTab(tk.Frame):
    # Số pixel di chuyển khi bấm phím mũi tên
    ARROW_MOVE_PX = 1
    
    def __init__(self, parent, config_manager, status_var):
        super().__init__(parent)
        self.config_manager = config_manager
        self.status_var = status_var
        self.bg_image = None
        self.tk_bg_image = None
        # Field đang được chọn (highlight) để điều khiển bằng phím
        self.selected_item = None
        self.selected_field = None
        
        # Multi-select: {field_name: canvas_item_id}
        self.selected_items = {}
        
        # Load custom font
        self.custom_font_family = self._load_custom_font()
        
        self._build_ui()
        self.refresh()
        
    def _load_custom_font(self):
        """Load font TTF vào hệ thống (Windows) để dùng trong canvas"""
        try:
            font_path = get_font_path()
            if not font_path or not os.path.exists(font_path):
                return None
            
            # Detect font family name from TTF file
            from PIL import ImageFont
            pil_font = ImageFont.truetype(font_path, 12)
            font_family = pil_font.getname()[0]  # e.g. "VNI-Commerce"
            
            # Windows: Load font privately into process
            import platform
            if platform.system() == "Windows":
                import ctypes
                # FR_PRIVATE = 0x10 — font only available to this process
                result = ctypes.windll.gdi32.AddFontResourceExW(font_path, 0x10, 0)
                if result > 0:
                    print(f"[CoordinateTab] Loaded font: {font_family} from {font_path}")
                    return font_family
                else:
                    print(f"[CoordinateTab] Failed to load font via AddFontResourceEx")
                    return None
            else:
                # Linux/Mac: tkinter usually can find system fonts
                return font_family
                
        except Exception as e:
            print(f"[CoordinateTab] Error loading custom font: {e}")
            return None
        
    def _build_ui(self):
        # 1. Canvas Area
        canvas_frame = tk.Frame(self)
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(canvas_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="#e0e0e0", relief="sunken", borderwidth=1)
        self.canvas.pack(anchor=tk.CENTER)
        
        self._load_bg()
        
        # 2. Controls
        controls_frame = tk.LabelFrame(self, text="Danh sách Fields (Click chọn, Ctrl+Click chọn nhiều, phím mũi tên di chuyển)", height=200)
        controls_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        columns = ("Field", "X", "Y", "Size", "Align")
        self.tree = ttk.Treeview(controls_frame, columns=columns, show="headings", height=6)
        
        for col in columns:
            self.tree.heading(col, text=col)
            width = 80 if col != "Field" else 120
            self.tree.column(col, width=width, anchor=tk.CENTER)
            
        scrollbar = ttk.Scrollbar(controls_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Click vào field để chọn, Ctrl+Click để chọn nhiều
        self.canvas.tag_bind("field", "<ButtonPress-1>", self.on_press)
        # Click vào vùng trống để bỏ chọn
        self.canvas.bind("<ButtonPress-1>", self._on_canvas_click)
        self.tree.bind("<Double-1>", self._on_tree_edit)
        
        # Bindings cho phím mũi tên (điều khiển field đã chọn)
        self.canvas.bind("<Left>", self.on_arrow_key)
        self.canvas.bind("<Right>", self.on_arrow_key)
        self.canvas.bind("<Up>", self.on_arrow_key)
        self.canvas.bind("<Down>", self.on_arrow_key)
        self.canvas.bind("<Escape>", self.on_deselect)
        
        # Ctrl+A để chọn tất cả
        self.canvas.bind("<Control-a>", lambda e: self._select_all())
        self.canvas.bind("<Control-A>", lambda e: self._select_all())
        
        # Cho phép canvas nhận focus
        self.canvas.config(takefocus=True)
        
        # Toolbar buttons (dạng dọc, bên phải)
        toolbar = tk.Frame(canvas_frame, bg="#ecf0f1", padx=5, pady=5)
        toolbar.place(relx=1.0, rely=0.0, anchor=tk.NE)
        
        # Title
        tk.Label(toolbar, text="🛠️ Công cụ", font=("Arial", 9, "bold"), bg="#ecf0f1").pack(pady=(0, 5))
        
        # Button thay đổi ảnh nền
        tk.Button(toolbar, text="🖼️ Ảnh nền", command=self._select_bg_image, font=("Arial", 8), width=14).pack(pady=2)
        
        # Separator
        ttk.Separator(toolbar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # Hướng dẫn phím tắt
        tk.Label(toolbar, text="Chọn field:", font=("Arial", 8, "bold"), bg="#ecf0f1").pack(pady=(0, 2))
        tk.Label(toolbar, text="Click: chọn 1", font=("Arial", 7), bg="#ecf0f1", fg="#666").pack()
        tk.Label(toolbar, text="Ctrl+Click: nhiều", font=("Arial", 7), bg="#ecf0f1", fg="#666").pack()
        tk.Label(toolbar, text="Ctrl+A: tất cả", font=("Arial", 7), bg="#ecf0f1", fg="#666").pack()
        
        
        # Separator
        ttk.Separator(toolbar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # Button lưu cấu hình
        tk.Button(toolbar, text="💾 Lưu cấu hình", command=self._save_config, font=("Arial", 8, "bold"), bg="#27ae60", fg="white", width=14).pack(pady=2)
        
        # Separator
        ttk.Separator(toolbar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # Button in thử
        tk.Button(toolbar, text="🖨️ In thử", command=self._test_print, font=("Arial", 8, "bold"), bg="#e67e22", fg="white", width=14).pack(pady=2)

    def _load_bg(self):
        self.canvas.delete("bg") # Clear old bg
        self.canvas.delete("select_bg")
        
        # Lấy thư mục app (thư mục chứa exe)
        app_dir = get_app_dir()
        
        # Search for phoimau.png / jpg trong thư mục app
        found_bg = None
        for ext in [".png", ".jpg", ".jpeg"]:
            path = os.path.join(app_dir, f"phoimau{ext}")
            if os.path.exists(path):
                found_bg = path
                break
        
        if found_bg:
            try:
                img = Image.open(found_bg)
                img = img.resize((CANVAS_WIDTH, CANVAS_HEIGHT), Image.Resampling.LANCZOS)
                self.tk_bg_image = ImageTk.PhotoImage(img)
                self.canvas.create_image(0, 0, image=self.tk_bg_image, anchor=tk.NW, tags="bg")
                self.canvas.tag_lower("bg") # Ensure it's at bottom
            except Exception as e:
                print(f"Error loading bg: {e}")
                self._draw_bg_placeholder()
        else:
            self._draw_bg_placeholder()
            
    def _draw_bg_placeholder(self):
        cx, cy = CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2
        text_id = self.canvas.create_text(cx, cy, text="Chưa có ảnh nền 'phoimau.png'.\nClick để chọn ảnh...", 
                                font=("Arial", 14), fill="#555", tags="select_bg")
        self.canvas.tag_bind("select_bg", "<Button-1>", self._select_bg_image)

    def _select_bg_image(self, event=None):
        path = filedialog.askopenfilename(title="Chọn ảnh nền phôi", filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if path:
            ext = os.path.splitext(path)[1].lower()
            # Valid ext?
            if ext not in [".png", ".jpg", ".jpeg"]:
                messagebox.showerror("Lỗi", "Chỉ hỗ trợ file ảnh png, jpg.")
                return
            
            # Lưu file vào thư mục app (cùng thư mục exe)
            app_dir = get_app_dir()
            dest = os.path.join(app_dir, f"phoimau{ext}")
            
            try:
                # Remove old files if mismatch ext
                for old_ext in [".png", ".jpg", ".jpeg"]:
                    old_path = os.path.join(app_dir, f"phoimau{old_ext}")
                    if os.path.exists(old_path) and old_path != dest:
                        os.remove(old_path)
                
                shutil.copy2(path, dest)
                self.status_var.set("Đã cập nhật ảnh nền.")
                self._load_bg()
                self.refresh() # Redraw fields on top
            except Exception as e:
                messagebox.showerror("Lỗi copy file", str(e))

    def refresh(self):
        self.canvas.delete("field")
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Draw Standard
        for name, conf in self.config_manager.field_positions.items():
            self._draw_field(name, conf, is_custom=False)
            
        # Draw Custom
        for name, conf in self.config_manager.custom_fields.items():
            self._draw_field(name, conf, is_custom=True)
            
        self.canvas.tag_raise("field")

    def _draw_field(self, name, conf, is_custom=False):
        x_mm = conf.get("x", 0)
        y_mm = conf.get("y", 0)
        size = conf.get("size", 12)
        align = conf.get("align", "L")
        
        x_px = x_mm * SCALE
        y_px = y_mm * SCALE
        
        # Xác định text hiển thị
        if is_custom:
            # Custom field: ưu tiên value, nếu rỗng thì hiển thị [tên field]
            value = conf.get("value", "")
            if value and str(value).strip():
                text = str(value)
            else:
                text = f"[{name}]"  # Hiển thị tên field trong ngoặc vuông khi chưa có value
        else:
            # Field tiêu chuẩn: dùng sample data hoặc tên field
            text = SAMPLE_DATA.get(name, name)
            
        anchor = tk.SW  # Tọa độ baseline-left (khớp PDF drawString)
        if align == "C": anchor = tk.S
        elif align == "R": anchor = tk.SE
        
        # Chọn font và convert text tùy theo cài đặt VNI
        use_vni = getattr(self.config_manager, "use_vni_font", True)
        
        if use_vni and self.custom_font_family:
            # VNI font: convert text sang VNI encoding
            from core.utils import convert_unicode_to_vni
            display_text = convert_unicode_to_vni(text)
            font_family = self.custom_font_family
        else:
            # Unicode font: dùng Arial
            display_text = text
            font_family = "Arial"
        
        display_size = int(size * 0.8)
        
        # Tính descent để chuyển từ baseline sang bottom (khớp với PDF drawString)
        # PDF drawString đặt text tại baseline, tkinter SW đặt tại đáy chữ
        # Cần dịch y_px xuống thêm descent để baseline nằm đúng vị trí y_mm
        import tkinter.font as tkFont
        try:
            tk_f = tkFont.Font(family=font_family, size=display_size)
            descent = tk_f.metrics("descent")
        except Exception:
            descent = int(display_size * 0.25)
        
        self.canvas.create_text(
            x_px, y_px + descent, 
            text=display_text, 
            font=(font_family, display_size), 
            fill="blue" if not is_custom else "red",
            anchor=anchor,
            tags=("field", name)
        )
        
        self.tree.insert("", tk.END, iid=name, values=(name, f"{x_mm:.1f}", f"{y_mm:.1f}", size, align))

    def on_press(self, event):
        """Click vào field để chọn, Ctrl+Click để chọn/bỏ chọn nhiều"""
        item = self.canvas.find_closest(event.x, event.y)[0]
        tags = self.canvas.gettags(item)
        if "field" not in tags:
            return
        
        # Tìm tên field
        field_name = None
        for tag in tags:
            if tag != "field" and tag != "current":
                field_name = tag
                break
        
        if not field_name:
            return
        
        ctrl_pressed = event.state & 0x4  # Ctrl key
        
        if ctrl_pressed:
            # Ctrl+Click: toggle chọn/bỏ chọn field này (multi-select)
            if field_name in self.selected_items:
                # Đang chọn rồi -> bỏ chọn
                self._unhighlight_field(item, field_name)
                del self.selected_items[field_name]
                # Nếu cũng là selected_item đơn, bỏ nó
                if self.selected_field == field_name:
                    self.selected_item = None
                    self.selected_field = None
            else:
                # Thêm vào danh sách chọn
                self.selected_items[field_name] = item
                self.canvas.itemconfig(item, fill="#00ff00")
            
            self.status_var.set(f"Đã chọn {len(self.selected_items)} field - Dùng phím mũi tên để di chuyển")
        else:
            # Click thường: chọn đơn (bỏ chọn tất cả trước)
            self._deselect_all_silent()
            
            self.selected_item = item
            self.selected_field = field_name
            self.selected_items[field_name] = item
            self.canvas.itemconfig(item, fill="#00ff00")
            
            self.status_var.set(f"Đã chọn: {field_name} - Dùng phím mũi tên để di chuyển")
        
        # Focus vào canvas để nhận keyboard events
        self.canvas.focus_set()
    
    def _on_canvas_click(self, event):
        """Click vào vùng trống trên canvas -> bỏ chọn tất cả"""
        # Kiểm tra xem click có trúng field nào không
        items = self.canvas.find_overlapping(event.x - 2, event.y - 2, event.x + 2, event.y + 2)
        for item in items:
            tags = self.canvas.gettags(item)
            if "field" in tags:
                return  # Click trúng field, để on_press xử lý
        
        # Click vào vùng trống -> bỏ chọn tất cả
        self._deselect_all()
    
    def _deselect_all_silent(self):
        """Bỏ chọn tất cả nhưng không cập nhật status bar"""
        for field_name, item_id in self.selected_items.items():
            self._unhighlight_field(item_id, field_name)
        self.selected_items.clear()
        
        if self.selected_item and self.selected_field:
            self._unhighlight_field(self.selected_item, self.selected_field)
            self.selected_item = None
            self.selected_field = None
    
    def on_arrow_key(self, event):
        """Xử lý phím mũi tên để di chuyển field đã chọn"""
        # Xác định hướng di chuyển
        dx, dy = 0, 0
        if event.keysym == "Left":
            dx = -self.ARROW_MOVE_PX
        elif event.keysym == "Right":
            dx = self.ARROW_MOVE_PX
        elif event.keysym == "Up":
            dy = -self.ARROW_MOVE_PX
        elif event.keysym == "Down":
            dy = self.ARROW_MOVE_PX
        
        if self.selected_items:
            # Di chuyển tất cả field đã chọn
            for field_name, item_id in self.selected_items.items():
                self.canvas.move(item_id, dx, dy)
                
                # Cập nhật vị trí mới vào config
                coords = self.canvas.coords(item_id)
                if coords:
                    new_x_mm = round(coords[0] / SCALE, 1)
                    new_y_mm = round(coords[1] / SCALE, 1)
                    self._update_field_position(field_name, new_x_mm, new_y_mm)
            
            self.status_var.set(f"*Di chuyển {len(self.selected_items)} field - Chưa lưu*")
        elif self.selected_item and self.selected_field:
            # Di chuyển 1 field
            self.canvas.move(self.selected_item, dx, dy)
            
            # Cập nhật vị trí mới vào config
            coords = self.canvas.coords(self.selected_item)
            new_x_mm = round(coords[0] / SCALE, 1)
            new_y_mm = round(coords[1] / SCALE, 1)
            
            self._update_field_position(self.selected_field, new_x_mm, new_y_mm)
    
    def on_deselect(self, event=None):
        """Bỏ chọn field (nhấn Escape)"""
        self._deselect_all()
    
    def _unhighlight_field(self, item, field_name):
        """Trả lại màu gốc cho field"""
        is_custom = field_name in self.config_manager.custom_fields
        original_color = "red" if is_custom else "blue"
        try:
            self.canvas.itemconfig(item, fill=original_color)
        except:
            pass
    

    
    def _select_all(self):
        """Chọn tất cả các field (Ctrl+A)"""
        
        # Xóa selection cũ
        self.selected_items.clear()
        
        # Tìm tất cả canvas items có tag "field"
        all_items = self.canvas.find_withtag("field")
        
        for item in all_items:
            tags = self.canvas.gettags(item)
            field_name = None
            for tag in tags:
                if tag != "field" and tag != "current":
                    field_name = tag
                    break
            
            if field_name:
                self.selected_items[field_name] = item
                self.canvas.itemconfig(item, fill="#00ff00")  # Highlight
        
        self.canvas.focus_set()
        self.status_var.set(f"Đã chọn tất cả {len(self.selected_items)} field - Dùng phím mũi tên để di chuyển")
    
    def _deselect_all(self):
        """Bỏ chọn tất cả các field"""
        # Bỏ highlight tất cả field trong multi-select
        for field_name, item_id in self.selected_items.items():
            self._unhighlight_field(item_id, field_name)
        self.selected_items.clear()
        
        # Bỏ selection đơn
        if self.selected_item and self.selected_field:
            self._unhighlight_field(self.selected_item, self.selected_field)
            self.selected_item = None
            self.selected_field = None
        
        self.status_var.set("Đã bỏ chọn tất cả")
    
    def _save_config(self):
        """Lưu cấu hình"""
        try:
            self.config_manager.save()
            self.status_var.set("✅ Đã lưu cấu hình thành công!")
            ToastNotification.success(self, "Đã lưu cấu hình!")
        except Exception as e:
            if str(e) == "NEED_SAVE_AS":
                # Config mới chưa có đường dẫn, hỏi user chọn nơi lưu
                filepath = filedialog.asksaveasfilename(
                    title="Lưu file cấu hình",
                    defaultextension=".json",
                    initialfile="config.json",
                    filetypes=[("JSON Config", "*.json"), ("Tất cả file", "*.*")]
                )
                if filepath:
                    try:
                        self.config_manager.set_config_path(filepath)
                        self.config_manager.save()
                        self.status_var.set("✅ Đã lưu cấu hình thành công!")
                        ToastNotification.success(self, "Đã lưu cấu hình!")
                    except Exception as e2:
                        messagebox.showerror("Lỗi", f"Không thể lưu cấu hình: {str(e2)}")
            else:
                messagebox.showerror("Lỗi", f"Không thể lưu cấu hình: {str(e)}")

    
    def _update_field_position(self, field_name, new_x_mm, new_y_mm):
        """Cập nhật vị trí field vào config và lưu"""
        conf = None
        is_custom = False
        
        if field_name in self.config_manager.field_positions:
            conf = self.config_manager.field_positions[field_name]
        elif field_name in self.config_manager.custom_fields:
            conf = self.config_manager.custom_fields[field_name]
            is_custom = True
        
        if conf:
            conf["x"] = new_x_mm
            conf["y"] = new_y_mm
            
            # Cập nhật tree view
            try:
                self.tree.set(field_name, "X", f"{new_x_mm:.1f}")
                self.tree.set(field_name, "Y", f"{new_y_mm:.1f}")
            except:
                pass
            
            # Đánh dấu đã thay đổi (không auto-save)
            self.config_manager.mark_dirty()
            self.status_var.set(f"*Đã thay đổi {field_name}: ({new_x_mm}, {new_y_mm}) - Chưa lưu*")

    def _on_tree_edit(self, event):
        item = self.tree.selection()
        if not item: return
        name = item[0]
        col = self.tree.identify_column(event.x)
        idx = int(col[1:]) - 1
        
        if idx == 0: return 
        
        conf = None
        if name in self.config_manager.field_positions:
            conf = self.config_manager.field_positions[name]
        elif name in self.config_manager.custom_fields:
            conf = self.config_manager.custom_fields[name]
            
        if not conf: return
        
        col_map = ["name", "x", "y", "size", "align"]
        key = col_map[idx]
        current_val = conf.get(key)
        
        if key == "align":
            aligns = ["L", "C", "R"]
            curr = conf.get("align", "L")
            i = aligns.index(curr) if curr in aligns else 0
            conf["align"] = aligns[(i + 1) % 3]
        else:
            new_val = simpledialog.askfloat("Sửa", f"Nhập giá trị {key}:", initialvalue=float(current_val) if key in ["x","y","size"] else 0)
            if new_val is not None:
                if key == "size":
                    conf[key] = int(new_val)
                else:
                    conf[key] = new_val
        
        self.config_manager.mark_dirty()  # Đánh dấu thay đổi, không auto-save
        self.status_var.set(f"*Đã thay đổi - Chưa lưu*")
        self.refresh()

    def _test_print(self):
        """In thử 1 trang PDF mẫu với dữ liệu mẫu để kiểm tra toạ độ"""
        import tempfile
        import threading
        
        self.status_var.set("🖨️ Đang tạo bản in thử...")
        
        def _do_print():
            try:
                from core.pdf_generator import PDFGenerator
                from core.pdf_service import PDFService
                
                generator = PDFGenerator()
                pdf_service = PDFService()
                
                # Tạo dữ liệu mẫu
                sample_data = dict(SAMPLE_DATA)
                
                # Tạo file PDF tạm
                temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, prefix="quyy_test_")
                temp_path = temp_file.name
                temp_file.close()
                
                # Tạo PDF với toạ độ hiện tại
                use_vni = getattr(self.config_manager, "use_vni_font", True)
                use_background = getattr(self.config_manager, "use_background_image", False)
                generator.create_single_pdf(
                    sample_data,
                    temp_path,
                    field_positions=self.config_manager.field_positions,
                    custom_fields=self.config_manager.custom_fields,
                    use_vni=use_vni,
                    use_background=use_background
                )
                
                # In ra máy in mặc định
                pdf_service.print_file(temp_path, printer_name=None)
                
                # Cập nhật UI từ main thread
                self.after(0, lambda: self._on_test_print_done(True, "Đã gửi bản in thử ra máy in mặc định!"))
                
                # Xóa file tạm sau 10 giây (đợi máy in nhận xong)
                import time
                time.sleep(10)
                try:
                    os.remove(temp_path)
                except:
                    pass
                    
            except Exception as e:
                self.after(0, lambda: self._on_test_print_done(False, f"Lỗi in thử: {str(e)}"))
        
        thread = threading.Thread(target=_do_print, daemon=True)
        thread.start()
    
    def _on_test_print_done(self, success, message):
        """Callback sau khi in thử xong (gọi từ main thread)"""
        if success:
            self.status_var.set(f"✅ {message}")
            ToastNotification.success(self, f"🖨️ {message}")
        else:
            self.status_var.set(f"❌ {message}")
            ToastNotification.show(self, f"⚠️ {message}", bg_color="#e74c3c", position="bottom")

