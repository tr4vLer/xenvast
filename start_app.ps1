# start_app.ps1
# This assumes that the current directory is the $XENVAST_DIR

# Start the Python application
Start-Process "python" -ArgumentList "app.py"

# Wait for the server to start
Start-Sleep -Seconds 2

# Open the default web browser
Start-Process "http://127.0.0.1:4999"
