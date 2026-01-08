from ctypes import sizeof
# from distutils import extension
from itertools import accumulate
import struct
from enum import Enum
from datetime import datetime

from lib import IoByte
from lib import MASK_BIT
from lib import MASK_NIBBLE
from lib import SHIFT_NIBBLE
from lib import ByteBuffer
from devices.calamp.messages.schema import MessageConfig as cf

FACTORKPH = 0.621371
FACTORCMS = 0.0223694
FACTORCM = 0.0328084

class MessageTypes(Enum):
	NULL = 0
	ACKNOWLEDGEMENT = 1
	EVENT_REPORT = 2
	ID_REPORT = 3
	USER = 4
	APPLICATION = 5
	PARAMETER = 6
	UNIT_REQUEST = 7
	LOCATE_REPORT = 8
	USER_ACCUMULATORS = 9
	MINI_EVENT_REPORT = 10
	MINI_USER = 11
	MINI_APPLICATION = 12
	DEVICE_VERSION = 13
	APPLICATION_ACCUMULATORS = 14

	@classmethod
	def is_supported(self, other):
		supported = [self.NULL, self.ACKNOWLEDGEMENT, self.EVENT_REPORT, self.ID_REPORT, self.UNIT_REQUEST, self.MINI_EVENT_REPORT]
		return any((i == other) for i in supported)

class AppMessageTypes(Enum):
    # Application Message (MessageTypes APPLICATION=5)
	IP_REQUEST = 10
	IP_REPORT = 11
	TIME_SYNC = 50
	SERVICES = 80
	SVR_MESSAGING = 81
	DOWNLOAD_ID_REPORT = 100
	DOWNLOAD_AUTHORIZATION = 101
	DOWNLOAD_REQUEST = 102
	DOWNLOAD_UPDATE = 103
	DOWNLOAD_COMPLETE = 104
	DOWNLOAD_HTTP_LMU_FW = 105
	DOWNLOAD_HTTP_FILE = 106
	OTA_DOWNLOAD = 107
	AT_COMMAND = 110
	VERSION_REPORT = 111
	GPS_STATUS_REPORT = 112
	MESSAGE_STATISTICS_REPORT = 113
	STATE_REPORT = 115
	GEO_ZONE_ACTION_MESSAGE = 116
	GEO_ZONE_UPDATE_MESSAGE = 117
	PROBE_ID_REPORT = 118
	CAPTURE_REPORT = 120
	MOTION_LOG_REPORT = 122
	COMPRESSED_MOTION_LOG_REPORT = 123
	VBUS_DATA_REPORT = 130
	VEHICLE_ID_REPORT = 131
	VBUS_DTC_REPORT = 132
	VBUS_VIN_DECODE_LOOKUP = 133
	SQUARELL_COMMAND_MESSAGE = 134
	SQUARELL_STATUS_MESSAGE = 135
	VBUS_REGISTER_DEVICE_MESSAGE = 136
	VBUS_FREEZE_FRAME = 137
	VBUS_DIAGNOSTICS_REPORT = 138
	VBUS_REMOTE_OBD = 140
	VBUS_GROUP_DATA_REPORT = 142
	VBUS_MANAGEMENT_OUTBOUND = 145
	VBUS_MANAGEMENT_INBOUND = 148

class ServiceTypes(Enum):
	"""
	Device to Server_______________________________service type________________Server to Device____________________
	Device not requesting Acknowledgement 		<- UNACKNOWLEDGED (0) 	    -> Non-Acknowledged Request
	Device requesting Acknowledgement 			<- ACKNOWLEDGED (1)   	    -> Acknowledge Request
	Device responding to an acknowledge message <- ACKNOWLEDGE_RESPONSE (2) -> Response to an Acknowledged Request
	"""
	UNACKNOWLEDGED 			= 0
	ACKNOWLEDGED 			= 1
	ACKNOWLEDGE_RESPONSE 	= 2

