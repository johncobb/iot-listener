# Making a PEG Script Example Project
## Table of Contents
[[_TOC_]]
## Overview
This sample exercise designed to walk through the process of building a PEG script from scratch given a list of parameters form a client. 

## Information

### Events (Pram 512)
Events are

### Parameters
Parameters set specific values on the LMU. For example the Inbound IP address/ port, timers, speed thresholds, and accumulator thresholds. There many other 

### Triggers

### Modifiers

### Conditions

### Accumulators

[Accumulators types](https://puls.calamp.com/wiki/PEG_Programming_Guide#Accumulator_Types)

## Getting Started

### Prerequisites

### Sample Project Scope
Your client Marko Ramius wants to be able to track trucks full of nuclear explosives traveling across Russia. He is very clear that the explosives must reach their designation as fast as possible.

Marko wants to be able to know: 
  
  - The exact location of each truck
  - When each truck is in idle
  - Any time the trucks speed exceeds 70 mph (112 kmh)

### PEG Planning 

Events

- Ignition On - Event 0
- Ignition Off - Event 1
- Timer 2 minutes - Event 2
- Speed Above 70 mph - Event 3
- Speed Below 70 mph -Event 4

Accumulators

- Acc 0 - Vehicle Stop Time
- Acc 1 - Idle Time
- Acc 2 - In Motion Time
  
### Using the LMU Manager

- ``File`` --> ``New Unit..`` --> Enter a name --> Enter 0.0.0.0 as the ``IP Address`` --> Select ``32-Bit`` For the LMU 3035 or select ``8-bit`` for the LMU 1230 --> ``OK``

![img here 1](/img/Capture1.1.PNG)
- The middle pane ``PEG Related Configuration`` is for setting Accumulators, S-Registers, and Speeding Thresholds

![img here 2](img/Capture2.PNG)

- The right pane is for setting events up

![img here 3](img/Capture3.PNG)

- Double tapping an event index will bring up an Event Configuration window to set the ``Trigger``, ``Trigger Modifier``, `Condition 1 and 2`, and ``Action and Action Modifier`` Along with a PEG Comment explaining each line

![img here 7](img/Capture7.PNG)

- The bottom pane is for setting parameters a.k.a settings
important parameters are inbound server settings(Pram 768),(Pram 769), and (Pram 2319)
![img here 4](img/Capture4.PNG)


- Setting Speed Thresholds

![img here 6 ](img/Capture6.PNG)

### Setting Event 0

- Select (Double-click) Index `512.0`

![img 8](img/Capture8.PNG)

### Explaining things in the example script s4.csv 32-bit PEG Script



![img](img/Capture9.PNG)

```
Event 0
AT$AP
```
![img](img/Capture10.PNG)
```
Event 1

```
![img](img/Capture11.PNG)
```
Event 2

```
![img](img/Capture12.PNG)
```
Event 3

```
![img](img/Capture13.PNG)
```
Event 4

```
![img](img/Capture14.PNG)
```
Event 5 

```
![img](img/Capture15.PNG)
```
Event 6

```
![img](img/Capture16.PNG)
```
Event 7

```
![img](img/Capture17.PNG)
```
Event 8

```
![img](img/Capture18.PNG)
```
Event 9

```
![img](img/Capture19.PNG)
```
Event 10

```
![img](img/Capture20.PNG)
```
Event 11

```
![img](img/Capture21.PNG)
```
Event 12

```
![img](img/Capture22.PNG)
```
Event 13

```
![img](img/Capture23.PNG)
```
Event 14

```
![img](img/Capture24.PNG)
```
Event 15

```
![img](img/Capture25.PNG)
```
Event 16

```
![img](img/Capture26.PNG)
```
Event 17

```
![img](img/Capture27.PNG)
```
Event 18

```
![img](img/Capture28.PNG)
```
Event 19

```
![img](img/Capture29.PNG)

```
Event 100

```
![img](img/Capture30.PNG)

```
Event 101

```
![img](img/Capture31.PNG)
```
Event 102

```
![img](img/Capture32.PNG)
```
Event 103

```
![img](img/Capture33.PNG)
```
Event 104

```
![img](img/Capture34.PNG)
```
Event 105

```
![img](img/Capture35.PNG)

Setting Moving Speed Thresholds and Speed Thresholds

![img](img/Capture36.PNG)

Set Inbound Server Parameters

![img here 5](img/Capture5.PNG)

Set S-Registers Parameters

Setting the PEG Script ID and the Configuration Version

![img](img/Capture37.1.PNG)

![img](img/Capture38.PNG)


