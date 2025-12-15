# -*- coding: utf-8 -*-
import pandas as pd
import os

class ExcelHandler:
    """Xử lý đọc file Excel"""
    
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
