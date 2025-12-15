import os
import shutil
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm

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
        if font_path:
            self.font_path = font_path
        else:
            self.font_path = self._setup_local_font()
            
        self.font_name = FONT_NAME
        self.font_registered = False
        
    def _setup_local_font(self):
        """
        Thiết lập font từ thư mục thực thi.
        Nếu chưa có, copy từ nguồn (bundled) ra.
        """
        font_filename = os.path.basename(FONT_FILE) # e.g., "quyyfont.ttf"
        
        # Xác định thư mục chứa file thực thi (hoặc root khi chạy script)
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.getcwd()
            
        target_path = os.path.join(base_dir, font_filename)
        
        # 1. Nếu file font đã tồn tại cạnh file exe, dùng nó
        if os.path.exists(target_path):
            return target_path
            
        # 2. Nếu chưa có, tìm font gốc và copy ra
        source_path = FONT_FILE # Mặc định từ config (relative path)
        
        # Xử lý đường dẫn khi chạy trong PyInstaller bundle (_MEIPASS)
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # FONT_FILE là "fonts/quyyfont.ttf", cần join với _MEIPASS
            # Lưu ý user dùng `add-data "fonts;fonts"`, nên cấu trúc trong _MEIPASS là root/fonts/...
            candidate = os.path.join(sys._MEIPASS, FONT_FILE)
            if os.path.exists(candidate):
                source_path = candidate
                
        # Thực hiện copy nếu nguồn tồn tại
        if os.path.exists(source_path):
            try:
                shutil.copy2(source_path, target_path)
                return target_path
            except Exception as e:
                print(f"Không thể copy font ra ngoài: {e}")
                return source_path # Dùng tạm file trong bundle
        
        return source_path # Fallback về config gốc nếu không tìm thấy gì

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
        # Check orientation from config
        is_landscape = (PDF_ORIENTATION == "landscape")
        pagesize = landscape(A4) if is_landscape else A4
        page_width, page_height = pagesize
        
        c = canvas.Canvas(output_path, pagesize=pagesize)
        
        self.register_font()
        c.setFont(self.font_name, 12)
        
        # Vẽ các trường cố định (field_positions)
        for field, config in positions.items():
            if field in data:
                self._draw_field(c, data[field], config, page_height)
                
        # Vẽ các trường tùy chỉnh (custom_fields)
        # Custom fields có thể là static text (value) hoặc dynamic (nếu khớp key data?)
        # Theo logic hiện tại, custom field có 'value' cứng.
        for field_name, config in customs.items():
            self._draw_custom_field(c, field_name, config, page_height)
            
        c.save()

    def create_merged_pdf(self, data_list, output_path, field_positions=None, custom_fields=None, progress_callback=None):
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
            
            # Draw standard fields
            for field, config in positions.items():
                if field in data:
                    self._draw_field(c, data[field], config, page_height)
            
            # Draw custom fields
            for field_name, config in customs.items():
                self._draw_custom_field(c, field_name, config, page_height)
                
            c.showPage() # End page
            
            if progress_callback:
                progress_callback(i + 1, total)
                
        c.save()
        return total

    def _draw_field(self, c, text, config, page_height):
        """Vẽ một trường lên canvas"""
        if not text: return
        
        x = config["x"] * mm
        # ReportLab coordinate system starts from bottom-left
        # But our config is likely top-left based (common in UI).
        # Convert y: y_draw = page_height - y_config
        y = page_height - (config["y"] * mm)
        
        size = config.get("size", 12)
        font_name = self.font_name
        
        # Apply Bold/Italic via font switching if available, or just standard font for now.
        # TTFont registers a single face. To support Bold, we need slightly difference handling or register variants.
        # For simplicity, assuming the font supports it or we just use size/align.
        # User config includes 'bold', 'italic'. ReportLab needs 'FontName-Bold'.
        # Since we only registered 'QuyYFont', we sticking to it.
        # Maybe simulate bold? c.setTextRenderMode(2)? No.
        # We will ignore bold/italic for custom font unless we register variants.
        
        c.setFont(font_name, size)
        
        align = config.get("align", "L")
        
        if align == "C":
            c.drawCentredString(x, y, str(text))
        elif align == "R":
            c.drawRightString(x, y, str(text))
        else:
            c.drawString(x, y, str(text))

    def _draw_custom_field(self, c, name, config, page_height):
        """Vẽ custom field"""
        text = config.get("value", "")
        # Custom field logic is same structure as standard field
        self._draw_field(c, text, config, page_height)
