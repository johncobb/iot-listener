#!/bin/bash
# ======================================================================================================================
# Copyright (c) 2024 CP Handheld Technologies, LLC. All rights reserved.
#
# Author: John Cobb
# ======================================================================================================================


if [ -n "$ZSH_VERSION" ]; then
  echo "zsh: ${ZSH_VERSION}"
  PWD="$(cd "$(dirname "${0}")" && pwd)/.."
elif [ -n "$BASH_VERSION" ]; then
  echo "bash: ${BASH_VERSION}"
  PWD="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
fi

PYTHONPATH=$PWD $PWD/env/bin/python src/tools/calamp/calamp_test_multiclient.py $*
