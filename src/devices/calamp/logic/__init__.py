from enum import Enum

class Timeouts(Enum):
    IGNITION_ON     = 5
    # IGNITION_ON     = 180
    IGNITION_OFF    = 180
    # IDLE            = 180
    IDLE            = 5
    VBATT_LOW       = 300

class DeviceStates(Enum):
	UNKNOWN 			= 0
	PARKED 				= 1
	IGNITION_ON			= 2
	IGNITION_OFF		= 3
	PENDING_IDLE 		= 4
	IDLE 				= 5
	MOVING 				= 6
	OVER_SPEED	 		= 7
	SLEEP 				= 8
	DISCONNECTED 		= 9
	RESERVED_10 		= 10
	RESERVED_11 		= 11
	RESERVED_12 		= 12
	RESERVED_13			= 13
	RESERVED_14			= 14
	RESERVED_15			= 15

class Notify(Enum):
	DEVICE_BATT_LOW	    = 0
	VEHICLE_BATT_LOW	= 1
	OTA_DOWNLOAD		= 2
	OTA_COMPLETE		= 3
	IDLE_END			= 4
	OK					= 5