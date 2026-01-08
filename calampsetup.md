# LMU3040 Manual device setup

## Table of Contents
[Overview](#overview)<br>
[Requirements](#requirements)<br>
[Activate Sim](#activate-sim)<br>
[Device Setup](#device-setup)<br>
[Execute Script](#execute-script)<br>
[Checking Status](#checking-status)<br>
[FAQ](#faq)<br>

## Overview

This setup guide is for provisioning the LMU 3040 calamp devices before being shipped out for vehicles in the field. This goes from activating a sim for the current plan, adding the script, setting up the device, and executing the script. Currently under testing and review before finalization.

## Requirements

- Command Prompt/Terminal or WinSCP
- PuTTy (optional)

<br>

## Activate Sim

- Grab a nano sim. Hans/Matt should have a list of available nano sims to use.
- Log into [KORE](https://connect.korewireless.com/) with your credentials.
- On the left hand side of the screen under <b>Quick Links</b> on the KORE website, click <b>Activate</b>
- Click <b>Paste Sims</b> and hit <b>Continue</b>.

<b>Note</b>: If the sim is found in the Rejected category, that sim may already be active.

- If the sim as accepted, hit <b>Continue</b>.
- Hit <b>Continue</b> again. This screen should just show you its moving the sim to an active state.
- In the  <b>Profile Parameters</b> screen , choose <b>Redsky no sms</b>.
- Verify the following are checked: <b>US LTE Dynamic 10569</b> and <b>USG Service - Data</b>
- For the <b>Activate</b> screen, click on <b>LTE 25MB Pooled - 25MB SIM daily usage</b> and <b>LTE 25MB Pooled - 50MB SIM monthly usage</b>.
- Review your selections, then hit <b>Confirm</b>

The sim will now be in a request activation state. It can take anywhere between 5 - 10 minutes for activation.

- Confirm device activation on the next screen. An email will go to Hans.
- Inform JN/Hans/Matt of the sim activated, IMEI and ECD of LMU device via Slack. You should be able to fimd the LMU device information on the side of the device. 
- Add the provided information (ESN, IMEI, and ICCID) to the inventory sheet for redsky.

<br>

## Device Setup

- Clone repo [peg scripts](https://gitlab.com/cpht/redsky/services/peg_script) or download the zip file to your local machine. This holds the peg script you need to move over to the LMU device.
- Insert sim into LMU device, the envelope side of the sim card goes in first and should snap into place.
- Power on the DC power supply and adjust to the correct setting. Voltage needs to be at a minimum 13.8V.
- Power off the DC supply.
- Connect LMU device to the circuit board. The circuit board should already be hooked up to the DC power supply on the desk. 
- Connect LMU device to your computer via usb cable provided for the device.
- Power on DC power supply again. The power supply must be at a minimum threshold of 13.8v to simulate a vehicle starting up which you should already have done. 

- <b>If your computer is using Windows</b> You can use Command Prompt or WinSCP to move over the file to your LMU device.
    - <b>If you're on Linux</b>: You can use the terminal to issue the commands.

### If you're using Command Prompt or Terminal

- Open Command Prompt/Terminal app, depending on your coumputer OS.
- Once Command Prompt/Terminal opens, use the command `cd` to navigate into the [peg scripts](https://gitlab.com/cpht/redsky/services/peg_script) repo directory you downloaded earlier. The directory should be called `peg-script master`.
- <b>If you are on Windows</b>: Issue the command `dir` to list the files and find the most recent peg script name. The file should be <b>Matt_PEG2_testScript_versionnumber.pg2</b>. 
   - <b>On Linux/Mac</b>: Run the command `ls` instead to see the list of files.

The most recent `versionnumber` is 4 (subject to change). You can see this below.

<kbd><br><img src=/calampsetupimg/win1.png><br></kbd>

Regardless of which system you're using, you should be able to locate the correct files

- To transfer the file, run `scp Matt_PEG2_testScript_versionnumber.pg2 calamp@192.168.225.1:/data/configs/files`. Remember to replace `versionnumber` with the latest version number. At the time of this documentation, the latest version number is 4.
- Enter the password for the calamp device: <b>welcome123</b>.

SCP will transfer the file over to the device and show the percentage completion (which you can see in the figure below). Keep the Command Prompt/terminal up for the next step.

<kbd><br><img src=/calampsetupimg/win2.png><br></kbd>

### If using WindowsSCP

- Open WinSCP or [download WinSCP](https://winscp.net/eng/download.php).
- Start the application.
- Fill in the following information: Using <b>SFTP</b> file protocol, IP address of <b>192.168.225.1</b> and port <b>22</b>. The username will be <b>calamp</b> and password is <b>welcome123</b>.

<b>Note</b>: If you get a warning, just click <b>Yes</b> to continue.

- Naviagte into the directory `data/configs/files/`. This should be on the right hand side of your screen.

<kbd><br><img src="/calampsetupimg/winscp01.PNG"><br></kbd>

- Move the PEG2 file into this location `data/configs/files`.
- Double check to see if the PEG2 file is in the correct directory.

<kbd><br><img src="/calampsetupimg/winscp02.PNG"><br></kbd>

<b>Note</b>: There may be more then one script files already in this file location as the script is set using a command later on.

- From the task bar above, choose <b>Sessions</b> and select <b>Close session</b> or click the "X" on your session tab.

You may now close out of WinSCP and move on to the next section.

<br>

## Execute script

You'll now need to log into the device and execute the peg script. Follow the instructions below for either using Command Prompt/Terminal or using PuTTy.

### If you're using Command Prompt or Terminal

- Log in to the calamp device with ssh using the command `ssh calamp@192.168.225.1`
- Enter the same password: <b>welcome123</b> and you will be in the device's terminal. You should see a <b>calamp@mdm9607</b> on the left side of the screen.
- Run the command `cd ../../data/configs/files/`.
- Run the command `ls` to verify the files you moved over are in the directory.

<kbd><br><img src="/calampsetupimg/win3.png"><br></kbd>

- Execute the setup script with the command `dnld_cli prog_file 0 22 Matt_PEG2_testScript_versionnumber.pg2`. Remember to replace `versionnumber` with the latest number in the repo.

After execution, you should get a message saying <b>prog_file - [0] success</b>. Stay logged into the LMU device to check its status.

<kbd><br><img src="/calampsetupimg/win4.png"><br></kbd>

### If you're using PuTTy

- Open Putty
- Using the same IP address <b>192.168.225.1</b> and Port <b>22</b>.

<b>Note</b>: These connections can be saved with the "save" button for easier and faster connections in the
future for devices that use the same parameters.

- When the connection is successfull a promt asking for login will appear, for the username: <b>calamp</b>
- Next a promt will ask for a password: <b>welcome123</b>

<b>Note</b>: If you haven't used PuTTy before, when you type your password, it won't appear on your terminal.

If the login was success you should see something similar to `calamp@mdm9607:~$` appear on the terminal. This indicates you're now inside the LMU3040 device and can execute the script.

- Next navigate into the files folder, to do this use the command `cd ../..data/configs/files/`
- Use the command `ls` to list the files in this directory, the file uploaded with WinSCP should be seen here.
- To set the script you would like the device to use enter the following command. `dnld_cli prog_file 0 22 <PEG2 File>.pg2`, where `<PEG2 File>` is replaced with the EXACT name of the file as you see it in the directory.
- A success attempt at setting this file will get the response: `prog_file - [0] success`.
- Enter the command `exit` to close out of PuTTy.

You can now disconnect the LMU3040 from your computer.

<br>

## Checking Status

Once the peg script is executed, you can check by using the command `atcon` to review the LMU device status. This will determine if the device can receive data. 

- While still in the calamp device, run the command `atcon`. This will take you into the command terminal for calamp devices
- Run the command `atic`. This will bring back the general status of the device.
- Check the top four categories that come up. You should have the following respond.

| Category | Status |
|---|---|
| Radio Access | LTE |
| GSM Registered | Yes, Home |
| GPRS Registered | Yes, Home |
| Connection | Yes |

All the categories listed can be seen in the screenshot below.

<kbd><br><img src="/calampsetupimg/win5.png"><br></kbd>

<b>Note</b>: Categories <b>Phone Number</b> and <b>GPRS APN</b> may not appear, but are registered for the device. This is all set up through the script.

<br>

## FAQ

- APN is set, but may or may not show up when checking general settings.
