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
git clone https://github.com/tr4avler/xenvast.git
sleep 3
echo "---------------------------"

cd xenvast
sleep 3
echo "---------------------------"


echo "Applying chmod 777 to all files and directories..."
sudo chmod -R 777 .
sleep 3
echo "---------------------------"

sudo python3 app.py
sleep 3
echo "---------------------------"

echo "Installation complete."

