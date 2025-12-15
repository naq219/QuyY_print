# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from ui.components.dialogs import CustomFieldDialog

class CustomFieldTab(tk.Frame):
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
            text="Thêm các trường tùy chỉnh với giá trị cố định (ví dụ: user = naq)",
            font=("Arial", 10),
            fg="#7f8c8d"
        ).pack(anchor=tk.W, pady=(10, 10), padx=10)
        
        # Treeview
        columns = ("Tên Field", "Giá Trị", "X (mm)", "Y (mm)", "Size", "Align")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.tree.heading(col, text=col)
            width = 100 if col in ("Tên Field", "Giá Trị") else 70
            self.tree.column(col, width=width, anchor=tk.CENTER)
            
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10, padx=(0, 10))
        
        self.tree.bind("<Double-1>", self._on_double_click)
        
        # Buttons
        btn_frame = tk.Frame(self.master.master if not hasattr(self, 'master') else self.master) 
        # Note: Button processing usually is in MainWindow or bottom of Tab.
        # In original app, buttons were at bottom of Tab.
        
        btn_frame = tk.Frame(self, padx=10, pady=10)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # We put buttons inside the tab for simplicity
        tk.Button(btn_frame, text="➕ Thêm Field", command=self._add, bg="#27ae60", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="✏️ Sửa Field", command=self._edit, bg="#f39c12", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🗑️ Xóa Field", command=self._delete, bg="#e74c3c", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        customs = self.config_manager.custom_fields
        for field_name, conf in customs.items():
            self.tree.insert("", tk.END, iid=field_name, values=(
                field_name,
                conf.get("value", ""),
                conf.get("x", 0),
                conf.get("y", 0),
                conf.get("size", 12),
                conf.get("align", "L")
            ))

    def _add(self):
        dialog = CustomFieldDialog(self, "Thêm Custom Field")
        if dialog.result:
            name, value, x, y, size, align = dialog.result
            try:
                self.config_manager.add_custom_field(name, value, x, y, size, align)
                self.refresh()
                self.status_var.set(f"Đã thêm: {name}")
            except ValueError as e:
                messagebox.showwarning("Lỗi", str(e))
                
    def _edit(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Cảnh báo", "Chọn field cần sửa!")
            return
        
        name = item[0]
        conf = self.config_manager.custom_fields[name]
        
        dialog = CustomFieldDialog(self, "Sửa Custom Field", initial=(
            name, conf.get("value"), conf.get("x"), conf.get("y"), conf.get("size"), conf.get("align")
        ))
        
        if dialog.result:
            new_name, value, x, y, size, align = dialog.result
            try:
                self.config_manager.update_custom_field(name, new_name, value, x, y, size, align)
                self.refresh()
                self.status_var.set(f"Đã sửa: {new_name}")
            except ValueError as e:
                messagebox.showwarning("Lỗi", str(e))

    def _delete(self):
        item = self.tree.selection()
        if not item: return
        name = item[0]
        if messagebox.askyesno("Xác nhận", f"Xóa field {name}?"):
            self.config_manager.delete_custom_field(name)
            self.refresh()
            self.status_var.set(f"Đã xóa: {name}")

    def _on_double_click(self, event):
        item = self.tree.selection()
        if not item: return
        
        # Trigger edit on double click
        self._edit()
