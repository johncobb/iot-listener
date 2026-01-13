#!/bin/bash
#
#
# sudo find / -name dump.rdb



# if [ -n "$ZSH_VERSION" ]; then
#   echo "zsh: ${ZSH_VERSION}"
#   PWD="$(cd "$(dirname "${0}")" && pwd)/.."
# elif [ -n "$BASH_VERSION" ]; then
#   echo "bash: ${BASH_VERSION}"
#   PWD="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
# fi

HOME=eval echo ~/
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  echo "Linux detected."
    if [[ "$OSTYPE" == "linux-gnueabi"* ]]; then
      echo "Raspberry Pi detected."
    else
      echo "Linux other."
    fi
    # MODULE_PATH="/home/h4ck3d/RedisTimeSeries/bin/linux-x64-release/redistimeseries.so"
    MODULE_PATH="$HOME/RedisTimeSeries/bin/linux-x64-release/redistimeseries.so"
elif [[ "$OSTYPE" == "darwin"* ]]; then
  echo "MacOS detected."
    if [[ $(uname -m) == 'arm64' ]]; then
        echo M1
        MODULE_PATH="RedisTimeSeries/bin/macos-arm64v8-release/redistimeseries.so"
    fi
fi


# $PWD/env/bin/python src/service_entry.py

# redis-server --loadmodule $MODULE_PATH
redis-server
