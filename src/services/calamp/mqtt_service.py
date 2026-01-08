
import time
import signal
import socket

from queue import Queue
from enum import Enum
from src.lib import IoThread
from src.services.calamp import IoEventTypes
from src.services.calamp import IoEvent
from src.services.calamp import IoEventData
from src.services.calamp import CalampClient
from src.services.calamp import Ack
from src.services.calamp import Job

class CalampMqttServer(IoThread):
	def __init__(self, mqtt_thread):
		self._mqtt_thread = mqtt_thread
		self._event_queue = Queue(100)
		self._db_ack_queue = Queue(100)
		self._client_index = 0
		self._clients = {}

		""" stub out local connectivity calls """
		self.on_connect = self.callback_mqtt_onconnect
		self.on_disconnect = self.callback_mqtt_ondisconnect
		self.on_data = self.callback_mqtt_ondata
		self.on_ack = self.callback_mqtt_onack
		IoThread.__init__(self, None)

	@property	
	def mqtt_thread(self):
		return self._mqtt_thread
	@property
	def event_queue(self):
		return self._event_queue
	@property
	def db_ack_queue(self):
		return self._db_ack_queue
	@property
	def client_index(self):
		return self._client_index
	@property	
	def clients(self):
		return self._clients

	def thread_handler(self):
		self.exec()

	def enqueue(self, data):
		self.event_queue.put(data)
	
	def enqueue_db_ack(self, ack):
		self.db_ack_queue.put(ack)

	def callback_mqtt_onconnect(self, data):
		event = IoEvent(IoEventTypes.ON_CONNECT, data)
		self.enqueue(event)

	def callback_mqtt_ondisconnect(self, data):
		event = IoEvent(IoEventTypes.ON_DISCONNECT, data)
		self.enqueue(event)

	def callback_mqtt_ondata(self, data):
		event = IoEvent(IoEventTypes.ON_DATA, data)
		self.enqueue(event)

	def callback_mqtt_onack(self, data):
		event = IoEvent(IoEventTypes.ON_ACK, data)
		self.enqueue(event)

	def db_load_printers(self):
		self.printers = None

	def __client_lookup(self, key):
		return self.clients.get(key)

	def proc_event(self, event):
		if (event.event_type == IoEventTypes.ON_CONNECT):
			iodata = event.event_data
			client_id = iodata.id
			client = self._client_lookup(client_id)
			if (client == None):
				client = CalampClient(client_id)
				self._clients[client_id] = client

			print("client on_connect: {} timestamp: {}".format(client.client_id, client.last_update))
			return

		if (event.event_type == IoEventTypes.ON_DISCONNECT):
			iodata = event.event_data
			client_id = iodata.id
			client = self._client_lookup(client_id)
			if (client is not None):
				self._clients.pop(client.client_id)
				print("client on_disconnect: {} timestamp: {}".format(client.client_id, client.last_update))

			print("clients: {}".format(len(self.clients)))
			return

		if (event.event_type == IoEventTypes.ON_DATA):
			job = event.event_data
			print("on_data: job: {} client_id: {} data: {}".format(job.job_id, job.client_id, job.data))

			# """ lookup client """
			client = self._client_lookup(job.client_id)
			# """ add client to list if not found (this scenario could possibly play out if we miss a disconnect) """
			if (client is None):
				client = Printer(job.client_id)
				self._clients[job.client_id] = client

			client.enqueue(event.event_data)

		if (event.event_type == IoEventTypes.ON_ACK):
			ack = event.event_data
			client = self._client_lookup(ack.client_id)
			if (client is None):
				client = Printer(ack.client_id)
				self._clients[ack.client_id] = client
			print("on_ack: client_id: {} job_id: {} data: {} jobs:".format(ack.client_id, ack.job_id, client.letter_queue.qsize()))
			client.pending_job = None
			""" add to db queue so we can update record in database """
			self.enqueue_db_ack(ack)

	def proc_event_queue(self):
		if (self.event_queue.qsize() > 0):
			event = self.event_queue.get(True)
			self.event_queue.task_done()
			self.proc_event(event)
	
	def proc_db_queue(self):
		""" todo: query database and enqueue jobs to printer(s) """

		if (self.db_ack_queue.qsize() > 0):
			ack = self.db_ack_queue.get(True)
			""" todo: update table """
			print("db_ack_queue: {} len: {}".format(ack.job_id, self.db_ack_queue.qsize()))


	""" iterate one client at a time per current client_index """
	def proc_client_jobs2(self):
		""" no clients connected. """
		if (len(self.clients) == 0):
			return
		if (self.client_index == len(self.clients)):
			self._client_index = 0

		""" lookup by client_index """	
		client = self.clients.get(list(self.clients)[self.client_index])
		if (client.pending_job is None):
			if (client.letter_queue.qsize() > 0):
				job  = client.letter_queue.get(True)
				client.pending_job = job
				self.mqtt_thread.enqueue(job)

		self._client_index += 1

	""" iterate through all client connections """
	def proc_client_jobs(self):
		for key in self.clients:
			client = self.clients.get(key)
			if (client.pending_job is None):
				if (client.letter_queue.qsize() > 0):
					job  = client.letter_queue.get(True)
					client.pending_job = job
					print("proc_client_jobs: client_id: {} job_id: {} data: {}".format(client.client_id, job.job_id, job.data))
					self.mqtt_thread.enqueue_outbox(job)


	def exec(self):
		while(self.shutdown_flag == False):
			""" process database queue """
			self.proc_db_queue()
			""" process queued jobs for each printer"""
			self.proc_client_jobs()
			# self.proc_client_jobs_2()
			""" handle any queued events """
			self.proc_event_queue()
			time.sleep(.025)

		self.shutdown = True

def main():

	calamp_server = CalampMqttServer()
	calamp_server.start_thread()
	x = False
	y = False
	z = False
	try:
		""" step 1: on_connect """
		calamp_server.on_connect(IoEventData("0001", time.time_ns()))
		calamp_server.on_connect(IoEventData("0002", time.time_ns()))
		calamp_server.on_connect(IoEventData("0003", time.time_ns()))

		while(calamp_server.running):

			""" step 4: on_disconnect """
			if (x == True):
				if (y == True):
					if (z == False):
						""" simulate on disconnect """
						calamp_server.on_disconnect(IoEventData("0001", time.time_ns()))
						calamp_server.on_disconnect(IoEventData("0002", time.time_ns()))
						calamp_server.on_disconnect(IoEventData("0003", time.time_ns()))
						
						z = True

			""" step 3: on_ack """
			if (x == True):
				if (y == False):
					""" simulate on disconnect """
					calamp_server.on_ack(Ack("0001", "1623685896732643000"))
					calamp_server.on_ack(Ack("0002", "1623685896759101000"))
					calamp_server.on_ack(Ack("0003", "1623685896785119000"))

					y = True

			""" step 2: on_data """
			if (x == False):
				""" simulate on data """
				calamp_server.on_data(Job("1623685896732643000", "0001", "zpl_data: xyz"))
				calamp_server.on_data(Job("1623685896759101000", "0002", "zpl_data: xyz"))
				calamp_server.on_data(Job("1623685896785119000", "0003", "zpl_data: xyz"))
				x = True


			time.sleep(1)
	except KeyboardInterrupt as ki:
		calamp_server.shutdown_thread()

if __name__ == "__main__":
	main()