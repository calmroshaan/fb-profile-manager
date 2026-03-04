@echo off
title FB Profile Manager
color 0B
cls

echo.
echo  ============================================================
echo   FB PROFILE MANAGER - Starting...
echo  ============================================================
echo.

:: ── Find Python ─────────────────────────────────────────────
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python not found!
    echo  Please install Python from https://python.org
    echo  Make sure to check "Add Python to PATH" during install!
    pause
    exit /b
)

:: ── Go to the folder where this .bat file lives ──────────────
cd /d "%~dp0"

:: ── Remove playwright-stealth if installed (conflicts) ───────
pip show playwright-stealth >nul 2>&1
if %errorlevel% equ 0 (
    echo  [!] Removing conflicting package: playwright-stealth...
    pip uninstall playwright-stealth -y >nul 2>&1
)

:: ── Check if correct Playwright version is installed ─────────
python -c "import playwright; assert playwright.__version__ == '1.40.0'" >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!] Installing correct Playwright version...
    pip install playwright==1.40.0
    playwright install chromium
)

:: ── Launch the tool ──────────────────────────────────────────
python main.py

if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Something went wrong. See message above.
    pause
)
