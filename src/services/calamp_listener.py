import binascii
import threading
import traceback
import socket

from lib.socket import InterruptableUdpSocket
from lib.socket import SocketInterruption

from settings import LOG_FILE
from settings import LOG_RAW

from settings import HOST
from settings import PORT
from settings import COPY_TO_PRODUCTION
from settings import PL_HOST
from settings import PL_PORT
from settings import REMOTE_HOST
from settings import REMOTE_PORT
from settings import SEND_ACK

UDP_PACKET_SIZE = 512

class UdpServer(threading.Thread):
	def __init__(self, log, client_manager_def, db_manager_def):
		threading.Thread.__init__(self)
		self._log = log
		self._log_raw = LOG_RAW
		self._shutdown_flag = threading.Event()
		self._lock = threading.Lock()
		self._is_shutdown = False
		self._shutdown = False
		self._packet_counter = 0
		self._copy_to_production = COPY_TO_PRODUCTION
		self._send_ack = SEND_ACK

		try:
			self._socket = InterruptableUdpSocket(socket.AF_INET, socket.SOCK_DGRAM)
			# self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self._socket.bind((HOST , PORT))

		except Exception as e:
			# self._log.critical("{}({}) failed to bind {}:{}: {}".format(self.name, self.ident, HOST, PORT, e))
			self._log.critical("{}({}) failed to bind {}:{}: {}".format(self.name, self.get_native_id(), HOST, PORT, e))
			raise e

		self._log_startup()
		self._db_manager = db_manager_def(self._log)
		self._client_manager = client_manager_def(self, self._log)
		self._client_manager.start()
		self._db_manager.start()

	def run(self):
		# self._log.info("{}({}) started.".format(self.name, self.ident))
		self._log.info("{}({}) started.".format(self.name, self.get_native_id()))

		while not self._shutdown_flag.is_set():
			try:
				packet = self._socket.interruptable_recvfrom(UDP_PACKET_SIZE)
				# packet = self._socket.recvfrom(UDP_PACKET_SIZE)
				self._log_raw_packet(packet)
				self._packet_counter += 1
				self._client_manager.enqueue_packet(packet)

			# socket resvfrom was interrupted
			except SocketInterruption:
				continue

			except Exception as e:
				"""TODO: see socket.py for todo on fixing [Error 9] Bad File Descriptor"""
				# self._log.error("{}({}) Exception: {}".format(self.name, self.ident, e))
				self._log.error("{}({}) Exception: {}".format(self.name, self.get_native_id(), e))
				# traceback.print_exc()
				continue

		self._socket.close()
		# self._log.info("{}({}) clients: ({}) packets: ({})".format(self.name, self.ident, self._client_manager.clients, self.packet_counter))
		self._log.info("{}({}) clients: ({}) packets: ({})".format(self.name, self.get_native_id(), self._client_manager.clients, self.packet_counter))
		# self._client_manager.shutdown()
		# self._client_manager.join()
		# self._db_manager.shutdown()
		# self._db_manager.join()
		# self.log.info("{}({}) Shutdown Complete".format(self.name, self.ident))
		self.log.info("{}({}) Shutdown Complete".format(self.name, self.get_native_id()))

	def _log_raw_packet(self, packet):
		if (self._log_raw == True):
			raw_log = open(LOG_FILE + ".raw", "a+")
			raw_log.write(str(binascii.hexlify(packet[0]), 'utf-8')+ "\n")
			raw_log.flush()
			raw_log.close()

	def shutdown(self):
		self._shutdown_flag.set()
		self._socket.interrupt()
		self._is_shutdown = True

	@property
	def name(self):
		return type(self).__name__
	@property
	def factory(self):
		return self._factory
	@property
	def db_manager(self):
		return self._db_manager
	@property
	def send_ack(self):
		return self._send_ack
	@property
	def is_shutdown(self):
		return self._is_shutdown
	@property
	def log(self):
		return self._log
	@property
	def socket(self):
		return self._socket
	@property
	def packet_counter(self):
		return self._packet_counter
