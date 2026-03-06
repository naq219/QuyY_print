#!/bin/bash

echo "========================================"
echo "  BUILD QUY Y PRINTER"
echo "========================================"
echo ""

echo "[1/3] Checking dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Cannot install dependencies!"
    exit 1
fi

echo ""
echo "[2/3] Building executable..."
pyinstaller --onefile --windowed --name "QuyYPrinter" --add-data "fonts:fonts" main.py
if [ $? -ne 0 ]; then
    echo "Error: Cannot build executable!"
    exit 1
fi

echo ""
echo "[3/3] Copying font files..."
cp -r fonts dist/

echo ""
echo "========================================"
echo "  BUILD SUCCESSFUL!"
echo "========================================"
echo "Executable: dist/QuyYPrinter"
echo ""
