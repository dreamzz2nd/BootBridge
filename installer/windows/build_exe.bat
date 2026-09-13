@echo off
TITLE BootBridge Windows Package Builder (.exe)
COLOR 0B

echo ===================================================
echo     BootBridge Windows .EXE Builder v1.0.0
echo ===================================================
echo.

cd /d "%~dp0..\..\"

echo [1/3] Checking PyInstaller...
python -m pip install --upgrade pyinstaller

echo.
echo [2/3] Building Standalone BootBridge-Setup.exe...
python build_windows_exe.py

echo.
echo [3/3] Checking Inno Setup Compiler (ISCC)...
where iscc >nul 2>&1
if %errorlevel% equ 0 (
    echo Building Inno Setup Installer EXE...
    iscc installer\windows\inno_setup.iss
    echo [OK] Inno Setup Installer created in dist/
) else (
    echo [Info] Inno Setup compiler (ISCC) not found in PATH.
    echo Standalone PyInstaller executable created successfully in dist/BootBridge-Setup/
)

echo.
echo ===================================================
echo Windows Build Completed! Check 'dist/' folder.
echo ===================================================
pause
