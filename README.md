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
> Proceed with the installation **on your computer**. It won't work for machines rented from vast.ai.

### **macOS installation**
Open terminal and paste below command. (MANUAL START after reboot!  `cd xenvast && python3 app.py`)
```bash
brew update && brew install wget && wget https://raw.githubusercontent.com/tr4vLer/xenvast/main/autostart_macOS.sh && chmod +x autostart_macOS.sh && ./autostart_macOS.sh
```
<!-- Separator Line -->
<hr>

### **Windows installation**
run PowerShell as **ADMINISTRATOR** and paste below command! If installation fails after first attempt, **REBOOT** your computer and execute command again.
```bash
cd $HOME; PowerShell.exe -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/tr4vLer/xenvast/main/autostart_windows.ps1' -OutFile 'autostart_windows.ps1'; .\autostart_windows.ps1"
```
<!-- Separator Line -->
<hr>

### **Linux installation**
Execute the command below in the terminal. 
```bash
sudo apt update && sudo apt -y install wget && sudo wget https://raw.githubusercontent.com/tr4vLer/xenvast/main/autostart_linux.sh && sudo chmod +x autostart_linux.sh && ./autostart_linux.sh
```
Version without a desktop icon.
```bash
sudo apt update && sudo apt -y install wget && sudo wget https://raw.githubusercontent.com/tr4vLer/xenvast/main/autostart.sh && sudo chmod +x autostart.sh && sudo ./autostart.sh
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

### Market Order workflow
![image](https://github.com/tr4vLer/xenvast/assets/149298759/34897955-429f-4cba-926c-3b741fd25f0a)
-  **Searching for GPUs:** The script is looking for GPUs that are available for rent on the market and match the specific type ("GPU name") you're looking for.
-  **Ordering GPUs:** When it finds matching GPUs, the script will try to rent them. It decides which ones to rent based on single GPU unit cost* and whether they meet your needs. 
   _*Single GPU price = (total instance price) / (instance gpus)_
-  **Monitoring:** After renting a GPU, the script keeps an eye on it to make sure it's working correctly. It checks to see if the GPU is running and being used as expected. If a GPU isn't working right, the script will stop renting it and look for another.
-  **Threading for Efficiency:** The script uses something called "threading" to monitor multiple GPUs at once without getting slowed down. This means it can keep track of several rented GPUs simultaneously, making sure they're all working as they should.
-  **Handling Instances:** If a GPU rental (an "instance") isn't functioning properly—perhaps it's not operating correctly or isn't utilized adequately—the script will terminate the rental. Additionally, it places certain machine IDs on a blacklist to prevent renting it again.
-  **Repeating the Process:** The script keeps searching for, renting, and monitoring GPUs until it's rented the number of GPUs you specified in the "GPU’s quantity" box.
-  **Finishing Up:** Once the script has rented and successfully set up the desired number of GPUs, it stops running and logs that it's done. The entire process might take 10 minutes or more, depending on the specified amount and machine condition.
<!-- Separator Line -->
<hr>

### Limit Order workflow
![image](https://github.com/tr4vLer/xenvast/assets/149298759/c9d12799-8822-4b60-9a37-4198e9f54510)
- **GPU Searching:** The script searches through GPUs available on the market based on predefined criteria such as GPU name and the hourly cost that you are willing to pay ("Limit price per GPU"). It will not place any orders until an offer that meets your criteria is found. Similarly to Market Order script calculates chepest offers using same formula; Single GPU price = (total instance price) / (instance gpus)
- **Order Placement:** Upon finding suitable GPU offers, the script attempts to place orders for them. It determines the Docker image version based on CUDA compatibility and sends a request to the API to initiate the rental process.
- **Instance Monitoring:** After placing an order, the script monitors the rented GPU instances to ensure they are running and utilized properly. It checks for GPU utilization and DPH (Dollar Per Hour) rates to verify successful operation.
- **Instance Destruction:** If a rented instance fails to meet requirements within a specified timeout period, the script terminates the rental and adds the machine ID to the ignore list to prevent future rentals.
- **Threading for Efficiency:** The script utilizes threading to handle multiple rental and monitoring processes concurrently, improving efficiency by parallelizing tasks.
- **Order Limit Handling:** The script keeps track of successful orders and stops renting GPUs once the maximum order limit for instances is reached. Please note that this limit refers to the number of **instances**, not the total number of GPUs, as in the Market Order. This approach maximizes the opportunity hunt to its fullest potential.
- **Script Completion:** Once the script has reached the maximum order limit or encountered errors, it finishes execution and logs the completion status.
<!-- Separator Line -->
<hr>

### XUNI Farming workflow
![image](https://github.com/tr4vLer/xenvast/assets/149298759/4ac8f522-3d93-4989-80a5-6bfc0602943c)
- **XUNI Time Window Handling:** The script waits for a specific time window (the 53rd minute of every hour) to ensure GPUs are ready and start XUNI farming at 55th minute of each hour.
- **GPU Searching:** The script searches for available GPUs on the market based on predefined GPU names. It utilizes the Market Order mechanism to place orders; however, it only performs one round of condition checks. If any of these checks fail, the subsequent order will not be placed due to the limited time window.
- **Order Limit Handling:** The script keeps track of successful GPU orders and stops renting GPUs once the maximum order limit for instances is reached.
- **XUNI Instance Destruction:** After the XUNI time window, which occurs at the 6th minute of each hour, the script destroys the rented instances used for farming to ensure resource optimization.
-  **Repeating the Process:** The script continues to repeat all of the above steps until it is manually stopped.
<!-- Separator Line -->
<hr>

### Instances tab
![image](https://github.com/tr4vLer/xenvast/assets/149298759/f4360c62-2b09-4745-98c9-afc8bb688d23)
The instance tab provides you with basic information regarding the machines you are renting. You can see the resource usage, machine IDs, GPU names, and the number of GPUs for each instance. It also identifies if an instance is running and provides the current status. Additionally, it provides users with the possibility to perform basic tasks like reboot, rebuild, and destroy.

The rebuild function is mainly intended for users who already own instances and want to rebuild them to obtain fully automated machines that do not require any manual attention or interactions. It can also be used to rebuild instances with different ETH addresses.

The Instances tab also provides information about Hash speed and mined blocks. Please note that this information comes from the performance bot and is updated every 5 minutes.
<!-- Separator Line -->
<hr>

### Performance tab
![image](https://github.com/tr4vLer/xenvast/assets/149298759/9c119aed-c098-4b9a-b189-d62a014b5d41)
- **Instance Listing:** Script Retrieves information about instances from the vast.ai platform using an API call. Information includes instance ID, GPU name, GPU utilization, disk utilization, CPU utilization, etc.
- **SSH Connection and Log Retrieval:** Script establishes an SSH connection to each instance to retrieve log information. It retrieves data such as mining status, hash rate, runtime, and difficulty from instance log files every 5mim but you can request that instantly on button click
- **Data Processing and Analysis:** Processes and analyzes retrieved log information. Calculates metrics like average hash rate, standard deviation, outliers, and performance statistics for each GPU type.
- **Table Generation:** Every 5min script generates formatted tables containing performance data. It generates text and HTML outputs with performance summaries, detailed performance data, warnings about underutilized GPUs, outliers, and statistics. Outputs are stored in files named table_output.txt, table_output.html.

### Note
The tool is deploying [v1.1.3 xenblocksMiner by woodysoil](https://github.com/woodysoil/XenblocksMiner/releases/tag/v1.1.3) to each instance it rents. Please note that there is a minimum preset DEVfee of 5%.

