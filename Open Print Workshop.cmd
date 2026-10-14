@echo off
setlocal
where pwsh.exe >nul 2>nul
if errorlevel 1 (
    echo PowerShell 7 ^(pwsh.exe^) was not found on PATH.
    echo Install PowerShell 7, then reopen this launcher.
    echo One-time project setup: pwsh -NoProfile -File "%~dp0scripts\setup.ps1"
    echo This launcher does not install dependencies or tools.
    pause
    exit /b 1
)
pwsh.exe -NoProfile -File "%~dp0scripts\start_workshop.ps1" %*
set "workshopExit=%ERRORLEVEL%"
if not "%workshopExit%"=="0" pause
exit /b %workshopExit%
