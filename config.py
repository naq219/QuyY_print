# -*- coding: utf-8 -*-
"""
Cấu hình tọa độ và định dạng cho lá phái quy y
Tọa độ tính theo mm trên khổ A4 landscape (297mm x 210mm)
"""

# Font settings
FONT_FILE = "fonts/quyyfont.ttf"
FONT_NAME = "QuyYFont"

# A4 dimensions (mm) - Landscape orientation (ngang)
A4_WIDTH = 297
A4_HEIGHT = 210

# PDF Orientation
PDF_ORIENTATION = "landscape"  # Options: "portrait", "landscape"

# Tọa độ các trường (x, y theo mm, origin ở góc trên bên trái)
# Có thể điều chỉnh qua GUI
FIELD_POSITIONS = {
    "phap_danh": {
        "x": 85,  # mm từ trái sang
        "y": 147,  # mm từ trên xuống
        "size": 18,
        "bold": False,
        "italic": True,
        "align": "L"
    },
    "ho_ten": {
        "x": 85,
        "y": 147,
        "size": 18,
        "bold": False,
        "italic": True,
        "align": "L"
    },
    "sinh_nam": {
        "x": 85,
        "y": 157,
        "size": 12,
        "bold": False,
        "italic": True,
        "align": "L"
    },
    "dia_chi": {
        "x": 85,
        "y": 165,
        "size": 12,
        "bold": True,
        "italic": True,
        "align": "L"
    },
    "ngay_duong": {
        "x": 110,
        "y": 198,
        "size": 11,
        "bold": False,
        "italic": True,
        "align": "C"
    },
    "thang_duong": {
        "x": 130,
        "y": 198,
        "size": 11,
        "bold": False,
        "italic": True,
        "align": "C"
    },
    "nam_duong": {
        "x": 155,
        "y": 198,
        "size": 11,
        "bold": False,
        "italic": True,
        "align": "C"
    },
    "ngay_am": {
        "x": 110,
        "y": 206,
        "size": 11,
        "bold": False,
        "italic": True,
        "align": "C"
    },
    "thang_am": {
        "x": 130,
        "y": 206,
        "size": 11,
        "bold": False,
        "italic": True,
        "align": "C"
    },
    "nam_am": {
        "x": 155,
        "y": 206,
        "size": 11,
        "bold": True,
        "italic": True,
        "align": "C"
    },
    "phat_lich": {
        "x": 155,
        "y": 214,
        "size": 11,
        "bold": True,
        "italic": True,
        "align": "C"
    }
}

# Mapping từ field PDF -> cột Excel (có thể tuỳ chỉnh)
EXCEL_FIELD_MAPPING = {
    "ho_ten": "hovaten",
    "phap_danh": "phapdanh",
    "nam_sinh": "namsinh",
    "dia_chi": "diachithuongtru_short",
    "ngay_quy_y": "dauthoigian"
}

# Custom fields - các trường tùy chỉnh với giá trị cố định
# Ví dụ: {"user": {"value": "naq", "x": 50, "y": 100, "size": 12, ...}}
CUSTOM_FIELDS = {
    # Uncomment và chỉnh sửa để thêm custom field
    # "user": {
    #     "value": "naq",
    #     "x": 50,
    #     "y": 100,
    #     "size": 12,
    #     "bold": False,
    #     "italic": False,
    #     "align": "L"
    # }
}
