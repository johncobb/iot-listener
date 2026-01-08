import threading
import time
import traceback
from queue import Queue
from typing import Any
from pyproj import CRS
# from pyproj import Proj
# from pyproj import transform as Transfrom
from pyproj import Transformer
from shapely.geometry import Point
from shapely.ops import transform
from shapely import from_geojson
from shapely import to_geojson

import urllib.parse

from settings import THREAD_POLLING
from settings import PROXIMITY_PRECISION

class LandmarkWorker(threading.Thread):
	"""
	a landmark worker (an account worker) is an clients account that is over all of its device/assets
	"""
	def __init__(self, log, id, db_write_handler):
		self._log = log
		threading.Thread.__init__(self)
		self._shutdown_flag = threading.Event()
		self._init = threading.Event()
		self._running = threading.Event()
		self._device_queue = Queue()	# loc - (mobile_id, (lat, long))
		self._db_handler = db_write_handler
		self._id = id	# an accounts id
		self._landmark_registry = {}
		self._landmark_cache = {}	# {LandmarkId: [MobileId, MobileId, ...], LandmarkId: [...], ...}

		# on init load all accounts landmarks
		self._load_landmark_registry()

	def _loc2poly(self, lat, lon, radius_m):
		# Takes a location and radius to construct a circle with a radius in a computable coordinate system
		proj4str = '+proj=aeqd +lat_0=%s +lon_0=%s +x_0=0 +y_0=0' % (lat, lon)
		transformer = Transformer.from_crs(CRS.from_proj4(proj4str), CRS.from_authority('epsg', 4326), always_xy=True)
		return transform(transformer.transform, Point(0, 0).buffer(radius_m))

	def _geom2poly(self, geom):
		# converts a geojson to a shapely geometry
		return from_geojson(geom)

	def _landmark_data_handler(self, landmarks):
		# called by database manager in its callback
		for landmark in landmarks:
			# store a polygon in the landmark dict to test with later
			if landmark['GeoFence'] != None:
				self._landmark_registry[landmark['RecordId']] = self._geom2poly(landmark['GeoFence'])
			else:
				self._landmark_registry[landmark['RecordId']] = self._loc2poly(landmark['Latitude'], landmark['Longitude'], landmark['TriggerProximity'])
		self._init.set()	# set init event because landmarks where loaded
  
	def _load_landmark_registry(self):
		"""
		@property db_object - dict - The dict object from the the landmarks db entry
		"""
		GET_LANDMARKS = "SELECT RecordId, Label, ST_AsGeoJSON(GeoFence) as GeoFence, Latitude, Longitude, TriggerProximity, TriggerParkRequired FROM Landmarks WHERE AccountId = '{}' AND Archived = 0;"
		
		# enqueue a db call to get all of an accounts landmarks and passed a data handler to get the data back from the db
		self._db_handler(GET_LANDMARKS.format(self.id), self._landmark_data_handler)
			
	def _worker_task(self, loc):
		"""
		the worker task processes each devices location and updates the landmark activity
		feed in the database
		@property loc - tuple - (mobile_id, (lat, long))
		"""
		mobile_id = loc[0]
		latitude = loc[1][0]
		longitude = loc[1][1]
	
		test_poly = self._loc2poly(latitude, longitude, PROXIMITY_PRECISION)

		def device_arrived(_landmark_id, _proximity):
			self._landmark_cache.setdefault(_landmark_id, []).append(mobile_id)
			INSERT_LANDMARK_ACTIVITY = """INSERT INTO LandmarkActivity (LandmarkId, MobileId, ArrivalTime, DepartureTime, Proximity, StartLatitude, StartLongitude) 
											VALUES ({}, '{}', UTC_TIMESTAMP(3), FROM_UNIXTIME(1), {}, {}, {}); """	# no odometer
			
			self._db_handler(INSERT_LANDMARK_ACTIVITY.format(_landmark_id, mobile_id, _proximity, latitude, longitude))

		def device_departed(_landmark_id):
			self._landmark_cache[_landmark_id].remove(mobile_id)
			UPDATE_LANDMARK_ACTIVITY = """UPDATE LandmarkActivity SET DepartureTime = UTC_TIMESTAMP(3), EndLatitude = {}, EndLongitude = {} WHERE LandmarkId = {} AND MobileId = '{}' AND DepartureTime = FROM_UNIXTIME(1) """

			self._db_handler(UPDATE_LANDMARK_ACTIVITY.format(latitude, longitude, _landmark_id, mobile_id))
   
		""" Main Worker Routine"""
  
		# for each landmark in the registry test if the current location (loc) meets any of the states conditions
		for landmark_id, landmark_poly in self._landmark_registry.items():
      
			# if the geometries interact that means the location is in the landmark
			is_there = test_poly.intersects(landmark_poly)
   
			# if the mobile_ids location has been inside a landmark it may have departed
			has_been_there = mobile_id in self._landmark_cache[landmark_id] if landmark_id in self._landmark_cache else False 

			if not is_there and not has_been_there:
				continue
			if not is_there and has_been_there:
				device_departed(landmark_id)
				self._log.info("landmark: client: {} departed: {}".format(mobile_id, landmark_id))
				# self._log.debug("landmark: device: {} landmark_map: {}".format(mobile_id, "http://geojson.io/#data=data:application/json," + urllib.parse.quote(to_geojson(test_poly.union(landmark_poly)))))
			if is_there and not has_been_there:
				# the device arrives and we calculate the distance between both geometries
				device_arrived(landmark_id, test_poly.distance(landmark_poly.centroid))
				self._log.info("landmark: client: {} arrived: {}".format(mobile_id, landmark_id))
			if is_there and has_been_there:
				continue
	
	def enqueue(self, loc):
		self._device_queue.put(loc)

	def run(self):
		self._running.set()
		self._log.info("{}({}) started.".format(self.name, self.ident))

		# if landmarks are not loaded wait until they are
		# while self._init.wait():
		# 	self._log.warning("landmark_manager: account_worker: {} waiting for database to register landmarks!")
		# 	if not self._init.is_set():
		# 		time.sleep(.5)

		while True:
			time.sleep(THREAD_POLLING)
			if self._shutdown_flag.is_set() and self._device_queue.qsize() == 0:
				self._log.info("{}({}) Shutdown Complete".format(self.name, self.ident))
				break

			while (self._device_queue.qsize() > 0):
				try:
					loc = self._device_queue.get()
					self._worker_task(loc)
					self._device_queue.task_done()
				except Exception as e:
					self._log.error("{}({}): {}".format(self.name, self.ident, e))
					self._device_queue.task_done()
					# traceback.print_exc()

	def shutdown(self):
		self._log.info("{}({}) Shutdown Initiated...".format(self.name, self.ident))
		self._shutdown_flag.set()
		self._device_queue.join()

	@property
	def name(self):
		return type(self).__name__
	@property
	def is_running(self):
		return self._running.is_set()
	@property
	def is_shutdown(self):
		return self._shutdown_flag.is_set()
	@property
	def id(self):
		return self._id
	