class AckTypes(Enum):
	# ACK Types
	ACK_SUCCESSFUL = 0
	NAK_NO_REASON = 1
	NAK_NOT_SUPPORTED_MESSAGE_TYPE = 2
	NAK_NOT_SUPPORTED_OPERATION = 3
	NAK_UNABLE_PASS_SERIAL = 4
	NAK_AUTH_FAIL = 5
	NAK_MOBILE_ID_LOOKUP_FAIL = 6
	NAK_NON_ZERO_SEQUENCE = 7
	NAK_MESSAGE_AUTH_FAIL = 8
	NAK_MESSAGE_FORMAT_FAIL = 9
	NAK_PARAM_UPDATE_FAIL = 10

class MobileIdType(Enum):
	OFF = 0
	ESN = 1
	IMEI_EID = 2
	IMSI = 3
	USER_DEFINED = 4
	PHONE_NUMBER = 5
	IP_ADDRESS = 6
	CMDA_MEID_IMEI = 7

class CalampScriptInfo():
	def __init__(self, script_version=0, config_version=0):
		self.script_version = script_version
		self.config_version = config_version

	def __str__(self):
		return "{}.{}".format(self.script_version, self.config_version)
	@property
	def ver(self):
		return (self.script_version, self.config_version)

class CalampAppVersion():
	def __init__(self, byte_0=0, byte_1=0, byte_2=0):
		self.byte_0 = byte_0
		self.byte_1 = byte_1
		self.byte_2 = byte_2

	def __str__(self):
		return "{}.{}.{}".format(self.byte_0, self.byte_1, self.byte_2)

	def __eq__(self, other):
		return (self.byte_0 == other.byte_0 and self.byte_1 == other.byte_1 and self.byte_2 == other.byte_2)

	def __ne__(self, other):
		return not self.__eq__(other)

	def __lt__(self, other):
		if (self.byte_0 < other.byte_0):
			return self.byte_0 < other.byte_0
		elif (self.byte_1 < other.byte_1):
			return self.byte_1 < other.byte_1
		elif (self.byte_2 < other.byte_2):
			return self.byte_2 < other.byte_2
		else:
			return False

	def __gt__(self, other):
		return not self.__lt__(other) and self.__ne__(other)

	@property
	def ver(self):
		return (self.byte_0, self.byte_1, self.byte_2)

class CalampCellInfo:
	def __init__(self):
		self.esn = None
		self.imei = None
		self.imsi = None
		self.min = None
		self.iccid = None

	def __dict__(self):
		return {
			'esn': self.esn,
			'imei': self.imei,
			'imsi': self.imsi,
			'min': self.min,
			'iccid': self.iccid
		}

class CalampLocation:
	def __init__(self):
		self.latitude = None
		self.longitude = None
		self.heading = None
		self.altitude = None
		self.speed = None

	def __dict__(self):
		return {
			'latitude': self.latitude,
			'longitude': self.longitude,
			'heading': self.heading,
			'altitude': self.altitude,
			'speed': self.speed
		}
	@property
	def latitude_radix(self):
		return self.latitude/(10**7)

	@property
	def longitude_radix(self):
		return self.longitude/(10**7)

	@property
	def altitude_cm(self):
		return self.altitude * FACTORCM
	@property
	def speed_mph(self):
		return self.speed * FACTORCMS
	@property
	def speed_kph(self):
		return self.speed * FACTORKPH

class CalampAccumulator():
	def __init__ (self, id, val):
		self._id = id
		self._val = val

	def to_json(self):
		return {"id": self.id, "val": self.val}

	@property
	def id(self):
		return self._id
	@property
	def val(self):
		return self._val

class CalampAccumulators():
	def __init__(self):
		self._idle = 0
		self._engine_hours = 0

		for id in range(0, 16):
			setattr(self, 'accumulator_{}'.format(id), CalampAccumulator(0, 0))

	def __call__(self, id):
		return getattr(self, 'accumulator_{}'.format(id))

	def __dict__(self):
		return {self.__call__(key).id:self.__call__(key).val for key in range(0, 16)}

	def set(self, accumulator):
		setattr(self, 'accumulator_{}'.format(accumulator.id), accumulator)

	@property
	def idle(self):
		self._idle = self.accumulator_0.val
		return self._idle
	@property
	def engine_hours(self):
		self._engine_hours = self.accumulator_1.val
		return self._engine_hours
	@property
	def odometer(self):
		self._odometer = self.accumulator_2.val
		return self._odometer

