#!/bin/bash

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  echo "Linux detected."
  apt update
  apt upgrade
  apt install python3-pip3
  apt install python3-virtualenv
    if [[ "$OSTYPE" == "linux-gnueabi"* ]]; then
      echo "Raspberry Pi detected."
      apt install mariadb-server
    else
      apt install mysql-client-core-8.0
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
  echo "MacOS detected."
fi

# install virtualenv
pip3 install virtualenv
python3 -m virtualenv env

# activate environment
source "env/bin/activate"
# install dependencies
pip3 install -r requirements.txt
# deactivate environment
deactivate