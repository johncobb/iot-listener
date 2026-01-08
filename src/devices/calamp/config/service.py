import logging

CALAMP_LOG_FILE                 = "/tmp/calamp.log"
CALAMP_ROTATING_LOG_FILE        = "/tmp/calamp"
CALAMP_LOG_FORMAT               = "%(asctime)s %(levelname)s: %(message)s"
CALAMP_LOG_LEVEL                = logging.DEBUG
CALAMP_LOG_RAW                  = True

CALAMP_COPY_TO_PRODUCTION       = False
CALAMP_SEND_ACK                 = True
CALAMP_WORKERS                  = 1

CALAMP_PL_HOST                  = "0.0.0.0"
CALAMP_PL_PORT                  = 20510