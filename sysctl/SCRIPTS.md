
# Managing via systemd service manager.

Linux provides systemctl to automate the tasks of starting and stopping systemd services. Using systemctl allows us to develop and maintain a system service running in Linux. The scripts listed below automate some of the repetitive tasks of managing a service

## Installation
Loads calamp.service descriptor into systemctl.
```console
$ . sysctl/install.sh
```

## Starting
```console
$ . sysctl/start.sh
```

## Stopping
```console
$ . sysctl/stop.sh
```

## Status
```console
$ . sysctl/status.sh
```
## Remove
```console
$ . sysctl/remove.sh
```
