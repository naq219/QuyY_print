import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
# Since we run from root, 'config' is available. 
# If running as package, might need '..config' but absolute import 'config' is better if PYTHONPATH includes root.
try:
    from config import FIELD_POSITIONS, FONT_FILE, FONT_NAME, A4_WIDTH, A4_HEIGHT, PDF_ORIENTATION, CUSTOM_FIELDS, EXCEL_FIELD_MAPPING
except ImportError:
    # Fallback for testing inside core/
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import FIELD_POSITIONS, FONT_FILE, FONT_NAME, A4_WIDTH, A4_HEIGHT, PDF_ORIENTATION, CUSTOM_FIELDS, EXCEL_FIELD_MAPPING




class PDFGenerator:
    """Tạo PDF cho lá phái quy y"""
    
    def __init__(self, font_path=None):
        """
        Khởi tạo PDF Generator
        
        Args:
            font_path: đường dẫn đến file font TTF
        """
        self.font_path = font_path or FONT_FILE
        self.font_name = FONT_NAME
        self.font_registered = False
        
    def register_font(self):
        """Đăng ký font Unicode"""
        if not self.font_registered and os.path.exists(self.font_path):
            try:
                pdfmetrics.registerFont(TTFont(self.font_name, self.font_path))
                self.font_registered = True
                return True
            except Exception as e:
                print(f"Lỗi khi đăng ký font: {e}")
                return False
        return self.font_registered
    
    def create_single_pdf(self, data, output_path, field_positions=None, custom_fields=None):
        """
        Tạo PDF cho một bản ghi
        
        Args:
            data: dict chứa thông tin cần in
            output_path: đường dẫn file PDF output
            field_positions: dict tọa độ các trường (optional, dùng FIELD_POSITIONS nếu None)
            custom_fields: dict các trường tùy chỉnh (optional, dùng CUSTOM_FIELDS nếu None)
        """
        # Sử dụng config nếu không truyền vào
        positions = field_positions or FIELD_POSITIONS
        customs = custom_fields or CUSTOM_FIELDS
        
        # Tạo canvas PDF (A4 landscape hoặc portrait)
        if PDF_ORIENTATION == "landscape":
            pagesize = landscape(A4)
        else:
            pagesize = A4
        
        c = canvas.Canvas(output_path, pagesize=pagesize)
        
        # Vẽ nội dung trang
        self._draw_page_content(c, data, positions, customs)
        
        # Lưu PDF
        c.save()
    
    def _draw_page_content(self, canvas_obj, data, positions, customs):
        """
        Vẽ nội dung một trang lên canvas (không save)
        
        Args:
            canvas_obj: canvas object của reportlab
            data: dict chứa thông tin cần in
            positions: dict tọa độ các trường
            customs: dict các custom fields
        """
        # Đăng ký font nếu chưa
        if self.register_font():
            canvas_obj.setFont(self.font_name, 12)
        else:
            canvas_obj.setFont("Helvetica", 12)
            print("Cảnh báo: Không thể load font tùy chỉnh, sử dụng Helvetica")
        
        # In từng trường chuẩn
        self._draw_field(canvas_obj, "phap_danh", data.get("phap_danh", ""), positions)
        self._draw_field(canvas_obj, "ho_ten", data.get("ho_ten", ""), positions)
        self._draw_field(canvas_obj, "sinh_nam", data.get("sinh_nam", ""), positions)
        self._draw_field(canvas_obj, "dia_chi", data.get("dia_chi", ""), positions)
        self._draw_field(canvas_obj, "ngay_duong", data.get("ngay_duong", ""), positions)
        self._draw_field(canvas_obj, "thang_duong", data.get("thang_duong", ""), positions)
        self._draw_field(canvas_obj, "nam_duong", data.get("nam_duong", ""), positions)
        self._draw_field(canvas_obj, "ngay_am", data.get("ngay_am", ""), positions)
        self._draw_field(canvas_obj, "thang_am", data.get("thang_am", ""), positions)
        self._draw_field(canvas_obj, "nam_am", data.get("nam_am", ""), positions)
        self._draw_field(canvas_obj, "phat_lich", data.get("phat_lich", ""), positions)
        
        # In các custom fields
        for field_name, field_config in customs.items():
            value = field_config.get("value", "")
            self._draw_custom_field(canvas_obj, field_config, value)
    
    def create_merged_pdf(self, data_list, output_path, field_positions=None, custom_fields=None, progress_callback=None):
        """
        Tạo một PDF với nhiều trang từ danh sách dữ liệu
        
        Args:
            data_list: list các dict chứa thông tin cần in
            output_path: đường dẫn file PDF output
            field_positions: dict tọa độ các trường
            custom_fields: dict các custom fields
            progress_callback: callback để báo tiến độ (current, total)
        
        Returns:
            int: số trang đã tạo
        """
        positions = field_positions or FIELD_POSITIONS
        customs = custom_fields or CUSTOM_FIELDS
        
        # Tạo canvas PDF
        if PDF_ORIENTATION == "landscape":
            pagesize = landscape(A4)
        else:
            pagesize = A4
        
        c = canvas.Canvas(output_path, pagesize=pagesize)
        total = len(data_list)
        page_count = 0
        
        for idx, data in enumerate(data_list):
            # Vẽ nội dung trang
            self._draw_page_content(c, data, positions, customs)
            page_count += 1
            
            # Tạo trang mới (trừ trang cuối)
            if idx < total - 1:
                c.showPage()
            
            # Callback progress
            if progress_callback:
                progress_callback(idx + 1, total)
        
        # Lưu PDF
        c.save()
        return page_count

    
    def _draw_field(self, canvas_obj, field_name, text, positions=None):
        """
        Vẽ một trường text lên PDF
        
        Args:
            canvas_obj: đối tượng canvas của reportlab
            field_name: tên trường (key trong FIELD_POSITIONS)
            text: nội dung cần in
            positions: dict tọa độ các trường (optional)
        """
        if not text or text == "" or str(text).lower() == "nan":
            return
        
        field_positions = positions or FIELD_POSITIONS
        field = field_positions.get(field_name)
        if not field:
            return
        
        # Convert mm sang points (1mm = 2.834645669 points)
        x = field["x"] * mm
        y = (A4_HEIGHT - field["y"]) * mm  # Y đảo ngược (origin ở dưới trái)
        
        # Set font style
        font_size = field["size"]
        
        # Tạo font name với style
        font_style = self.font_name if self.font_registered else "Helvetica"
        
        # ReportLab không support italic và bold trực tiếp cho TTF
        # Ta sẽ sử dụng skew để tạo italic effect nếu cần
        if field.get("italic", False) and field.get("bold", False):
            # Bold + Italic: không hỗ trợ trực tiếp với TTF custom
            canvas_obj.setFont(font_style, font_size)
        elif field.get("italic", False):
            canvas_obj.setFont(font_style, font_size)
        elif field.get("bold", False):
            canvas_obj.setFont(font_style, font_size)
        else:
            canvas_obj.setFont(font_style, font_size)
        
        # Vẽ text
        text_str = str(text)
        
        # Căn chỉnh text
        if field.get("align") == "C":
            # Center align
            text_width = canvas_obj.stringWidth(text_str, font_style, font_size)
            x = x - text_width / 2
        elif field.get("align") == "R":
            # Right align
            text_width = canvas_obj.stringWidth(text_str, font_style, font_size)
            x = x - text_width
        
        canvas_obj.drawString(x, y, text_str)
    
    def _draw_custom_field(self, canvas_obj, field_config, text):
        """
        Vẽ một custom field lên PDF
        
        Args:
            canvas_obj: đối tượng canvas của reportlab
            field_config: dict cấu hình của field (x, y, size, bold, italic, align)
            text: nội dung cần in
        """
        if not text or text == "" or str(text).lower() == "nan":
            return
        
        # Convert mm sang points
        x = field_config.get("x", 0) * mm
        y = (A4_HEIGHT - field_config.get("y", 0)) * mm
        
        # Set font
        font_size = field_config.get("size", 12)
        font_style = self.font_name if self.font_registered else "Helvetica"
        canvas_obj.setFont(font_style, font_size)
        
        # Vẽ text
        text_str = str(text)
        
        # Căn chỉnh
        if field_config.get("align") == "C":
            text_width = canvas_obj.stringWidth(text_str, font_style, font_size)
            x = x - text_width / 2
        elif field_config.get("align") == "R":
            text_width = canvas_obj.stringWidth(text_str, font_style, font_size)
            x = x - text_width
        
        canvas_obj.drawString(x, y, text_str)

    
    
    # create_batch_pdf and _prepare_data removed - moved to PDFService and DataProcessor


# Test
if __name__ == "__main__":
    # Test với dữ liệu mẫu
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
    generator.create_single_pdf(test_data, "/home/claude/test_output.pdf")
    print("Test PDF created: /home/claude/test_output.pdf")
