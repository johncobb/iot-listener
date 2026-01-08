#!/bin/bash
# ======================================================================================================================
# Copyright (c) 2013 Exzigo. All rights reserved.
#
# Author: Sean Kerr [sean@code-box.org]
# ======================================================================================================================

export DB_HOST="localhost"
export DB_PORT=3306
export DB_USER="app_user"
export DB_PASS="Pencil1"
# export DB_NAME="RedSkyApp"
export DB_NAME="redskyapp.db"
export REDSKY_HOST="0.0.0.0"
export REDSKY_PORT=8000

if [ -n "$ZSH_VERSION" ]; then
  echo "zsh: ${ZSH_VERSION}"
  PWD="$(cd "$(dirname "${0}")" && pwd)/.."
elif [ -n "$BASH_VERSION" ]; then
  echo "bash: ${BASH_VERSION}"
  PWD="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
fi

PYTHONPATH=$PWD $PWD/env/bin/python src/db/testing/db_test.py