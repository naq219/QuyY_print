import os
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from core.utils import convert_unicode_to_vni

try:
    from config import FIELD_POSITIONS, FONT_NAME, A4_WIDTH, A4_HEIGHT, PDF_ORIENTATION, CUSTOM_FIELDS, EXCEL_FIELD_MAPPING
    from core.resource_manager import get_font_path
except ImportError:
    # Fallback for testing inside core/
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import FIELD_POSITIONS, FONT_NAME, A4_WIDTH, A4_HEIGHT, PDF_ORIENTATION, CUSTOM_FIELDS, EXCEL_FIELD_MAPPING
    from core.resource_manager import get_font_path, get_phoimau_path


class PDFGenerator:
    """Tạo PDF cho lá phái quy y"""
    
    def __init__(self, font_path=None):
        """
        Khởi tạo PDF Generator
        
        Args:
            font_path: đường dẫn đến file font TTF
        """
        if font_path:
            self.font_path = font_path
        else:
            # Sử dụng resource_manager để lấy đường dẫn font
            self.font_path = get_font_path()
            
        self.font_name = FONT_NAME
        self.font_registered = False

    def register_font(self):
        """Đăng ký font Unicode"""
        if not self.font_registered:
            # Check exist
            if os.path.exists(self.font_path):
                try:
                    pdfmetrics.registerFont(TTFont(self.font_name, self.font_path))
                    self.font_registered = True
                    return True
                except Exception as e:
                    print(f"Lỗi khi đăng ký font '{self.font_path}': {e}")
                    return False
            else:
                 print(f"File font không tồn tại: {self.font_path}")
                 return False
                 
        return self.font_registered
    
    def create_single_pdf(self, data, output_path, field_positions=None, custom_fields=None, use_vni=False, use_background=False):
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
        # Check orientation from config
        is_landscape = (PDF_ORIENTATION == "landscape")
        pagesize = landscape(A4) if is_landscape else A4
        page_width, page_height = pagesize
        
        c = canvas.Canvas(output_path, pagesize=pagesize)
        
        # Vẽ ảnh nền nếu bật
        if use_background:
            self._draw_background(c, page_width, page_height)
        
        self.register_font()
        c.setFont(self.font_name, 12)
        
        # Vẽ các trường cố định (field_positions)
        for field, config in positions.items():
            if field in data:
                self._draw_field(c, data[field], config, page_height, use_vni)
                
        # Vẽ các trường tùy chỉnh (custom_fields)
        # Custom fields có thể là static text (value) hoặc dynamic (nếu khớp key data?)
        # Theo logic hiện tại, custom field có 'value' cứng.
        for field_name, config in customs.items():
            self._draw_custom_field(c, field_name, config, page_height, use_vni)
            
        c.save()

    def create_merged_pdf(self, data_list, output_path, field_positions=None, custom_fields=None, progress_callback=None, use_vni=False, use_background=False):
        """
        Tạo 1 file PDF chứa nhiều trang (mỗi trang 1 bản ghi)
        """
        positions = field_positions or FIELD_POSITIONS
        customs = custom_fields or CUSTOM_FIELDS
        
        is_landscape = (PDF_ORIENTATION == "landscape")
        pagesize = landscape(A4) if is_landscape else A4
        page_width, page_height = pagesize
        
        c = canvas.Canvas(output_path, pagesize=pagesize)
        self.register_font()
        
        total = len(data_list)
        for i, data in enumerate(data_list):
            c.setFont(self.font_name, 12)
            
            # Vẽ ảnh nền nếu bật
            if use_background:
                self._draw_background(c, page_width, page_height)
            
            # Draw standard fields
            for field, config in positions.items():
                if field in data:
                    self._draw_field(c, data[field], config, page_height, use_vni)
            
            # Draw custom fields
            for field_name, config in customs.items():
                self._draw_custom_field(c, field_name, config, page_height, use_vni)
                
            c.showPage() # End page
            
            if progress_callback:
                progress_callback(i + 1, total)
                
        c.save()
        return total
    
    def _draw_background(self, c, page_width, page_height):
        """Đặt ảnh nền (phôi mẫu) vào PDF"""
        try:
            from core.resource_manager import get_app_dir
            app_dir = get_app_dir()
            bg_path = None
            for ext in [".jpg", ".jpeg", ".png"]:
                path = os.path.join(app_dir, f"phoimau{ext}")
                if os.path.exists(path):
                    bg_path = path
                    break
            
            if bg_path:
                c.drawImage(bg_path, 0, 0, width=page_width, height=page_height,
                           preserveAspectRatio=False, mask='auto')
        except Exception as e:
            print(f"[PDFGenerator] Lỗi vẽ ảnh nền: {e}")

    def _draw_field(self, c, text, config, page_height, use_vni=False):
        """Vẽ một trường lên canvas"""
        if not text: return
        
        # Convert encoding if needed
        if use_vni:
            text = convert_unicode_to_vni(str(text))
        
        x = config["x"] * mm
        y = page_height - (config["y"] * mm)
        
        size = config.get("size", 12)
        font_name = self.font_name
        
        c.setFont(font_name, size)
        
        align = config.get("align", "L")
        
        if align == "C":
            c.drawCentredString(x, y, str(text))
        elif align == "R":
            c.drawRightString(x, y, str(text))
        else:
            c.drawString(x, y, str(text))

    def _draw_custom_field(self, c, name, config, page_height, use_vni=False):
        """Vẽ custom field"""
        text = config.get("value", "")
        # Custom field logic is same structure as standard field
        self._draw_field(c, text, config, page_height, use_vni)
