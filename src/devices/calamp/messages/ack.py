
from devices.calamp.api import CalampMessageBase
from devices.calamp.api import CalampAppVersion
from devices.calamp.api import MessageTypes
from devices.calamp.api import AckTypes
from devices.calamp.messages.schema import MessageConfig as cf

class AckMessage(CalampMessageBase):
	def __init__(self, options_header, message_header):
		CalampMessageBase.__init__(self, options_header, message_header)
		self.ack = None
		self.app_version = CalampAppVersion(0, 0, 0)
		self.type = None
		self.spare = None
  
	def __dict__(self):
		return {
			'header': self.headers_to_dict(),
			'type': self.type.name,
			'ack': self.ack.name,
			'app_version': str(self.app_version)
		}
	
	def parse(self, buffer):
		self.type = MessageTypes(self.buffer.read(cf.ACK_TYPE_LEN))
		self.ack = AckTypes(self.buffer.read(cf.ACK_LEN))
		self.spare = self.buffer.read(cf.ACK_SPARE_LEN)

		self.app_version.byte_0 = self.buffer.read()
		self.app_version.byte_1 = self.buffer.read()
		self.app_version.byte_2 = self.buffer.read()
  
	def log(self, log):
		log.debug("ack message:")
		log.debug(" - type: {}({})".format(self.type.value, self.type.name))
		log.debug(" - ack: {}({})".format(self.ack.value, self.ack.name))
		log.debug(" - spare: {}".format(self.spare))
		log.debug("app_version: ({}, {}, {})".format(self.app_version.byte_0, self.app_version.byte_1, self.app_version.byte_2))
	def print(self):
		print("ack message:")
		print(" - type: {}".format(self.type))
		print(" - ack: {}".format(self.ack))
		print(" - app_version: {}".format(self.app_version))