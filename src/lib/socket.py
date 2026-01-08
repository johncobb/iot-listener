import os
import socket
import select

class SocketInterruption(Exception):
	pass

class InterruptableUdpSocket(socket.socket):
	def __init__(self, family, type, **kwargs):
		socket.socket.__init__(self, family, type, **kwargs)
		self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self._r_pipe, self._w_pipe = os.pipe()
		self._interrupted = False

	def interruptable_recvfrom(self, buffersize, **kwargs):
		if self._interrupted:
			raise RuntimeError("Cannot be reused")
		read, _w, errors = select.select([self._r_pipe, self], [], [self])
		if self in read:
			return self.recvfrom(buffersize, **kwargs)
		else:
			raise SocketInterruption()
		return ""

	def interrupt(self):
		self._interrupted = True
		os.write(self._w_pipe, "I".encode())
		
	@property
	def interrupted(self):
		return self._interrupted