# -*- coding: utf-8 -*-
import json
import os
import copy
from config import FIELD_POSITIONS, CUSTOM_FIELDS, EXCEL_FIELD_MAPPING

FIELD_FILE = "field.txt"
CUSTOM_FILE = "field_custom.txt"

class ConfigManager:
    """Quản lý cấu hình ứng dụng (Field positions, Custom fields)"""
    
    def __init__(self):
        # Defaults
        self.field_positions = copy.deepcopy(FIELD_POSITIONS)
        self.excel_mapping = copy.deepcopy(EXCEL_FIELD_MAPPING) # Included with main fields
        self.custom_fields = copy.deepcopy(CUSTOM_FIELDS) # Defaults usually empty or from config
        
        self._init_files()
        self.load()

    def _init_files(self):
        """Khởi tạo file nếu chưa tồn tại"""
        # field.txt
        if not os.path.exists(FIELD_FILE):
            data = {
                "field_positions": self.field_positions,
                "excel_mapping": self.excel_mapping
            }
            self._save_file(FIELD_FILE, data)
            
        # field_custom.txt
        if not os.path.exists(CUSTOM_FILE):
            # Lưu nội dung rỗng (empty dict)
            self._save_file(CUSTOM_FILE, {})

    def load(self):
        """Load configuration from TXT files"""
        # Load Main Fields
        try:
            if os.path.exists(FIELD_FILE):
                with open(FIELD_FILE, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        data = json.loads(content)
                        if "field_positions" in data:
                            self.field_positions = data["field_positions"]
                        if "excel_mapping" in data:
                            self.excel_mapping = data["excel_mapping"]
        except Exception as e:
            print(f"Lỗi load {FIELD_FILE}: {e}")

        # Load Custom Fields
        try:
            if os.path.exists(CUSTOM_FILE):
                with open(CUSTOM_FILE, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        data = json.loads(content)
                        # Nếu file chỉ chứa dict của custom fields
                        if isinstance(data, dict):
                            self.custom_fields = data
        except Exception as e:
            print(f"Lỗi load {CUSTOM_FILE}: {e}")

    def save(self):
        """Save configuration to TXT files"""
        # Save Main Fields
        try:
            data = {
                "field_positions": self.field_positions,
                "excel_mapping": self.excel_mapping
            }
            self._save_file(FIELD_FILE, data)
        except Exception as e:
            raise Exception(f"Lỗi lưu {FIELD_FILE}: {e}")

        # Save Custom Fields
        try:
            self._save_file(CUSTOM_FILE, self.custom_fields)
        except Exception as e:
            raise Exception(f"Lỗi lưu {CUSTOM_FILE}: {e}")

    def _save_file(self, filepath, data):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.field_positions = copy.deepcopy(FIELD_POSITIONS)
        self.excel_mapping = copy.deepcopy(EXCEL_FIELD_MAPPING)
        self.custom_fields = {} # Reset custom fields to empty as requested "lưu file mặc định và nội dung rỗng"
        # Or should it reset to config.CUSTOM_FIELDS? User said "nội dung rỗng" for file creation.
        # I'll stick to empty for custom.
        self.save()

    def add_custom_field(self, name, value, x, y, size, align="L"):
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
        self.save() # Auto save

    def update_custom_field(self, old_name, new_name, value, x, y, size, align):
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
        self.save() # Auto save

    def delete_custom_field(self, name):
        if name in self.custom_fields:
            del self.custom_fields[name]
            self.save() # Auto save

    # Helper needed for MainWindow load_config dialog
    def load_from_file(self, filepath):
        """Load legacy json or new structure?"""
        # Simplification: Loading external config might overwrite everything.
        # Check struct
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
