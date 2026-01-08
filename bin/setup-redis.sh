#!/bin/bash

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  echo "Linux detected."
    if [[ "$OSTYPE" == "linux-gnueabi"* ]]; then
      echo "Raspberry Pi detected."
    else
      echo "Linux other."
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
  echo "MacOS detected."
fi

# https://redis.io/docs/latest/develop/data-types/timeseries/quickstart/
# Clone RedisTimeSeries
git clone --recursive https://github.com/RedisTimeSeries/RedisTimeSeries.git
# Build RedisTimeSeries
make build -C RedisTimeSeries/

