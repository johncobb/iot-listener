#!/bin/bash

if [ -n "$ZSH_VERSION" ]; then
  echo "zsh: ${ZSH_VERSION}"
  PWD="$(cd "$(dirname "${0}")" && pwd)/.."
elif [ -n "$BASH_VERSION" ]; then
  echo "bash: ${BASH_VERSION}"
  PWD="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
fi

PYTHONPATH=$PWD $PWD/env/bin/python src/db/logic/__init__.py