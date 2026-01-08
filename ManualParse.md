
## Full Event Report example

83 05 12 75 03 12 69 01 01 01 02 00 04<br> 
60 9D 58 4D 60 9D 58 4C 16 9D DA E4 CB E7 0D BD<br>
00 00 24 5F 00 00 00 08 01 60 0E 02 01 9A FF B3<br>
0F 08 CF 00 FF FE 00 00 

## Header and Messenger Report

| Categories | Begin Options Header | Options Byte | Mobile ID Length | Mobile ID | Mobile Id Type Length | Mobile Id Type | End Options Header / Begin Message Header | Service Type | Message Type | Sequence Number | End Message Header/Begin Event Report |
|---|---|---|---|---|---|---|---|---|---|---|---|
|Tuple Length| | 2 | 2 | 10 | 2 | 2 | | 2 | 2 | 4 | |
| Hex | |83 | 05 | 1375031269 | 01 | 01| | 01 | 02 | 0004 | | 
| Binary | | 10000011 | 00000101 | |00000001 | 00000001 | | 00000001 | 00000010 | 00000100 | | 
| DEC | | 131 | 5 | 1375031269 | 1 | 1 | | 1 | 2 | 4 | | 

## Event Report 

| Categories | Update Time | Time of Fix | Latitude | Longitude | Altitude | Speed (cm/s) | Heading | Satellites | Fix Status | Carrier | RSSI | Comm State | HDOP | Inputs | Unit Status | Event Index | Event Code | Accumulators | Spare | 
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Tuple | 8 | 8 | 8 | 8 | 8 | 8 | 4 | 2 | 2 | 2 | 4 | 4 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 
| Hex | 609D584D | 609D584C | 169DDAE4 | CBE70DBD | 000024F5 | 00000008 | 0160 | 0E | 02 | 019A | FFB3 | 0F | 08 | CF | 00 | FF | FE | 00 | 00 |
| Bin | ||||| 1000 | 10110000 | 1110 | 10 | 110011010 | 1111111110110011 | 1111 | 1000 | 11001111 | 0 | 11111111 | 11111110 | 0 | 0 |
| Dec | 1620924493 | 1620924492 | 379443940 | 3420917181 | 9461 | 8 | 352 | 14 | 2 | 410 | -77 | 15 | 8 | 207 | 0 | 255 | 254 | 0 | 0 | 

## Mini Event Report

| Categories | Update Time | Latitude | Longitude | Heading | Speed (km/h) | Fixed Status | Comm State | Inputs | Event Code | Accums | 
|---|---|---|---|---|---|---|---|---|---|---|
| Tuples| 8 | 8 | 8  | 4 | 2 | 2 | 2 | 2 | 2 | 2 |  
| Hex | 609D7DAC | 169DD993 | CBE70FD1 | 0026 | 01 | 0D | 0F | 8F | 02 | 00 | 
| Bin | | | | 100110 | 0001 | 1101 | 1111 |  10001111 | 0010 | 0000 |
| Dec | 1620934060 | 379443603 | 3420917713 | 38 | 1 | 13 | 15 | 143 | 2 | 0 |  