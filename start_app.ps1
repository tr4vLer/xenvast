# start_app.ps1

# Start the Python application and keep the window open
python "%~dp0app.py"

# Wait for the server to start
Start-Sleep -Seconds 5

# Open the default web browser
Start-Process "http://127.0.0.1:4999"
