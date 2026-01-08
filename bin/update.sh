#!/bin/bash


if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  echo "Linux detected."
elif [[ "$OSTYPE" == "darwin"* ]]; then
  echo "MacOS detected."
fi


# install virtualenv
pip3 install virtualenv
virtualenv -p python3 env

# activate environment
source "env/bin/activate"
# install dependencies
pip3 install -r requirements.txt
# deactivate environment
deactivate

