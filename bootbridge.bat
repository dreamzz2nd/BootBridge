@echo off
TITLE BootBridge
cd /d "%~dp0"

where python >nul 2>&1
if %errorlevel% equ 0 (
    start "" python bootbridge.py %*
) else (
    where py >nul 2>&1
    if %errorlevel% equ 0 (
        start "" py bootbridge.py %*
    ) else (
        echo Python 3 not found in PATH.
        echo Launching BootBridge Setup Wizard...
        start "" bootbridge_installer.bat
    )
)