class CalampExtensionString():
	def __init__(self, tag, data):
		self._tag = tag.decode()
		self._data = data.decode()

	@property
	def tag(self):
		return self._tag
	@property
	def data(self):
		return self._data.split(',')


class CalampMessageHeader():
	def __init__(self, service_type=0, message_type=0, sequence_number=0):
		self.service_type = service_type
		self.message_type = message_type
		self.sequence_number = sequence_number

	def __bytes__(self):
		return struct.pack(">bbh", self.service_type, self.message_type, self.sequence_number)

	def parse(self, buffer):
		raise Exception("Sub-class must implement parse()")
	def log(self, server):
		raise Exception("Sub-class must implement log()")

MOBILE_ID_TYPE_ESN   = 1
class CalampOptionsHeader():
	def __init__(self, mobile_id="", mobile_id_type=0):

		self.mobile_id = mobile_id
		self.mobile_id_type = mobile_id_type

		self.options_byte = 0
		self.extension_byte = 0
		self.mobile_id_type_length = 0
		self.authentication_word_length = 0
		self.authentication_word = 0
		self.routing_length = 0
		self.routing = ""
		self.forwarding_length = 0
		self.forwarding_address = ""
		self.forwarding_port = 0
		self.forwarding_protocol = 0
		self.forwarding_operation = 0
		self.response_redirection_length = 0
		self.response_redirection_address = ""
		self.response_redirection_port = 0

		self.enable_extension_esn = 0
		self.enable_extension_vin = 0
		self.enable_extension_encryption = 0
		self.enable_extension_compression = 0
		self.enable_extension_routing = 0

		self.extension_esn_length = 0
		self.extension_esn = ""
		self.extension_vin_length = 0
		self.extension_vin = ""
		self.extension_encryption_length = 0
		self.extension_encryption = ""
		self.extension_compression_length = 0
		self.extension_compression = ""
		self.extension_routing_length = 0
		self.extension_routing = ""

	def __bytes__(self):
		_mobile_id = []
		[_mobile_id.append(x) for x in self.mobile_id]
		_mobile_id.reverse()

		_bytes = bytearray()

		""" pack options: (mobile_id, mobile_id_type) """
		_bytes.extend(struct.pack(">B", 1 << 0 | 1 << 1 | 1 << 7))

		""" pack options byte using iobyte """
		# _bytes.extend(self.__pack_options_byte())

		while _mobile_id:
			_bytes.extend(struct.pack(">B", int(_mobile_id.pop(), 16) << 4 | int(_mobile_id.pop(), 16)))

		_bytes.extend(struct.pack(">B", self.mobile_id_type))
		# print(_bytes)

		return bytes(_bytes)


	@property
	def opt(self):
		return self.options_byte
	@property
	def ext(self):
		return self.extension_byte

	def parse(self, buffer):
		raise Exception("Sub-class must implement parse()")
	def log(self, server):
		raise Exception("Sub-class must implement log()")

