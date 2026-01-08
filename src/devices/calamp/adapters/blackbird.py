import json

from devices.calamp.adapters import MessgageAdapter

from settings import BB_HOST
from settings import BB_PORT

from devices.calamp.config import CalampEvents

blackbird_adapter_events = [CalampEvents.IGNITION_ON, CalampEvents.IGNITION_OFF, CalampEvents.TIME_DISTANCE, CalampEvents.IDLE, CalampEvents.IDLE_END, CalampEvents.PARKING_HEARTBEAT]

class BlackbirdMessage(MessgageAdapter):
	def __init__(self, events=blackbird_adapter_events):
		MessgageAdapter.__init__(self, events)
		self.transform = self.to_json
		# self._source = (BB_HOST, BB_PORT)
		self._source = ("0.0.0.0", 1337)

	def input_to_json(self):
		return {
			"input_0_ignition_on": self.message.gpio.bit_0,
			"input_1": self.message.gpio.bit_1,
			"input_2": self.message.gpio.bit_2,
			"input_3": self.message.gpio.bit_3,
			"input_4": self.message.gpio.bit_4,
			"input_5": self.message.gpio.bit_5,
			"input_6": self.message.gpio.bit_6,
			"input_7": self.message.gpio.bit_7,
			}

	def accum_to_json(self):
		return {"accum_{}".format(self.message.accumulators(key).id):self.message.accumulators(key).val for key in range(0, self.message.accumulator_count)}

	def to_json(self):
		packet = dict([
			("mobile_id", self.message.options_header.mobile_id),
			('latitude', self.message.loc.latitude_radix),
			('longitude', self.message.loc.longitude_radix),
			('speed', self.message.loc.speed_mph),
			('heading', self.message.loc.heading),
			('satellites', self.message.satellites),
			('fix_invalid', self.message.fix_byte.invalid),
			('update_time', "{}".format(self.message.update_time_utc)),
			('event_code', self.message.event_code),
			('inputs', self.input_to_json()),
			('accumulators', self.accum_to_json()),
		])

		packet = json.dumps(packet, indent=2, sort_keys=False).replace('null', "")

		return packet
