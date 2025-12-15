# -*- coding: utf-8 -*-
import json
import os
import copy
from config import FIELD_POSITIONS, CUSTOM_FIELDS, EXCEL_FIELD_MAPPING

class ConfigManager:
    """Quản lý cấu hình ứng dụng (Field positions, Custom fields, Mapping)"""
    
    def __init__(self, config_file="field_config.json"):
        self.config_file = config_file
        # Initialize with defaults
        self.field_positions = copy.deepcopy(FIELD_POSITIONS)
        self.custom_fields = copy.deepcopy(CUSTOM_FIELDS)
        self.excel_mapping = copy.deepcopy(EXCEL_FIELD_MAPPING)
        
        # Try loading from file
        self.load()

    def load(self):
        """Load configuration from JSON file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                if "field_positions" in config:
                    self.field_positions = config["field_positions"]
                if "custom_fields" in config:
                    self.custom_fields = config["custom_fields"]
                if "excel_mapping" in config:
                    self.excel_mapping = config["excel_mapping"]
                return True
            except Exception as e:
                print(f"Lỗi khi load config: {e}")
                raise e
        return False
    
    def load_from_file(self, filepath):
        """Load configuration from a specific JSON file"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            if "field_positions" in config:
                self.field_positions = config["field_positions"]
            if "custom_fields" in config:
                self.custom_fields = config["custom_fields"]
            if "excel_mapping" in config:
                self.excel_mapping = config["excel_mapping"]
            return True
        except Exception as e:
            raise e

    def save(self):
        """Save configuration to JSON file"""
        config = {
            "field_positions": self.field_positions,
            "custom_fields": self.custom_fields,
            "excel_mapping": self.excel_mapping
        }
        
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise e

    def reset_to_defaults(self):
        """Reset configuration to defaults defined in config.py"""
        self.field_positions = copy.deepcopy(FIELD_POSITIONS)
        self.custom_fields = copy.deepcopy(CUSTOM_FIELDS)
        self.excel_mapping = copy.deepcopy(EXCEL_FIELD_MAPPING)
        
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

    def delete_custom_field(self, name):
        if name in self.custom_fields:
            del self.custom_fields[name]
