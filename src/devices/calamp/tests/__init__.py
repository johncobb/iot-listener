
import sys
import logging

from settings import DB_PROVIDER

from devices.calamp.config import peg
from db import DatabaseProviders
from db import DatabaseFactory

EVENT_DIR_PREFIX = "EVENT"

class ServerFixture():
	def __init__(self, config_prefix, log):
		self._config_prefix = config_prefix
		self._event_def = EVENT_DIR_PREFIX
		self._log = log
		self._db_provider = DB_PROVIDER
		self._db = DatabaseFactory.get_database(DB_PROVIDER, self)

	@property
	def config_prefix(self):
		return self._config_prefix

	@property
	def log(self):
		return self._log

	@property
	def db(self):
		return self._db
	@property
	def conn(self):
		return self._conn
	@property
	def db_provider(self):
		return self._db_provider
	@property
	def event_def(self):
		return self._event_def

	def get_event_def(self, event_code, *names):
		result = False
		for name in names:
			if event_code == getattr(peg,"{}_{}".format(self.event_def, name)):
				result = True
		return result
	
