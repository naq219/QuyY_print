# -*- coding: utf-8 -*-
"""
Printer Manager - Quản lý máy in trên Windows
- Lấy danh sách máy in
- Lấy máy in mặc định hiện tại
- Set máy in mặc định trong Windows
"""

import subprocess
import platform


class PrinterManager:
    """Quản lý máy in hệ thống Windows"""

    @staticmethod
    def get_printers():
        """Lấy danh sách máy in có sẵn trên hệ thống Windows
        
        Returns:
            list: Danh sách tên máy in, hoặc ["(Không có máy in)"] nếu rỗng
        """
        printers = []
        try:
            # Ưu tiên dùng win32print nếu có
            try:
                import win32print
                flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
                printer_list = win32print.EnumPrinters(flags, None, 2)
                printers = [p['pPrinterName'] for p in printer_list]
            except ImportError:
                # Fallback: dùng PowerShell
                result = subprocess.run(
                    ['powershell', '-Command', 
                     'Get-Printer | Select-Object -ExpandProperty Name'],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                if result.returncode == 0:
                    printers = [p.strip() for p in result.stdout.strip().split('\n') if p.strip()]
        except Exception as e:
            print(f"[PrinterManager] Không thể lấy danh sách máy in: {e}")

        return printers if printers else ["(Không có máy in)"]

    @staticmethod
    def get_default_printer():
        """Lấy tên máy in mặc định hiện tại trong Windows
        
        Returns:
            str: Tên máy in mặc định, hoặc None nếu không lấy được
        """
        try:
            # Ưu tiên dùng win32print
            try:
                import win32print
                return win32print.GetDefaultPrinter()
            except ImportError:
                pass

            # Fallback: PowerShell
            result = subprocess.run(
                ['powershell', '-Command',
                 'Get-CimInstance -ClassName Win32_Printer | Where-Object {$_.Default -eq $true} | Select-Object -ExpandProperty Name'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                name = result.stdout.strip()
                if name:
                    return name
        except Exception as e:
            print(f"[PrinterManager] Không thể lấy máy in mặc định: {e}")

        return None

    @staticmethod
    def set_default_printer(printer_name):
        """Set máy in mặc định trong Windows
        
        Args:
            printer_name: Tên máy in cần set làm mặc định
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if not printer_name or printer_name == "(Không có máy in)":
            return False, "Tên máy in không hợp lệ"

        try:
            # Ưu tiên dùng win32print 
            try:
                import win32print
                win32print.SetDefaultPrinter(printer_name)
                print(f"[PrinterManager] Đã set máy in mặc định: {printer_name}")
                return True, f"Đã đặt '{printer_name}' làm máy in mặc định"
            except ImportError:
                pass

            # Fallback: PowerShell (cần quyền admin trong một số trường hợp)
            # Trước hết tắt "Let Windows manage my default printer"
            subprocess.run(
                ['powershell', '-Command',
                 'Set-ItemProperty -Path "HKCU:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Windows" -Name "LegacyDefaultPrinterMode" -Value 1 -Type DWord -ErrorAction SilentlyContinue'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            # Set default printer
            safe_name = printer_name.replace("'", "''")
            result = subprocess.run(
                ['powershell', '-Command',
                 f'(New-Object -ComObject WScript.Network).SetDefaultPrinter("{safe_name}")'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if result.returncode == 0:
                print(f"[PrinterManager] Đã set máy in mặc định (PowerShell): {printer_name}")
                return True, f"Đã đặt '{printer_name}' làm máy in mặc định"
            else:
                error_msg = result.stderr.strip() if result.stderr else "Lỗi không xác định"
                print(f"[PrinterManager] Lỗi set default printer: {error_msg}")
                return False, f"Không thể đặt máy in mặc định: {error_msg}"

        except Exception as e:
            print(f"[PrinterManager] Lỗi set default printer: {e}")
            return False, f"Lỗi: {str(e)}"
