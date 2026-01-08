from ctypes import sizeof
import struct
from enum import Enum
from enum import auto
from datetime import datetime

from abc import ABC
from abc import ABCMeta
from abc import abstractmethod
from typing import Protocol

from lib import IoByte
from lib import MASK_BIT
from lib import MASK_NIBBLE
from lib import SHIFT_NIBBLE
from lib import ByteBuffer

FACTORKPH = 0.621371
FACTORCMS = 0.0223694
FACTORCM = 0.0328084

class MessageTypes(Enum):
	NULL = auto()
	ACKNOWLEDGEMENT = auto()
	EVENT_REPORT = auto()

class MobileIdType(Enum):
	OFF = auto()
	ESN = auto()
	IMEI_EID = auto()
	IMSI = auto()
	USER_DEFINED = auto()
	PHONE_NUMBER = auto()
	IP_ADDRESS = auto()
	CMDA_MEID_IMEI = auto()



# class P_IotAppVersion(Protocol):

#     def foo(self):
#         ...
#     def ver(self):
#         ...

class IIotAppVersion(metaclass=ABCMeta):
    """ coap version abstract base class """

    @staticmethod       # works class.foo() class().foo()
    @abstractmethod     # must be implemented
    def foo(self):
        pass

    @property
    def ver(self):
        pass

class AppVersion(IIotAppVersion):
    """ instance class of IotAppVersion """

    def foo():
        print("foo")
    def ver():
        print("ver")

class DeviceFactory:
    """ Device Class Factory """

    @staticmethod
    def get_device(device):
        if device == "coap":
            return AppVersion()

def main():
    DeviceFactory().get_device("coap")

class IotAppVersion():
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

class IotCellInfo:
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

class IotLocation:
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

class IotLoactionFix(IoByte):

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

class IotMessageHeader():
	def __init__(self, message_type=0, sequence_number=0):
	# def __init__(self, service_type=0, message_type=0, sequence_number=0):
		# self.service_type = service_type
		self.message_type = message_type
		self.sequence_number = sequence_number

	def __bytes__(self):
		# return struct.pack(">bbh", self.service_type, self.message_type, self.sequence_number)
		return struct.pack(">bbh", 0, self.message_type, self.sequence_number)

	def parse(self, buffer):
		raise Exception("Sub-class must implement parse()")
	def log(self, server):
		raise Exception("Sub-class must implement log()")

class IotMessageBase:
	def __init__ (self, options_header, message_header):
		self.buffer = None
		self.options_header = options_header
		self.message_header = message_header
		self.headers_to_dict = lambda : {'options': options_header.__dict__(), 'message': message_header.__dict__()}
		self.update_time = None
		self.coap_location = IotLocation()
		self.inputs = {}
		self.event_code = None
		# self.accumulator_count = None
		# self.accumulators = {}
		# self.accumulators = CalampAccumulators()
		# self.accums = None
		self.fix_byte = None
		# self.comm_byte = None
		self.input_byte = None
		# self.extension_strings = {}

	def set_buffer(self, buffer):
		self.buffer = buffer


	@property
	def mobile_id(self):
		return self.options_header.mobile_id
	@property
	def message_type(self):
		return self.message_header.message_type
	# @property
	# def service_type(self):
	# 	return self.message_header.service_type
	@property
	def sequence_number(self):
		return self.message_header.sequence_number
	@property
	def loc(self):
		return self.coap_location
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

	# def parse_accumulators(self, buffer):
		""" TODO: need to confirm name spare_byte """
		# spare_byte = buffer.read()

		# for i in range(0, self.accumulator_count):
		# 	self.accumulators[i] = CalampAccumulator(i, struct.unpack(">i", buffer.read(cf.ACCUMULATOR_LEN))[0])

		# for i in range(0, self.accumulator_count):
		# 	accumulator = CalampAccumulator(i, struct.unpack(">i", buffer.read(cf.ACCUMULATOR_LEN))[0])
		# 	self.accumulators.set(accumulator)

	# def parse_extension_strings(self, buffer):
	# 	extension_strings = ''
	# 	for i in range(buffer.index, buffer.bytes_remaining):
	# 		extension_strings += str(struct.unpack(">i", buffer.read())[0])

	# 	print(extension_strings)
	# 	# extension_strings.decode()
	# 	extension_strings.rstrip(b'\x00').split(b'\x00')
	# 	extension_strings_length = sizeof(extension_strings)

	# 	for i in range(0, extension_strings_length):
	# 		self.extension_strings[i] = CalampExtensionString(extension_strings.split(b':', 1))

if __name__ == "__main__":
    print("compiled.")
