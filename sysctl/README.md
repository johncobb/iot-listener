# Calamp Service

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prereq)
- [Service Install/Management](#install)
- [Logs](#logs)
- [Database](#database)

<div id='overview'>

## Overview
Running Calamp Services.

<div id='prereq'>

## Prerequisites
Setup and install prerequisites.
```console
. bin/setup.sh
```

<div id='install'>

## Service Install/Management
Install Calamp Service by issuing the following:
```console
. sysctl/install.sh
```

Reference the commands below to manage the service.
```console
. sysctl/reload.sh
. sysctl/start.sh
. sysctl/status.sh
. sysctl/stop.sh
. sysctl/reload.sh
. sysctl/remove.sh
```


<div id='logs'>

## Monitoring Log Output
Monitor the service output with the commands below.
```console
tail -f /tmp/calamp
```
Monitor logs for a specific device.
```console
tail -f /tmp/calamp | grep "6000007950"
```

<div id='database'>

## Install Database
Create the R3DSKY database.
```console
sudo mysql -u root -p < schema/sql/db_gen.sql
sudo mysql -u root -p < schema/sql/db_gen_schema.sql
sudo mysql -u root -p < schema/sql/db_gen_users.sql
```
