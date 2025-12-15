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
pyinstaller --onefile --windowed --name "QuyYPrinter" ^
  --add-data "phoimau.jpg;." ^
  --add-data "quyyfont.ttf;." ^
  main.py

if errorlevel 1 (
    echo Loi: Khong the build exe!
    pause
    exit /b 1
)

echo.
echo [3/3] Copy font files...
xcopy /Y /I fonts dist\fonts\

echo.
echo ========================================
echo   BUILD THANH CONG!
echo ========================================
echo File .exe: dist\QuyYPrinter.exe
echo.
pause
