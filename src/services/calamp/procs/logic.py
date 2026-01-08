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

                """ register client """
                client = register_client(log, _client_registry, report.mobile_id)

                """ optional, uncomment if removed from proc/default.py """
                # client.adapter_handler(report)

                """ process odometer handler """
                client.odometer_handler(report)
                """ process message """
                client.proc_message(report)
                """ process state handler """
                client.state_handler(report.message.event_code)
                """ process adapter handler """

                """ process landmark handler """
                client.landmark_handler(report.message)


                # if (client.state.change):
                #     log.info("STATE-CHANGE-CLIENT client: {} state_change: {}({}) -> {}({})".format(message.mobile_id, client.state.prev.value, client.state.prev.name, client.state.current.value, client.state.current.name))


                """ always insert logs """
                db.exec_sql(Device.logs.insert(report))

                """ todo: create client manager to maintain and track previous state of device"""
                if (message.message_type == MessageTypes.EVENT_REPORT or message.message_type == MessageTypes.MINI_EVENT_REPORT):

                    """ refactor once DeviceOdometer depedencies are fixed """
                    odometer = 0
                    virtual_odometer = 0
                    engine_hours = 0
                    state = 0
                    last_state = 0
                    current_state = 0

                    db.exec_sql(Device.assets.insert(report, client.state.current))
                    # db.exec_sql(Device.telemetry.insert(report, odometer, virtual_odometer, engine_hours))
                    if (client.state.change):
                        db.exec_sql(Device.activitylog.insert(report, client.state.current))
                elif (message.message_type == MessageTypes.ID_REPORT):
                    db.exec_sql(Device.meta.insert(report))
                    db.exec_sql(Device.devices.insert(report))

                """ forward message for further processing. """
                redis_server.publish(redis_channel_pub, report.packet.package_json)
                redis_server.set("{}:{}".format(redis_channel_pub, report.mobile_id), report.packet.to_str)


                """ uncomment below to log message to console """
                _log_debug(report)

