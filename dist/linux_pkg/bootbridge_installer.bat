@echo off
TITLE BootBridge Windows Installer & Setup
COLOR 0A

echo ===================================================
echo     BootBridge Windows 1-Click Installer v1.0.0
echo ===================================================
echo.

echo [1/3] Checking & Installing QEMU and PyGObject for Windows...
where qemu-system-x86_64 >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing QEMU via winget...
    winget install --id QEMU.QEMU -e --silent || echo Warning: winget install failed. Please install QEMU manually from qemu.org
) else (
    echo QEMU is already installed on Windows.
)

echo.
echo [2/3] Checking Python 3 Environment...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Python 3 via winget...
    winget install --id Python.Python.3.11 -e --silent
)

echo.
echo [3/3] Launching BootBridge Setup Wizard...
python gui_installer.py || python bootbridge.py

pause
