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
    echo.
    echo  Please install Python from https://python.org
    echo  Make sure to check "Add Python to PATH" during install!
    echo.
    pause
    exit /b
)

:: ── Go to the folder where this .bat file lives ──────────────
cd /d "%~dp0"

:: ── Check if Playwright is installed ────────────────────────
python -c "import playwright" >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!] Playwright not found. Installing now...
    echo      This only happens once, please wait...
    echo.
    pip install playwright
    echo.
    echo  [!] Installing Chromium browser...
    playwright install chromium
    echo.
    echo  [OK] Setup complete!
    echo.
)

:: ── Launch the tool ──────────────────────────────────────────
python main.py

:: ── If it crashes, show error instead of disappearing ───────
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Something went wrong. See message above.
    echo.
    pause
)
