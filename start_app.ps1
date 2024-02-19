# start_app.ps1

# Start the Python application in a new PowerShell window and keep it open
$ScriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
Start-Process "powershell.exe" -ArgumentList "-NoExit", "-Command", "python `"$ScriptDirectory\app.py`""



# Wait for the server to start
Start-Sleep -Seconds 5

# Open the default web browser
Start-Process "http://127.0.0.1:4999"
