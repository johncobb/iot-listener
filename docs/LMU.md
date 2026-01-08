<b>Note</b>: Work in progress

## Table of Contents 

[[_TOC_]]


## 1. Overview

<div id='overview'/>

The Red Sky experiment is all about using Cal Amp devices to track vehicles and assets using a small GPS device requiring 12 volts usage. 
    
Organizations use Cal Amps for tracking vechicles located around the globe. This can be for taking inventory, car locations, or even checking the status of the vehicle. 
    
Using the tracking device, companies can keep an accurate account of their vehicles no matter where they can be. Calmps uses satellite DBS technology and wireless networks for their scope.

The devices being used in the experiement is the LMU-1230 Standard Cal Amp and the LMU-3035. Getting started will require activating the SIM card to be activated and connected to CalAmp's Programming Update Logistics System (PULS) for software developments. You'll also need to be familiar for using Programming Event Script (PEG).

<div id='backgroundrecommendations'/>

## 2. Background Recommendations

-<b>Programming Event Generator (PEG)</b>: PEG is implemented for uploading scripts in use. For example, an organization can upload their own scripts when tracking vehicle locations. The scripts can go more into depth by keeping updates on their location via GPS, monitoring the speend, and validating the VIN to name a few. 

-<b>AT Commands</b>: The experimnet uses AT Command parameters using `AT$APP PARAM` Understanding how the parameters are set up will help read the script. Commands look like the following

`AT$APP PARAM <ID>,<index>,<value>` 

Parameter `<value>` can have more than one field that can be separated by a comma. Queries can be in two forms: either a single values of an index `AT$APP PARAM? <ID>,<index>` or a query on all the values included `AT$APP PARAM? <ID>,*`.

-<b>AT Command Compatibility</b>: This is a chart that lists all the commands that are comparable for which LMU device you have. You can reference this for general commands and what to use.

Theres more you can see when looking at the chart [here]()

<div id='experimentsetup'/>

## 3. Experiment Setup

For the OS, we are using a Unix system with a Windows box for LMU manager toolbox. Currently, Cal Amp only has a manager set up for Windows mahcines. We suspect the calls made for the cal amps work just as well on Linux.

