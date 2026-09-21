@echo off
setlocal EnableExtensions
title LitePic Builder
echo ============================================
echo LitePic Builder
echo ============================================
where py >nul 2>&1
if errorlevel 1 goto NOPYTHON
if not exist ".venv\Scripts\python.exe" py -3.11 -m venv .venv
if errorlevel 1 goto NOPYTHON
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install Pillow pyinstaller
if errorlevel 1 goto BUILDFAIL
echo Building LitePic.exe...
python -m PyInstaller --noconfirm --clean --onedir --windowed --name LitePic --icon=icon.ico app.py
if errorlevel 1 goto BUILDFAIL
copy /Y icon.ico dist\LitePic\icon.ico >nul
echo.
echo ============================================
echo DONE
echo ============================================
echo EXE: %CD%\dist\LitePic\LitePic.exe
echo.
pause
exit /b 0
:NOPYTHON
echo [ERROR] Python 3.11+ with py.exe is required for this BUILD step.
pause
exit /b 1
:BUILDFAIL
echo [ERROR] PyInstaller build failed.
pause
exit /b 1
