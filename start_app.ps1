# start_app.ps1

# Start the Python application and keep the window open
Start-Process "python" -ArgumentList "`"$PSScriptRoot\app.py`""

# Wait for the server to start
Start-Sleep -Seconds 2

# Open the default web browser
Start-Process "http://127.0.0.1:4999"
