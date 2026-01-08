import threading
import time
import datetime
from queue import Queue
from queue import Queue
from enum import Enum
import traceback
import binascii


# from services.toolchain import Toolchain
# from services.landmark import LandmarkManager
# from services.processor import ProcessorForwarder

from settings import THREAD_POLLING
from settings import REPORT_TIMEOUT
from settings import ACK_BACK_TIMEOUT
from settings import TOOCHAIN_ENABLE
from settings import CLIENT_DWELL_TIME
from settings import REPORT_TIMEOUT_ENABLE
from settings import ACKBACK_ENABLE
from settings import LANDMARK_ENABLE
from settings import PROC_FORWARDING_ENABLE

class Priority(Enum):
	HIGH = 0
	LOW  = 1

class Packet:
	def __init__(self, data, source):
		self._source = source
		self._data = data
		self._last_update = time.time_ns()
		self._timestamp = datetime.datetime.now()

	def __dict__(self):
		return {
			'source': {
				'address': self.ip,
				'port': self.port
			},
			'payload':  str(binascii.hexlify(self.payload), 'utf-8'),
			'last_update': self.last_update,
			'timestamp': self.timestamp.timestamp()
		}

	@property
	def name(self):
		return type(self).__name__
	@property
	def source(self):
		return self._source
	@property
	def ip(self):
		return self._source[0]
	@property
	def port(self):
		return self._source[1]
	@property
	def payload(self):
		return self._data
	@property
	def last_update(self):
		return (self._last_update != None)
	@property
	def timestamp(self):
		return self._timestamp

class Report:
	"""
	Report class
	@log: the log
	@packet: Packet instance
	"""
	def __init__(self, log, packet):
		self._log = log
		self._packet = packet
		self._id = packet.source
		self._message = None

	def __dict__(self):
		return {
			'report_id': self._id,
			'packet': self._packet.__dict__(),
			'message': self._message
		}

	@property
	def name(self):
		return type(self).__name__
	@property
	def packet(self):
		return self._packet
	@property
	def message(self):
		return self._message
	@property
	def id(self):
		return self._id
	@property
	def is_timeout(self):
		_time = (self._packet.timestamp + datetime.timedelta(seconds=REPORT_TIMEOUT))
		_timenow = datetime.datetime.now()
		_timeout = _timenow > _time
		self._log.debug("client: {} report: timeout: {} > {} == ({})".format(self.id, _timenow, _time, _timeout))
		return _timeout and REPORT_TIMEOUT_ENABLE
	@property
	def package(self):
		return self.__dict__()

class AckBack:
	def __init__(self, timeout, sentinel=0):
		self._count = 0
		self._sentinel = sentinel
		self._timeout = timeout
		self._flag = threading.Event()
		self._semaphore = threading.Semaphore(1)

	def _handle_count(self, n):
		"""adds or subtracts from the count.
		the semaphore protects the count from getting
		changed by two threads at the same time."""
		self._semaphore.acquire(True, ACK_BACK_TIMEOUT)
		self._count = self._count + n
		if (self._count > self._sentinel):
			self._flag.set()
		else:
			self._flag.clear()
		self._semaphore.release()

	def increment_ack(self):
		"""adds one to the ack count"""
		self._handle_count(1)

	def _decrement_ack(self):
		"""subtract an ack from the ack count
		blocks until the count is greater than 1"""
		self._handle_count(-1)

	def is_ack(self):
		"""requests an ack therefore subtracting from the count
		if the count """
		# self._decrement_ack()
		_flag = self._flag.wait(self._timeout)
		if _flag:
			self._decrement_ack()
		else:
			self.increment_ack()
		return _flag

	@property
	def count(self):
		return self._count

