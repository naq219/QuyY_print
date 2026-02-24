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
from core.lunar_converter import LunarConverter


class ConfigManager:
    """Quản lý cấu hình ứng dụng (Field positions, Custom fields)"""
    
    CONFIG_FILENAME = "config.json"
    
    def __init__(self, config_path=None):
        """
        Args:
            config_path: Đường dẫn file config.
                - Nếu là đường dẫn file -> load config từ file đó
                - Nếu None -> tạo config mới với giá trị mặc định (chưa lưu)
        """
        # Defaults
        self.field_positions = copy.deepcopy(FIELD_POSITIONS)
        self.excel_mapping = copy.deepcopy(EXCEL_FIELD_MAPPING)
        self.custom_fields = copy.deepcopy(CUSTOM_FIELDS)
        
        # Ngày quy y được chọn (dạng YYYY-MM-DD hoặc None)
        self.selected_date = None
        
        # Cấu hình encoding font
        self.use_vni_font = True
        
        # Chế độ xuất PDF: "single" (1 file) hoặc "multiple" (nhiều file)
        self.export_mode = "single"
        
        # Dirty flag - theo dõi trạng thái thay đổi chưa lưu
        self._dirty = False
        
        # Config path & trạng thái "tạo mới"
        self.config_path = config_path
        self.is_new_config = (config_path is None)  # True = chưa có file, cần save_as
        
        # Load config nếu có file
        if self.config_path and os.path.exists(self.config_path):
            self.load()
            print(f"[ConfigManager] Đã load config từ: {self.config_path}")
        else:
            if self.is_new_config:
                print("[ConfigManager] Tạo config mới (chưa lưu)")
            else:
                print(f"[ConfigManager] File config không tồn tại: {self.config_path}")
    
    def has_config_path(self):
        """Kiểm tra đã có đường dẫn file config chưa"""
        return self.config_path is not None
    
    def set_config_path(self, path):
        """Set đường dẫn file config (dùng khi save_as)"""
        self.config_path = path
        self.is_new_config = False
    
    def mark_dirty(self):
        """Đánh dấu có thay đổi chưa lưu"""
        self._dirty = True
    
    def is_dirty(self):
        """Kiểm tra có thay đổi chưa lưu không"""
        return self._dirty
    
    def clear_dirty(self):
        """Xóa trạng thái dirty (sau khi lưu thành công)"""
        self._dirty = False
    
    def _save_default_config(self):
        """Lưu config mặc định"""
        data = {
            "field_positions": self.field_positions,
            "excel_mapping": self.excel_mapping,
            "custom_fields": self.custom_fields,
            "use_vni_font": self.use_vni_font,
            "export_mode": self.export_mode
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
                        # selected_date không load từ config - luôn trống khi khởi động
                        # self.selected_date giữ nguyên None
                        if "use_vni_font" in data:
                            self.use_vni_font = data["use_vni_font"]
                        if "export_mode" in data:
                            self.export_mode = data["export_mode"]
                        # Backward compat check if needed, but not strictly required
                            
                print(f"[ConfigManager] Đã load config từ: {self.config_path}")
        except Exception as e:
            print(f"[ConfigManager] Lỗi load config: {e}")

    def save(self):
        """Save configuration to file
        
        Raises:
            Exception nếu chưa có config_path (cần gọi set_config_path trước)
        """
        if not self.config_path:
            raise Exception("NEED_SAVE_AS")  # Signal cho UI biết cần hỏi user chọn nơi lưu
        
        try:
            data = {
                "field_positions": self.field_positions,
                "excel_mapping": self.excel_mapping,
                "custom_fields": self.custom_fields,
                "use_vni_font": self.use_vni_font,
                "export_mode": self.export_mode
            }
            self._save_file(self.config_path, data)
            self.clear_dirty()
            self.is_new_config = False
            print(f"[ConfigManager] Đã lưu config: {self.config_path}")
        except Exception as e:
            if str(e) == "NEED_SAVE_AS":
                raise
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
        self.selected_date = None
        self.save()

    def set_selected_date(self, date_str):
        """
        Đặt ngày quy y được chọn và cập nhật các custom fields tương ứng
        
        Args:
            date_str: Ngày dạng "YYYY-MM-DD" hoặc None để xóa
        """
        self.selected_date = date_str
        self._update_date_fields_from_selected_date()

    def _update_date_fields_from_selected_date(self):
        """Cập nhật các custom fields ngày tháng từ selected_date"""
        if self.selected_date:
            try:
                date_info = LunarConverter.convert_date(self.selected_date)
                
                # Cập nhật giá trị cho các custom fields ngày tháng
                date_fields = {
                    "ngay_duong": str(date_info['solar_day']),
                    "thang_duong": str(date_info['solar_month']),
                    "nam_duong": str(date_info['solar_year']),
                    "ngay_am": str(date_info['lunar_day']),
                    "thang_am": str(date_info['lunar_month']),
                    "nam_am": str(date_info['lunar_year_name']),  # Sử dụng tên Can Chi (ví dụ: Ất Tỵ)
                    "phat_lich": str(date_info['buddhist_year'])
                }
                
                for field_name, value in date_fields.items():
                    if field_name in self.custom_fields:
                        self.custom_fields[field_name]["value"] = value
                        
            except Exception as e:
                print(f"[ConfigManager] Lỗi convert ngày: {e}")
        else:
            # Xóa giá trị nếu không có ngày được chọn
            for field_name in ["ngay_duong", "thang_duong", "nam_duong", "ngay_am", "thang_am", "nam_am", "phat_lich"]:
                if field_name in self.custom_fields:
                    self.custom_fields[field_name]["value"] = ""

    def get_selected_date(self):
        """Lấy ngày quy y được chọn"""
        return self.selected_date
    
    def is_date_selected(self):
        """Kiểm tra đã chọn ngày quy y chưa"""
        return self.selected_date is not None and self.selected_date != ""

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
        """Load config từ file bên ngoài (import) - cập nhật config_path"""
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
            # selected_date không load từ file - luôn trống khi khởi động
            if "use_vni_font" in data:
                self.use_vni_font = data["use_vni_font"]
            if "export_mode" in data:
                self.export_mode = data["export_mode"]
            
            # Cập nhật config_path sang file mới
            self.config_path = filepath
            self.is_new_config = False
            self.clear_dirty()
            
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
