
import struct
from datetime import datetime
from lib import IoByte
from devices.calamp.api import FixByte
from devices.calamp.api import CommByte
from devices.calamp.api import GpsByte
from devices.calamp.api import CalampMessageBase
from devices.calamp.messages.schema import MessageConfig as cf

# class UndefinedReport(CalampMessageBase):
# 	def __init__(self, options_header, message_header):
# 		CalampMessageBase.__init__(self, options_header, message_header)
  
# 	def parse(self, buffer):
# 		pass

# 	def log(self, :
# 		pass
#  	# log.info("undefined report:")
# 		# log.info(" - message_header:")
# 		# log.info("   service_type: {}".format(self.message_header.service_type))
# 		# log.info("   message_type: {}".format(self.message_header.message_type))
# 		# log.info("   sequence_number: {}".format(self.message_header.sequence_number))
  
class EventReport(CalampMessageBase):
	def __init__ (self, options_header, message_header):
		CalampMessageBase.__init__(self, options_header, message_header)
		self.time_of_fix = None
		self._satellites = None
		self.carrier = None
		self.rssi = None
		self.hdop = None
		self.event_index = None
  
	def __dict__(self):
		return {
			'header': self.headers_to_dict(),
			'update_time': self.update_time,
			'time_of_fix': self.time_of_fix,
			'location': self.calamp_location.__dict__(),
			'satellites': self._satellites,
			'fix': self.fix_byte.__dict__(),
			'carrier': self.carrier,
			'rssi': self.rssi,
			'comm': self.comm_byte.__dict__(),
			'gps': self.gps_byte.__dict__(),
			'event_index': self.event_index,
			'event_code': self.event_code,
			'hdop': self.hdop,
			'inputs': {
				'bit_0': self.input_byte.bit_0,
				'bit_1': self.input_byte.bit_1,
				'bit_2': self.input_byte.bit_2,
				'bit_3': self.input_byte.bit_3,
				'bit_4': self.input_byte.bit_4,
				'bit_5': self.input_byte.bit_5,
				'bit_6': self.input_byte.bit_6,
				'bit_7': self.input_byte.bit_7
			},
			'accumulators': self.accumulators.__dict__()
		}

	@property
	def time_of_fix_utc(self):
		return datetime.utcfromtimestamp(self.time_of_fix)

	@property
	def satellites(self):
		return self._satellites

	def parse(self, buffer):


		self.update_time = struct.unpack(">i", self.buffer.read(cf.UPDATE_TIME_LEN))[0]
		self.time_of_fix = struct.unpack(">i", self.buffer.read(cf.TIME_OF_FIX_LEN))[0]

		self.calamp_location.latitude = struct.unpack(">i", self.buffer.read(cf.LATITUDE_LEN))[0]
		self.calamp_location.longitude = struct.unpack(">i", self.buffer.read(cf.LONGITUDE_LEN))[0]
		self.calamp_location.altitude = struct.unpack(">i", self.buffer.read(cf.ALTITUDE_LEN))[0]
		self.calamp_location.speed = struct.unpack(">i", self.buffer.read(cf.EVT_SPEED_LEN))[0]
		self.calamp_location.heading = struct.unpack(">h", self.buffer.read(cf.HEADING_LEN))[0]
		self._satellites = self.buffer.read(cf.SATELLITES_LEN)


		self.fix_byte = FixByte(self.buffer.read(cf.FIX_BYTE_LEN))
		self.carrier = struct.unpack(">h", self.buffer.read(cf.CARRIER_LEN))[0]
		self.rssi = struct.unpack(">h", self.buffer.read(cf.RSSI_LEN))[0]
		self.comm_byte = CommByte(self.buffer.read(cf.COMM_BYTE_LEN))
		self.hdop = self.buffer.read(cf.HDOP_LEN)
		self.input_byte = IoByte(self.buffer.read(cf.INPUT_BYTE_LEN))
		self.gps_byte = GpsByte(self.buffer.read(cf.GPS_BYTE_LEN))
		self.event_index = self.buffer.read(cf.EVENT_INDEX_LEN)
		self.event_code = self.buffer.read(cf.EVENT_CODE_LEN)
		self.accumulator_count = self.buffer.read(cf.ACCUMULATOR_COUNT_LEN) & 0xFFFFFF

		if (self.accumulator_count > 0):
			self.parse_accumulators(buffer)
	
	def log(self, log):

		log.debug("event report:")
		log.debug(" - update_time: {}".format(self.update_time_utc))
		log.debug(" - time_of_fix: {}".format(self.time_of_fix_utc))
		log.debug(" - latitude: {}".format(self.calamp_location.latitude_radix))
		log.debug(" - longitude: {}".format(self.calamp_location.longitude_radix))
		log.debug(" - map: http://maps.google.com?q={},{}".format(self.calamp_location.latitude_radix, self.calamp_location.longitude_radix))
		log.debug(" - alt: {}".format(self.calamp_location.altitude))
		log.debug(" - speed: {}".format(self.calamp_location.speed))
		log.debug(" - heading: {}".format(self.calamp_location.heading))
		log.debug(" - satellites: {}".format(self.satellites))
		log.debug("fix_byte: {}".format(hex(self.fix_byte.byte_val)))
		log.debug(" - fix_predicted: {}".format(self.fix_byte.predicted))
		log.debug(" - fix_differentially_corrected: {}".format(self.fix_byte.differentially_corrected))
		log.debug(" - fix_last_known: {}".format(self.fix_byte.last_known))
		log.debug(" - fix2d: {}".format(self.fix_byte.fix2d))
		log.debug("carrier: {}".format(self.carrier))
		log.debug("rssi: {}".format(self.rssi))
		log.debug("comm_byte: {}".format(hex(self.comm_byte.byte_val)))
		log.debug(" - available: {}".format(self.comm_byte.available))
		log.debug(" - network_service: {}".format(self.comm_byte.network_service))
		log.debug(" - data_service: {}".format(self.comm_byte.data_service))
		log.debug(" - connected: {}".format(self.comm_byte.connected))
		log.debug(" - voice_call_is_active: {}".format(self.comm_byte.voice_call_is_active))
		log.debug(" - roaming: {}".format(self.comm_byte.roaming))
		log.debug(" - network_3g: {}".format(self.comm_byte.network_3g))
		log.debug("hdop: {}".format(self.hdop))
		log.debug("gps_byte: {}".format(hex(self.gps_byte.byte_val)))
		log.debug(" - http_ota_update_status_ok: {}".format(self.gps_byte.http_ota_update_status_ok))
		log.debug(" - gps_receiver_test_ok: {}".format(self.gps_byte.gps_receiver_test_ok))
		log.debug(" - gps_receiver_tracking: {}".format(self.gps_byte.gps_receiver_tracking))
		log.debug("event_index: {}".format(self.event_index))
		log.debug("event_code: {}".format(self.event_code))
		log.debug("input_byte: {}".format(hex(self.input_byte.byte_val)))
		log.debug(" - input[0] {}".format(self.input_byte.bit_0))
		log.debug(" - input[1] {}".format(self.input_byte.bit_1))
		log.debug(" - input[2] {}".format(self.input_byte.bit_2))
		log.debug(" - input[3] {}".format(self.input_byte.bit_3))
		log.debug(" - input[4] {}".format(self.input_byte.bit_4))
		log.debug(" - input[5] {}".format(self.input_byte.bit_5))
		log.debug(" - input[6] {}".format(self.input_byte.bit_6))
		log.debug(" - input[7] {}".format(self.input_byte.bit_7))
		log.debug("accumulators: {}".format(self.accumulator_count))
		if (self.accumulator_count > 0):
			for key in range(0, self.accumulator_count):
				log.debug(" - accum[{}]: {}".format(self.accumulators(key).id, self.accumulators(key).val))