- CalAmp LMU-3035 or LMU-1230: All experimentals are being used on these devices.
- [UDP](https://www.puls.calamp.com/wiki/Tools_%26_Utilities) Listener 
- [LMU Manager 8.3](https://www.puls.calamp.com/wiki/Tools_%26_Utilities)

<a href="https://www.puls.calamp.com/wiki/Tools_%26_Utilities">test link</a>

|LUM-3035|LMU-1230|
|:----------|:-----------|
|Verizon SIM|AT&T Hologram SIM|
|Vehicle with OBD-2 diagonistics port|12V power supply|
|USB to RS-232 serial cable with a 4 to 5 pin Molex cable|USB to RS-232 serial cable|

<div id='helloworld'/>

## 4. Hello, World!" Test: LMU-3035

This tutorial will show you have to run a basic script for getting a response. Consider this test similar to the "Hello, World!" popular test working with a new IDE for the first time. Before starting the tutorial, go ahead and open [Hologram Portal](dashboard.hologram.io) for the sim and the [PULS device manager](puls.calamp.com/devicemgr) for managing the software in separate tabs.

- On the LMU-3035, remove the plastic case.
- Insert the Verizon Sim. (Went through the verizon site)
- Close the cover.

#### If using the AT&T sim

- Go onto the Hologram Portal and click the blue button `Activate SIMs` if you haven't already.

<b>Note</b>: the LMU-3035 can only activate when plugged into a running vehicle. this is because for the device to recognize the ingntion has started, it needs to read 13 volts. Be advised that it may take about 5 to 10 minutes before you get a reading on it.

- Pull up the PULS device manager. This will bring you to the device manager screen.
- Click the blue button on the top called `Status`.
- If the ESN number for the device does not show up, refresh the page until you see the confirmation. Otherwise click the `SELECT` button to display all the devices. A new page will appear with all the various devices activated. (
- For this experiment, look for the device numbered `4572063491`
- Connnect your device with the usb serial cable.
- Open a terminal on your Unix system and type the command `cu -s 115200 -l /dev/ttyusb-RS232`. This will open another system as a dial-in terminal a serial connection at 11200. 

<b>Note</b>: speed `115200` is the recommended speed when making a status connection at the time. 

<b>Note</b>: In case you are running into problems with making the call connection, you may have to use `screen` for your system

- Type `at` into the new session to see if you get a response `OK`.

<img src="/img/atcommand.png">

- Type `atic` to get the general status of the device.

<img src="/img/aticcommand.png">

- To check for the device to see if its connect, use the command `AT&APP COMM STATUS?`.

Hello world example here

```
AT$APP PARAM 768,0,<IP ADDRESS> //Inbound IP address, currently using IP 67.115.44.14
AT$APP PARAM 769,0,<IP ADDRESS> //Inbound Port
AT$APP PARAM 2319,0,<IP ADDRESS> //Inbound URL
AT$APP PARAM 2319,1,<IP ADDRESS>  //Inbound URL -> what does index 1 mean vs 0?

```
- Open LMU Toolbox on your windows device 
- Go to `UDP Receiver` and check `UDP receiver ON`
- Watch for your device to respond

<div id='helloworld2'/>

## 5. "Hello, World!" Test: LMU-3035 upload

This section will show you how to upload a script with the AT commands. The commands can be written to a `.csv` file. 

<b>Warning</b>: When you are making a csv file script, do not make this in excel. Since Cal amps is reading in hex values, excel does not catch this. If you create a csv file on your Windows device, it will also strongly encourage you to open the file in Excel. It's best that if you are working on a script to import, do this in vim.

- Open the PULS manager
- On the top bar click the `config` tab.
- Upload your `.csv` file by clicking `Import CSV`
- Go back to `Status` and click `SELECT` to see all the devices.

<div id='helloworldcsv'>

## 6. helloWorld.csv

This is a basic script that comes up when the cal amp activates for the first time.

```
paramter_id,parameter_index,parameter_value
512,0,0F000000012A0000,If the ignition is on then there will be a report number 42 sent to udp server
512,1,1000000001010000,If the ignition is off then there will be a report number 1 sent to the udp server
512,2,0F00050031810000
1024,1,04
1024,23,1
1026,0,08

```
<div id='appidforlmu1230'>

## 7. App id for LMU-1230

Still need info from Noah on his experiment for this section. The same steps are applied for creating and importing for the LMU-1230. 

<div id='pegscriptwithwindows'>

## 8. PEG script with Windows

For using the Windows interface, one thing you will need to change is the port forward. Make sure the port forwarded is `20500` for the Windows ip address. This script will show how the ignition is determined on or off

`AT$APP PARAM 512,0,15,0,0,0,1,0,0,0`

|ID Value|Definition|
|:-----------------------:|:-------|
| 512 | Event Record recorder (this has 9 modifiers |
| 0 | Event 0, 0 meaning the event is not active |
| 15 | Trigger code 15 represents LMU's ignition input transitioning from low to high |
| 0 | Tigger Modifier, LMU ignition does not have a modifier |
| 0 | Condition 1 Code, LMU does not have any conditions attached |
| 0 | Condition 1 modifier, LMU does not have any modifiers attached |
| 1 | Action Code, 1 represents sending an event report |
| 0 | Action Modifier , no action modifier added|
| 0 | Codition 2 Code, no condition executres|
| 0 | Condition 2 Modifier, no modifier executes |

Code for ignition off

`AT$APP PARAM 512,1,16,0,0,0,1,1,0,0`

|ID Value|Definition|
|:-------:|:---------:|
| 512 |Event Record recorder (this has 9 modifiers)|
| 1 | Event 1, 1 meaning the LMU is active |
| 16 | Trigger code 16, 16 LMU ignition is going from high to low  |
| 0 | Tigger Modifier, no trigger modifier needed|
| 0 | Condition 1 Code, no condition code needed |
| 0 | Condition 1 modifier, no condition modifier necessary |
| 1 | Action Code, 1 sends an event report with the event code |
| 1 | Action Modifier 1, 1 is the event code from earlier |
| 0 | Codition 2 Code, no condition code needed |
| 0 | Condition 2 Modifier, no conidition modifier necessary |

<div id='knownissues'/>

## 9. Known Issues

- Remeber to activate the sim before starting the device.
- Send `AT#FACTORY` to factory reset modem
- Send `AT$APP DEFAULT ALL` to reset all settings
- Problems did arise when trying to call for the device after a factory reset using a Linux machine. Repeating the experiment inside on the board proved successful though

<div id='questions'/>

## 10. Questions

- Windows being used solely for LMU manager and LMU toolbox
- Send Bindary 89? Is this for the hex values only? (helps compress but not doing what we want) 


## Notes for myself

- Peg split into Triggers, conditions, and actions
- Triggers tell what events happen, ans scans for the Event list. Trigger Code a numeric value, trigger modifiers describes the trigger. Some triggers do not have modifiers, refer to appendix A for that.
- Trigger conditions determine when the evens can occur. Conditions are also in code as well and can have some modifiers.
- Actions are what happens when the event starts. Also in code and have modifiers attached to them. 
- Once the trigger fires, it goes into a queue and is checked through an event list. the event list starts at 0.  When a trigger is matched with an event, the conditions are then tested before the action executes. After the action, the trigger continues for any more matching the event. Once the list is terminated, the next trigger is pulled from in queue and processed.

PEG

- PEG can transmist location data either via UDP/IP or SMS
- LM reporting is the following: event reports, mini event reports, user messages, id reports, version reports, and acknowledgements
- Message logging has store and forward, batch, and unacknowledged. PEG has several actions that can create an event report or mini event reports(Check PEG actions)
- Null messages act as a check
- Logs and User messages are also send. Log full is triggered when at 80% capacity. Log Inactive is trigged when the log is completely full.
- Accumulators have to be started by a PEG action.
- Accumulating the average diestant of a vehicle can use the Accumulator divide (88) 
- Timers do countdowns to zero
- Speed Threshholds and movement are also there
- Triggers can be delayed 
- PEG zones can be broken into 5 zones: Lat/Long coordinates, distance in meters, a second distance in meters, geometry of value, hystereis value (how far outside or inside the rectangle the LMU must travel)
<b>Note</b>: Geo-Zones is not a parameter and need special steps to work properly.
- Text messages can be support from 15 to 63 characters long.
- Binary messages covered by the Send Binary (89) which the action modifier dictates three items.
- `AT$APP PARAM 2176,5,"100A02H800EC100300"` = Long string parameter (2176) short string is 2177, 
- PEG flags are booleans for multiple events, also has 3 conditions to flag status
- Date and time are parameter 267 (actual time of day) and parameter 268 (measured in seconds). Parameter 269 stores 4 day of week strings (bit 0-6 = Sunday-Saturday)
- Voice call being used?
- PEG Enviornments are predetermined by either the bit set or bit cleared

## LMU guide

- IP the one we are using? / input port 20500
- UDP selection
- Unit must be created before importing a script, do not need a mobile number
- APN cannot block IP (216.177.93.246)

check in for PULS

```
AT$APP PEG ACTION 49 129
AT$APP PEG SNDID 129
!R3,49,129

```
Communicate->Read->Unit Configuration or Communicate->Write->Unit Config
- LMUToolbox to decode the message, LMUManager is to build the configs