class Client(threading.Thread):
	def __init__(self, client_manager, log, id):
		threading.Thread.__init__(self)
		self._client_manager = client_manager
		self._log = log
		self._id = id
		self._instance_time = datetime.datetime.now()
		self._socket = None
		self._shutdown_flag = threading.Event()
		self._sleep = threading.Event()
		self._sleep.set()
		self._server_sendto = None
		self._inbox = Queue()
		self.ackback = AckBack(ACK_BACK_TIMEOUT)
		self._outbox = OutboxHandler(self, self._log, self._id, client_manager.server_sendto)

		self._log.debug("client: {} client_type: {}({}) client created".format(self._id, self.name, self.ident))

	def inbox_enqueue(self, report):
		"""ClientManager places report in here """
		self._inbox.put(report)

	def outbox_enqueue(self, packet):
		"""
		@packet - raw packet data
		"""
		_destination = None
		if not self._outbox.is_alive():
			self._outbox.start()

		if self._report != None:
			_destination = self._report.packet.source

		payload = (packet, _destination)
		self._outbox.enqueue(payload)

	def run(self):
		self._log.info("{}({}) started.".format(self.name, self.ident))

		while True:
			time.sleep(THREAD_POLLING)
			if self._shutdown_flag.is_set() and self._inbox.qsize() == 0:
				self._log.info("client: {} client_type: {}({}) Shutdown Complete".format(self._id, self.name, self.ident))
				break

			# if self.is_timeout:
			# 	self.shutdown()

			while self._inbox.qsize() > 0:
				report = self._inbox.get()
				self._inbox_handler(report)
				self._inbox.task_done()

		if self._outbox.is_alive():
			self._outbox.join()

	def shutdown(self):
		self._log.info("client: {} client_type:{}({}) Shutdown Initiated...".format(self._id, self.name, self.ident))
		self._shutdown_flag.set()
		self._inbox.join()
		self._outbox.shutdown()

	@property
	def name(self):
		return type(self).__name__
	@property
	def id(self):
		return (self._id, self.ident)
	@property
	def log(self):
		return self._log
	@property
	def is_shutdown(self):
		return self._shutdown_flag.isSet()
	@property
	def report(self):
		return self._report
	@property
	def is_timeout(self):
		if self._report == None:
			_dwell_offset = self._instance_time + datetime.timedelta(seconds=CLIENT_DWELL_TIME)
		else:
			_dwell_offset = self._report.packet.timestamp + datetime.timedelta(seconds=CLIENT_DWELL_TIME)

		_timenow = datetime.datetime.now()
		_timeout = _timenow > _dwell_offset
		# self._log.debug("client: {} dwell: {} > {} == {}".format(self.id, _timenow, _dwell_offset, _timeout))
		return _timeout

	@property
	def package(self):
		return self._asdict()

