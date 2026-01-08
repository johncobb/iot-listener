#!/bin/bash

export HOST="0.0.0.0"
export TOOLCHAIN_PORT=20505
export TOOCHAIN_ENABLE=1
export TOOLCHAIN_LOG_FILE="/tmp/toolchain.log"

# Redis Server
export REDIS_HOST="localhost"
export REDIS_PORT=6379
export REDIS_CHANNEL="redsky:calamp:01:queue"       # read from this queue
# export REDIS_CHANNEL_PUB="redsky:calamp:01:proc" # write to this queue


if [ -n "$ZSH_VERSION" ]; then
  echo "zsh: ${ZSH_VERSION}"
  PWD="$(cd "$(dirname "${0}")" && pwd)/.."
elif [ -n "$BASH_VERSION" ]; then
  echo "bash: ${BASH_VERSION}"
  PWD="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
fi

PYTHONPATH=$PWD $PWD/env/bin/python src/proc.py --proc toolchain
