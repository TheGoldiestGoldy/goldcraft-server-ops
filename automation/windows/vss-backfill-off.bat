@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0maintenance\set-vss-backfill.ps1" -Mode off
if errorlevel 1 (
  pause
  exit /b 1
)
pause
