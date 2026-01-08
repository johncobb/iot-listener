# Redsky Notes

CalAmp login on lastpass

[Device Managment Portal](https://puls.calamp.com/devicemgr/)

[Wiki](https://puls.calamp.com/wiki/Main_Page)

## [Getting Started](https://puls.calamp.com/wiki/Getting_Started#Sending_a_Script_Through_Serial_Connection)

### Setting up APN (not needed if using a CORE SIM)
```
AT$APP PARAM 2306,0,<APN>

AT$APP PARAM 2306,1,<APN>

AT$APP PARAM 1024,35,255,1 - sets APN
```
### Pointing the device to a UDP listener/backend server with at commands 
```
AT$APP PARAM 768,0,<IP ADDRESS>

AT$APP PARAM 769,0,<PORT>

AT$APP PARAM 2319,0,<IP ADDRESS>

AT$APP PARAM 2319,1,<IP ADDRESS>
```
### [AT Commands](https://puls.calamp.com/wiki/LMU-3030_Hardware_%26_Installation_Guide)

AT#FACTORY - Resets modem to factory

AT$APP DEFAULT ALL - Resets all settings

AT$APP COMM STATUS? - Network information

## Troubleshooting AT Commands

Is there a SIM in the device and is it activated

Is your lmu acting up slap it with a AT#FACTORY to factory reset it

### [Example Scripting](https://puls.calamp.com/wiki/Scripting_Samples)

### Listener
on wiki
windows app
[ ] find python app
[ ] get communicating with listener
[ ] get sms working

## Notes for LMU1230 

#### [Puls  Manager](https://puls.calamp.com/wiki/PULS_User%27s_Guide)

[PULS API](https://puls.calamp.com/wiki/PULS_API) 

#### Auto Provisioning
The calamp should auto provision

username and password automaticly set to dummy if S-Register 155 is 1
 ```
 AT$APP PARAM 1024,35,1,0 
```
#### [PEG](https://puls.calamp.com/wiki/PEG_Programming_Guide)  
**[Parameters](https://puls.calamp.com/wiki/Parameters#Parameters)**

**[Triggers, Conditions, and Actions](https://puls.calamp.com/wiki/PEG)**

- **Event**
	- Trigger code
	- Trigger Modifier
	- Condition Codes
	- Condition Modifiers
	- Action Code 
	- Action Modifier

[Example Scripts](pegExample)
[Sample Configs](https://puls.calamp.com/wiki/Sample_Configs)
[Example Trailer Script](https://puls.calamp.com/wiki/Sample_Configs#TTU-7x0_Trailing_Tracking)

#### PULS (Programming, Updates, and Logistics System)

#### [LM Direct](https://puls.calamp.com/wiki/LM_Direct_Reference_Guide)


## Notes for [LMU123](https://puls.calamp.com/wiki/LMU-3030_Hardware_%26_Installation_Guide) (OBD2 device)

Uses Verizon SIM

Needs to be plugged into a vehicle to initilize (the device looks for 13 volts)

[//]: <Noah's Notes>