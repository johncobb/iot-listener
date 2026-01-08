# Calamp Application Architecture

## Table of Contents
- [Overview](#overview)
- [Getting Started](#gettingstarted)
- [Usage](#usage)
- [Directory Structure](#structure)
- [Entry Point](#entry)

<div id='overview'>

## Overview
The Calamp Listener is a multi-threaded protocol invariant listener. The listener has an abstract model for
receiving reports from a socket. The lister fallows a basic model of the fallowing of a server and a client manager.
There are additional services such as the DataBase Manager and ToolChain Manager that have callback functions that are given to the client manager.

<div id ='gettingstarted'>

## Getting Started

### Requirements
- Python3
- MySql or MySqlite

### Local Setup
#### Service
To begin clone down the repository and run the service setup.
```
$ git clone git@gitlab.com:cpht/redsky/services/calamp-listener.git
$ cd calamp-listener
$ ./bin/setup
```
To use the service without a database change the flag `PROC_DB_ENABLE` to 0. The service will still function, but
expect errors.
#### Database
To use the service with the a database setting up the MySql Database is required. There are no additional configurations to make in the launcher (`launcher.sh`).

First create a local database user in your mysql service and give it rights to view your database.
```
$ mysql -u root
```
Add the database user below. Make sure the environmental variables in `launcher.sh` match the user and password below.
```
-- create the user
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'Pencil1!';
-- grant the privileges
GRANT ALL PRIVILEGES ON RedSkyApp.* TO 'app_user'@'localhost' IDENTIFIED BY 'Pencil1!';

FLUSH PRIVILEGES;
EXIT;
```
generate the sql database schema by running the database setup script.
```
$ ./bin/setup_db.sh
```
The database is now setup and installed. Install a table viewer software or cli tool to verify table entries.

<div id ='usage'>

## Usage

### Starting the Service
```
$ ./bin/launcher.sh
```

### Send Test Client Reports
Sending a simulated message from a device to the listener is simple. Checkout `/data/` and pick out a packet to send. For filling a database I recommend using the `reports5000.dat` file, loading will take about 30 seconds.

```
-- Local
$ ./bin/calamp_test_client data/<FILE>

-- Remote (Ex. Server is on a Raspberry Pi, EC2... etc.)
$ ./bin/calamp_test_client --host <HOST> data/<FILE>

-- Send a raw packet string
$ ./bin/calamp_test_client --raw <RAW_PACKET>

-- Ask for help
$ ./bin/calamp_test_client --help
```
<div id='structure'>

## Directory Structure

| Source | Description |
|--------|--------|
|project-root/| project folder |
|/bin | scripts for running/service and testing |
|/data| example message structures for testing |
|/docs| self explanatory |
|/src| all project source code |
|/src/db| database factory and drivers |
|/src/db/calamp| calamp specific database connectors |
|/src/db/calamp/schema | calamp specific database schema |
|/src/devices| device specific implementation |
|/src/devices/calamp| calamp implementation |
|/src/devices/calamp/api| device class abstraction |
|/src/devices/calamp/config| Device PEG2 event code implementation details |
|/src/devices/calamp/logic| client logic implementation details containing states and acknowledgments |
|/src/devices/calamp/messages| report message type implementation |
|/src/devices/calamp/messages/adapters| message adapter implementation |
|/src/devices/calamp/messages/schema| packet parsing field constants for each report type |
|/src/devices/calamp/tests| message parsing unit tests |
|/src/lib| shared library (utility classes) |
|/src/services| service definitions |
|/src/services/calamp| calamp service implementation |
|/src/tools| calamp service developer tools |
|/sysctl| service management scripts |

<div id='entry'>

## Entry Point
Application entry point (main). The application instantiates the service and server.
```console
src/service_entry.py
```

### Class Hierarchies
#### Declarative
  * UdpServer
    * CalampUdpServer
  * ClientManager
    * CalampClientManager
  * OutboxHandler
  * Toolchain
    * CalampToolchain
  * Client
    * CalampClient
  * DatabaseFactory
    * Database
      * CalampDatabase
  * DbManager
    * CalampDbManager
  * Report
    * CalampReport
  * Packet
    * CalampPacket

#### Implementation - Default
  * UdpServer
    * ClientManager
      * Toolchain
      * Client
        * OutboxHandler
        * Report
          * Packet
    * DbManager
      * Database

#### Implementation - Calamp
  * CalampUdpServer
    * CalampClientManager
      * CalampToolchain
      * CalampClient
        * OutboxHandler
        * CalampReport
          * CalampPacket
        * DeviceAcknowledgement
        * DeviceState
    * CalampDbManager
      * CalampDatabase