@echo off
echo ========================================
echo   violet_tool
echo ========================================
echo.
echo [*] Checking dependencies...
python -c "import requests; import ttkbootstrap" 2>nul
if %errorlevel% neq 0 (
    echo [*] Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)

echo [*] Starting...
python main.py
pause
