# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
from PIL import Image, ImageTk
import os
import shutil

from core.resource_manager import get_app_dir, get_phoimau_path

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
        self.drag_data = {"x": 0, "y": 0, "item": None, "field": None}
        
        # Field đang được chọn (highlight) để điều khiển bằng phím
        self.selected_item = None
        self.selected_field = None
        
        self._build_ui()
        self.refresh()
        
    def _build_ui(self):
        # 1. Canvas Area
        canvas_frame = tk.Frame(self)
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(canvas_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="#e0e0e0", relief="sunken", borderwidth=1)
        self.canvas.pack(anchor=tk.CENTER)
        
        self._load_bg()
        
        # 2. Controls
        controls_frame = tk.LabelFrame(self, text="Danh sách Fields (Kéo thả trên hình hoặc sửa số liệu bên dưới)", height=200)
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
        
        # Bindings cho chuột
        self.canvas.tag_bind("field", "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind("field", "<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.tree.bind("<Double-1>", self._on_tree_edit)
        
        # Bindings cho phím mũi tên (điều khiển field đã chọn)
        # Bind vào canvas để nhận keyboard events
        self.canvas.bind("<Left>", self.on_arrow_key)
        self.canvas.bind("<Right>", self.on_arrow_key)
        self.canvas.bind("<Up>", self.on_arrow_key)
        self.canvas.bind("<Down>", self.on_arrow_key)
        self.canvas.bind("<Escape>", self.on_deselect)
        
        # Cho phép canvas nhận focus
        self.canvas.config(takefocus=True)
        
        # Context menu for BG? Or Button? Click logic handles it if missing.
        # Add a button just in case
        btn = tk.Button(canvas_frame, text="Thay đổi Ảnh Nền", command=self._select_bg_image, font=("Arial", 8))
        btn.place(relx=1.0, rely=0.0, anchor=tk.NE)

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
        
        text = SAMPLE_DATA.get(name, conf.get("value", name))
        if is_custom:
            text = conf.get("value", name)
            
        anchor = tk.SW  # Tọa độ là điểm dưới cùng bên trái
        if align == "C": anchor = tk.S  # Giữa dưới
        elif align == "R": anchor = tk.SE  # Dưới cùng bên phải
        
        self.canvas.create_text(
            x_px, y_px, 
            text=text, 
            font=("Arial", int(size * 0.8), "bold" if is_custom else "normal"), 
            fill="blue" if not is_custom else "red",
            anchor=anchor,
            tags=("field", name)
        )
        
        self.tree.insert("", tk.END, iid=name, values=(name, f"{x_mm:.1f}", f"{y_mm:.1f}", size, align))

    def on_press(self, event):
        item = self.canvas.find_closest(event.x, event.y)[0]
        tags = self.canvas.gettags(item)
        if "field" in tags:
            # Bỏ highlight field cũ (nếu có)
            if self.selected_item and self.selected_item != item:
                self._unhighlight_field(self.selected_item, self.selected_field)
            
            self.drag_data["item"] = item
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            
            # Tìm tên field
            field_name = None
            for tag in tags:
                if tag != "field" and tag != "current":
                    field_name = tag
                    break
            
            self.drag_data["field"] = field_name
            
            # Highlight và lưu selection để điều khiển bằng phím
            self.selected_item = item
            self.selected_field = field_name
            self.canvas.itemconfig(item, fill="#00ff00")  # Highlight màu xanh lá
            
            # Focus vào canvas để nhận keyboard events
            self.canvas.focus_set()
            
            self.status_var.set(f"Đã chọn: {field_name} - Dùng phím mũi tên để di chuyển")

    def on_drag(self, event):
        item = self.drag_data["item"]
        if item:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            self.canvas.move(item, dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def on_release(self, event):
        item = self.drag_data["item"]
        name = self.drag_data["field"]
        
        if item and name:
            coords = self.canvas.coords(item)
            new_x_mm = round(coords[0] / SCALE, 1)
            new_y_mm = round(coords[1] / SCALE, 1)
            
            self._update_field_position(name, new_x_mm, new_y_mm)

        # Reset drag data nhưng GIỮ NGUYÊN selection để có thể dùng phím mũi tên
        self.drag_data["item"] = None
        self.drag_data["field"] = None
    
    def on_arrow_key(self, event):
        """Xử lý phím mũi tên để di chuyển field đã chọn"""
        if not self.selected_item or not self.selected_field:
            return
        
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
        
        # Di chuyển item trên canvas
        self.canvas.move(self.selected_item, dx, dy)
        
        # Cập nhật vị trí mới vào config
        coords = self.canvas.coords(self.selected_item)
        new_x_mm = round(coords[0] / SCALE, 1)
        new_y_mm = round(coords[1] / SCALE, 1)
        
        self._update_field_position(self.selected_field, new_x_mm, new_y_mm)
    
    def on_deselect(self, event=None):
        """Bỏ chọn field (nhấn Escape)"""
        if self.selected_item and self.selected_field:
            self._unhighlight_field(self.selected_item, self.selected_field)
            self.selected_item = None
            self.selected_field = None
            self.status_var.set("Đã bỏ chọn field")
    
    def _unhighlight_field(self, item, field_name):
        """Trả lại màu gốc cho field"""
        is_custom = field_name in self.config_manager.custom_fields
        original_color = "red" if is_custom else "blue"
        try:
            self.canvas.itemconfig(item, fill=original_color)
        except:
            pass
    
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
