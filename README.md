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
- **Searching for GPUs:** The script scans the market for available GPUs that match your specified criteria.
- **Ordering GPUs:** Once suitable GPUs are found, the script attempts to rent them based on their individual unit costs and your requirements.
  - *Single GPU price = (total instance price) / (instance gpus)*
- **Monitoring:** After renting a GPU, the script continuously monitors its performance to ensure it's functioning correctly and being utilized effectively. If any issues arise, the script ceases rental and seeks alternative options.
- **Efficient Threading:** Utilizes threading to concurrently monitor multiple GPUs, maintaining efficiency without compromising performance.
- **Handling Instances:** If a rented GPU instance malfunctions or is underutilized, the script terminates the rental and adds the corresponding machine ID to a blacklist to prevent future rentals.
- **Automated Repetition:** The script iterates through the process of searching, renting, and monitoring GPUs until the specified quantity is reached.
- **Completion Notification:** Upon successfully renting and setting up the desired number of GPUs, the script concludes its operation, providing a log of completion. The duration of this process varies but may take 10 minutes or more, depending on specified parameters and machine conditions.



