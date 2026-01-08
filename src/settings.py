import os
import logging
from enum import Enum

# from db import DatabaseProviders

THREAD_POLLING = float(os.getenv('THREAD_POLLING', '0.001'))

# ======================================================================================================================
# UDP SERVER
# ======================================================================================================================
class ServiceType(Enum):
    UDP = 0
    TCP = 1

class ServiceProviders(Enum):
    NONE        = 0
    CALAMP      = 1

SERVICE_PROVIDER = ServiceProviders.CALAMP
SERVICE_TYPE = ServiceType.UDP

HOST                    = os.getenv('HOST', '0.0.0.0') # service listener
PORT                    = int(os.getenv('PORT', 20500))

COPY_TO_PRODUCTION      = True if (int(os.getenv('COPY_TO_PRODUCTION', 0)) == 1) else False

# ======================================================================================================================
# LOGGING
# ======================================================================================================================
""" README
WARNING: DO NOT SET THE LOG LEVEL TO DEBUG IN A PRODUCTION ENVIRONMENT!
The vigil service forwards the logs to a open unsecure webpage.
Debug logs contain sensitive information which pertains to the server and its clients.
"""
logLevel = {'CRITICAL':logging.CRITICAL, 'ERROR':logging.ERROR, 'WARNING':logging.WARNING, 'INFO':logging.INFO, 'DEBUG':logging.DEBUG}

LOG_LEVEL = logLevel[(os.getenv('LOG_LEVEL', "INFO"))]

"""TODO: Add verbosity to log.debug statements. Create more log levels. Issue #24
"""
class DebugVerbosity(Enum):
    HIGH    = 0
    MEDIUM  = 1
    LOW     = 2

DEBUG_VERBOSITY = os.getenv("DEBUG_VERBOSITY", "LOW")

LOG_FILE                = os.getenv("LOG_FILE", "/tmp/calamp.log")
LOG_FORMAT              = os.getenv("LOG_FORMAT")
LOG_MAXBYTES            = int(os.getenv("LOG_MAXBYTES", 1024*1024*5))
LOG_BACKUPS             = int(os.getenv("LOG_BACKUPS", 5))
LOG_RAW                 = True if (int(os.getenv('LOG_RAW', 1)) == 1) else False


PL_HOST                 = os.getenv('PL_HOST', '0.0.0.0')
PL_PORT                 = int(os.getenv('PL_PORT', 20510))

# ======================================================================================================================
# CalAmp UDP SERVER
# ======================================================================================================================
SEND_ACK                = True if (int(os.getenv('SEND_ACK', 0)) == 1) else False

# ======================================================================================================================
# Report
# ======================================================================================================================
CLIENT_DWELL_TIME = int(os.getenv('CLIENT_DWELL_TIME', '43200'))
REPORT_TIMEOUT = int(os.getenv('REPORT_TIMEOUT', '30'))
ACK_BACK_TIMEOUT = int(os.getenv('ACK_BACK_TIMEOUT', '10'))
ACKBACK_ENABLE = True if (int(os.getenv('ACKBACK_ENABLE', 0)) == 1) else False
REPORT_TIMEOUT_ENABLE = True if (int(os.getenv('REPORT_TIMEOUT_ENABLE', 1)) == 1) else False
LOG_TRIP_DETAILS = True if (int(os.getenv('LOG_TRIP_DETAILS', 0)) == 1) else False

# ======================================================================================================================
# TERMINAL SERVER (CALAMP)
# ======================================================================================================================
TOOCHAIN_ENABLE = True if (int(os.getenv('TOOLCHAIN_ENABLE', 1)) == 1) else False
TOOLCHAIN_PORT           = int(os.getenv('TOOLCHAIN_PORT', 20505))
TOOLCHAIN_LOG_FILE = os.getenv('TOOLCHAIN_LOG_FILE', "/tmp/toolchain.log")

# ======================================================================================================================
# DATABASE
# ======================================================================================================================
class DatabaseProviders(Enum):
    MySql = 0
    MySqlite = 1

