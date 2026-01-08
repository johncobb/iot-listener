## Redsky Setup

[Overview](#overview)<br>
[Setup](#setup)<br>
[Testing](#testing)<br>


## Overview

Documentation for setting up Project Red Sky, aka the Calamp listener. You should be able to clone this project onto your OS and begin testing the Calamp Listener package. At the end of the setup, there is a testing section you can use for successful verification. 

<br>

## Setup

- Clone the project into your desired location.
- Run the setup launcher using `. /bin/setup`. The setup script will detect your operating system and pull down the required packages.

<kbd><br><img src="img/01setup.png"><br></kbd>

- Start the project up with the command `. bin/launcher.sh`. You should get a confirmation message back on your end. 

<kbd><br><img src="img/02launcher.png"><br></kbd>


- Either start a screen session or open another terminal and check the logs with the command `tail -f /tmp/calamp.log`

<kbd><br><img src="img/03checkinglogs.png"><br></kbd>

<br>

## Testing

You can now test the client by running the command `./bin/calamp_test_client`. You should get a message back saying 366 packets have been sent. 

<kbd><br><img src="img/04calamptest.png"><br></kbd>

- Check the `calamp.log` and see your result. 

<kbd><br><img src="img/05testclientresults.png"><br></kbd>

## Configure `core_config.py`

