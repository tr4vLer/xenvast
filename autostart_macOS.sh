#!/bin/bash

# Update package list and install necessary packages

# Install system packages
echo "Installing system packages..."
brew install python3
sleep 3
echo "---------------------------"

brew install openssl
sleep 3
echo "---------------------------"

brew install libffi
sleep 3
echo "---------------------------"

xcode-select --install
sleep 3
echo "---------------------------"

brew install curl
sleep 3
echo "---------------------------"

brew install git
sleep 3
echo "---------------------------"

# Install Python packages
echo "Installing Python packages..."
pip3 install requests
sleep 3
echo "---------------------------"

pip3 install eth-utils
sleep 3
echo "---------------------------"

pip3 install paramiko
sleep 3
echo "---------------------------"

pip3 install prettytable
sleep 3
echo "---------------------------"

pip3 install flask
sleep 3
echo "---------------------------"

pip3 install flask-socketio
sleep 3
echo "---------------------------"

pip3 install Flask-Bootstrap
sleep 3
echo "---------------------------"

pip3 install "eth-hash[pycryptodome]"
sleep 3
echo "---------------------------"

pip3 install numpy
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
chmod -R 777 .
sleep 3
echo "---------------------------"

python3 app.py
sleep 3
echo "---------------------------"

echo "Installation complete."