class LandmarkManager(threading.Thread):
	"""
	Landmark manager is responsible for dispatching a devices location to
	each worker for each account. A future feature would be a scalable account
	workers.

	The client manager has a handler that each client can use to dispatch its location
	to this manager.

	TODO: Make a processor to handle a clients metadata like this, 
	make this solution more scalable to support more devices without degradation.

	"""
	def __init__(self, db_enqueue, log):
		threading.Thread.__init__(self)
		self._log = log
		self._init = threading.Event()
		self._shutdown_flag = threading.Event()
		self._loc_queue = Queue()

		self._db_enqueue = db_enqueue
		self._worker_registry = {}
		self._device_cache = {}		# {MobileId:AccountId, MobileId:AccountId}

		# on service init load the accounts
		try:
			self._load_accounts()
		except Exception as e:
			self._log.warning("landmark: account: Accounts not loaded encountered exception: {}!".format(e))
   
	def add_account(self, account_id):
		# called by API
		self._worker_registry[account_id] = LandmarkWorker(self._log, account_id, self._db_enqueue)
		self._log.debug("landmark: account: {} added".format(account_id))
		self._load_account_devices(account_id)

	def delete_account(self, account_id):
		self._worker_registry.pop(account_id)
	
	def _account_data_handler(self, accounts):
		# called by database
		for account in accounts:
			self.add_account(account['RecordId'])
		
		self._init.set()

	def _device_data_handler(self, devices):
		if devices == ():
			return
		for device in devices:
			self._log.debug("landmark: account: {} loading device: {}".format(device['AccountId'], device['MobileId']))
			self._device_cache[device['MobileId']] = device['AccountId']

	def _asset_data_handler(self, asset):
		self._device_cache[asset['MobileId']] = asset['AccountId']

	def _load_accounts(self):
		GET_ACCOUNTS = "SELECT RecordId FROM Accounts WHERE Archived = 0;"
		self._db_enqueue(GET_ACCOUNTS, self._account_data_handler)

	def _load_account_devices(self, account_id):
		GET_DEVICES = "SELECT MobileId, AccountId FROM Devices WHERE AccountId = {} AND Archived = 0"
		self._db_enqueue(GET_DEVICES.format(account_id), self._device_data_handler)

	def _task_handler(self, loc):
		# do run task
		mobile_id = loc[0]
		for (_mobile_id, _account_id) in self._device_cache.items():
			if mobile_id == _mobile_id:
				worker = self._worker_registry[_account_id]
				if not worker.is_alive():
					worker.start()

				worker.enqueue(loc)

	def enqueue_loc(self, loc):
		self._loc_queue.put(loc)

	def run(self):
		self._log.info("{}({}) started.".format(self.name, self.ident))

		# if landmarks are not loaded wait until they are
		# if self._init.is_set():
		# 	self._log.info("landmark_manager: waiting for database to register accounts!")
		# 	self._init.wait()

		while True:
			time.sleep(THREAD_POLLING)
			if self._shutdown_flag.is_set() and self._loc_queue.qsize() == 0:
				self._log.info("{}({}) Shutdown Complete".format(self.name, self.ident))
				break

			while (self._loc_queue.qsize() > 0):
				try:
					loc = self._loc_queue.get()
					self._task_handler(loc)
					self._loc_queue.task_done()
				except Exception as e:
					self._log.error("{}({}): {}".format(self.name, self.ident, e))
					self._loc_queue.task_done()
					# traceback.print_exc()

		self._join_workers()

	def _shutdown_workers(self):
		for (id, worker) in self._worker_registry.items():
			if worker.is_alive():
				worker.shutdown()
   
	def _join_workers(self):
		for (id, worker) in self._worker_registry.items():
			if worker.is_alive():
				worker.join()
   
	def shutdown(self):
		self._log.info("{}({}) Shutdown Initiated...".format(self.name, self.ident))
		self._shutdown_flag.set()
		self._loc_queue.join()
		self._shutdown_workers()

	@property
	def name(self):
		return type(self).__name__
	@property
	def is_shutdown(self):
		return self._shutdown_flag.is_set()