#!/bin/bash


# Redis Server
export REDIS_HOST="localhost"
export REDIS_PORT=6379
export REDIS_CHANNEL="redsky:calamp:01:queue"       # read from this queue
export REDIS_CHANNEL_PUB="redsky:calamp:01:proc" # write to this queue
# export REDIS_PUB_CHANNEL_DB="redsky:calamp:01:db"   # write to this queue

# CalAmp Adapters
export PROC_ADAPTER_ENABLE=1
export PROC_ADAPTER_FORWARDING_ENABLE=1
# export BB_HOST="redsky.engenx.com"
export BB_HOST="0.0.0.0"
export BB_PORT=1337
export BB_LOGINFO=0

if [ -n "$ZSH_VERSION" ]; then
  echo "zsh: ${ZSH_VERSION}"
  PWD="$(cd "$(dirname "${0}")" && pwd)/.."
elif [ -n "$BASH_VERSION" ]; then
  echo "bash: ${BASH_VERSION}"
  PWD="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
fi

PYTHONPATH=$PWD $PWD/env/bin/python src/proc.py --proc default
