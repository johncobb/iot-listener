# LMU Packet Structure
[Overview](#overview)<br>
[Example Piece](#example-piece)<br>
[IP and UDP Header](#ip-and-udp-header)<br>
[Options Header ](#options-header)<br>
[Options Byte Analysis](#options-byte-analysis)<br>
[Options Header Continued](#options-header-continued)<br>
[Message Header](#message-header)<br>
[Event Report](#event-report)<br>
[Complete Message](#complete-message)<br>
[Specific Conversions](#specific-conversions)<br>
[Summary](#summary)<br>


## Overview

This section dissects the structure of the LM Direct packet messaging structure that passes from the Calamp Device to the UDP server. Messages come back to the server in bytes and must be parsed out for human readability's (thanks to our peg script). The message bytes can be broken up into the following categories below.

The way the packet that comes back is structured as the following: IP Header -> UDP Header -> Options Header -> Message Header -> Message contents (also known as application data). Application data results in either a null message, and event report, and ID report, or a mini even report. Below is a helpful graph showing the packet structure.

```
______________________________________________________________________________
|IP Header| UDP Header | Options Header | Message Header | ApplicationData   |
|_________|____________|________________|________________|___________________|
<------------------------- Packet ------------------------------------------->
                                  <------- Null Message -------------------->
                                               - OR -
                                  <------- Event Report Message ------------>
                                               - OR -
                                  <------- ID Report Message --------------->
                                               - OR -
                                  <------- Mini Event Report Message ------->
```


### Example piece

Throughout the explanation, we will use some example code byte strings that come through

```
45 00 00 51 00 0A 00 00 80 11 BE 8B 33 33 33 33 44 69 F2 37 
50 1E 50 14 00 3D 52 3B 83 05 45 72 06 49 03 01 01  01 02 18 
A5 60 FE E1 1F 60 FE E1 1F 16 9D DD 78 CB E7 13 4B 00 00 
24 91 00 00 00 02 00 66 0E 02 01 9A FF B7 AF 07 00 00 FF 02 
01 00 00 00 00 00
```

<br>

## IP and UDP Header

From the example above is the IP and the UDP Header.

##### Example packet: IP header 
<b>45 00 00 51 00 0A 00 00 80 11 BE 8B 33 33 33 33 44 69 F2 37</b><br> 
50 1E 50 14 00 3D 52 3B 83 05 45 72 06 49 03 01 01  01 02 18<br>
A5 60 FE E1 1F 60 FE E1 1F 16 9D DD 78 CB E7 13 4B 00 00<br> 
24 91 00 00 00 02 00 66 0E 02 01 9A FF B7 AF 07 00 00 FF 02<br> 
01 00 00 00 00 00

##### Example packet: UDP header 

45 00 00 51 00 0A 00 00 80 11 BE 8B 33 33 33 33 44 69 F2 37<br> <b>50 1E 50 14 00 3D 52 3B</b> 83 05 45 72 06 49 03 01 01  01 02 18<br> 
A5 60 FE E1 1F 60 FE E1 1F 16 9D DD 78 CB E7 13 4B 00 00<br> 
24 91 00 00 00 02 00 66 0E 02 01 9A FF B7 AF 07 00 00 FF 02<br> 
01 00 00 00 00 00

Neither the IP Header or the UDP header will appear when message requests come back. This is due to the python socket taking are of both headers. 

<br>

## Options Header

45 00 00 51 00 0A 00 00 80 11 BE 8B 33 33 33 33 44 69 F2 37<br>
50 1E 50 14 00 3D 52 3B <b>83 05 45 72 06 49 03 01 01</b>  01 02 18<br> 
A5 60 FE E1 1F 60 FE E1 1F 16 9D DD 78 CB E7 13 4B 00 00<br> 
24 91 00 00 00 02 00 66 0E 02 01 9A FF B7 AF 07 00 00 FF 02 <br>
01 00 00 00 00 00

<b>Options Header</b> is the most dynamic frame of the packet sent. The options byte broken down into binary will indicate the fields that follow marked by 0's and 1's. Depending on their status, ti will add on to the packet length.

```_____________________________________________________________________________________________
       | Options Byte | Mobile Id Length |     Mobile Id    | Mobile Id Type Length | Mobile Id Type |
       |______________|__________________|__________________|_______________________|________________|
Raw Data|      83      |         05       |  45 72 06 49 03  |          01           |      01        |
Decimal |       -      |          5       |    4572064903    |           1           |       1        |
Binary  |   1000 0011  |          -       |        -         |           -           |                |
       |______________|__________________|__________________|_______________________|________________|
length  0              1                  2                  6                       7                8
       <----------------------------------- Options Header ----------------------------------------->
```

### Options Byte Analysis

Before decoding the end of the options header, you need to understand what the <b>Options Byte</b> is indicating. The options byte can be broken down into binary and tell via boolean if a field is enabled (1) or disabled (0). This starts with the most significant bit (leftmost binary number) below.
```
________________________________________________________________________________________________________________________________________________________________
|  Options Byte                                                                                                                                                  |
|  ASCII - 83                                                                                                                                                    |
|  Binary - 1 0 0 0 0 0 1 1                                                                                                                                      |
| Mobile ID = 1 | Mobile ID Type = 1 | Authentication Word = 0 | Routing = 0 | forwarding = 0 | Response Redirection = 0 | Options Extension = 0 | Always On = 1 |
|________________________________________________________________________________________________________________________________________________________________|


```
So from the example above, the options header fields are the following.

- 1: Always set to 1
- 0: Options extension disabled
- 0: Response Redirection disabled
- 0: Forwarding disabled
- 0: Routing disabled
- 0: Authentication Word disabled
- 1: Mobile ID Type enabled
- 1: Mobile ID enabled

<b>Note</b>: The usual options needed are just Mobile ID and Mobile ID Type. That's more than enough to get the data we need to come back. This means the options header byte will most likely be <b>83</b>.

<br>

## Options Header Continued

After breaking down the options header byte, you can continue with the options header starting with the <b>Mobile ID Length</b>, indicated by the byte <b>05</b>

| ASCII | 83 | 05 | 45 72 06 49 03 | 01 | 01 |
| -: | :-: | :-: | :-: | :-: | :-: |
| DEC | - | 5 | 4572064903 | 1 | 1 |
| BIN | 1000 0011 | - | - | - | - |

- Mobile ID Length (05): Indicates how many bytes are contained in the Mobile ID. Typical is 5 bytes, so the next 5 bytes will be Mobile ID of the device.
- Mobile ID (45 72 06 49 03): Mobile ID of LMU device that is either sending or receiving a message.
- Mobile ID Type Length (01): Will always be 1.
- Mobile ID Type (01): Indicates the type of Mobile ID

<details><summary>Mobile ID Types</summary>

| Code | Description |
|---|---|
| 00 | OFF |
| 01 | ESN |
| 02 | IMEI or EID |
| 03 | IMSI (for GSM and GPRS only) |
| 04 | User specified Mobile ID |
| 05 | Phone number |
| 06 | IP of LMU |
| 07 | MEID or IMEI of modem |

</details>

<br>

## Message Header

the message header follows the options header field. For the message header, three fields will indicate what application data will be returned from the message. The three fields spilt up are Service Type, Message Type, and Sequence number. See below the bolded section indicating the Message header

##### Example Packet: Message header
45 00 00 51 00 0A 00 00 80 11 BE 8B 33 33 33 33 44 69 F2 37<br> 
50 1E 50 14 00 3D 52 3B 83 05 45 72 06 49 03 01 01 <b>01 02 18<br>
A5</b> 60 FE E1 1F 60 FE E1 1F 16 9D DD 78 CB E7 13 4B 00 00<br> 
24 91 00 00 00 02 00 66 0E 02 01 9A FF B7 AF 07 00 00 FF 02<br> 
01 00 00 00 00 00

So in concept, this separates the header into the following below:

```
        _____________________________________________________
       |  Service Type  | Message Type |   Sequence Number   |
       |________________|______________|_____________________|
Raw Data|      01        |      02      |       18 A5         |
Decimal |       1        |       2      |        6309         |
       |________________|______________|_____________________|
length  0                1              2                     6
```



- <b>Service Type</b> (01): Tells us what type of request is coming through. 00 is an Unacknowledge Request, 01 is Acknowledged Request, and 02 is a Response to an Acknowledge Request.

- <b>Message Type</b> (02): Message type sends back the type of message we should be receiving. For our case, we are only worried about the following four messages that will come across. 

| Message Type Number | Message Type Name |
| --- | --- |
| 00 | NULL Message |
| 02 | Event Report |
| 03 | Id Report |
| 10 or 0A | Mini Event Report |

A <b>Null Message</b> just sends us an empty message and contains no data. Null messages are used to keep the connection open and the firewalls active for the packet frame. If we do get a null message back, there should be 3 trailing bytes that follow containing zeros, with the sequence number responding.

#### Example null message

```console
83 05 01 02 03 04 05 01 01 00 00 00 01
```

<b>Event Report</b> comes back from the PEG script. The event report contains the most data information regarding vehicle location and details through GPS coordinates. 

<b>ID Reports</b> are sent back to help troubleshooting and debugging issue. The user gets back the script version and config version of the device out in the field and can be used to see the problem. Uses three scenarios to response either through a <b>PEG Action</b>, a <b>Unit Request Message</b>, or from an <b>SMS SENDTO</b> request.

<b>Mini Event Reports</b> is a watered-down version of the Event report. Only so many fields come back when requests are sent.

<b>Note</b>: Mini Event Report doesn't cover everything we would like to get back for accurate coordinates and due to accumulator stopping and starting randomly. You will mostly focus on the other three reports above. 

<br>

## Event Report

Event Reports will be the most common and documented pieces that come back in the decoded message. The LMU initiates the PEG script and reports back the message structure. The requests that come back can be either <b>Acknowledged</b> or <b>Unacknowledged</b>. The message header sets up what will come through for the parser to grab. 

##### Example Packet: Event Report continued from above

45 00 00 51 00 0A 00 00 80 11 BE 8B 33 33 33 33 44 69 F2 37<br> 
50 1E 50 14 00 3D 52 3B 83 05 45 72 06 49 03 01 01 01 02 18<br>
A5 <b>60 FE E1 1F 60 FE E1 1F 16 9D DD 78 CB E7 13 4B 00 00<br> 
24 91 00 00 00 02 00 66 0E 02 01 9A FF B7 AF 07 00 00 FF 02<br> 
01 00 00 00 00 00</b>

A more detailed structured of the Event Report can be seen below. 


```
        ________________________________________________________________________________________________________
       |  Update Time  | Time of fix  |   Latitude   |   Longitude  |  Altitude   |    Speed    |  Heading  | ...
       |_______________|______________|______________|______________|_____________|_____________|___________|___
Raw Data|  60 FE E1 1F  | 60 FE E1 1F  |  16 9D DD 78 | CB E7 13 4B  | 00 00 24 91 | 00 00 00 00 |   00 66   |        
Decimal |   1627316511  |  1627316511  |   379444600  |  3420918603  |    9361     |      0      |     102   |
Binary  |       -       |       -      |       -      |      -       |      -      |      -      |     -     |
       |_______________|______________|______________|______________|_____________|_____________|___________|
Length  0               3              7             11             15            19             23          25
       <--------------------------------- Event Report Message ----------------------------------------------
 
       _______________________________________________________________________________________________
       ...|  Satellites  | Fix Status  |  Carrier  |  RSSI   |  Comm State  |  HDOP  |  Inputs    | ...
       ___|______________|_____________|___________|_________|______________|________|____________|___
Raw Data   |       0E     |      02     |   01 9A   |  FF B7  |      66      |   07   |     00     |
Decimal    |       14     |      -      |    410    | 6546463 |      -       |    7   |      -     |
Binary     |       -      |  0000 0010  |     -     |    -    |   1010 1111  |    -   | 0000 0000  |
          |______________|_____________|___________|_________|______________|________|____________|
Length     25             26            27          29        31             32       33           34
          ---------------------------------- Event Report Message --------------------------------
 
       ___________________________________________________________________________________________________________
       ...|  Unit Status  |  Event Index  | Event Code  |  n * Accumulators  |  Spare Byte  |  Accumulators List  |
       ___|_______________|_______________|_____________|____________________|______________|_____________________|
Raw Data   |       00      |       FF      |      02     |         01         |      00      |     00 00 00 00     |
Decimal    |        0      |      255      |       2     |          1         |       -      |          0          |
          |_______________|_______________|_____________|____________________|______________|_____________________|
Length     34              35              36            37                   38             39                    39n 
           ------------------------------ Event Report Message -------------------------------------------------->

```

The breakdown below will show how the parser takes the raw data converts most of the fields into decimals. If any of the fields are broken into binary, this will be notified below.

- <b>Update Time</b> (60 FE E1 1F): This is the time of date the message came through, starting from Jan. 1, 1970. When this is converted with the calculation, the decimal value comes out to 452032 hours, 21 minutes, and 51 seconds. Or an easier read would be 18834 days, 16 hours, 21 minutes, and 51 seconds. That corresponds to 7/26/2021 16:21:51 GMT starting from Jan. 1, 1970. 
- <b>Time of Fix</b> (60 FE E1 1F): Last recorded GPS fixed location. This is also using Jan 1, 1970 and gives us back the same response as the update time section.

<b>Note</b>: The next three fields come back in signed 2's complement.
- <b>Latitude</b> (16 9D DD 78): GPS latitude reading. This comes out to 37.9444600 degrees
- <b>Longitude</b> (CB E7 13 4B): GPS longitude reading. The solution is -87.4048693 (negative due to 2's complement).
- <b>Altitude</b> (00 00 24 91): GPS altitude reading. Altitude is measured in centimeters above WGS-84 Datum (World Geodetic System) on Earth. In this case, altitude is 9361 centimeters above WGS-84.

Proof of this is through the quick way og getting the 2's Compliment value.

#### 2's Compliment Conversion Example: Longitude

```
- Take the raw data of our longitude data (CB E7 13 4B).
- Convert the data to binary (CB E7 13 4B = 11001011 11100111 00010011 01001011). You can double check this on a conversion calculator or website.
- Flip the bits except for the least significant bit (the right-most bit). Should have the section below.

11001011 11100111 00010011 01001011
00110100 00011000 11101100 10110101

- Convert back into decimal and add the negative sign to the final answer.
00110100 00011000 11101100 10110101 = 874048693 = -87.4048693
```

- <b>Speed</b> (00 00 00 00): Speed of the vehicle in motion. The GPS measures this in centimeters per second. In this example, the vehicle is stationary, measured at 0.
- <b>Heading</b> (00 66): Compass direction of said vehicle. This is measure in degrees from true North. The event reports the heading is 102 degrees from north
- <b>Satellites</b> (0E): Number of satellites called for finding the GPS coordinates. In this case, its 14. 
- <b>Fixed Status</b> (02): Fixed status is bit-mapped in binary (02 = 0000 0010). The various status are in the dropdown below. In our case, 02 represents the last known fix, meaning the current position is unavailable but a previous fix is obtainable.

<details><summary> Fix Status Indicators</summary>

| Fix Status | Data Field | Explanation |
|---|---|---|
| bit 0 | Predicted | horizontal position estimate is lower than Horizontal Position Accuracy Threshold. |
| bit 1 | Diff Corrected | WAAS DGPS is enabled and position is altered |
| bit 2 | Last Known | Current position is invalid but previous is available. |
| bit 3 | Invalid Fix | Only appears after a power-up or reset before getting coordinates. |
| bit 4 | 2D Fix | 3 or fewer satellites are used for GPS location. |
| bit 5 | Historic | Appears when message is logged by LMU. |
| bit 6 | Invalid Time | Only appears after a power-up or reset before obtaining a valid time-sync. |
| bit 7 | Reserved ||


</details>

- <b>Carrier</b> (01 9A): States what wireless modem is being used for GSM and CDMA devices. GSM uses the mobile network code (MNC) while CDSM uses the system identification number (SID). Our example is GSM since its using AT&T, and 410 corresponds with U.S. 
- <b>RSSI</b> (FF B7): short for Received Signal Strength Indicator, this field represents how good the signal strength is of the modem in use. The values is also in 2's complement, so the number comes out to -73, which is about fair or decent signal strength. 
- <b>Comm State</b> (66): Comm state is also bit mapped into binary, with our example `66` converted is `1010 1111`. All 1's indicate the status being active, with 0 being inactive.

<details><summary>Comm State indicators</summary>

| State | Data | Explanation |
|---|---|---|
| bit 0| Availability | Device is open to communication. |
| bit 1| Network Service | Network communication is available. |
| bit 2 | Data Service  | Device can send and receive information |
|bit 3| Connected | Point to Point Protocol (PPP) session is active. |
|bit 4| Voice Call |User can call the device with a mobile number. |
|bit 5| Roaming | Roaming services are active. |
|bits 6-7| Network Technology (has four options)| Reveals what network is being used. 00 = 2G on CDMA or GSM, 01 = 3G UMTS, 10 = 4G LTE, 11 = Reserved.|

</details>

- <b>HDOP</b> (07): Short for Horizontal Dilution or precision. This estimates the margin of error the satellite has when finding the GPS coordinates 
- <b>Inputs</b> (00): Current input states bitmapped in binary (0000 0000). At 00, this is the ignition. For our setup, we have the following mapped for the inputs.

<details><summary>Input Bits</summary>

| Input bit | LMU1240 & LMU2630 | LMU2035 & LMU3040 |
|---|---|---|
| bit 0 | Ignition On | Engine On |
| bit 1 | Input 1 - Pin3 (White) - Digital input| Motion Sensor (low = no motion, high = motion) |
| bit 2 | Input 2 - Pin12 (Orange) - Digital input | Power State (low = main power, high = battery power) |
| bit 3 | Input 3 - Pin6 (Violet) - Digital input | Vbatt Low |
| bit 4 | Input 4 - Pin7 (Grey) - Digital inputs| Vin Active (LMU3030 uses Input 4 for Ignition Input Wake Up Monitor instead of input 0|

</details>

- <b>Unit Status</b> (00): State of modules in the devices.  
- <b>Event Index</b> 255: Index number that creates the report. Peg scripts appear as 255 and is standard for our device.
- <b>Event Code</b> (02): Reflects the type of event code. You already see this in the Message Header. 02 represents an Event Report Message. 
- <b>n * Accumulators (01)</b>: Section showing the number of accumulators used in the message. Will most likely be 1. 
- <b>Spare Byte</b>: Leftover byte.
- <b>Accumulators List</b>: Total determined number of accumulators. Dependent on the Accumulator Reporting Format Type. 

<br>


## Complete Message

So by the end of the message, the Event report would report like the following.

```
This is an Event Report. This message comes in on 7/26/21 at 16:21:51 GMT. Last known GPS fix was on 7/26/21 at 16:21:51 GMT. 
Latitude and Longitude comes at 37.9444600, -87.4048693, with an altitude of 9361 centimeters above WGS-84 Datum. 
Speed registered is 0 centimeters per second (converted to mph in the script). Heading location is 102 degrees from North. 14 satellites were used to find the GPS location.

Fixed status reveals the following: Predicted is not set, WAAS DGPS is enabled, last known coordinates not known, invalid fix is disabled, 2D fix using three or fewer satellites is not enabled, historic values have not been logged, and invalid time is disabled.

Carrier type 410 is GSM, using AT&T and located in the United States. Received Signal Strength Indicator comes in at -73 (fair). 

Communication States gives the following: This device is available, network service is open, data service is available, connection with PPP session is available, voice call is deactivated, roaming is available, and network technology is 4G LTE.

The Horizontal Dilution of Precision is 7. 

No inputs are available for the wired capabilities. 


Unit status is okay. GPS antenna is okay. GPS Receiver is okay, and GPS receiver tracking is okay.

```
<br>

## Specific Conversions

When you look at the data from above, the python script takes care of a few extra conversions when the data from the LMU devices come through. The categories that take exceptions to the conversions are Update Time, Time of Fix, Longitude, Latitude, Fix Status, Comm State, and Accumulators.
 
<br>

## Summary

- Fields <b>Mobile ID</b>, <b>Mobile ID Type</b>, and <b>Accumulator List</b> are the lengths that cane different. All the other fields are static 
- Options header should be 18 characters (9 bytes), Message header should be 8 characters (4 bytes), Event Report is 80 characters (40 bytes). 
- <b>Options Byte</b>, <b>Fix Status</b>, <b>Comm State</b>, and <b>Inputs</b> are broken down into binary and can determine different fields that are active.
- Longitude, Latitude, and RSSI are in signed binary that give us the negative value.
- Fixed status is not used in our read, but kept in the example for clarity.

- We also have a list of current event codes listed below.

<details><summary>Event Codes</summary>

| Event Code | Event |
|---|---|
| 0 | Ignition On | 
| 1 | Ignition Off |
| 2 | Time Distance |
| 3 | Over speed limit |
| 4 | OTA Download | 
| 5 | OTA Complete |
| 6 | Idle Receipt |
| 7 | Parking Heartbeat |
| 8 | Calamp Battery Low |
| 9 | Vbattery Low |
| 10 | Reserved |
| 11 | Reserved |
| 12 | Reserved |
| 13 | Reserved |
| 14 | Reserved |
| 15 | Reserved |

</details>
