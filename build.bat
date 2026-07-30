@echo off
echo ========================================
echo   violet_tool - Build EXE
echo ========================================
echo.

echo [*] Checking PyInstaller...
pyinstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Installing PyInstaller...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo [*] Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [*] Building EXE...
pyinstaller --onefile --windowed --name "violet_tool" --add-data "config.json;." --hidden-import ttkbootstrap --hidden-import requests --clean --noconfirm main.py

if %errorlevel% neq 0 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Build Complete!
echo   EXE: dist\violet_tool.exe
echo   Copy config.json next to violet_tool.exe
echo ========================================
pause
