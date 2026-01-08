from devices.calamp.api import CalampMessageBase
from devices.calamp.messages.schema import MessageConfig as cf

class UndefinedReport(CalampMessageBase):
	def __init__(self, options_header, message_header):
		CalampMessageBase.__init__(self, options_header, message_header)
  
	def parse(self, buffer):
		pass

	def __dict__(self):
		return {
			'options_header': self.options_header.__dict__(),
			'message_header': self.message_header.__dict__()
		}

	def log(self, server):
		pass

 	# server.log.info("undefined report:")
		# server.log.info(" - message_header:")
		# server.log.info("   service_type: {}".format(self.message_header.service_type))
		# server.log.info("   message_type: {}".format(self.message_header.message_type))
		# server.log.info("   sequence_number: {}".format(self.message_header.sequence_number))