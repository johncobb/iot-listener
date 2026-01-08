import threading
import time
import json
import redis

from settings import REDIS_HOST
from settings import REDIS_PORT
from settings import REDIS_PASS
from settings import REDIS_CHANNEL


class ProcessorForwarder:
	def __init__(self, log=None, topic_prefix='default'):
		self._log = log
		self._topic_prefix = topic_prefix
		self._redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS)
        # self._log.info("{}: Service Started".format(self.name))

	def send(self, id, payload):
		"""publishes a clients report to redis under a channel with the devices
  			id as the channels name.

     		@param id - clients id (ex. 1234567890) - will look like this in redis -> redsky
       		@param payload - str - client payload"""
		self._redis.publish("{}.{}.{}".format(REDIS_CHANNEL, self._topic_prefix, id), payload)
		# self._log.debug("client: {} processor_forwarder: report published!".format(id))
		# self._log.info(payload)

	@property
	def name(self):
		return type(self).__name__

class CalampProcessorForwarder(ProcessorForwarder):
	def __init__(self, log, topic_prefix='calamp'):
		ProcessorForwarder.__init__(self, log, topic_prefix)

def proc_main():
    forward = ProcessorForwarder(None, 'blackbird')
