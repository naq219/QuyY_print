# -*- coding: utf-8 -*-
import unicodedata
import re

# Logic convert tham khảo từ docs/guide_convert_VNI.py

UNICODE_CHARS = [
    "À", "Á", "Â", "Ã", "È", "É", "Ê", "Ì", "Í", "Ò",
    "Ó", "Ô", "Õ", "Ù", "Ú", "Ý", "à", "á", "â", "ã",
    "è", "é", "ê", "ì", "í", "ò", "ó", "ô", "õ", "ù",
    "ú", "ý", "Ă", "ă", "Đ", "đ", "Ĩ", "ĩ", "Ũ", "ũ",
    "Ơ", "ơ", "Ư", "ư", "Ạ", "ạ", "Ả", "ả", "Ấ", "ấ",
    "Ầ", "ầ", "Ẩ", "ẩ", "Ẫ", "ẫ", "Ậ", "ậ", "Ắ", "ắ",
    "Ằ", "ằ", "Ẳ", "ẳ", "Ẵ", "ẵ", "Ặ", "ặ", "Ẹ", "ẹ",
    "Ẻ", "ẻ", "Ẽ", "ẽ", "Ế", "ế", "Ề", "ề", "Ể", "ể",
    "Ễ", "ễ", "Ệ", "ệ", "Ỉ", "ỉ", "Ị", "ị", "Ọ", "ọ",
    "Ỏ", "ỏ", "Ố", "ố", "Ồ", "ồ", "Ổ", "ổ", "Ỗ", "ỗ",
    "Ộ", "ộ", "Ớ", "ớ", "Ờ", "ờ", "Ở", "ở", "Ỡ", "ỡ",
    "Ợ", "ợ", "Ụ", "ụ", "Ủ", "ủ", "Ứ", "ứ", "Ừ", "ừ",
    "Ử", "ử", "Ữ", "ữ", "Ự", "ự", "Ỳ", "ỳ", "Ỵ", "ỵ",
    "Ỷ", "ỷ", "Ỹ", "ỹ"
]

VNI_WIN_CHARS = [
    "AØ", "AÙ", "AÂ", "AÕ", "EØ", "EÙ", "EÂ", "Ì" , "Í" , "OØ",
    "OÙ", "OÂ", "OÕ", "UØ", "UÙ", "YÙ", "aø", "aù", "aâ", "aõ",
    "eø", "eù", "eâ", "ì" , "í" , "oø", "où", "oâ", "oõ", "uø",
    "uù", "yù", "AÊ", "aê", "Ñ" , "ñ" , "Ó" , "ó" , "UÕ", "uõ",
    "Ô" , "ô" , "Ö" , "ö" , "AÏ", "aï", "AÛ", "aû", "AÁ", "aá",
    "AÀ", "aà", "AÅ", "aå", "AÃ", "aã", "AÄ", "aä", "AÉ", "aé",
    "AÈ", "aè", "AÚ", "aú", "AÜ", "aü", "AË", "aë", "EÏ", "eï",
    "EÛ", "eû", "EÕ", "eõ", "EÁ", "eá", "EÀ", "eà", "EÅ", "eå",
    "EÃ", "eã", "EÄ", "eä", "Æ" , "æ" , "Ò" , "ò" , "OÏ", "oï",
    "OÛ", "oû", "OÁ", "oá", "OÀ", "oà", "OÅ", "oå", "OÃ", "oã",
    "OÄ", "oä", "ÔÙ", "ôù", "ÔØ", "ôø", "ÔÛ", "ôû", "ÔÕ", "ôõ",
    "ÔÏ", "ôï", "UÏ", "uï", "UÛ", "uû", "ÖÙ", "öù", "ÖØ", "öø",
    "ÖÛ", "öû", "ÖÕ", "öõ", "ÖÏ", "öï", "YØ", "yø", "Î" , "î" ,
    "YÛ", "yû", "YÕ", "yõ"
]

# Tạo map dictionary để lookup nhanh
UNICODE_TO_VNI_MAP = {}
for u, v in zip(UNICODE_CHARS, VNI_WIN_CHARS):
    UNICODE_TO_VNI_MAP[u] = v

def convert_unicode_to_vni(text):
    """
    Chuyển đổi chuỗi Unicode dựng sẵn sang VNI-Windows
    Dựa trên bảng mã tham khảo.
    """
    if not text:
        return ""
    
    # Normalize về dựng sẵn (NFC) để khớp với bảng map
    text = unicodedata.normalize('NFC', text)
    
    res = []
    for char in text:
        if char in UNICODE_TO_VNI_MAP:
            res.append(UNICODE_TO_VNI_MAP[char])
        else:
            res.append(char)
            
    return "".join(res)


def slugify(text):
    """
    Chuyển đổi chuỗi sang dạng URL-friendly (không dấu, lowercase, gạch ngang)
    Ví dụ: "Nguyễn Văn A" -> "nguyen-van-a"
    """
    if not text:
        return ""
        
    text = str(text).lower()
    text = text.replace("đ", "d")
    text = unicodedata.normalize('NFD', text)
    text = "".join(c for c in text if unicodedata.category(c) != 'Mn')
    text = unicodedata.normalize('NFC', text)
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def get_safe_print_filename(index, total, name):
    slug_name = slugify(name)
    return f"laphai_{index}_{total}_{slug_name}.pdf"
