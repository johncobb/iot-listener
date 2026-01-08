import struct
from devices.calamp.api import MessageTypes
from devices.calamp.api import ServiceTypes
from devices.calamp.api import AckTypes


class DeviceAcknowledgement:
	def __init__(self, service_type=ServiceTypes.UNACKNOWLEDGED, message_type=MessageTypes.NULL, sequence_number=0, ack_handler=None):
		self._service_type = service_type
		self._message_type = message_type
		self._sequence_number = sequence_number
		self._ack_handler = ack_handler
		self._ack_back = False

	def reg_ack_handler(self, ack_handler):
		self._ack_handler = ack_handler

	def _type(self, service_type):
		if (service_type == ServiceTypes.UNACKNOWLEDGED):
			return None # no ack
		elif (service_type == ServiceTypes.ACKNOWLEDGED):
			return ServiceTypes.ACKNOWLEDGE_RESPONSE.value
		elif (service_type == ServiceTypes.ACKNOWLEDGE_RESPONSE):
			return service_type == ServiceTypes.ACKNOWLEDGED.value
		else:
			return None # no ack
			
	def _status(self, message_type):
		return AckTypes.ACK_SUCCESSFUL.value

		""" TODO: verify with CalAmp support that sending a not supported Message type is necessary """
		if (MessageTypes.is_supported(message_type)):
			return AckTypes.ACK_SUCCESSFUL.value
		elif (MessageTypes(message_type)):
			return AckTypes.NAK_NOT_SUPPORTED_MESSAGE_TYPE.value
		else:
			return AckTypes.NAK_NOT_SUPPORTED_OPERATION.value

	def _dispatch_ack(self, packet):
		if(self._ack_handler != None):
			self._ack_handler(packet)

	def ack(self):
		""" handle ack types that need to be sent back to the device.
			On a service requested ack it dispatches a ack worker to
			monitor the client queue for a ack message 
		"""

		""" short circuit if ack is not needed """
		if (self._service_type != ServiceTypes.ACKNOWLEDGED):
			return

		""" reset the ack_back flag. """
		self._ack_back = True

		payload = struct.pack(">2bH6b", self._type(self._service_type),
										MessageTypes.ACKNOWLEDGEMENT.value,
										self._sequence_number,
										self._service_type.value,
										self._status(self._message_type),
										0,       # spare byte
										0, 0, 0) # app version (3 bytes)

		self._dispatch_ack(payload)

	def ack_handler(self, service_type, message_type, sequence_number):
		self._service_type = service_type
		self._message_type = message_type
		self._sequence_number = sequence_number
		self._ack_back = False
		self.ack()

	@property
	def ack_back(self):
		return self._ack_back
		