class CalampMessageBase:
	def __init__ (self, options_header, message_header):
		self.buffer = None
		self.options_header = options_header
		self.message_header = message_header
		self.headers_to_dict = lambda : {'options': options_header.__dict__(), 'message': message_header.__dict__()}
		self.update_time = None
		self.calamp_location = CalampLocation()
		self.inputs = {}
		self.event_code = None
		self.accumulator_count = None
		# self.accumulators = {}
		self.accumulators = CalampAccumulators()
		self.accums = None
		self.fix_byte = None
		self.comm_byte = None
		self.input_byte = None
		self.extension_strings = {}

	def set_buffer(self, buffer):
		self.buffer = buffer


	@property
	def mobile_id(self):
		return self.options_header.mobile_id
	@property
	def message_type(self):
		return self.message_header.message_type
	@property
	def service_type(self):
		return self.message_header.service_type
	@property
	def sequence_number(self):
		return self.message_header.sequence_number
	@property
	def loc(self):
		return self.calamp_location
	@property
	def gpio(self):
		return self.input_byte

	@property
	def satellites(self):
		raise Exception("Sub-class must implement satellites")

	@property
	def update_time_utc(self):
		return datetime.utcfromtimestamp(self.update_time)

	def parse(self, buffer):
		raise Exception("Sub-class must implement parse()")

	def log(self, server):
		raise Exception("Sub-class must implement log()")

	def parse_accumulators(self, buffer):
		""" TODO: need to confirm name spare_byte """
		spare_byte = buffer.read()

		# for i in range(0, self.accumulator_count):
		# 	self.accumulators[i] = CalampAccumulator(i, struct.unpack(">i", buffer.read(cf.ACCUMULATOR_LEN))[0])

		for i in range(0, self.accumulator_count):
			accumulator = CalampAccumulator(i, struct.unpack(">i", buffer.read(cf.ACCUMULATOR_LEN))[0])
			self.accumulators.set(accumulator)

	def parse_extension_strings(self, buffer):
		extension_strings = ''
		for i in range(buffer.index, buffer.bytes_remaining):
			extension_strings += str(struct.unpack(">i", buffer.read())[0])

		print(extension_strings)
		# extension_strings.decode()
		extension_strings.rstrip(b'\x00').split(b'\x00')
		extension_strings_length = sizeof(extension_strings)

		for i in range(0, extension_strings_length):
			self.extension_strings[i] = CalampExtensionString(extension_strings.split(b':', 1))


class OptionsByte(IoByte):

	def __init__(self, iobyte):
		IoByte.__init__(self, iobyte)

	def __dict__(self):
		return {
			'mobile_id_enable': self.enable_mobile_id,
			'mobile_id_type_enable': self.enable_mobile_id_type,
			'authentication_word_enable': self.enable_authentication_word,
			'routing_enable': self.enable_routing,
			'forwarding_enable': self.enable_forwarding,
			'response_redirection_enable': self.enable_response_redirection,
			'options_extension_enable': self.enable_options_extension,
			'reserved_always_on': self.always_on
		}

	def log(self, server):
		server.log.debug("options_byte: {}".format(hex(self.byte_val)))
		server.log.debug(" - mobile_id_enable: {}".format(self.enable_mobile_id))
		server.log.debug(" - mobile_id_type_enable: {}".format(self.enable_mobile_id_type))
		server.log.debug(" - authentication_word_enable: {}".format(self.enable_authentication_word))
		server.log.debug(" - routing_enable: {}".format(self.enable_routing))
		server.log.debug(" - forwarding_enable: {}".format(self.enable_forwarding))
		server.log.debug(" - response_redirection_enable: {}".format(self.enable_response_redirection))
		server.log.debug(" - options_extension_enable: {}".format(self.enable_options_extension))
		server.log.debug(" - always_on(reserved): {}".format(self.always_on))

	@property
	def enable_mobile_id(self):
		return self.bit_0
	@property
	def enable_mobile_id_type(self):
		return self.bit_1
	@property
	def enable_authentication_word(self):
		return self.bit_2
	@property
	def enable_routing(self):
		return self.bit_3
	@property
	def enable_forwarding(self):
		return self.bit_4
	@property
	def enable_response_redirection(self):
		return self.bit_5
	@property
	def enable_options_extension(self):
		return self.bit_6
	@property
	def always_on(self):
		return self.bit_7

