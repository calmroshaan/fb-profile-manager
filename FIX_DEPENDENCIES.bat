@echo off
title FB Profile Manager - Fix Dependencies
color 0C
echo.
echo  ============================================================
echo   Fixing dependencies...
echo  ============================================================
echo.

echo  [1/3] Uninstalling playwright-stealth (conflicts with our tool)...
pip uninstall playwright-stealth -y
echo.

echo  [2/3] Pinning Playwright to stable version 1.40.0...
pip install playwright==1.40.0
echo.

echo  [3/3] Reinstalling browser...
playwright install chromium
echo.

echo  ============================================================
echo   Done! Now run START.bat to launch the tool.
echo  ============================================================
echo.
pause
