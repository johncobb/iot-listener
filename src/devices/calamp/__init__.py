import struct
from datetime import datetime
from lib import IoByte
from lib import IoByteUtil
from lib import ByteBuffer

from lib import MESSAGE_SIZE_MIN
from lib import MASK_BIT
from lib import MASK_NIBBLE
from lib import SHIFT_NIBBLE
from devices.calamp.api import OptionsByte
from devices.calamp.api import ExtensionsByte
from devices.calamp.api import FixByte
from devices.calamp.api import FixByteMini
from devices.calamp.api import CommByte
from devices.calamp.api import CommByteMini
from devices.calamp.api import GpsByte
from devices.calamp.api import MessageTypes
from devices.calamp.api import ServiceTypes
from devices.calamp.api import MobileIdType
from devices.calamp.api import CalampLocation
from devices.calamp.api import CalampAccumulator
from devices.calamp.api import CalampMessageBase
from devices.calamp.api import CalampMessageHeader
from devices.calamp.api import CalampOptionsHeader

from devices.calamp.messages.schema import MessageConfig as cf

""" https://docs.python.org/3/library/struct.html """

def parse_mobile_id(packet):
    iobuffer = ByteBuffer(packet)

    opt_header = OptionsHeader()
    opt_header.parse(iobuffer)

    return opt_header.mobile_id

class MessageHeader(CalampMessageHeader):
	def __init__(self, service_type=ServiceTypes.UNACKNOWLEDGED, message_type=MessageTypes.NULL, sequence_number=0):
		CalampMessageHeader.__init__(self, service_type, message_type, sequence_number)

	def parse(self, buffer):
		self.service_type = ServiceTypes(buffer.read(cf.SERVICE_TYPE_LEN))
		self.message_type = MessageTypes(buffer.read(cf.MESSAGE_TYPE_LEN))
		self.sequence_number = struct.unpack(">H", buffer.read(cf.SEQUENCE_NUMBER_LEN))[0]

	def __dict__(self):
		return {
			'service_type': self.service_type.name,
			'message_type': self.message_type.name,
			'sequence_number': self.sequence_number
		}

	def log(self, log):
		log.debug(" message_header:")
		log.debug(" - service_type: {}({})".format(self.service_type.value, self.service_type.name))
		log.debug(" - message_type: {}({})".format(self.message_type.value, self.message_type.name))
		log.debug(" - sequence_number: {}".format(self.sequence_number))

