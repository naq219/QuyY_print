# -*- coding: utf-8 -*-
"""
Test script để kiểm tra PDF generation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from pdf_generator import PDFGenerator
from lunar_converter import LunarConverter
import pandas as pd

def test_single_pdf():
    """Test tạo một PDF đơn lẻ"""
    print("=== TEST TẠO PDF ĐƠN LẺ ===")
    
    # Dữ liệu mẫu
    test_data = {
        "phap_danh": "",
        "ho_ten": "Nguyễn Văn A",
        "sinh_nam": "1990",
        "dia_chi": "Hà Nội",
        "ngay_duong": "2",
        "thang_duong": "5",
        "nam_duong": "2025",
        "ngay_am": "5",
        "thang_am": "4",
        "nam_am": "2025",
        "phat_lich": "2569"
    }
    
    generator = PDFGenerator()
    output_path = "/home/claude/test_single.pdf"
    
    try:
        generator.create_single_pdf(test_data, output_path)
        print(f"✓ Tạo PDF thành công: {output_path}")
        return True
    except Exception as e:
        print(f"✗ Lỗi: {e}")
        return False

def test_lunar_conversion():
    """Test chuyển đổi âm lịch"""
    print("\n=== TEST CHUYỂN ĐỔI ÂM LỊCH ===")
    
    test_dates = [
        "2025-05-02",
        "2025-12-15",
        "2024-01-01"
    ]
    
    for date in test_dates:
        result = LunarConverter.convert_date(date)
        print(f"\nDương lịch: {result['solar_day']}/{result['solar_month']}/{result['solar_year']}")
        print(f"Âm lịch: {result['lunar_day']}/{result['lunar_month']}/{result['lunar_year']}")
        print(f"Phật lịch: {result['buddhist_year']}")

def test_excel_reading():
    """Test đọc file Excel"""
    print("\n=== TEST ĐỌC FILE EXCEL ===")
    
    excel_path = "/home/claude/quy_y_printer/sample_data.xlsx"
    
    if not os.path.exists(excel_path):
        print("✗ File Excel không tồn tại")
        return False
    
    try:
        df = pd.read_excel(excel_path)
        df = df[df['hovaten'].notna()]
        
        print(f"✓ Đọc thành công: {len(df)} bản ghi")
        print(f"\nDữ liệu mẫu (5 dòng đầu):")
        print(df[['hovaten', 'namsinh', 'diachithuongtru_short']].head())
        return True
    except Exception as e:
        print(f"✗ Lỗi: {e}")
        return False

def test_batch_pdf():
    """Test tạo PDF hàng loạt"""
    print("\n=== TEST TẠO PDF HÀNG LOẠT ===")
    
    excel_path = "/home/claude/quy_y_printer/sample_data.xlsx"
    output_dir = "/home/claude/test_output"
    
    if not os.path.exists(excel_path):
        print("✗ File Excel không tồn tại")
        return False
    
    os.makedirs(output_dir, exist_ok=True)
    
    generator = PDFGenerator()
    
    def progress_callback(current, total):
        print(f"Đang xử lý: {current}/{total}", end="\r")
    
    try:
        # Test với 3 bản ghi đầu tiên
        df = pd.read_excel(excel_path)
        df = df[df['hovaten'].notna()].head(3)
        
        # Tạo file Excel tạm với 3 bản ghi
        temp_excel = "/home/claude/temp_test.xlsx"
        df.to_excel(temp_excel, index=False)
        
        success, error, errors = generator.create_batch_pdf(
            temp_excel,
            output_dir,
            progress_callback
        )
        
        print(f"\n✓ Hoàn thành: {success} thành công, {error} lỗi")
        
        if errors:
            print("Chi tiết lỗi:")
            for err in errors:
                print(f"  - {err}")
        
        # Cleanup
        os.remove(temp_excel)
        
        return True
    except Exception as e:
        print(f"✗ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Chạy tất cả tests"""
    print("=" * 50)
    print("  TEST QUY Y PRINTER")
    print("=" * 50)
    
    tests = [
        ("Chuyển đổi âm lịch", test_lunar_conversion),
        ("Tạo PDF đơn lẻ", test_single_pdf),
        ("Đọc file Excel", test_excel_reading),
        ("Tạo PDF hàng loạt", test_batch_pdf)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' gặp lỗi: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("  KẾT QUẢ TEST")
    print("=" * 50)
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8s} - {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nTổng: {passed}/{total} tests passed")
    print("=" * 50)

if __name__ == "__main__":
    main()
