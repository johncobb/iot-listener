import pymysql
from pymysql.cursors import DictCursor
import sqlite3
import traceback
import threading 
import queue
import time
import typing
from functools import partial

from settings import PROC_DB_ENABLE
from settings import THREAD_POLLING
from settings import DB_PROVIDER
from settings import DB_NAME
from settings import DB_HOST
from settings import DB_PORT
from settings import DB_USER
from settings import DB_PASS
from settings import DatabaseProviders

class DatabaseWrapper():
	def __init__(self):
		self._log = None

	def set_logger(self, log):
		self._log = log

	@property
	def log(self):
		return self._log
	def connect(self):
		raise Exception("Sub-class must implement connect()")
	def exec_sql(self):
		raise Exception("Sub-class must implement exec_sql()")

class MySql(DatabaseWrapper):
	def __init__(self):
		DatabaseWrapper.__init__(self)

	def _connect(self):
		""" Connect to MySQL Database. """
		try:
			conn = pymysql.connect(
				host = DB_HOST,
				port = DB_PORT,
				user = DB_USER,
				password = DB_PASS,
				database = DB_NAME
			)
			conn.autocommit(True)
			return conn

		except pymysql.MySQLError as e:
			raise Exception(e)

		except Exception as e:
			self.log.error("dal: {} open connection: {}".format(DB_PROVIDER ,e))
			# traceback.print_exc()
			return None

	def exec_sql(self, sql):
		try:
			conn = self._connect()
			cursor = conn.cursor(DictCursor)
			if cursor is not None:
				with cursor as cur:
					cur.execute(sql)
					result = cur.fetchall()
					cur.close()
					return result

			else:
				self.log.error("dal: cursor is none!")

			conn.close()

		except pymysql.MySQLError as e:
			# traceback.print_exc()
			# traceback.print_stack()
			return None

		except Exception as e:
			# traceback.print_exc()
			self.log.error("dal: {} ERROR: {}".format(DB_PROVIDER, e))
			return None

class MySqlite(DatabaseWrapper):
	def __init__(self):
		self = DatabaseWrapper.__init__(self)

	def _connect(self):
		try:
			return sqlite3.connect(DB_NAME, isolation_level=None)
		except Exception as e:
			self.log.error("dal: {} open connection: {}".format(DB_PROVIDER, e))
			traceback.print_exc()
			return None

	def exec_sql(self, sql):
		try:
			conn = self._connect()
			cursor = conn.cursor()
			cursor.execute(sql)
		except Exception as e:
			self.log.error(e)
			traceback.print_exc()
			return None

class DatabaseFactory:
	def __init__(self, log):
		self._db_provider = DB_PROVIDER
		self._log = log
		self._db = None

		if (self._db_provider == None):
			self._log.error("dal: database provider not set!")
			return

		if (self._db == None):
			""" special case using sqlite3 """
			if (self._db_provider == DatabaseProviders.MySqlite):
				self._db = MySqlite()
			elif (self._db_provider == DatabaseProviders.MySql):
				self._db = MySql()
			else:
				return

			self._db.set_logger(self._log)
	@property
	def db(self):
		return self._db

class Database(DatabaseFactory, threading.Thread):
	def __init__(self, log):
		DatabaseFactory.__init__(self, log)
		threading.Thread.__init__(self)
		self._shutdown_flag = threading.Event()
		self._queue = queue.Queue()

	def enqueue(self, sql_call, callback_func=lambda x:None):
     
		if not PROC_DB_ENABLE:
			raise Exception("Database not enabled!")
		
		def callback(callback_func, response):
			try:
				callback_func(response)
			except Exception as e:
				self._log.error("dal: {}".format(e))
    
		cb = partial(callback, callback_func)

		self._queue.put((sql_call, cb))	# called like cb(response)


	def run(self):
		self._log.info("{}({}) started".format(self.name, self.ident))
		while True:
			time.sleep(THREAD_POLLING)
			if self._shutdown_flag.is_set() and self._queue.qsize() == 0:
				self._log.info("{}({}) Shutdown Complete".format(self.name, self.ident))
				break

			while (self._queue.qsize() > 0):
				try:
					(sql, cb) = self._queue.get()
					cb(self._db.exec_sql(sql))
					self._queue.task_done()
				except Exception as e:
					self._log.error("{}({}): {}".format(self.name, self.ident, e))
					self._queue.task_done()
					# traceback.print_exc()

	def shutdown(self):	
		self._log.info("{}({}) Shutdown Initiated...".format(self.name, self.ident))
		self._shutdown_flag.set()
		self._queue.join()
	
	@property
	def name(self):
		return type(self).__name__
	@property
	def log(self):
		return self._log


class DbManager(threading.Thread):
	def __init__(self, log, database=Database):
		threading.Thread.__init__(self)
		self._log = log
		self._db = database(self._log)
		self._shutdown_flag = threading.Event()
		self._queue = queue.Queue()

		self._log.info("{}({}) starting.".format(self.name, self.ident))
		self._log.info(" - db_provider: {}".format(DB_PROVIDER))
		self._log.info(" - db_class: {}".format(type(self._db).__name__))
		self._log.debug(" - db_name: {}".format(DB_NAME))
		self._log.debug(" - db_host: {}:{}".format(DB_HOST, DB_PORT))
		self._log.debug(" - db_user: {}".format(DB_USER))

		if PROC_DB_ENABLE:
			self._db.start()

	def enqueue(self, sql, callback=lambda x:None):
		self._db.enqueue(sql, callback)
		
	def enqueue_db_report(self, db_report: typing.Tuple):
		"""
		@db_report - formatted tuple - (report, state)
		"""
		self._queue.put(db_report)

	def run(self):
		self._log.info("{}({}) started".format(self.name, self.ident))
		while True:
			time.sleep(THREAD_POLLING)
			if self._shutdown_flag.is_set() and self._queue.qsize() == 0:
				self._log.info("{}({}) Shutdown Complete".format(self.name, self.ident))
				break

			while (self._queue.qsize() > 0):
				try:
					db_report = self._queue.get()
					self._handle_db(db_report)
					self._queue.task_done()

				except Exception as e:
					self._log.error("{}({}): {}".format(self.name, self.ident, e))
					self._queue.task_done()
					# traceback.print_exc()
     
		self._db.join()

	def shutdown(self):
		self._log.info("{}({}) Shutdown Initiated...".format(self.name, self.ident))
		self._shutdown_flag.set()
		self._queue.join()
		self._db.shutdown()
		
	@property
	def name(self):
		return type(self).__name__
	@property
	def log(self):
		return self._log