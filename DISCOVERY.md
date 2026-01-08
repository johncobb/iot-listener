# Project Redsky
Project currently designed to target python 3.

### Requirements
- ``virtualenv``
- pip
- Raspberry Pi set up on rack

#### Getting started

## Getting started on Linux box or PI
Set python ``virtualenv`` and install dependencies. (-p is the path for python3)

```
$ virtualenv -p python3 env
$ pip install -r requirements.txt
```
NOTE: When running pip install.. on a linux system a few packages might need to be installed. ``$ sudo apt-get install libffi-dev libpq-dev python-dev``
```
$ source env/bin/activate
$ ./bin/calamp
```
### Configure ``core_config.py``
make sure the development ip address is 0.0.0.0 or the device ip address.

set the inbound ip address on the CalAmp device using the PEG script or AT Commands below

Note: Don't forget to remove the "<>" brackets on the following commands:
```
AT$APP PARAM 768,0,<IP Address>
AT$APP PARAM 769,0,<Port>
AT$APP PARAM 2319,0,<IP Address>
AT$APP PARAM 2319,1,<IP Address>
```
### Start Serivce
```
$ . env/bin/activate
$ ./bin/calamp
```

#### CalAmp service log
```
$ tail -f /tmp/calamp.log 
```

#### JSON forwarded net cat and to EnginX blackbird server
```
$ nc -lvu 127.0.0.1 1338
```

#### Troubleshooting steps
Sometimes the CalAmp device refuses to connect to PULS. Use the AT Command below to force the device to check in. 
```
AT$APP PEG ACTION 49 129
```
Or a SMS command
```
!R3,49,129
```

Sometimes while configuring the UDP server issues can occur while exposing the raspberry pi to the outside world.
1. make sure that the service IP Address in ``core_config.py`` labeled PRODUCTION_IP is ``0.0.0.0`` or the devices local IP. NOT localhost or ``127.0.0.1``.
2. Is the router is port forwarding 20500 to the device ip?
3. Is the service running?
4. Is the servers public ip address configured on the CalAmp device inbound ip and is the port 20500?
5. Use the ``calamp_test_client.py`` from the server, local device, and external device to check if the service allows connections.
6. Is the modem allowing IP Passthrough?
7. Try using ``traceroute <IP Address>`` to make sure the external computer hits the raspberry pi.

#### Links

- https://puls.calamp.com/devicemgr/

