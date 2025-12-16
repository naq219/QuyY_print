# -*- coding: utf-8 -*-
import os
import threading
import platform
import tempfile
import shutil
from core.pdf_generator import PDFGenerator
from core.data_processor import DataProcessor

class PDFService:
    """Service quản lý việc tạo và in PDF"""
    
    def __init__(self):
        self.generator = PDFGenerator()
    
    def _get_available_filepath(self, filepath):
        """Tìm đường dẫn file khả dụng, tránh file đang bị lock
        
        Nếu file đang được mở bởi app khác (không thể ghi đè),
        sẽ tự động thêm số tăng dần: file.pdf -> file_1.pdf -> file_2.pdf
        
        Returns:
            tuple: (filepath, was_renamed) - đường dẫn khả dụng và flag đã đổi tên
        """
        if not os.path.exists(filepath):
            return filepath, False
        
        # Thử xem file có thể ghi được không
        try:
            with open(filepath, 'a'):
                pass
            return filepath, False
        except (IOError, PermissionError):
            # File đang bị lock, tìm tên mới
            pass
        
        # Tách tên file và extension
        base, ext = os.path.splitext(filepath)
        counter = 1
        max_attempts = 100
        
        while counter <= max_attempts:
            new_filepath = f"{base}_{counter}{ext}"
            if not os.path.exists(new_filepath):
                return new_filepath, True
            
            # Nếu file tồn tại, kiểm tra xem có thể ghi được không
            try:
                with open(new_filepath, 'a'):
                    pass
                return new_filepath, True
            except (IOError, PermissionError):
                counter += 1
                continue
        
        # Fallback: dùng timestamp
        import time
        timestamp = int(time.time())
        new_filepath = f"{base}_{timestamp}{ext}"
        return new_filepath, True
    
    def run_batch_export(self, df, output_dir, config_manager, mode="multiple", progress_callback=None, completion_callback=None):
        """Chạy tiến trình xuất PDF trong thread riêng"""
        thread = threading.Thread(
            target=self._export_process,
            args=(df, output_dir, config_manager, mode, False, progress_callback, completion_callback)
        )
        thread.daemon = True
        thread.start()

    def run_print_job(self, df, config_manager, mode="multiple", progress_callback=None, completion_callback=None):
        """Chạy tiến trình in PDF (tạo temp -> in -> xóa temp)"""
        thread = threading.Thread(
            target=self._export_process,
            args=(df, None, config_manager, mode, True, progress_callback, completion_callback)
        )
        thread.daemon = True
        thread.start()
        
    def _export_process(self, df, output_dir, config_manager, mode, is_print, progress_callback, completion_callback):
        # Setup temp dir for printing
        if is_print:
            temp_dir_obj = tempfile.mkdtemp()
            work_dir = temp_dir_obj
        else:
            work_dir = output_dir
            os.makedirs(work_dir, exist_ok=True)
            
        generated_files = []
        result = {"type": "print" if is_print else "export", "success": 0, "error": 0, "errors": [], "message": ""}
        
        try:
            success_count = 0
            error_count = 0
            errors = []
            
            total = len(df)
            field_positions = config_manager.field_positions
            custom_fields = config_manager.custom_fields
            use_vni = getattr(config_manager, "use_vni_font", True)
            
            # --- GENERATION PHASE ---
            
            if mode == "single":
                # SINGLE PDF MODE
                data_list = []
                for idx, row in df.iterrows():
                    # Không try-except để bắt exception - DataProcessor sẽ xử lý lỗi nội bộ
                    data = DataProcessor.process_row(row, idx)
                    data_list.append(data)
                    
                    # Đếm lỗi nếu có
                    if data.get('_has_error', False):
                        error_count += 1
                        errors.append(f"Dòng {data.get('_row_index', idx+2)}: {'; '.join(data.get('_error_details', []))}")
                    
                    if progress_callback:
                         progress_callback(idx + 1, total * 2) # 50% for prep
                
                if data_list:
                    try:
                        original_path = os.path.join(work_dir, "QuyY_TatCa.pdf")
                        output_path, was_renamed = self._get_available_filepath(original_path)
                        
                        if was_renamed:
                            errors.append(f"File gốc đang được mở, đã lưu sang: {os.path.basename(output_path)}")
                        
                        def gen_progress(current, total_gen):
                            if progress_callback:
                                progress_callback(total + current, total * 2)
                                
                        page_count = self.generator.create_merged_pdf(
                            data_list,
                            output_path,
                            field_positions=field_positions,
                            custom_fields=custom_fields,
                            progress_callback=gen_progress,
                            use_vni=use_vni
                        )
                        success_count = page_count # Count pages/records
                        generated_files.append(output_path)
                    except Exception as e:
                        error_count += len(data_list)
                        errors.append(f"Lỗi tạo file gộp: {str(e)}")
            else:
                # MULTIPLE FILES MODE
                for idx, row in df.iterrows():
                    try:
                        # DataProcessor xử lý lỗi nội bộ, không throw exception
                        data = DataProcessor.process_row(row, idx)
                        
                        # Đếm lỗi nếu có (nhưng vẫn tạo PDF)
                        if data.get('_has_error', False):
                            error_count += 1
                            errors.append(f"Dòng {data.get('_row_index', idx+2)}: {'; '.join(data.get('_error_details', []))}")
                        
                        ho_ten = str(row.get('hovaten', f'person_{idx}')).strip()
                        
                        if is_print:
                            # Print temp file: use strict ASCII to avoid OS errors
                            import time
                            safe_filename = f"job_{idx}_{int(time.time()*1000)}"
                        else:
                            # Export file: keep readability
                            safe_filename = "".join(c for c in ho_ten if c.isalnum() or c in (' ', '_')).strip()
                            if not safe_filename:
                                safe_filename = f"record_{idx}"
                            
                        original_path = os.path.join(work_dir, f"{safe_filename}.pdf")
                        output_path, was_renamed = self._get_available_filepath(original_path)
                        
                        if was_renamed:
                            errors.append(f"File '{safe_filename}.pdf' đang được mở, đã lưu sang: {os.path.basename(output_path)}")
                        
                        self.generator.create_single_pdf(
                            data,
                            output_path,
                            field_positions=field_positions,
                            custom_fields=custom_fields,
                            use_vni=use_vni
                        )
                        success_count += 1
                        generated_files.append(output_path)
                    except Exception as e:
                        # Lỗi tạo PDF (không phải lỗi dữ liệu)
                        error_count += 1
                        errors.append(f"Lỗi tạo PDF dòng {idx+2}: {str(e)}")
                    
                    if progress_callback:
                        progress_callback(idx + 1, total)

            # --- PRINTING PHASE ---
            if is_print and generated_files:
                import time
                for i, pdf_file in enumerate(generated_files):
                    try:
                        # Optional: Update status? UI might not have generic listener for status text only
                        # For now just print
                        self.print_file(pdf_file)
                        # Small delay to prevent printer queue overload
                        time.sleep(1) 
                    except Exception as e:
                        errors.append(f"Lỗi in file {os.path.basename(pdf_file)}: {e}")

            # Result construction
            result["success"] = success_count
            result["error"] = error_count
            result["errors"] = errors
            
            if is_print:
                result["message"] = f"Đã gửi lệnh in {len(generated_files)} file. (Thành công: {success_count})"
            else:
                result["message"] = f"Hoàn thành: {success_count} thành công, {error_count} lỗi"
                if mode == "single" and success_count > 0:
                    result["message"] = f"Hoàn thành: 1 file PDF với {success_count} trang"

        except Exception as e:
            result["error"] += 1
            result["errors"].append(str(e))
            result["message"] = f"Lỗi nghiêm trọng: {str(e)}"
            
        finally:
            # Cleanup temp dir
            if is_print and 'work_dir' in locals() and os.path.exists(work_dir):
                try:
                    shutil.rmtree(work_dir)
                except:
                    pass
            
            if completion_callback:
                completion_callback(result)

    def open_output_folder(self, path):
        """Mở thư mục output theo HDH"""
        if not os.path.exists(path): return
        system = platform.system()
        if system == 'Windows':
            os.startfile(path)
        elif system == 'Darwin':
            os.system(f'open "{path}"')
        else:
            os.system(f'xdg-open "{path}"')
    
    def print_file(self, pdf_path, printer_name=None):
        """In file PDF ra máy in
        
        Args:
            pdf_path: Đường dẫn file PDF
            printer_name: Tên máy in (None = máy in mặc định)
        """
        system = platform.system()
        try:
            if system == 'Windows':
                # Attempt 1: Win32 API ShellExecute 'print'
                try:
                    import win32api
                    import win32print
                    
                    # Sử dụng máy in được chỉ định hoặc máy in mặc định
                    if printer_name is None:
                        printer_name = win32print.GetDefaultPrinter()
                    
                    # 0 -> Hide window
                    win32api.ShellExecute(0, "print", pdf_path, f'/d:"{printer_name}"', ".", 0)
                    return True
                except Exception as e:
                    print(f"Win32 print failed: {e}")
                
                # Attempt 2: os.startfile with 'print' verb (uses default printer)
                try:
                    print("Trying os.startfile print...")
                    os.startfile(pdf_path, "print")
                    return True
                except Exception as e:
                    print(f"os.startfile print failed: {e}")
                    
                # Attempt 3: FINAL FALLBACK - Open file for manual printing
                print("Printing failed. Opening file for manual print.")
                os.startfile(pdf_path) 
                # Raise warning so UI knows
                raise Exception("Không tìm thấy ứng dụng hỗ trợ in tự động. Đã mở file để bạn in thủ công.")
                
            elif system == 'Darwin':
                if printer_name:
                    os.system(f'lpr -P "{printer_name}" "{pdf_path}"')
                else:
                    os.system(f'lpr "{pdf_path}"')
            else:
                if printer_name:
                    os.system(f'lp -d "{printer_name}" "{pdf_path}"')
                else:
                    os.system(f'lp "{pdf_path}"')
        except Exception as e:
            # Re-raise nicely formatted
            if "No application is associated" in str(e) or str(e) == "NO_ASSOC":
                # Fallback open happened above or needs to happen here? 
                # If Attempt 2 fails with 1155, we fallback to Attempt 3.
                pass 
            print(f"Lỗi in {pdf_path}: {e}")
            raise e

