import signal
from threading import Thread, Event
from queue import Queue
from queue import PriorityQueue

MESSAGE_SIZE_MIN = 33
MASK_BIT = 0x01
MASK_NIBBLE  = 0x0F
SHIFT_NIBBLE = 4

class ByteBufferException(Exception):
	pass

class IoThread(Thread):
	def __init__(self):
		self.shutdown = False
		self.shutdown_flag = Event()

	""" Start thread """
	def start_thread(self):
		self._thread = Thread(target=self.thread_handler, daemon=True)
		self._thread.start()

	""" Shutdown thread """
	def shutdown_thread(self):
		self.shutdown_flag.set()

	def thread_handler(self):
		raise Exception("Sub-class must implement thread_handler()")

	""" Service Running? """
	@property
	def running(self):
		return not self.shutdown

class IoByteUtil:
	def bit_mask(data, shift):
		"""
		masks parts of data.

		@param data The data.
		@param shift The length to shift.
		"""
		return data >> shift & MASK_BIT == 1

	def bcd_unpack(iobuffer, length, ignore=MASK_NIBBLE):
		bcd_val = ""
		for i in range(0, length):
			_data = iobuffer.read()
			_chunk = _data >> SHIFT_NIBBLE
			if (_chunk != MASK_NIBBLE):
				bcd_val += str(_chunk)
			
			_chunk = _data & MASK_NIBBLE

			if (_chunk != MASK_NIBBLE):
				bcd_val += str(_chunk)

		return bcd_val


class ByteBuffer():
	def __init__(self, buffer, len=None):
		self._buffer = buffer
		self._len = len
		self._index = 0

	def _read(self):
		val = self._buffer[self._index]
		self._index += 1
		return val

	def read(self, size=1):
		if size == 1:
			return self._read()

		tmp = bytearray()	
		for i in range(size):
			tmp.append(self._read())
		
		return bytes(tmp)

	def reset(self):
		self._buffer = bytearray()

	@property
	def buffer(self):
		return self._buffer
	@property
	def length(self):
		return len(self._buffer) - self._index
	@property
	def index(self):
		return self._index

	@property
	def bytes_remaining(self):
		return (len(self._buffer) - self._index) + 1


class IoByte():
	def __init__(self, iobyte_val):
		self._iobyte_val = iobyte_val
		self._bit_0 = 0
		self._bit_1 = 0
		self._bit_2 = 0
		self._bit_3 = 0
		self._bit_4 = 0
		self._bit_5 = 0
		self._bit_6 = 0
		self._bit_7 = 0
		self._parse()

	def _parse(self):
		self._bit_0 = IoByteUtil.bit_mask(self._iobyte_val, 0)
		self._bit_1 = IoByteUtil.bit_mask(self._iobyte_val, 1)
		self._bit_2 = IoByteUtil.bit_mask(self._iobyte_val, 2)
		self._bit_3 = IoByteUtil.bit_mask(self._iobyte_val, 3)
		self._bit_4 = IoByteUtil.bit_mask(self._iobyte_val, 4)
		self._bit_5 = IoByteUtil.bit_mask(self._iobyte_val, 5)
		self._bit_6 = IoByteUtil.bit_mask(self._iobyte_val, 6)
		self._bit_7 = IoByteUtil.bit_mask(self._iobyte_val, 7)
	
	def parse(self, iobyte_val):
		self._iobyte_val = iobyte_val
		self._parse()

	@property
	def byte_val(self):
		return self._iobyte_val

	@property
	def bit_0(self):
		return self._bit_0
	@property
	def bit_1(self):
		return self._bit_1
	@property
	def bit_2(self):
		return self._bit_2
	@property
	def bit_3(self):
		return self._bit_3
	@property
	def bit_4(self):
		return self._bit_4
	@property
	def bit_5(self):
		return self._bit_5
	@property
	def bit_6(self):
		return self._bit_6
	@property
	def bit_7(self):
		return self._bit_7
