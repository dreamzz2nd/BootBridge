@echo off
TITLE BootBridge
cd /d "%~dp0"

REM 1. Check Python executable
where python >nul 2>&1
if %errorlevel% equ 0 (
    start "" python bootbridge.py %*
    exit /b 0
)

REM 2. Check Python launcher 'py'
where py >nul 2>&1
if %errorlevel% equ 0 (
    start "" py bootbridge.py %*
    exit /b 0
)

REM 3. If Python is not found, launch setup wizard
echo Python 3 is required to run BootBridge.
echo Launching BootBridge Setup Wizard...
start "" setup_wizard.py
pause
