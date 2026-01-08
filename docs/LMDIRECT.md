# LM Direct Message Protocol

## Table of Contents
[[_TOC_]]

## Overview 
#### Reading Messages
The Raw data is in Hex ASCII 
```
Raw Data:
 83 05 01 02 03 04 05 01 01 01 02 00 01 4F B4 64 88 4F B4 64
 88 13 BF 71 A8 BA 18 A5 06 00 00 1333 00 00 00 00 11 11 02 
 33 44 44 55 55 66 77 88 99 10 11 ?? 00 ?? 

Decoded:
  -------Message Header--------
  01           Service Type, for this message 1 = Acknowledged Request
  02           Message Type, for this message 2 = Event Report
  -------Event Report----------
  4FB46488     Update Time (5/17/12 @ 2:38pm)
  4FB46488     Time of Fix (5/17/12 @ 2:38pm)
  13BF71A8     Latitude (33.1313576)
  BA18A506     Longitude (-117.2790010)
  00001333     Altitude
  00000000     Speed
  1111         Heading
  02           Satellites
  33           Fix Status
  4444         Carrier
  5555         RSSI
  66           Comm State
  77           HDOP
  88           Inputs
  99           Unit Status
  10           Event Index
  11           Event Code
  ??           Accums (# of 4-byte Accum List values)
  00           Spare
  ??           Accum List (Varies depending on the # of Accums reporting)
  ```

#### Event Report Message Types


`Type 0` - Null Message

`Type 1` - Acknowledge Messages

`Type 2` - Event Report Messages **Popular**

`Type 3` - ID Message Report

`Type 4` - User Message

`Type 5` - Application Message

`Type 6` - Parameter Message

`Type 7` - Unit Request Message

`Type 8` - Locate Report Message

`Type 9` - User Message with Accumulators

`Type 10` - Mini Event Report Message

`Type 11` - Mini User Message

`Type 12` - Mini App Message

`Type 13` - Device Version Report Message

`Type 14` - App Message with Accumulators

#### Event Message Flow
Events flow from the device to the LM Direct server to a listener.

## Helpful Links
[LM Direct Server](https://puls.calamp.com/wiki/LM_Direct_Reference_Guide)