class ExtensionsByte(IoByte):

	def __init__(self, iobyte):
		IoByte.__init__(self, iobyte)

	def log(self, server):
		server.log.debug("extension_byte: {}".format(hex(self.byte_val)))
		server.log.debug(" - extensions_byte: {}".format(hex(self.byte_val)))
		server.log.debug(" - enable_extension_esn: {}".format(self.enable_extension_esn))
		server.log.debug(" - enable_extension_vin: {}".format(self.enable_extension_vin))
		server.log.debug(" - enable_extension_encryption: {}".format(self.enable_extension_encryption))
		server.log.debug(" - enable_extension_compression: {}".format(self.enable_extension_compression))
		server.log.debug(" - enable_extension_routing: {}".format(self.enable_extension_routing))

	@property
	def enable_extension_esn(self):
		return self.bit_0
	@property
	def enable_extension_vin(self):
		return self.bit_1
	@property
	def enable_extension_encryption(self):
		return self.bit_2
	@property
	def enable_extension_compression(self):
		return self.bit_3
	@property
	def enable_extension_routing(self):
		return self.bit_4

class FixByte(IoByte):

	def __init__(self, iobyte):
		IoByte.__init__(self, iobyte)

	def __dict__(self):
		return {
			'predicted': self.predicted,
			'differentially_corrected': self.differentially_corrected,
			'last_known': self.last_known,
			'invalid': self.invalid,
			'fix2d': self.fix2d,
			'historic': self.historic,
			'invalid_time': self.invalid_time,
			'reserved_bit7': self.bit_7
		}

	def log(self, server):
		server.log.debug("fix_byte: {}".format(hex(self.byte_val)))
		server.log.debug(" - predicted: {}".format(self.predicted))
		server.log.debug(" - differentially_corrected: {}".format(self.differentially_corrected))
		server.log.debug(" - last_known: {}".format(self.last_known))
		server.log.debug(" - invalid: {}".format(self.invalid))
		server.log.debug(" - fix2d: {}".format(self.fix2d))
		server.log.debug(" - historic: {}".format(self.historic))
		server.log.debug(" - invalid_time: {}".format(self.invalid_time))
		server.log.debug(" - tbd_7 (reserved): {}".format(self.tbd_7))

	@property
	def predicted(self):
		return self.bit_0
	@property
	def differentially_corrected(self):
		return self.bit_1
	@property
	def last_known(self):
		return self.bit_2
	@property
	def invalid(self):
		return self.bit_3
	@property
	def fix2d(self):
		return self.bit_4
	@property
	def historic(self):
		return self.bit_5
	@property
	def invalid_time(self):
		return self.bit_6

class FixByteMini(IoByte):
	def __init__(self, iobyte):
		IoByte.__init__(self, iobyte)

	def __dict__(self):
		return {
			'satellites': self.satellites,
			'invalid_time': self.invalid_time,
			'invalid': self.invalid,
			'last_known': self.last_known,
			'historic': self.historic
		}

	def log(self, server):
		server.log.debug("fix_byte_mini: {}".format(hex(self.byte_val)))
		server.log.debug(" - satellites: {}".format(self.satellites))
		server.log.debug(" - invalid_time: {}".format(self.invalid_time))
		server.log.debug(" - invalid: {}".format(self.invalid))
		server.log.debug(" - last_known: {}".format(self.last_known))
		server.log.debug(" - historic: {}".format(self.historic))

	@property
	def satellites(self):
		return self.byte_val & MASK_NIBBLE
	@property
	def invalid_time(self):
		return self.bit_4
	@property
	def invalid(self):
		return self.bit_5
	@property
	def last_known(self):
		return self.bit_6
	@property
	def historic(self):
		return self.bit_7

class CommByte(IoByte):
	def __init__(self, iobyte):
		IoByte.__init__(self, iobyte)

	def __dict__(self):
		return {
			'available': self.available,
			'network_service': self.network_service,
			'data_service': self.data_service,
			'connected': self.connected,
			'voice_call_is_active': self.voice_call_is_active,
			'roaming': self.roaming,
			'network_3g': self.network_3g,
			'reserved_bit7': self.bit_7
		}

	def log(self, server):
		server.log.debug("comm_byte: {}".format(hex(self.byte_val)))
		server.log.debug(" - available: {}".format(self.available))
		server.log.debug(" - network_service: {}".format(self.network_service))
		server.log.debug(" - data_service: {}".format(self.data_service))
		server.log.debug(" - connected: {}".format(self.connected))
		server.log.debug(" - voice_call_is_active: {}".format(self.voice_call_is_active))
		server.log.debug(" - roaming: {}".format(self.roaming))
		server.log.debug(" - network_3g: {}".format(self.network_3g))
		server.log.debug(" - tbd_7 (reserved): {}".format(self.tbd_7))

	@property
	def available(self):
		return self.bit_0
	@property
	def network_service(self):
		return self.bit_1
	@property
	def data_service(self):
		return self.bit_2
	@property
	def connected(self):
		return self.bit_3
	@property
	def voice_call_is_active(self):
		return self.bit_4
	@property
	def roaming(self):
		return self.bit_5
	@property
	def network_3g(self):
		return self.bit_6

