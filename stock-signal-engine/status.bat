@echo off
:: ==============================================================================
::   QUANT DESK — 1-CLICK WINDOWS STATUS VIEWER
::   Double-click this file anytime on Windows to see 4-desk live status!
:: ==============================================================================
title Quant Desk Status
"C:\Program Files\Git\bin\bash.exe" -c "cd ~/stock-signal-engine && ./quant status"
echo.
pause
