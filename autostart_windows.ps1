# Update package list and install necessary packages

# Check if Chocolatey is already installed
if (-not (Test-Path "$env:ProgramData\chocolatey")) {
    # Check if running as administrator, if not, relaunch as administrator
    if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Warning "You need to run this script as an administrator. Relaunching script with elevated privileges..."
        Start-Sleep -Seconds 3
        Start-Process -FilePath "PowerShell.exe" -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
        Exit
    }

    # Install Chocolatey (Windows Package Manager)
    try {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072

        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
    }
    catch {
        Write-Error "Error occurred during Chocolatey installation: $_"
        Exit 1
    }

    # Wait for Chocolatey to install
    Start-Sleep -Seconds 3

    # Check if Chocolatey installation directory is added to PATH
    $chocoPath = "C:\ProgramData\chocolatey\bin"
    if (-not ($env:Path -split ';' | Select-String -Pattern ([regex]::Escape($chocoPath)))) {
        Write-Host "Chocolatey installation directory is not added to PATH. Adding it..."
        $env:Path += ";$chocoPath"
        [System.Environment]::SetEnvironmentVariable("Path", $env:Path, [System.EnvironmentVariableTarget]::Machine)
    }
}

# Verify if Chocolatey is accessible
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Error "Chocolatey is not installed or not accessible. Exiting script."
    Exit 1
}

# Install Python and Git using Chocolatey
Write-Host "Installing Python and Git..."
choco install python git -y

# Wait for installations to complete
Start-Sleep -Seconds 3

# Proceed with the rest of the script

# Install Python packages
Write-Host "Installing Python packages..."
pip install requests eth-utils paramiko prettytable flask flask-socketio Flask-Bootstrap "eth-hash[pycryptodome]" numpy

# Clone the repository and build the project
Write-Host "Cloning the repository and building the project..."
git clone https://github.com/tr4vLer/xenvast.git

# Set the current location to the xenvast directory
Set-Location xenvast

# Store the absolute path to the xenvast directory
$XENVAST_DIR = Get-Location

# Create the WScript.Shell COM object to make the shortcut
$WScriptShell = New-Object -ComObject WScript.Shell

# Create a desktop shortcut object
$Shortcut = $WScriptShell.CreateShortcut("$([System.Environment]::GetFolderPath('Desktop'))\XenBlocksMiner.lnk")

# Set the properties of the shortcut if the shortcut object is valid
$Shortcut.TargetPath = "cmd.exe"
$Shortcut.Arguments = "Set-Location '$XENVAST_DIR'; -ExecutionPolicy Bypass -File 'start_app.ps1'"
$Shortcut.IconLocation = "$XENVAST_DIR\static\logo.ico"
$Shortcut.Save()

Write-Host "Desktop shortcut created successfully."


# Run the application
Start-Process "powershell.exe" -ArgumentList "-NoExit -Command Set-Location '$XENVAST_DIR'; python app.py; Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:4999'"

Write-Host "Installation complete."