class OptionsHeader(CalampOptionsHeader):
	def __init__(self, mobile_id="", mobile_id_type=0):
		CalampOptionsHeader.__init__(self, mobile_id, mobile_id_type)
		self.buffer = None

	def parse_mobile_id(self):
		self.mobile_id_length = self.buffer.read(cf.MOBILEID_LEN)
		""" decode (binary coded decimal) """
		for i in range(0, self.mobile_id_length):
			_mobile_id = self.buffer.read()
			self.mobile_id += str(_mobile_id >> SHIFT_NIBBLE)
			self.mobile_id += str(_mobile_id & MASK_NIBBLE)

	""" TODO: Research getting following method working to replace manual parse_mobile_id above. """
	# def parse_mobile_id(self):
	# 	self.mobile_id_length = self.buffer.read(cf.MOBILEID_LEN)
	# 	""" decode (binary coded decimal) """
	# 	self.mobile_id = IoByteUtil.bcd_unpack(self.buffer, self.mobile_id_type_length)

	def parse_mobile_id_type(self):
		""" TODO: refactor to handle reading of mobile_id_type the number of bytes read for mobile_id_type_length. """
		self.mobile_id_type_length = self.buffer.read()
		self.mobile_id_type = MobileIdType(self.buffer.read(cf.MOBILEID_TYPE_LEN))

	def parse_authentication_word(self):
		self.authentication_word = self.buffer.read(cf.AUTHENTICATION_LEN).decode()

	def parse_routing(self):
		self.routing_length = self.buffer.read(cf.ROUTING_LEN)
		for i in range(self.routing_length):
			self.routing += self.buffer.read()

	def parse_forwarding(self):
		self.forwarding_length = self.buffer.read(cf.FORWARDING_LEN)
		self.forwarding_address = "{}.{}.{}.{}".format(self.buffer.read(), self.buffer.read(), self.buffer.read(), self.buffer.read())
		# for i in range(self.forwarding_length):
		# 	self.forwarding_address += self.buffer.read()

		for i in range(cf.FORWARDING_PORT_LEN):
			self.forwarding_port = self.forwarding_port * 256 + self.buffer.read()

		self.forwarding_protocol = self.buffer.read()
		self.forwarding_operation = self.buffer.read()

	def parse_redirection(self):
		self.response_redirection_length = self.buffer.read()
		for i in range(self.response_redirection_length):
			self.response_redirection_address += self.buffer.read()

	def parse_extension_esn(self):
		pass

	def parse_extension_vin(self):
		self.vin_length = self.buffer.read(cf.VIN_LEN)
		for i in range(self.vin_length):
			self.vin += self.buffer.read()

	def parse_extension_encryption(self):
		pass

	def parse_extension_routing(self):
		pass

		self.response_redirection_port = self.buffer.read()
	def _set_buffer(self, buffer):
		self.buffer = buffer

	def parse(self, buffer):
		self._set_buffer(buffer)
		self.options_byte = OptionsByte(self.buffer.read())

		if (self.opt.enable_mobile_id):
			self.parse_mobile_id()
		if (self.opt.enable_mobile_id_type):
			self.parse_mobile_id_type()
		if (self.opt.enable_authentication_word):
			self.parse_authentication_word()
		if (self.opt.enable_routing):
			self.parse_routing()
		if (self.opt.enable_forwarding):
			self.parse_forwarding()
		if (self.opt.enable_response_redirection):
			self.parse_redirection()

		if (self.opt.enable_options_extension):
			self.extension_byte = ExtensionsByte(self.buffer.read())
			if (self.ext.enable_extension_esn):
				self.parse_extension_esn()
			if (self.ext.enable_extension_vin):
				self.parse_extension_vin()
			if (self.ext.enable_extension_encryption):
				self.parse_extension_encryption()
			if (self.ext.enable_extension_compression):
				""" --- no data fields are associated with the LM direct compression. (skip) --- """
				pass
			if (self.ext.enable_extension_routing):
				self.parse_extension_routing()

	def __dict__(self):
		datagram = {}

		if self.opt.enable_mobile_id:
			datagram['mobile_id'] = self.mobile_id
		if self.opt.enable_mobile_id_type:
			datagram['mobile_id_type'] = self.mobile_id_type.name
		if self.opt.enable_authentication_word:
			datagram['authentication'] = self.authentication_word
		if self.opt.enable_routing:
			datagram['routing'] = self.routing
		if self.opt.enable_forwarding:
			datagram['forwarding'] = {
				'address': self.forwarding_address,
				'port': self.forwarding_port,
				'protocol': self.forwarding_protocol,
				'operation': self.forwarding_operation
			}
		if self.opt.enable_response_redirection:
			datagram['response_redirection'] = {
				'address': self.response_redirection_address,
				'port': self.response_redirection_port
			}
		if self.opt.enable_options_extension:
			datagram['options_extension'] = {
				'esn': self.extension_esn,
				'vin': self.extension_vin,
				'encryption': self.extension_encryption,
				'compression': self.extension_compression,
				'routing': self.extension_routing
			}
		return datagram

	def log(self, log):

		if self.mobile_id is None:
			log.debug("Mobile Id not valid. Not a Valid Packet!")
			return

		# self.opt.log(server)

		if self.opt.enable_options_extension:
			# if (self.ext is not None):
			# 	self.ext.log.debug()
			log.debug("options extension: ")
			log.debug(" - extension_esn: {}".format(self.extension_esn))
			log.debug(" - extension_vin: {}".format(self.extension_vin))
			log.debug(" - extension_encryption: {}".format(self.extension_encryption))
			log.debug(" - extension_compression: {}".format(self.extension_compression))
			log.debug(" - extension_routing: {}".format(self.extension_routing))

		log.debug("options data: ")
		if self.opt.enable_mobile_id:
			log.debug(" - mobile_id: {}".format(self.mobile_id))
		if self.opt.enable_mobile_id_type:
			log.debug(" - mobile_id_type: {}({})".format(self.mobile_id_type.value, self.mobile_id_type.name))
		if self.opt.enable_authentication_word:
			log.debug(" - authentication: {}".format(self.authentication_word))
		if self.opt.enable_routing:
			log.debug(" - routing: {}".format(self.routing))
		if self.opt.enable_forwarding:
			log.debug(" - forwarding_address: {}".format(self.forwarding_address))
			log.debug(" - forwarding_port: {}".format(self.forwarding_port))
			log.debug(" - forwarding_protocol: {}".format(self.forwarding_protocol))
			log.debug(" - forwarding_operation: {}".format(self.forwarding_operation))

		if self.opt.enable_response_redirection:
			log.debug(" - response_redirection_address: {}".format(self.response_redirection_address))
			log.debug(" - response_redirection_port: {}".format(self.response_redirection_port))

		if self.opt.enable_options_extension:
			log.debug(" ")
			log.debug(" options extension data:")

		if self.ext:
			if self.ext.enable_extension_esn:
				log.debug(" - extension_esn: {}".format(self.extension_esn))

			if self.ext.enable_extension_vin:
				log.debug(" - extension_vin: {}".format(self.extension_vin))

