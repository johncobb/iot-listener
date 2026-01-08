from enum import Enum

# CURRENT EVENT CODES
class CalampEvents(Enum):
    IGNITION_ON = 0
    IGNITION_OFF = 1
    TIME_DISTANCE = 2
    OVERSPEED = 3
    OTA_DOWNLOAD = 4
    OTA_COMPLETE = 5
    IDLE = 6
    PARKING_HEARTBEAT = 7
    CALAMP_BATT_LOW = 8
    VBATT_LOW = 9
    IDLE_END = 10
    BATT_PWR = 11
    SRC_PWR = 12
    POWER_UP= 13
    WAKE_UP = 14
    MOVING_POST_IG = 15
    TEST_PING = 16
    DEVICE_UNPLUGGED = 17
    DEVICE_PLUGGED_IN = 18
    OVERSPEED_END = 19
    RESERVED_20 = 20
    RESERVED_21 = 21
    RESERVED_22 = 22
    RESERVED_23 = 23
    RESERVED_24 = 24

# ACCUMULATORS
class CalampAccumulatorsDefs(Enum):
    IDLE_TIME = 0
    ENGINE_HOURS = 1

# LEGACY EVENT CODES
class CalampLegacyEvents(Enum):
    JOB_CLOCK_PUNCH      = 1 # legacy
    PARKING_HEARTBEAT    = 9
    DAILY_HEARTBEAT      = 10
    IGNITION_OFF         = 12
    IGNITION_ON          = 13
    TIME_DISTANCE        = 14
    SPEED_WARNING        = 16 # Overspeed @ 81 mph 
    EXTERNAL_POWER_LOW   = 19
    TOW_WARNING          = 28
    GEOFENCE_ENTER       = 32
    GEOFENCE_EXIT        = 33
    POWER_ON             = 53
    EXTENDED_STOP        = 57
    MOVING_EXTENDED_STOP = 60