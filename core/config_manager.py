# -*- coding: utf-8 -*-
"""
Config Manager - Quản lý cấu hình ứng dụng
Gộp field_positions, custom_fields, excel_mapping vào 1 file config.json duy nhất
File config được lưu cùng thư mục với file exe
"""

import json
import os
import copy
from config import FIELD_POSITIONS, CUSTOM_FIELDS, EXCEL_FIELD_MAPPING
from core.resource_manager import get_config_path, get_app_dir


class ConfigManager:
    """Quản lý cấu hình ứng dụng (Field positions, Custom fields)"""
    
    CONFIG_FILENAME = "config.json"
    
    def __init__(self):
        # Defaults
        self.field_positions = copy.deepcopy(FIELD_POSITIONS)
        self.excel_mapping = copy.deepcopy(EXCEL_FIELD_MAPPING)
        self.custom_fields = copy.deepcopy(CUSTOM_FIELDS)
        
        
        # Cấu hình encoding font
        self.use_vni_font = True
        
        # Dirty flag - theo dõi trạng thái thay đổi chưa lưu
        self._dirty = False
        
        # Lấy đường dẫn config file (cùng thư mục exe)
        self.config_path = get_config_path()
        
        # Khởi tạo và load config
        self._init_config()
        self.load()
    
    def mark_dirty(self):
        """Đánh dấu có thay đổi chưa lưu"""
        self._dirty = True
    
    def is_dirty(self):
        """Kiểm tra có thay đổi chưa lưu không"""
        return self._dirty
    
    def clear_dirty(self):
        """Xóa trạng thái dirty (sau khi lưu thành công)"""
        self._dirty = False

    def _init_config(self):
        """Khởi tạo file config nếu chưa tồn tại"""
        if not os.path.exists(self.config_path):
            print(f"[ConfigManager] Tạo file config mới: {self.config_path}")
            self._save_default_config()
    
    def _save_default_config(self):
        """Lưu config mặc định"""
        data = {
            "field_positions": self.field_positions,
            "excel_mapping": self.excel_mapping,
            "custom_fields": self.custom_fields,
            "use_vni_font": self.use_vni_font
        }
        self._save_file(self.config_path, data)

    def load(self):
        """Load configuration từ file config.json"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        data = json.loads(content)
                        
                        if "field_positions" in data:
                            self.field_positions = data["field_positions"]
                        if "excel_mapping" in data:
                            self.excel_mapping = data["excel_mapping"]
                        if "custom_fields" in data:
                            self.custom_fields = data["custom_fields"]
                        if "use_vni_font" in data:
                            self.use_vni_font = data["use_vni_font"]
                        # Backward compat check if needed, but not strictly required
                            
                print(f"[ConfigManager] Đã load config từ: {self.config_path}")
        except Exception as e:
            print(f"[ConfigManager] Lỗi load config: {e}")

    def save(self):
        """Save configuration to config.json"""
        try:
            data = {
                "field_positions": self.field_positions,
                "excel_mapping": self.excel_mapping,
                "custom_fields": self.custom_fields,
                "use_vni_font": self.use_vni_font
            }
            self._save_file(self.config_path, data)
            self.clear_dirty()  # Xóa dirty flag sau khi lưu thành công
            print(f"[ConfigManager] Đã lưu config: {self.config_path}")
        except Exception as e:
            raise Exception(f"Lỗi lưu config: {e}")

    def _save_file(self, filepath, data):
        """Lưu data dưới dạng JSON"""
        # Đảm bảo thư mục tồn tại
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.field_positions = copy.deepcopy(FIELD_POSITIONS)
        self.excel_mapping = copy.deepcopy(EXCEL_FIELD_MAPPING)
        self.custom_fields = {}  # Reset custom fields về rỗng
        self.save()

    def add_custom_field(self, name, value, x, y, size, align="L"):
        """Thêm custom field mới"""
        if name in self.custom_fields:
            raise ValueError(f"Field '{name}' đã tồn tại!")
            
        self.custom_fields[name] = {
            "value": value,
            "x": float(x),
            "y": float(y),
            "size": int(size),
            "bold": False,
            "italic": False,
            "align": align
        }
        self.mark_dirty()  # Đánh dấu đã thay đổi, không auto-save

    def update_custom_field(self, old_name, new_name, value, x, y, size, align):
        """Cập nhật custom field"""
        if new_name != old_name and new_name in self.custom_fields:
            raise ValueError(f"Field '{new_name}' đã tồn tại!")

        if new_name != old_name:
            del self.custom_fields[old_name]
            
        self.custom_fields[new_name] = {
            "value": value,
            "x": float(x),
            "y": float(y),
            "size": int(size),
            "bold": False,
            "italic": False,
            "align": align
        }
        self.mark_dirty()  # Đánh dấu đã thay đổi, không auto-save

    def delete_custom_field(self, name):
        """Xóa custom field"""
        if name in self.custom_fields:
            del self.custom_fields[name]
            self.mark_dirty()  # Đánh dấu đã thay đổi, không auto-save

    def load_from_file(self, filepath):
        """Load config từ file bên ngoài (import)"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Smart merge
            if "field_positions" in data:
                self.field_positions = data["field_positions"]
            if "custom_fields" in data:
                self.custom_fields = data["custom_fields"]
            if "excel_mapping" in data:
                self.excel_mapping = data["excel_mapping"]
                
            self.save()
            return True
        except Exception as e:
            raise e

    def export_to_file(self, filepath):
        """Export config ra file (cho việc backup/share)"""
        data = {
            "field_positions": self.field_positions,
            "excel_mapping": self.excel_mapping,
            "custom_fields": self.custom_fields,
            "use_vni_font": self.use_vni_font
        }
        self._save_file(filepath, data)
