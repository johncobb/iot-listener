import struct

from lib import ByteBuffer
from devices.calamp.api import CalampMessageBase

class UnitRequest(CalampMessageBase):
	""" Unit Request allows multiple constructor overloads. """
	""" Check argument type to determine how to construct the object. """
	""" ByteBuffer used for parsing packets received from socket. """
	""" Class objects used to create instances for use within API. """
	def __init__ (self, options_header, message_header, action=0, byte8=0, byte16=0, byte32=0):
		CalampMessageBase.__init__(self, options_header, message_header)
		self.action = action
		self.byte8 = byte8
		self.byte16 = byte16
		self.byte32 = byte32
  
	def __dict__(self):
		return {
			'options_header': self.options_header.__dict__(),
			'message_header': self.message_header.__dict__(),
			'mobile_id': self.mobile_id,
			'action': self.action,
			'byte8': self.byte8,
			'byte16': self.byte16,
			'byte32': self.byte32
		}

	def parse(self, buffer):

		if (self.buffer.bytes_remaining > 0):
			self.action = self.buffer.read()

		if (self.buffer.bytes_remaining > 0):
			self.byte8 = self.buffer.read()
   
		if (self.buffer.bytes_remaining >= 2):
			self.byte16 = self.buffer.read()
			self.byte16 = self.buffer.read()
   
		if (self.buffer.bytes_remaining >= 4):
			self.byte32 = self.buffer.read()
			self.byte32 = self.buffer.read()
			self.byte32 = self.buffer.read()
			self.byte32 = self.buffer.read()
		pass

	def __bytes__(self):
		_bytes = bytearray()
		_bytes.extend(bytes(self.options_header), bytes(self.message_header))
		_bytes.extend(struct.pack(">B", 1 << 0 | 1 << 1 | 1 << 7))

	def log(self, log):	
		log.debug("unit request:")
		log.debug(" - mobile_id: {}".format(self.mobile_id))
		log.debug(" - action: {}".format(self.action))
		log.debug(" - byte8: {}".format(self.byte8))
		log.debug(" - byte16: {}".format(self.byte16))
		log.debug(" - byte32: {}".format(self.byte32))

	def __bytes__(self):
		# return struct.pack(">BBHI", self.action, self.byte8, self.byte16, self.byte32)
		_bytes = bytearray()
		_bytes.extend(bytes(self.options_header))
		_bytes.extend(bytes(self.message_header))

		_bytes.extend(struct.pack(">BBHI", self.action, self.byte8, self.byte16, self.byte32))
		return bytes(_bytes)