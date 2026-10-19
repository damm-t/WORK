@echo off
:: ==============================================================================
::   QUANT DESK — 1-CLICK WINDOWS 24/7 SETUP LAUNCHER
::   Just double-click this file on Windows!
:: ==============================================================================
echo Starting 24/7 Quant Desk configuration...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_windows.ps1"
pause
