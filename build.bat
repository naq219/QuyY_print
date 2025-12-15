@echo off
echo ========================================
echo   BUILD QUY Y PRINTER EXE
echo ========================================
echo.

echo [1/3] Kiem tra cai dat dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Loi: Khong the cai dat dependencies!
    pause
    exit /b 1
)

echo.
echo [2/3] Build file .exe...
REM Bundle phoimau.jpg và quyyfont.ttf vào exe
REM Các file này sẽ được extract ra thư mục exe khi chạy lần đầu
pyinstaller --onefile --windowed --name "QuyYPrinter" ^
  --icon "icon.ico" ^
  --add-data "phoimau.jpg;." ^
  --add-data "quyyfont.ttf;." ^
  main.py

if errorlevel 1 (
    echo Loi: Khong the build exe!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   BUILD THANH CONG!
echo ========================================
echo File .exe: dist\QuyYPrinter.exe
echo.
echo Khi chay lan dau, cac file sau se duoc tao ra:
echo   - phoimau.jpg  (anh phoi mau)
echo   - quyyfont.ttf (font chu)
echo   - config.json  (cau hinh)
echo.
pause
