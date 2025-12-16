# -*- coding: utf-8 -*-
import pandas as pd

class DataProcessor:
    """Xử lý dữ liệu từ Excel Row sang định dạng in PDF"""
    
    @staticmethod
    def process_row(row):
        """
        Chuyển đổi một dòng dữ liệu (pandas Series) sang dict in PDF
        
        Lưu ý: Các trường ngày tháng (ngay_duong, thang_duong, nam_duong, 
        ngay_am, thang_am, nam_am, phat_lich) được quản lý thông qua 
        custom_fields và ngày được chọn từ UI, không lấy từ Excel.
        """
        phap_danh = row.get('phapdanh')
        ho_ten = row.get('hovaten', '')
        nam_sinh = row.get('namsinh', '')
        dia_chi = row.get('diachithuongtru_short', '')
        
        if pd.isna(phap_danh) or str(phap_danh).strip() == '':
            phap_danh = ""
        
        return {
            "phap_danh": phap_danh,
            "ho_ten": ho_ten,
            "sinh_nam": str(nam_sinh) if not pd.isna(nam_sinh) else "",
            "dia_chi": str(dia_chi) if not pd.isna(dia_chi) else ""
        }

