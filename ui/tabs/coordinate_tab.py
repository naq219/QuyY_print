# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

class CoordinateTab(tk.Frame):
    def __init__(self, parent, config_manager, status_var):
        super().__init__(parent)
        self.config_manager = config_manager
        self.status_var = status_var
        
        self._build_ui()
        self.refresh()
        
    def _build_ui(self):
        # Instructions
        tk.Label(
            self,
            text="Double-click vào ô để chỉnh sửa giá trị. Nhấn Enter để xác nhận.",
            font=("Arial", 10),
            fg="#7f8c8d"
        ).pack(anchor=tk.W, pady=(10, 10), padx=10)
        
        # Treeview
        columns = ("Field", "X (mm)", "Y (mm)", "Size", "Bold", "Italic", "Align")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=12)
        
        for col in columns:
            self.tree.heading(col, text=col)
            width = 100 if col == "Field" else 70
            self.tree.column(col, width=width, anchor=tk.CENTER)
            
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10, padx=(0, 10))
        
        self.tree.bind("<Double-1>", self._on_double_click)
        
    def refresh(self):
        """Reload data from config manager"""
        # Clear
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add
        positions = self.config_manager.field_positions
        for field_name, field_config in positions.items():
            self.tree.insert("", tk.END, iid=field_name, values=(
                field_name,
                field_config.get("x", 0),
                field_config.get("y", 0),
                field_config.get("size", 12),
                "✓" if field_config.get("bold", False) else "",
                "✓" if field_config.get("italic", False) else "",
                field_config.get("align", "L")
            ))
            
    def _on_double_click(self, event):
        item = self.tree.selection()
        if not item: return
        
        field_name = item[0]
        column = self.tree.identify_column(event.x)
        col_index = int(column[1:]) - 1
        
        if col_index == 0: return # Name not editable
        
        # Current data
        field_data = self.config_manager.field_positions[field_name]
        col_keys = ["Field", "x", "y", "size", "bold", "italic", "align"]
        key = col_keys[col_index]
        
        if key in ("bold", "italic"):
            # Toggle
            field_data[key] = not field_data.get(key, False)
        elif key == "align":
            # Cycle
            aligns = ["L", "C", "R"]
            curr = field_data.get("align", "L")
            idx = aligns.index(curr) if curr in aligns else 0
            field_data["align"] = aligns[(idx + 1) % 3]
        else:
            # Edit
            curr = field_data.get(key, 0)
            new_val = simpledialog.askfloat(
                "Chỉnh sửa", 
                f"Giá trị mới cho {key}:", 
                initialvalue=float(curr)
            )
            if new_val is not None:
                if key == "size":
                    field_data[key] = int(new_val)
                else:
                    field_data[key] = new_val
        
        self.refresh()
        self.status_var.set(f"Đã cập nhật {field_name}.{key}")
