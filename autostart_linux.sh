#!/bin/bash

# Update package list and install necessary packages

# Install system packages
echo "Installing system packages..."
sudo apt -y install python3-pip
sleep 3
echo "---------------------------"

sudo apt-get install -y python3-dev python3-pip
sleep 3
echo "---------------------------"

sudo apt-get install -y libssl-dev libffi-dev
sleep 3
echo "---------------------------"

sudo apt-get install -y build-essential
sleep 3
echo "---------------------------"

sudo apt-get install -y curl
sleep 3
echo "---------------------------"

sudo apt-get install -y git
sleep 3
echo "---------------------------"



# Install Python packages
echo "Installing Python packages..."
sudo pip install requests
sleep 3
echo "---------------------------"

sudo pip install eth-utils
sleep 3
echo "---------------------------"

sudo pip install paramiko
sleep 3
echo "---------------------------"

sudo pip install prettytable
sleep 3
echo "---------------------------"

sudo pip install flask
sleep 3
echo "---------------------------"

sudo pip install flask-socketio
sleep 3
echo "---------------------------"

sudo pip install Flask-Bootstrap
sleep 3
echo "---------------------------"

sudo pip install "eth-hash[pycryptodome]"
sleep 3
echo "---------------------------"

sudo pip install numpy
sleep 3
echo "---------------------------"


# Clone the repository and build the project
echo "Cloning the repository and building the project..."
git clone https://github.com/tr4vLer/xenvast.git
sleep 3
echo "---------------------------"


cd xenvast
sleep 3
echo "---------------------------"


echo "Applying chmod 777 to all files and directories..."
sudo chmod -R 777 .
sleep 3
echo "---------------------------"

# Get the absolute path to the xenvast directory
XENVAST_DIR=$(pwd)

# Create a desktop shortcut
create_desktop_shortcut() {
    # Determine the desktop directory for the current user without using sudo
    # This assumes the script is not run with sudo
    DESKTOP_PATH="$HOME/Desktop"

    # Make sure the Desktop directory exists
    if [ ! -d "$DESKTOP_PATH" ]; then
        echo "The desktop directory $DESKTOP_PATH does not exist."
        return 1
    fi

    local desktop_file="$DESKTOP_PATH/XenBlocksMiner.desktop"
    echo "[Desktop Entry]
Version=1.0
Name=XenBlocksMiner
Comment=Run XenBlocksMiner application
Exec=gnome-terminal --working-directory=$XENVAST_DIR -- bash -c 'python3 app.py & (sleep 2 && xdg-open http://127.0.0.1:4999); exec bash'
Icon=$XENVAST_DIR/static/logo.png
Terminal=true
Type=Application
Categories=Utility;Application;" > "$desktop_file"

    # Make the desktop file executable
    chmod +x "$desktop_file"
}

# Call the function to create the desktop shortcut
# Make sure to run this part without sudo
create_desktop_shortcut

# Check if the shortcut was created successfully
if [ $? -eq 0 ]; then
    echo "Desktop shortcut created successfully."
else
    echo "Failed to create desktop shortcut."
    exit 1
fi


sudo python3 app.py &
sleep 3
echo "---------------------------"
echo "Installation complete."

# Open the default web browser
xdg-open http://127.0.0.1:4999
