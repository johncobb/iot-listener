import os
import redis
import binascii
import time
import datetime
import json
import traceback
import argparse

from services.calamp.procs.default import proc_main as proc_default
from services.calamp.procs.db import proc_main as proc_db
from services.calamp.procs.logic import proc_main as proc_logic
from services.calamp.procs.landmark import proc_main as proc_landmark
from services.calamp.procs.toolchain import proc_main as proc_toolchain

DESC = "Starts processor."
EPILOG ="For development use only."
DEFAULT_PROC = "redis"
MSG_PROC = "Processor name launch. (Default: {})".format(DEFAULT_PROC)
MSG_CORES = "Max number of CPU cores to run on. (Default: {})".format(DEFAULT_PROC)

parser = argparse.ArgumentParser(description=DESC, epilog=EPILOG)
parser.add_argument('--proc', type=str, default=DEFAULT_PROC, help=MSG_PROC)
# parser.add_argument('--cores', type=int, default=1, help=MSG_CORES)

args = parser.parse_args()

# ===============
# USAGE
# ===============
# . bin/launcher.sh
# . bin/proc_redis.sh
# . bin/calamp_test_client --host localhost --port 20500 data/id_report.dat




def main():

    if (args.proc == "default"):
        proc_default()
    if (args.proc == "db"):
        proc_db()
    if (args.proc == "logic"):
        proc_logic()
    if (args.proc == "landmark"):
        proc_landmark()
    if (args.proc == "toolchain"):
        proc_toolchain()

if __name__ == "__main__":
    main()
