import os
import struct
import socket
import redis
import socket
import binascii
import time
import datetime
import json
import traceback
import logging
from logging.handlers import RotatingFileHandler

from services.calamp.procs import CalampPacket
from services.calamp.procs import CalampReport
from services.calamp.procs import CalampClient
from services.calamp.procs.ack import send_ack
from services.calamp.procs import message_to_hex

from devices.calamp import MessageTypes
from devices.calamp.config import CalampEvents
from devices.calamp.logic.adapter import DeviceAdapters
from devices.calamp.adapters.blackbird import BlackbirdMessage


# from settings import PROC_FORWARDING_ENABLE

""" enable forwarding to adapters (Blackbird) """
from settings import PROC_ADAPTER_ENABLE
""" blackbird host:port """
from settings import BB_HOST
from settings import BB_PORT

""" database """
from settings import DB_PROVIDER
from settings import DB_NAME
from settings import DB_HOST
from settings import DB_PORT
from settings import DB_USER
from settings import DB_PASS

""" logging """
from settings import LOG_FORMAT
from settings import LOG_MAXBYTES
from settings import LOG_BACKUPS
from settings import LOG_LEVEL
from settings import LOG_FILE

""" client dwell time determins how long we keep clients in registry """
from settings import CLIENT_DWELL_TIME


from devices.calamp.logic import DeviceStates
from devices.calamp.logic.acknowledgement import DeviceAcknowledgement
from devices.calamp.logic.states import DeviceState
from devices.calamp.logic import DeviceStates

from devices.calamp.logic.landmark import LandmarksProcessor

from db import DatabaseFactory
from db.calamp.connection import Device

""" used to manage clients (state/management) """
from services.calamp.procs import register_client
_client_registry = {}


logging.basicConfig(format=LOG_FORMAT)
formatter = logging.Formatter(LOG_FORMAT)
log_handler = RotatingFileHandler(LOG_FILE, maxBytes=LOG_MAXBYTES, backupCount=LOG_BACKUPS)
log_handler.setFormatter(formatter)
log = logging.getLogger('calamp')
log.addHandler(log_handler)
log.setLevel(LOG_LEVEL)

# ===============
# USAGE
# ===============
# . bin/launcher.sh
# . bin/proc_redis.sh
# . bin/calamp_test_client --host localhost --port 20500 data/id_report.dat

# ===============
# REF
# ===============
# https://pypi.org/project/redis/4.0.2/
# https://funprojects.blog/2018/10/18/redis-for-iot/

# ======================================================================================================================
# REDIS
# ======================================================================================================================
REDIS_HOST      = os.getenv('REDIS_HOST')
REDIS_PORT      = int(os.getenv('REDIS_PORT', 0))
REDIS_DB        = os.getenv('REDIS_DB')
REDIS_CHANNEL   = os.getenv('REDIS_CHANNEL')

REDIS_CHANNEL   = os.getenv('REDIS_CHANNEL')
REDIS_CHANNEL_PUB   = os.getenv('REDIS_CHANNEL_PUB')

""" publish outbound message to channel(s) """
# REDIS_PUB_CHANNEL   = os.getenv('REDIS_PUB_CHANNEL')
# REDIS_PUB_CHANNEL_DB   = os.getenv('REDIS_PUB_CHANNEL_DB')


def _log_debug(report):
    log.debug("({}:{}): {}".format(report.packet.ip, report.packet.port, report.packet.payload))
    log.debug(" - id: {}".format(report.id))
    log.debug(" - timestamp: {}".format(report.packet.timestamp))
    log.debug(" - message_header: {}".format(report.message.message_header))
    log.debug(" - name: {}".format(report.name))
    log.debug(" - ver: {}".format(report.ver))
    log.debug(" - id: {}".format(report.id))
    log.debug(" - mobile_id: {}".format(report.mobile_id))
    log.debug(" - lat: {}".format(report.message.loc.latitude))
    log.debug(" - lng: {}".format(report.message.loc.longitude))
    log.debug(" - heading: {}".format(report.message.loc.heading))
    log.debug(" - alt: {}".format(report.message.loc.altitude))
    log.debug(" - speed: {}".format(report.message.loc.speed))


def parse_message(data):
    report = None
    if (isinstance(data, str)):
        """ convert the data to json """
        json_data = json.loads(data)
        """ assign ip """
        ip = json_data["source"]["address"]
        """ assign port """
        port = json_data["source"]["port"]
        """ assign payload """
        payload = json_data["payload"]
        """ convert the hex payload to binary """
        payload_bytes = bytes.fromhex(payload)
        """ parse packet """
        packet = CalampPacket(payload_bytes, (ip, port))
        """ parse report """
        report = CalampReport(packet)

    """ return the report """
    return report


def proc_main():
    """ todo: odometer logic """
    # _odometer = DeviceOdometer(self._state)

    db = DatabaseFactory(None).db

    """ *** landmark processing code *** """
    proc_landmark = LandmarksProcessor(log)

    landmarks  = db.exec_sql(Device.landmarks.lookup_all())

    # proc_landmark.load_landmarks(landmarks)
    """ *** landmark processing code *** """

    """ connect to redis """
    redis_server = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    """ register with pubsub """
    p = redis_server.pubsub()

    """ calculate channnel path """
    redis_channel_sub = "{}".format(REDIS_CHANNEL)
    redis_channel_pub = "{}".format(REDIS_CHANNEL_PUB)


    """ subscribe to channel """
    p.subscribe(redis_channel_sub)


    log.info(" redis connection establised: ({}:{})".format(REDIS_HOST, REDIS_PORT))
    log.info(" - channel sub: {}".format(redis_channel_sub))
    log.info(" - channel pub: {}".format(redis_channel_pub))

    """ loop duh... """
    while True:
        """ listen for data """
        for buffer in p.listen():
            log.debug(buffer)
            """ do we have a message? """
            if buffer['type'] == 'message':
                data = buffer['data']
                """ parse received message """
                report = parse_message(data)

                """ sanity check """
                if (report == None):
                    return

                message = report.message

                # proc_landmark.is_landmark(1, (message.loc.latitude, message.loc.longitude))

                """ register client """
                client = register_client(log, _client_registry, report.mobile_id)



                """ always insert logs """
                # db.exec_sql(Device.logs.insert(report))

                """ forward message for further processing. """
                redis_server.publish(redis_channel_pub, report.packet.package_json)
                redis_server.set("{}:{}".format(redis_channel_pub, report.mobile_id), report.packet.to_str)


                """ uncomment below to log message to console """
                _log_debug(report)




import time
import traceback
from queue import Queue
from typing import Any
from pyproj import CRS
from pyproj import Transformer
from shapely.geometry import Point
from shapely.ops import transform
from shapely import from_geojson
from shapely import to_geojson

import urllib.parse

from settings import THREAD_POLLING
from settings import PROXIMITY_PRECISION



class LandmarkProcessor():
	"""
	a landmark worker (an account worker) is an clients account that is over all of its device/assets
	"""
	def __init__(self, log, id, db_write_handler):
		self._log = log
		# self._db_handler = db_write_handler
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
		# self._db_handler(GET_LANDMARKS.format(self.id), self._landmark_data_handler)
		rs_landmarks = db.exec_sql(GET_LANDMARKS.format(self.id))

	def landmark_handler(self, loc):
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

		""" main landmark processing routine"""

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


