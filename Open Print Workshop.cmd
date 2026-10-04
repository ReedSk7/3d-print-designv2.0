@echo off
pwsh.exe -NoProfile -File "%~dp0scripts\start_workshop.ps1"
if errorlevel 1 pause
