@echo off
TITLE BootBridge
cd /d "%~dp0"

REM 0. Check standalone BootBridge.exe
if exist "%~dp0BootBridge.exe" (
    start "" "%~dp0BootBridge.exe" %*
    exit /b 0
)

REM 1. Check Python in PATH
where python >nul 2>&1
if %errorlevel% equ 0 (
    start "" python bootbridge.py %*
    exit /b 0
)

REM 2. Check Python Launcher 'py'
where py >nul 2>&1
if %errorlevel% equ 0 (
    start "" py bootbridge.py %*
    exit /b 0
)

REM 3. If Python is not installed yet on Windows, auto-provision environment
echo ===================================================
echo   BootBridge Windows Environment Initializer
echo ===================================================
echo Python 3 belum terdeteksi di komputer Anda.
echo Mempersiapkan instalasi otomatis komponen...
echo.

where winget >nul 2>&1
if %errorlevel% equ 0 (
    echo Mengunduh & memasang Python 3 via Winget...
    winget install --id Python.Python.3.11 -e --silent
    echo.
    echo Menjalankan BootBridge...
    py bootbridge.py || python bootbridge.py
    pause
    exit /b 0
)

echo Silakan pasang Python 3 dari https://python.org untuk menjalankan BootBridge.
pause