PROC_DB_ENABLE                  = True if (int(os.getenv('PROC_DB_ENABLE', 0)) == 1) else False

# DB_PROVIDER                       = None
# DB_PROVIDER                       = DatabaseProviders.MySqlite # local/dev environments only
DB_PROVIDER                     = DatabaseProviders.MySql # dev/stage/prod environments

if (DB_PROVIDER == DatabaseProviders.MySql):
    DB_NAME                         = os.getenv('MYSQL_DATABASE')
    DB_HOST                         = os.getenv('MYSQL_HOST')
    DB_PORT                         = int(os.getenv('MYSQL_PORT', 0))
    DB_USER                         = os.getenv('MYSQL_USER')
    DB_PASS                         = os.getenv('MYSQL_PASSWORD')
elif (DB_PROVIDER == DatabaseProviders.MySqlite):
    DB_NAME                         = os.getenv('MYSQLITE_DATABASE')
    DB_HOST                         = os.getenv('MYSQLITE_HOST')
    DB_PORT                         = int(os.getenv('MYSQLITE_PORT', 0))
    DB_USER                         = os.getenv('MYSQLITE_USER')
    DB_PASS                         = os.getenv('MYSQLITE_PASSWORD')

# ======================================================================================================================
# REDIS
# ======================================================================================================================
REDIS_HOST                      = os.getenv('REDIS_HOST')
REDIS_PORT                      = int(os.getenv('REDIS_PORT', 0))
REDIS_DB                        = os.getenv('REDIS_DB')
REDIS_CHANNEL                   = os.getenv('REDIS_CHANNEL')
REDIS_CHANNEL_PUB                   = os.getenv('REDIS_CHANNEL_PUB')

# ======================================================================================================================
# LANDMARKS
# ======================================================================================================================
LANDMARK_ENABLE = True if (int(os.getenv('LANDMARK_ENABLE', 0)) == 1) else False
PROXIMITY_PRECISION = 2.5    # 5 meters is the average length of a vehicle

# ======================================================================================================================
# BLACKBIRD MESSAGE FORWARDER
# ======================================================================================================================
PROC_ADAPTER_ENABLE     = True if (int(os.getenv('PROC_ADAPTER_ENABLE', 0)) == 1) else False
BB_HOST                 = os.getenv('BB_HOST', 'localhost')
BB_PORT                 = int(os.getenv('BB_PORT', 0))
BB_LOGINFO              = True if (int(os.getenv('BB_LOGINFO', 0)) == 1) else False

# ======================================================================================================================
# PROCESSOR FORWARDING
# ======================================================================================================================
PROC_FORWARDING_ENABLE  = True if (int(os.getenv('PROC_FORWARDING_ENABLE', 0)) == 1) else False
REDIS_HOST              = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT              = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASS              = os.getenv('REDIS_PASS')
PUBLISH_SERVER_PREFIX   = os.getenv('PUBLISH_SERVER_PREFIX', 'redsky')

# ======================================================================================================================
# FORWARDING ENDPOINTS (Send copies of messages to these endpoints.
# ======================================================================================================================
# CALAMP_FORWARDING_ENDPOINTS = [{"host": "134.209.38.218", "port": 20500}]
# CALAMP_FORWARDING_ENDPOINTS = []

# ======================================================================================================================
# NINO PACKET FORWARDER
# ======================================================================================================================

REMOTE_HOST = "127.0.0.1"
REMOTE_PORT = 1337

NINO_HOST        = "0.0.0.0"
NINO_PORT        = 20510
# NINO_REMOTE_HOST = "72.167.39.55"
NINO_REMOTE_HOST = "localhost"
NINO_REMOTE_PORT = 1720

NINO_LOG_FILE   = "/tmp/forward.log"
NINO_LOG_FORMAT = "%(asctime)s %(levelname)s: %(message)s"
NINO_LOG_LEVEL  = logging.DEBUG
NINO_LOG_RAW    = False

NINO_WORKERS = 1
