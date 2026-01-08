#!/bin/bash

export PROC_DB_ENABLE=1
export MYSQL_HOST="localhost"
export MYSQL_PORT=3306
export MYSQL_USER="app_user"
export MYSQL_PASSWORD="Pencil1!"
export MYSQL_DATABASE="RedSkyApp"

# Redis Server
export REDIS_HOST="localhost"
export REDIS_PORT=6379
# export REDIS_CHANNEL="redsky:calamp:01:queue" # read from this queue
export REDIS_CHANNEL_PUB="redsky:calamp:01:queue" # write to this queue

# UDPServer listener
export HOST="0.0.0.0"
export PORT=20505

export COPY_TO_PRODUCTION=0
export SEND_ACK=1
export REPORT_TIMEOUT_ENABLE=1
export ACKBACK_ENABLE=1
export CLIENT_DWELL_TIME=5

# logger
export LOG_FILE="/tmp/calamp.log"
export LOG_FORMAT="%(asctime)s %(levelname)s: %(message)s"
export LOG_LEVEL="INFO"
export LOG_MAXBYTES=(1024*1024*5)
export LOG_BACKUPS=5
export LOG_RAW=1
export LOG_TRIP_DETAILS=1

# Toolchain listener
export TOOCHAIN_ENABLE=1
export TOOLCHAIN_LOG_FILE="/tmp/toolchain.log"
export TOOLCHAIN_PORT=20505

export PL_HOST="0.0.0.0"
export PL_PORT=20510

# CalAmp Adapters
export PROC_ADAPTER_ENABLE=0
# export BB_HOST="redsky.engenx.com"
# export BB_PORT=1982
export BB_HOST="0.0.0.0"
export BB_PORT=1337
export BB_LOGINFO=0

# Landmark Processor
export LANDMARK_ENABLE=1

# Redis Forwarder
export PROC_FORWARDING_ENABLE=1

if [ -n "$ZSH_VERSION" ]; then
  echo "zsh: ${ZSH_VERSION}"
  PWD="$(cd "$(dirname "${0}")" && pwd)/.."
elif [ -n "$BASH_VERSION" ]; then
  echo "bash: ${BASH_VERSION}"
  PWD="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
fi

PYTHONPATH=$PWD $PWD/env/bin/python src/service_entry.py
