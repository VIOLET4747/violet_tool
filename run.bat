@echo off
chcp 65001 >nul
title violet_tool

echo ========================================
echo   violet_tool
echo ========================================
echo.
echo [*] Checking dependencies...
python -c "import requests; import ttkbootstrap" 2>nul
if %errorlevel% neq 0 (
    echo [*] Installing dependencies...
    pip install -r requirements.txt
)
echo [*] Starting...
start "" pythonw main.py
exit