class CommByteMini(CommByte):
	def __init__(self, iobyte):
		CommByte.__init__(self, iobyte)

	def __dict__(self):
		return {
			'available': self.available,
			'network_service': self.network_service,
			'data_service': self.data_service,
			'connected': self.connected,
			'voice_call_is_active': self.voice_call_is_active,
			'roaming': self.roaming,
			'gps_antenna_status_ok': self.gps_antenna_status_ok,
			'gps_receiver_tracking': self.gps_receiver_tracking
		}

	def log(self, server):
		server.log.debug("comm_byte: {}".format(hex(self.byte_val)))
		server.log.debug(" - available: {}".format(self.available))
		server.log.debug(" - network_service: {}".format(self.network_service))
		server.log.debug(" - data_service: {}".format(self.data_service))
		server.log.debug(" - connected: {}".format(self.connected))
		server.log.debug(" - voice_call_is_active: {}".format(self.voice_call_is_active))
		server.log.debug(" - roaming: {}".format(self.roaming))
		server.log.debug(" - gps_antenna_status_ok: {}".format(self.gps_antenna_status_ok))
		server.log.debug(" - gps_receiver_tracking: {}".format(self.gps_receiver_tracking))

	@property
	def gps_antenna_status_ok(self):
		return self.bit_6
	@property
	def gps_receiver_tracking(self):
		return self.bit_7

class GpsByte(IoByte):
	def __init__(self, iobyte):
		IoByte.__init__(self, iobyte)

	def __dict__(self):
		return {
			'http_ota_update_status_ok': self.http_ota_update_status_ok,
			'gps_antenna_status_ok': self.gps_antenna_status_ok,
			'gps_receiver_test_ok': self.gps_receiver_test_ok,
			'gps_receiver_tracking': self.gps_receiver_tracking,
			'vbus_disabled': self.vbus_disabled
		}

	def log(self, server):
		server.log.debug("gps_byte: {}".format(hex(self.byte_val)))
		server.log.debug(" - http_ota_update_status_ok: {}".format(self.http_ota_update_status_ok))
		server.log.debug(" - gps_antenna_status_ok: {}".format(self.gps_antenna_status_ok))
		server.log.debug(" - gps_receiver_test_ok: {}".format(self.gps_receiver_test_ok))
		server.log.debug(" - gps_receiver_tracking: {}".format(self.gps_receiver_tracking))
		server.log.debug(" - vbus_disabled: {}".format(self.vbus_disabled))

	@property
	def http_ota_update_status_ok(self):
		return self.bit_0 == 0			# (http_ota_update_status_ok == (0 == OK) || (1 == Error) ) (Not set on LMU8)
	@property
	def gps_antenna_status_ok(self):
		return self.bit_1 == 0			# (gps_antenna_status_ok == (0 == OK) || (1 == Error) )
	@property
	def gps_receiver_test_ok(self):
		return self.bit_2 == 0			# (gps_receiver_test_ok == (0 == OK) || (1 == Error) ) (LMU32 Only)
	@property
	def gps_receiver_tracking(self):
		return self.bit_3 == 0  		# (gps_receiver_tracking == (0 == YES) || (1 == NO) )
	@property
	def vbus_disabled(self):  			# (vbus_disabled == (0 == YES) || (1 == NO) )
		return self.bit_4 == 0
