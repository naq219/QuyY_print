# -*- coding: utf-8 -*-
"""
Quản lý tài nguyên (resources) cho ứng dụng
Xử lý việc extract file từ bundle khi chạy exe
"""

import os
import sys
import shutil
import base64


# ========== EMBEDDED RESOURCE DATA ==========
# Dữ liệu file được encode base64 và nhúng trực tiếp vào code
# Được generate từ script hoặc cập nhật thủ công

EMBEDDED_RESOURCES = {
    # Sẽ được điền khi build hoặc có thể load từ bundle
}


def get_app_dir():
    """
    Lấy thư mục chứa file exe (khi build) hoặc thư mục gốc project (khi dev)
    """
    if getattr(sys, 'frozen', False):
        # Chạy từ file exe (PyInstaller)
        return os.path.dirname(sys.executable)
    else:
        # Chạy từ source code
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_bundle_dir():
    """
    Lấy thư mục _MEIPASS của PyInstaller (chứa file bundled)
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return get_app_dir()


def ensure_resource(filename, target_dir=None):
    """
    Đảm bảo file resource tồn tại trong thư mục target.
    
    Nếu file chưa có, sẽ copy từ bundle (PyInstaller) ra thư mục exe.
    
    Args:
        filename: Tên file (vd: "phoimau.jpg", "quyyfont.ttf")
        target_dir: Thư mục đích (mặc định là thư mục exe)
        
    Returns:
        str: Đường dẫn đầy đủ đến file resource
    """
    if target_dir is None:
        target_dir = get_app_dir()
        
    target_path = os.path.join(target_dir, filename)
    
    # 1. Nếu file đã tồn tại ở thư mục đích, dùng nó
    if os.path.exists(target_path):
        return target_path
        
    # 2. Tìm file trong bundle (PyInstaller _MEIPASS)
    bundle_path = os.path.join(get_bundle_dir(), filename)
    
    if os.path.exists(bundle_path):
        try:
            shutil.copy2(bundle_path, target_path)
            print(f"[ResourceManager] Extracted: {filename} -> {target_path}")
            return target_path
        except Exception as e:
            print(f"[ResourceManager] Không thể copy {filename}: {e}")
            return bundle_path  # Fallback dùng file trong bundle
    
    # 3. Fallback: file không tồn tại ở đâu cả
    print(f"[ResourceManager] CẢNH BÁO: Không tìm thấy {filename}")
    return target_path  # Trả về path dự kiến


def ensure_all_resources():
    """
    Extract tất cả các file resource cần thiết khi khởi động app
    """
    resources = ["phoimau.jpg", "quyyfont.ttf"]
    
    extracted = []
    for res in resources:
        path = ensure_resource(res)
        extracted.append((res, path))
        
    return extracted


def get_phoimau_path():
    """Lấy đường dẫn file phoimau.jpg"""
    return ensure_resource("phoimau.jpg")


def get_font_path():
    """Lấy đường dẫn file quyyfont.ttf"""
    return ensure_resource("quyyfont.ttf")


def get_config_path():
    """
    Lấy đường dẫn file config.json (lưu cùng thư mục exe)
    """
    return os.path.join(get_app_dir(), "config.json")


# Auto-extract khi module được import
if __name__ != "__main__":
    # Chỉ extract khi được import, không phải khi chạy trực tiếp module
    pass
