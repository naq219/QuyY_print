# -*- coding: utf-8 -*-
import pandas as pd
import re

class DataProcessor:
    """Xử lý dữ liệu từ Excel Row sang định dạng in PDF"""
    
    # Giới hạn ký tự
    MAX_FIELD_LENGTH = 50
    
    @staticmethod
    def process_row(row, row_index=0):
        """
        Chuyển đổi một dòng dữ liệu (pandas Series) sang dict in PDF
        
        Lưu ý: Các trường ngày tháng (ngay_duong, thang_duong, nam_duong, 
        ngay_am, thang_am, nam_am, phat_lich) được quản lý thông qua 
        custom_fields và ngày được chọn từ UI, không lấy từ Excel.
        
        Returns:
            dict: Dữ liệu đã xử lý với các trường:
                - phap_danh
                - ho_ten
                - sinh_nam
                - dia_chi
                - _has_error: bool - True nếu có lỗi
                - _error_details: list - Danh sách lỗi chi tiết
        """
        errors = []
        excel_row = row_index + 2  # +2 vì Excel bắt đầu từ 1 và có header
        
        # === XỬ LÝ HỌ TÊN ===
        ho_ten = row.get('hovaten', '')
        if pd.isna(ho_ten) or str(ho_ten).strip() == '':
            ho_ten = f"[LỖI: Thiếu họ tên - Dòng {excel_row}]"
            errors.append("Thiếu họ tên")
        else:
            ho_ten = str(ho_ten).strip()
            if len(ho_ten) > DataProcessor.MAX_FIELD_LENGTH:
                errors.append(f"Họ tên quá dài ({len(ho_ten)} ký tự)")
                # Cắt bớt và thêm "..."
                ho_ten = ho_ten[:DataProcessor.MAX_FIELD_LENGTH - 3] + "..."
        
        # === XỬ LÝ PHÁP DANH ===
        phap_danh = row.get('phapdanh', '')
        if pd.isna(phap_danh) or str(phap_danh).strip() == '':
            phap_danh = ""  # Pháp danh có thể để trống
        else:
            phap_danh = str(phap_danh).strip()
            if len(phap_danh) > DataProcessor.MAX_FIELD_LENGTH:
                errors.append(f"Pháp danh quá dài ({len(phap_danh)} ký tự)")
                phap_danh = phap_danh[:DataProcessor.MAX_FIELD_LENGTH - 3] + "..."
        
        # === XỬ LÝ NĂM SINH ===
        nam_sinh = row.get('namsinh', '')
        if pd.isna(nam_sinh) or str(nam_sinh).strip() == '':
            nam_sinh = ""  # Năm sinh có thể để trống
        else:
            nam_sinh_str = str(nam_sinh).strip()
            # Nếu là số float (ví dụ: 1990.0), lấy phần nguyên
            if '.' in nam_sinh_str:
                nam_sinh_str = nam_sinh_str.split('.')[0]
            
            # Validate phải là 4 chữ số
            if re.match(r'^\d{4}$', nam_sinh_str):
                nam_sinh = nam_sinh_str
            else:
                errors.append(f"Năm sinh không hợp lệ: '{nam_sinh}' (phải 4 chữ số)")
                # Giữ nguyên giá trị gốc nhưng đánh dấu lỗi
                nam_sinh = f"[{nam_sinh_str}?]"
        
        # === XỬ LÝ ĐỊA CHỈ ===
        dia_chi = row.get('diachithuongtru_short', '')
        if pd.isna(dia_chi) or str(dia_chi).strip() == '':
            dia_chi = ""  # Địa chỉ có thể để trống
        else:
            dia_chi = str(dia_chi).strip()
            # Địa chỉ cho phép dài hơn (100 ký tự)
            max_addr_length = DataProcessor.MAX_FIELD_LENGTH * 2
            if len(dia_chi) > max_addr_length:
                errors.append(f"Địa chỉ quá dài ({len(dia_chi)} ký tự)")
                dia_chi = dia_chi[:max_addr_length - 3] + "..."
        
        return {
            "phap_danh": phap_danh,
            "ho_ten": ho_ten,
            "sinh_nam": nam_sinh,
            "dia_chi": dia_chi,
            "_has_error": len(errors) > 0,
            "_error_details": errors,
            "_row_index": excel_row
        }
    
    @staticmethod
    def process_dataframe(df):
        """
        Xử lý toàn bộ DataFrame và trả về danh sách dữ liệu đã xử lý
        
        Returns:
            tuple: (data_list, error_count, error_summary)
        """
        data_list = []
        error_count = 0
        error_rows = []
        
        for idx, row in df.iterrows():
            data = DataProcessor.process_row(row, idx)
            data_list.append(data)
            
            if data.get('_has_error', False):
                error_count += 1
                error_rows.append({
                    'row': data.get('_row_index', idx + 2),
                    'name': data.get('ho_ten', 'N/A')[:30],
                    'errors': data.get('_error_details', [])
                })
        
        # Tạo error summary
        error_summary = None
        if error_count > 0:
            lines = [f"⚠️ {error_count} dòng có vấn đề:\n"]
            for err_row in error_rows[:10]:  # Hiển thị tối đa 10 dòng
                err_details = "; ".join(err_row['errors'])
                lines.append(f"• Dòng {err_row['row']}: {err_details}")
            
            if len(error_rows) > 10:
                lines.append(f"... và {len(error_rows) - 10} dòng khác")
            
            error_summary = '\n'.join(lines)
        
        return data_list, error_count, error_summary