class ClientManager(threading.Thread):
	""" A parent class that handles enqueuing and dequeueing packets from the server
	"""
	def __init__(self, server, log, toolchain_def, landmark_def, processor_def, client_def=Client, report_def=Report, packet_def=Packet):
		"""
		@server: UDPServer instance
		@log: logger
		@client: Client object - used to instantiate each client
		@packet: Packet object - used to instantiate each clients packet
		@report: Report object - used to instantiate each clients report
		"""
		threading.Thread.__init__(self)
		self._server = server
		self._log = log
		self._toolchain_def = toolchain_def
		self._landmark_def = landmark_def
		self._processor_def = processor_def
		self._client_def = client_def
		self._report_def = report_def
		self._packet_def = packet_def
		self._shutdown_flag = threading.Event()
		self._packet_queue = LifoQueue(100)
		self._client_registry = {}

		self._toolchain = self._toolchain_def(self, self._log, self.enqueue_client_outbox)
		if TOOCHAIN_ENABLE:
			self._toolchain.start()

		self._landmark_manager = self._landmark_def(self._server.db_manager.enqueue, self._log)
		if LANDMARK_ENABLE:
			self._landmark_manager.start()

		self._processor = self._processor_def(self._log)

		self._log.info("{}({}) starting.".format(self.name, self.ident))
		self._log.info(" - toolchain_class_def: {}".format(self._toolchain_def.__name__))
		self._log.info(" - client_class_def: {}".format(self._client_def.__name__))
		self._log.info(" - report_class_def: {}".format(self._report_def.__name__))
		self._log.info(" - packet_class_def: {}".format(self._packet_def.__name__))

	def publish_to_proc(self, id, report):
		if not PROC_FORWARDING_ENABLE:
			return

		self._processor.send(id, report)

	def enqueue_landmark_proc(self, loc):
		"""
		@property loc - tuple - (mobile_id, (lat, long))
		"""
		self._landmark_manager.enqueue_loc(loc)

	def server_sendto(self, payload):
		"""
		Function used for enqueueing packets to be sent using the servers socket.
		@packet = packet.payload - formatted tuple (packet, destination)
		destination = (ip, port) *pack in tuple
		"""
		(_packet, _destination) = payload
		self._server.socket.sendto(_packet, _destination)
		self._log.debug("client_manager: payload sent!")

	def enqueue_db_report(self, db_report):
		"""
		function used for enqueueing reports and other objects specific to a devices dbManager class
		@db_report - formatted tuple - (report, etc... )
		ex. CalAmp - db_report - (report, state)
		"""
		self._server.db_manager.enqueue_db_report(db_report)

	def enqueue_client_outbox(self, packet):
		"""function used for enqueueing a packet to its outbox.
		@packet - the packet from the toolchain server
		NOTE: the packet must be configured to request an ack back from the device"""
		_packet = self._packet_def(*packet)
		_report = self._report_def(self._log, _packet)

		client = self._register_client(_report.id)
		client.outbox_enqueue(packet[0])

	def client_lookup(self, client_id):
		client = self._client_registry.get(client_id)
		return client

	def enqueue_packet(self, packet):
		self._packet_queue.put(packet)

	def _packet_handler(self, packet):
		_packet = self._packet_def(*packet)
		_report = self._report_def(self._log, _packet)

		client = self._register_client(_report.id)
		client.inbox_enqueue(_report)

	def run(self):
		self._log.info("{}({}) started.".format(self.name, self.ident))

		while True:
			time.sleep(THREAD_POLLING)
			if self._shutdown_flag.is_set() and self._packet_queue.qsize() == 0:
				self._log.info("{}({}) Shutdown Complete".format(self.name, self.ident))
				break

			while self._packet_queue.qsize() > 0:
				try:
					packet = self._packet_queue.get()
					self._packet_handler(packet)
					self._packet_queue.task_done()

				except Exception as e:
					self._log.error("{}({}): {}".format(self.name, self.ident, e))
					self._packet_queue.task_done()
					# traceback.print_exc()

		self._toolchain.join()
		self._join_clients()
		self._landmark_manager.join()

	def _register_client(self, client_id):
		""" add client to registry if not already registered. """
		client = self.client_lookup(client_id)
		if (client == None):
			client = self._client_def(self, self._log, client_id)
			self._client_registry[client_id] = client
			client.start()
			self._log.debug("client: {} registered.".format(client.id))
		return client

	def _unregister_client(self, client_id):
		self._client_registry.pop(client_id)

	def _shutdown_clients(self):
		for client_id in self._client_registry:
			self._client_registry[client_id].shutdown()

	def _join_clients(self):
		for client_id in self._client_registry:
			self._client_registry[client_id].join()

	def shutdown(self):
		self._log.info("{}({}) Shutdown Initiated...".format(self.name, self.ident))
		self._shutdown_flag.set()
		self._packet_queue.join()
		self._toolchain.shutdown()
		self._shutdown_clients()
		self._landmark_manager.shutdown()


	@property
	def name(self):
		return type(self).__name__
	@property
	def is_shutdown(self):
		return self._shutdown_flag.is_set()
	@property
	def clients(self):
		return len(self._client_registry)

