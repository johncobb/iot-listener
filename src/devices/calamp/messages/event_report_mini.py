import struct
from lib import IoByte
from devices.calamp.api import FixByteMini
from devices.calamp.api import CommByteMini
from devices.calamp.api import CalampMessageBase
from devices.calamp.messages.schema import MessageConfig as cf

class EventReportMini(CalampMessageBase):
	def __init__ (self, options_header, message_header):
		CalampMessageBase.__init__(self, options_header, message_header)
  
	def __dict__(self):
		return {
			'options_header': self.options_header.__dict__(),
			'message_header': self.message_header.__dict__(),
			'update_time': self.update_time,
			'location': self.calamp_location.__dict__(),
			'fix': self.fix_byte.__dict__(),
			'comm': self.comm_byte.__dict__(),
			'event_code': self.event_code,
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

	def parse(self, buffer):
		self.update_time = struct.unpack(">i", self.buffer.read(cf.UPDATE_TIME_LEN))[0]

		self.calamp_location.latitude = struct.unpack(">i", self.buffer.read(cf.LATITUDE_LEN))[0]
		self.calamp_location.longitude = struct.unpack(">i", self.buffer.read(cf.LONGITUDE_LEN))[0]
		self.calamp_location.heading = struct.unpack(">h", self.buffer.read(cf.HEADING_LEN))[0]
		self.calamp_location.speed = self.buffer.read(cf.EVTMINI_SPEED_LEN)

		self.fix_byte = FixByteMini(self.buffer.read())
		self.comm_byte = CommByteMini(self.buffer.read())
		self.input_byte = IoByte(self.buffer.read())
		self.event_code = self.buffer.read()
		self.accumulator_count = self.buffer.read() & 0xFFFFFF

		if (self.accumulator_count > 0):
			self.parse_accumulators()

	@property
	def satellites(self):
		return self.fix_byte.satellites

	def log(self, log):
		log.debug("mini event report:")
		log.debug(" - update_time: {}".format(self.update_time_utc))
		log.debug(" - latitude: {}".format(self.calamp_location.latitude_radix))
		log.debug(" - longitude: {}".format(self.calamp_location.longitude_radix))
		log.debug(" - speed: {}".format(self.calamp_location.speed))
		log.debug(" - heading: {}".format(self.calamp_location.heading))
		log.debug("fix_byte: {}".format(hex(self.fix_byte.byte_val)))
		log.debug(" - satellites: {}".format(self.fix_byte.satellites))
		log.debug(" - last_known: {}".format(self.fix_byte.last_known))
		log.debug(" - invalid: {}".format(self.fix_byte.invalid))
		log.debug(" - invalid_time: {}".format(self.fix_byte.invalid_time))
		log.debug(" - historic: {}".format(self.fix_byte.historic))
		log.debug("comm_byte: {}".format(hex(self.comm_byte.byte_val)))
		log.debug(" - available: {}".format(self.comm_byte.available))
		log.debug(" - network_service: {}".format(self.comm_byte.network_service))
		log.debug(" - data_service: {}".format(self.comm_byte.data_service))
		log.debug(" - connected: {}".format(self.comm_byte.connected))
		log.debug(" - voice_call_is_active: {}".format(self.comm_byte.voice_call_is_active))
		log.debug(" - roaming: {}".format(self.comm_byte.roaming))
		log.debug(" - gps_antenna_ok: {}".format(self.comm_byte.gps_antenna_status_ok))
		log.debug(" - gps_receiver_tracking: {}".format(self.comm_byte.gps_receiver_tracking))
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