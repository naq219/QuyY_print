# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from PIL import Image, ImageTk
import os

# Constants
A4_WIDTH_MM = 297
A4_HEIGHT_MM = 210
SCALE = 2.5  # Pixels per mm
CANVAS_WIDTH = int(A4_WIDTH_MM * SCALE)
CANVAS_HEIGHT = int(A4_HEIGHT_MM * SCALE)

SAMPLE_DATA = {
    "phap_danh": "TÂM AN",
    "ho_ten": "NGUYỄN VĂN A",
    "sinh_nam": "1990",
    "dia_chi": "Hà Nội, Việt Nam",
    "ngay_duong": "15",
    "thang_duong": "07",
    "nam_duong": "2025",
    "ngay_am": "15",
    "thang_am": "06",
    "nam_am": "Ất Tỵ",
    "phat_lich": "2569"
}

class CoordinateTab(tk.Frame):
    def __init__(self, parent, config_manager, status_var):
        super().__init__(parent)
        self.config_manager = config_manager
        self.status_var = status_var
        self.bg_image = None
        self.tk_bg_image = None
        self.drag_data = {"x": 0, "y": 0, "item": None, "field": None}
        
        self._build_ui()
        self.refresh()
        
    def _build_ui(self):
        # 1. Canvas Area
        canvas_frame = tk.Frame(self)
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Center the canvas
        self.canvas = tk.Canvas(canvas_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="#e0e0e0", relief="sunken", borderwidth=1)
        self.canvas.pack(anchor=tk.CENTER)
        
        self._load_bg()
        
        # 2. Controls / List Area
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
        
        # Bindings
        self.canvas.tag_bind("field", "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind("field", "<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.tree.bind("<Double-1>", self._on_tree_edit)

    def _load_bg(self):
        bg_path = os.path.join("file", "bg_template.png")
        if os.path.exists(bg_path):
            try:
                img = Image.open(bg_path)
                img = img.resize((CANVAS_WIDTH, CANVAS_HEIGHT), Image.Resampling.LANCZOS)
                self.tk_bg_image = ImageTk.PhotoImage(img)
                self.canvas.create_image(0, 0, image=self.tk_bg_image, anchor=tk.NW, tags="bg")
            except Exception as e:
                print(f"Error loading bg: {e}")
                self.canvas.create_text(CANVAS_WIDTH//2, CANVAS_HEIGHT//2, text="No Background Image")
        else:
            self.canvas.create_text(CANVAS_WIDTH//2, CANVAS_HEIGHT//2, text="File ảnh nền không tồn tại\nfile/bg_template.png")

    def refresh(self):
        self.canvas.delete("field")
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Standard
        for name, conf in self.config_manager.field_positions.items():
            self._draw_field(name, conf, is_custom=False)
            
        # Custom
        for name, conf in self.config_manager.custom_fields.items():
            self._draw_field(name, conf, is_custom=True)
            
        # Raise fields to top
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
            
        anchor = tk.NW
        if align == "C": anchor = tk.N
        elif align == "R": anchor = tk.NE
        
        item_id = self.canvas.create_text(
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
            self.drag_data["item"] = item
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            for tag in tags:
                if tag != "field" and tag != "current":
                    self.drag_data["field"] = tag
                    break
            self.canvas.itemconfig(item, fill="#00ff00") # Highlight drag

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
            
            # Update config
            conf = None
            is_custom = False
            if name in self.config_manager.field_positions:
                conf = self.config_manager.field_positions[name]
            elif name in self.config_manager.custom_fields:
                conf = self.config_manager.custom_fields[name]
                is_custom = True
            
            if conf:
                conf["x"] = new_x_mm
                conf["y"] = new_y_mm
                
                self.canvas.itemconfig(item, fill="blue" if not is_custom else "red")
                self.tree.set(name, "X", f"{new_x_mm:.1f}")
                self.tree.set(name, "Y", f"{new_y_mm:.1f}")
                self.status_var.set(f"Cập nhật {name}: ({new_x_mm}, {new_y_mm})")

        self.drag_data["item"] = None
        self.drag_data["field"] = None

    def _on_tree_edit(self, event):
        item = self.tree.selection()
        if not item: return
        name = item[0]
        col = self.tree.identify_column(event.x)
        idx = int(col[1:]) - 1
        
        if idx == 0: return # Name
        
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
        
        # Refresh to update canvas
        self.refresh()
