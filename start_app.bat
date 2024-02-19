@echo off
cd "%~dp0"
powershell.exe -ExecutionPolicy Bypass -File "start_app.ps1"
cmd /k
