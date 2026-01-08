#!/bin/bash

sudo systemctl stop calamp.service
sudo systemctl disable calamp.service

sudo rm /etc/systemd/system/calamp.service

sudo systemctl daemon-reload
sudo systemctl reset-failed
