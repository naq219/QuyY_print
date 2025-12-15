# -*- coding: utf-8 -*-
import pandas as pd
from core.lunar_converter import LunarConverter

class DataProcessor:
    """Xử lý dữ liệu từ Excel Row sang định dạng in PDF"""
    
    @staticmethod
    def process_row(row):
        """
        Chuyển đổi một dòng dữ liệu (pandas Series) sang dict in PDF
        """
        phap_danh = row.get('phapdanh')
        ho_ten = row.get('hovaten', '')
        nam_sinh = row.get('namsinh', '')
        dia_chi = row.get('diachithuongtru_short', '')
        ngay_quy_y = row.get('dauthoigian', '')
        
        if pd.isna(phap_danh) or str(phap_danh).strip() == '':
            phap_danh = ""
        
        if ngay_quy_y and not pd.isna(ngay_quy_y):
            # LunarConverter is now in core
            date_info = LunarConverter.convert_date(str(ngay_quy_y))
        else:
            date_info = {
                'solar_day': '', 'solar_month': '', 'solar_year': '',
                'lunar_day': '', 'lunar_month': '', 'lunar_year': '',
                'buddhist_year': ''
            }
        
        return {
            "phap_danh": phap_danh,
            "ho_ten": ho_ten,
            "sinh_nam": str(nam_sinh) if not pd.isna(nam_sinh) else "",
            "dia_chi": str(dia_chi) if not pd.isna(dia_chi) else "",
            "ngay_duong": str(date_info['solar_day']) if date_info['solar_day'] else "",
            "thang_duong": str(date_info['solar_month']) if date_info['solar_month'] else "",
            "nam_duong": str(date_info['solar_year']) if date_info['solar_year'] else "",
            "ngay_am": str(date_info['lunar_day']) if date_info['lunar_day'] else "",
            "thang_am": str(date_info['lunar_month']) if date_info['lunar_month'] else "",
            "nam_am": str(date_info['lunar_year']) if date_info['lunar_year'] else "",
            "phat_lich": str(date_info['buddhist_year']) if date_info['buddhist_year'] else ""
        }
