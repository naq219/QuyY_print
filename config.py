# -*- coding: utf-8 -*-
"""
Cấu hình tọa độ và định dạng cho lá phái quy y
Tọa độ tính theo mm trên khổ A4 landscape (297mm x 210mm)
"""

# Font settings
FONT_NAME = "QuyYFont"

# A4 dimensions (mm) - Landscape orientation (ngang)
A4_WIDTH = 297
A4_HEIGHT = 210

# PDF Orientation
PDF_ORIENTATION = "landscape"  # Options: "portrait", "landscape"

# Tọa độ các trường từ Excel (x, y theo mm, origin ở góc trên bên trái)
# Chỉ chứa 4 trường chính lấy từ dữ liệu Excel
FIELD_POSITIONS = {
    "phap_danh": {
        "x": 196.6,  # mm từ trái sang
        "y": 139.0,  # mm từ trên xuống
        "size": 18,
        "bold": False,
        "italic": True,
        "align": "L"
    },
    "ho_ten": {
        "x": 196.6,
        "y": 129.4,
        "size": 18,
        "bold": False,
        "italic": True,
        "align": "L"
    },
    "sinh_nam": {
        "x": 197.0,
        "y": 147.0,
        "size": 12,
        "bold": False,
        "italic": True,
        "align": "L"
    },
    "dia_chi": {
        "x": 197.4,
        "y": 154.2,
        "size": 12,
        "bold": True,
        "italic": True,
        "align": "L"
    }
}

# Mapping từ field PDF -> cột Excel (có thể tuỳ chỉnh)
EXCEL_FIELD_MAPPING = {
    "ho_ten": "hovaten",
    "phap_danh": "phapdanh",
    "nam_sinh": "namsinh",
    "dia_chi": "diachithuongtru_short"
}

# Custom fields - các trường tùy chỉnh với giá trị cố định
# Bao gồm các trường ngày tháng (được cập nhật khi chọn ngày quy y)
CUSTOM_FIELDS = {
    "pl": {
        "value": "",
        "x": 206.0,
        "y": 178.0,
        "size": 12,
        "bold": False,
        "italic": False,
        "align": "L"
    },
    "ngay_duong": {
        "value": "",
        "x": 235.2,
        "y": 178.4,
        "size": 11,
        "bold": False,
        "italic": True,
        "align": "C"
    },
    "thang_duong": {
        "value": "",
        "x": 259.6,
        "y": 178.0,
        "size": 11,
        "bold": False,
        "italic": True,
        "align": "C"
    },
    "nam_duong": {
        "value": "",
        "x": 276.6,
        "y": 178.0,
        "size": 11,
        "bold": False,
        "italic": True,
        "align": "C"
    },
    "ngay_am": {
        "value": "",
        "x": 235.6,
        "y": 182.8,
        "size": 11,
        "bold": False,
        "italic": True,
        "align": "C"
    },
    "thang_am": {
        "value": "",
        "x": 259.2,
        "y": 182.8,
        "size": 11,
        "bold": False,
        "italic": True,
        "align": "C"
    },
    "nam_am": {
        "value": "",
        "x": 277.8,
        "y": 183.6,
        "size": 11,
        "bold": True,
        "italic": True,
        "align": "C"
    },
    "phat_lich": {
        "value": "",
        "x": 155,
        "y": 214,
        "size": 11,
        "bold": True,
        "italic": True,
        "align": "C"
    }
}
