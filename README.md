# XENBLOCKS Mining Toolbox by tr4vler

## Description

This tool automates the mining process for users who rent GPUs through vast.ai. It automatically configures and deploys mining software, allowing users to begin mining XENBLOCKS in under a minute. All you need to do is go through four setup steps, which shouldn't take more than 1 minute to complete.
The tool evaluates the performance of the rented machines by conducting multiple condition checks to determine whether a machine should continue running or be terminated. Based on these evaluations, it automatically takes actions such as termination, without requiring any user intervention.

As a member of the XEN community, I've developed this tool, which is freely available for everyone to use. Feel free to explore the source code to understand its inner workings.
Please note that the tool is continuously undergoing improvements. For further assistance or to report any issues, please join XENBLOCKS official Telegram group.

Telegram Group: https://t.me/+Db-eLPJTy7Y4ZWZj

## Table of Contents

- [Installation](#installation)
- [Features](#features)
- [Usage](#usage)


## Installation
[![Video Tutorial](https://img.youtube.com/vi/Zu7tduxMQb4/0.jpg)](https://www.youtube.com/watch?v=Zu7tduxMQb4)

**macOS**
```bash
sudo apt update && sudo apt -y install wget && sudo wget https://raw.githubusercontent.com/tr4vLer/xenvast/main/autostart.sh && sudo chmod +x autostart.sh && sudo ./autostart.sh
```

**Linux Ubuntu**
```bash
sudo apt update && sudo apt -y install wget && sudo wget https://raw.githubusercontent.com/tr4vLer/xenvast/main/autostart_linux.sh && sudo chmod +x autostart_linux.sh && ./autostart_linux.sh
```

**Windows** **(run PowerShell as ADMINISTRATOR!!!)**
```bash
PowerShell.exe -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/tr4vLer/xenvast/main/autostart_windows.ps1' -OutFile 'autostart_windows.ps1'; .\autostart_windows.ps1"
```

## Features

XENBLOCKS Mining Toolbox offers:

- **Market Order GPU:** Rent GPUs instantly from the market and start mining within minute.
  
- **Limit Order GPU:** Rent instances with predefined hourly costs and start mining once they are filled.

- **Instance Overview:** Get detailed information about the instances you are currently using.

- **Performance Bot:** Analyze performance and identify bottom-performing instances you are renting.

- **XUNI Farming:** Farm XUNIs during the designated window between the 55th and 5th minute of each hour.

- **Mining Information:** Track your total rank and the number of blocks mined, along with an overview of network activity.

- **TOOLS:**
  - **Instance Rebuilder:** Rebuild existing instances to make them fully automated. You can also use it to change the ETH address on miners with a single click.
  
  - **Dust Cleaner:** Delete stalled instances with one click. This includes instances in "Offline," "Scheduling," or "Inactive" status.



## Usage

![image](https://github.com/tr4vLer/xenvast/assets/149298759/34897955-429f-4cba-926c-3b741fd25f0a)
### Market Order workflow:
•  Searching for GPUs: The script is looking for GPUs that are available for rent on the market and match the specific type you're looking for.
•  Ordering GPUs: When it finds matching GPUs, the script will try to rent them. It decides which ones to rent based on single GPU unit cost* and whether they meet your needs. 
*Single GPU price = (total instance price) / (instance gpus)
•  Monitoring: After renting a GPU, the script keeps an eye on it to make sure it's working correctly. It checks to see if the GPU is running and being used as expected. If a GPU isn't working right, the script will stop renting it and look for another.
•  Threading for Efficiency: The script uses something called "threading" to monitor multiple GPUs at once without getting slowed down. This means it can keep track of several rented GPUs simultaneously, making sure they're all working as they should.
•  Handling Instances: If a GPU rental (an "instance") isn't functioning properly—perhaps it's not operating correctly or isn't utilized adequately—the script will terminate the rental. Additionally, it places certain machine IDs on a blacklist to prevent renting them again.
•  Repeating the Process: The script keeps searching for, renting, and monitoring GPUs until it's rented the number of GPUs you specified in the GPU’s quantity box.
•  Finishing Up: Once the script has rented and successfully set up the desired number of GPUs, it stops running and logs that it's done. The entire process might take 10 minutes or more, depending on the specified amount and machine condition.



