import binascii
import threading
import traceback
import socket

from lib.socket import InterruptableUdpSocket
from lib.socket import SocketInterruption

from settings import HOST
from settings import TOOLCHAIN_PORT
from settings import TOOLCHAIN_LOG_FILE
from settings import TOOCHAIN_ENABLE

UDP_PACKET_SIZE = 512

class Toolchain(threading.Thread):
	# def __init__(self, client_manager, log, handler=None):
	def __init__(self, log, handler=None):
		threading.Thread.__init__(self)
		# self._client_manager = client_manager
		self._handler = self.default_handler if handler is None else handler
		self._log = log
		self._shutdown_flag = threading.Event()
		self._lock = threading.Lock()
		self._host = HOST
		self._port = TOOLCHAIN_PORT
		self._shutdown = False
		self._packet_counter = 0

		try:
			self._socket = InterruptableUdpSocket(socket.AF_INET, socket.SOCK_DGRAM)
			self._socket.bind((self._host, self._port))

		except Exception as e:
			self._log.warning("{}({}) failed to bind {}:{} Error: {}".format())

		# self._log.info("{}({}) starting. ".format(self.name, self.ident))
		self._log.info("{} initializing. ".format(self.name))
		self._log.debug(" - host: {}:{}".format(self._host, self._port))
		self._log.info(" - log_raw: {}".format(TOOLCHAIN_LOG_FILE))
		self._log.info(" - enabled: {}".format(TOOCHAIN_ENABLE))

	def default_handler(self, packet):
		self._log.info("toolchain {}({}) payload: {}".format(self.name, self.ident, packet[0]))

	def register_handler(self, handler):
		"""
		@handler - function_ptr(packet)
		"""
		self._handler = handler

	def run(self):
		self._log.info("{}({}) started.".format(self.name, self.ident))

		while not self._shutdown_flag.is_set():
			try:
				packet = self._socket.interruptable_recvfrom(UDP_PACKET_SIZE)
				self._packet_counter += 1
				self._log_raw_packet(packet)
				self._log.info("toolchain: packet received.")
				self._handler(packet)

			# socket resvfrom was interrupted
			except SocketInterruption:
				continue

			except Exception as e:
				self._log.error("Server Exception: {}".format(e))
				# traceback.print_exc()
				continue

		self._socket.close()
		self._log.info("{}({}) packets: ({})".format(self.name, self.ident, self._packet_counter))

	def shutdown(self):
		self._log.info("{}({}) Shutdown Initiated...".format(self.name, self.ident))
		self._shutdown_flag.set()
		self._socket.interrupt()
		self._is_shutdown = True

	def _log_raw_packet(self, packet):
		raw_log = open(TOOLCHAIN_LOG_FILE + ".raw", "a+")
		raw_log.write(str(binascii.hexlify(packet[0]), 'utf-8')+ "\n")
		raw_log.flush()
		raw_log.close()

	@property
	def name(self):
		return type(self).__name__
	@property
	def is_shutdown(self):
		return self._is_shutdown
