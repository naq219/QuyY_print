# -*- coding: utf-8 -*-
import pandas as pd
import os
import re

class ExcelHandler:
    """Xử lý đọc file Excel với validation"""
    
    # Các cột Excel cần thiết (mapping từ excel_mapping)
    REQUIRED_COLUMNS = ['hovaten', 'phapdanh', 'namsinh', 'diachithuongtru_short']
    
    # Giới hạn ký tự tối đa cho mỗi field
    MAX_FIELD_LENGTH = 50
    
    @staticmethod
    def read_file(filepath):
        """
        Đọc file Excel và trả về DataFrame đã lọc
        Returns: (count, dataframe)
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File không tồn tại: {filepath}")
            
        try:
            df = pd.read_excel(filepath)
            # Lọc bỏ dòng header (những dòng mà hovaten bị Nan)
            if 'hovaten' in df.columns:
                df = df[df['hovaten'].notna()]
            return len(df), df
        except Exception as e:
            raise Exception(f"Lỗi đọc file Excel: {str(e)}")
    
    @staticmethod
    def validate_excel(df):
        """
        Validate file Excel và trả về danh sách cảnh báo
        
        Returns:
            dict: {
                'has_warnings': bool,
                'missing_columns': list,      # Các cột bị thiếu ở header
                'row_warnings': list,         # List các warning theo dòng
                'summary': str                # Tóm tắt lỗi
            }
        """
        warnings = {
            'has_warnings': False,
            'missing_columns': [],
            'row_warnings': [],
            'summary': ''
        }
        
        # 1. Kiểm tra các cột bắt buộc có trong header không
        existing_columns = list(df.columns)
        for col in ExcelHandler.REQUIRED_COLUMNS:
            if col not in existing_columns:
                warnings['missing_columns'].append(col)
        
        if warnings['missing_columns']:
            warnings['has_warnings'] = True
        
        # 2. Kiểm tra từng dòng
        for idx, row in df.iterrows():
            row_issues = []
            excel_row = idx + 2  # +2 vì Excel bắt đầu từ 1 và có header
            
            # Kiểm tra hovaten (bắt buộc)
            ho_ten = row.get('hovaten', '')
            if pd.isna(ho_ten) or str(ho_ten).strip() == '':
                row_issues.append("Thiếu họ tên")
            elif len(str(ho_ten)) > ExcelHandler.MAX_FIELD_LENGTH:
                row_issues.append(f"Họ tên quá dài ({len(str(ho_ten))} ký tự)")
            
            # Kiểm tra phapdanh (optional nhưng nếu có thì kiểm tra độ dài)
            phap_danh = row.get('phapdanh', '')
            if not pd.isna(phap_danh) and str(phap_danh).strip() != '':
                if len(str(phap_danh)) > ExcelHandler.MAX_FIELD_LENGTH:
                    row_issues.append(f"Pháp danh quá dài ({len(str(phap_danh))} ký tự)")
            
            # Kiểm tra namsinh (phải 4 chữ số)
            nam_sinh = row.get('namsinh', '')
            if not pd.isna(nam_sinh) and str(nam_sinh).strip() != '':
                nam_sinh_str = str(nam_sinh).strip()
                # Nếu là số float, lấy phần nguyên
                if '.' in nam_sinh_str:
                    nam_sinh_str = nam_sinh_str.split('.')[0]
                if not re.match(r'^\d{4}$', nam_sinh_str):
                    row_issues.append(f"Năm sinh không hợp lệ: '{nam_sinh}' (phải 4 chữ số)")
            
            # Kiểm tra diachithuongtru_short
            dia_chi = row.get('diachithuongtru_short', '')
            if not pd.isna(dia_chi) and str(dia_chi).strip() != '':
                if len(str(dia_chi)) > ExcelHandler.MAX_FIELD_LENGTH * 2:  # Cho phép dài hơn cho địa chỉ
                    row_issues.append(f"Địa chỉ quá dài ({len(str(dia_chi))} ký tự)")
            
            if row_issues:
                warnings['row_warnings'].append({
                    'row': excel_row,
                    'name': str(ho_ten) if not pd.isna(ho_ten) else f"Dòng {excel_row}",
                    'issues': row_issues
                })
        
        if warnings['row_warnings']:
            warnings['has_warnings'] = True
        
        # 3. Tạo summary
        summary_parts = []
        
        if warnings['missing_columns']:
            summary_parts.append(f"⚠️ Thiếu cột: {', '.join(warnings['missing_columns'])}")
        
        if warnings['row_warnings']:
            summary_parts.append(f"⚠️ {len(warnings['row_warnings'])} dòng có vấn đề")
        
        if summary_parts:
            warnings['summary'] = '\n'.join(summary_parts)
        else:
            warnings['summary'] = '✅ Dữ liệu hợp lệ'
        
        return warnings
    
    @staticmethod
    def format_validation_message(warnings):
        """
        Format thông báo validation thành chuỗi để hiển thị
        """
        if not warnings['has_warnings']:
            return None
        
        lines = ["⚠️ CẢNH BÁO DỮ LIỆU EXCEL ⚠️\n"]
        
        if warnings['missing_columns']:
            lines.append("📋 Thiếu các cột bắt buộc:")
            for col in warnings['missing_columns']:
                col_name = {
                    'hovaten': 'Họ và tên',
                    'phapdanh': 'Pháp danh',
                    'namsinh': 'Năm sinh',
                    'diachithuongtru_short': 'Địa chỉ'
                }.get(col, col)
                lines.append(f"   • {col_name} ({col})")
            lines.append("")
        
        if warnings['row_warnings']:
            lines.append(f"📝 Các dòng có vấn đề ({len(warnings['row_warnings'])} dòng):")
            
            # Chỉ hiển thị tối đa 10 dòng đầu
            max_show = 10
            for i, row_warn in enumerate(warnings['row_warnings'][:max_show]):
                issues_str = "; ".join(row_warn['issues'])
                lines.append(f"   • Dòng {row_warn['row']} ({row_warn['name'][:20]}...): {issues_str}")
            
            if len(warnings['row_warnings']) > max_show:
                lines.append(f"   ... và {len(warnings['row_warnings']) - max_show} dòng khác")
        
        lines.append("\n⚡ Bạn vẫn có thể tiếp tục in, nhưng kết quả có thể không chính xác.")
        
        return '\n'.join(lines)
