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

from services.calamp.procs import CalampPacket
from services.calamp.procs import CalampReport
from services.calamp.procs.ack import send_ack
from services.calamp.procs import message_to_hex

from devices.calamp import MessageTypes
from devices.calamp.config import CalampEvents
from devices.calamp.logic.adapter import DeviceAdapters
from devices.calamp.adapters.blackbird import BlackbirdMessage

from settings import PROC_FORWARDING_ENABLE
from settings import PROC_ADAPTER_ENABLE

from settings import BB_HOST
from settings import BB_PORT

from settings import DB_PROVIDER
from settings import DB_NAME
from settings import DB_HOST
from settings import DB_PORT
from settings import DB_USER
from settings import DB_PASS
from db import DatabaseFactory

from db.calamp.connection import Device

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

""" publish outbound message to channel(s) """
REDIS_PUB_CHANNEL   = os.getenv('REDIS_PUB_CHANNEL')
REDIS_PUB_CHANNEL_DB   = os.getenv('REDIS_PUB_CHANNEL_DB')

def _log(report):
    print("({}:{}): {}".format(report.packet.ip, report.packet.port, report.packet.payload))
    print(" - id: {}".format(report.id))
    print(" - timestamp: {}".format(report.packet.timestamp))
    print(" - message_header: {}".format(report.message.message_header))
    print(" - name: {}".format(report.name))
    print(" - ver: {}".format(report.ver))
    print(" - id: {}".format(report.id))
    print(" - mobile_id: {}".format(report.mobile_id))
    print(" - lat: {}".format(report.message.loc.latitude))
    print(" - lng: {}".format(report.message.loc.longitude))
    print(" - heading: {}".format(report.message.loc.heading))
    print(" - alt: {}".format(report.message.loc.altitude))
    print(" - speed: {}".format(report.message.loc.speed))


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


from devices.calamp.logic import DeviceStates
def proc_main():

    db = DatabaseFactory(None).db

    """ connect to redis """
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    """ register with pubsub """
    p = r.pubsub()

    """ calculate channnel path """
    redis_path = "{}".format(REDIS_CHANNEL)

    """ subscribe to channel """
    p.subscribe(redis_path)

    """ forward message for further processing. """
    redis_pub = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

    """ loop duh... """
    while True:
        """ listen for data """
        for buffer in p.listen():
            print(buffer)
            """ do we have a message? """
            if buffer['type'] == 'message':
                data = buffer['data']
                """ parse received message """
                report = parse_message(data)

                """ sanity check """
                if (report == None):
                    return

                message = report.message

                """ always insert logs """
                db.exec_sql(Device.logs.insert(report))

                """ todo: this logic is not currently working (placeholder) """
                if (message.message_type == MessageTypes.EVENT_REPORT or message.message_type == MessageTypes.MINI_EVENT_REPORT):
                    state_change = False
                    odometer = 0
                    virtual_odometer = 0
                    engine_hours = 0
                    state = 0
                    last_state = 0
                    current_state = 0

                    db.exec_sql(Device.assets.insert(report, DeviceStates.UNKNOWN))
                    db.exec_sql(Device.telemetry.insert(report, odometer, virtual_odometer, engine_hours))
                    if (state_change):
                        db.exec_sql(Device.activitylog.insert(report, last_state, current_state))
                elif (message.message_type == MessageTypes.ID_REPORT):
                    db.exec_sql(Device.meta.insert(report))
                    db.exec_sql(Device.devices.insert(report))


                """ uncomment below to pass into redis. """
                redis_pub.set("{}:{}".format(REDIS_PUB_CHANNEL, report.mobile_id), report.packet.to_str)

                """ uncomment below to log message to console """
                _log(report)