class OutboxHandler(threading.Thread):
	"""this class handles outbox messages enqueued by the client or client manager from the toolchain listener"""
	def __init__(self, client, log, id, outbox_handler):
		"""
		@client - A reference to the Client instance
		@log - the log instance
		@id - The id of the client
		@outbox_handler - a function handler - function(packet) - handles the packet that is sent back to the device
		"""
		threading.Thread.__init__(self)
		self._client = client
		self._log = log
		self._id = id
		self._outbox_handler = outbox_handler
		self._backlog_queue = Queue()
		self._queue = Queue()
		self._shutdown_flag = threading.Event()

	def _enqueue_backlog(self, packet):
		self._backlog_queue.put(packet)
		self._log.debug("client: {} outbox: size {} backlog: size: {}".format(self._id, self._queue.qsize(), self._backlog_queue.qsize()))

	def _backfill_backlog(self):
		while self._queue.qsize() > 0:
			(_packet, _old_destination) = self._queue.get()
			self._enqueue_backlog(_packet)

		self._log.info("client: {} outbox: size: {} backlog_size: {} timeout -> backfilling backlog".format(self._id, self._queue.qsize(), self._backlog_queue.qsize()))

	def proc_backlog(self, destination):
		"""calls internal proc for backlog. attempts to process backlog of packets with an updated destination.
		@destination - (ip, port)
		"""
		if self._backlog_queue.qsize() == 0:
			return

		self._log.debug("client: {} backlog: putting backlog in main queue".format(self._id))
		while self._backlog_queue.qsize() > 0:
			packet = self._backlog_queue.get()
			self._queue.put((packet, destination))

	def enqueue(self, payload):
		"""
		@payload - tuple object - formatted (packet.payload, destination)
		destination - tuple object - formatted (ip, port) from the client
		the client fills the payload with the last known destination
		"""
		(_packet, destination) = payload
		self._queue.put(payload)
		self.proc_backlog(destination)

	def _client_report_timeout(self):
		if self._client.report == None:
			return True
		else:
			return self._client.report.is_timeout

	def run(self):
		self._log.info("client: {} {}({}) started.".format(self._id, self.name, self.ident))

		while True:
			time.sleep(THREAD_POLLING)
			if self._shutdown_flag.is_set() and self._queue.qsize() == 0:
				self._log.info("client: {} outbox: size: {} backlog_size: {} Shutdown Complete".format(self._id, self._queue.qsize(), self._backlog_queue.qsize()))
				break

			while self._queue.qsize() > 0:
				if self._client_report_timeout():
					self._log.debug("client: {} outbox: client report has timed out... putting packet in backlog".format(self._id))
					self._backfill_backlog()
					break

				payload = self._queue.get()
				self._log.debug("client: {} outbox: sending packet".format(self._id))
				self._log.info("client: {} outbox: size: {} backlog_size: {} sent outbox packet".format(self._id, self._queue.qsize(), self._backlog_queue.qsize()))
				"""send outbound message to server outbox"""
				self._outbox_handler(payload)

				"""wait for the client to receive an ack if it doesn't"""
				if ACKBACK_ENABLE:
					if not self._client.ackback.is_ack():
						self._log.debug("client: {} ackback: count: {}".format(self._id, self._client.ackback.count))
						(_packet, _old_destination) = payload
						self._enqueue_backlog(_packet)
						self._queue.task_done()
						self._backfill_backlog()
				else:
					self._queue.task_done()

			# if backlog is empty and queue is empty shutdown outbox
			# if (self._backlog_queue.qsize() == 0 and self._queue.qsize() == 0):
			# 	self.shutdown()

	def shutdown(self):
		self._log.info("client: {} outbox: {}({}) Shutdown Initiated...".format(self._id, self.name, self.ident))
		self._shutdown_flag.set()
		# self._queue.join()

	@property
	def name(self):
		return type(self).__name__
	@property
	def is_shutdown(self):
		return self._shutdown_flag.is_set()
