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

""" logging """
from settings import LOG_FORMAT
from settings import LOG_MAXBYTES
from settings import LOG_BACKUPS
from settings import LOG_LEVEL
from settings import LOG_FILE

from settings import THREAD_POLLING

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
REDIS_CHANNEL_PUB   = os.getenv('REDIS_CHANNEL_PUB')


""" publish outbound message to channel(s) """
# REDIS_PUB_CHANNEL   = os.getenv('REDIS_PUB_CHANNEL')
# REDIS_PUB_CHANNEL_DB   = os.getenv('REDIS_PUB_CHANNEL_DB')

def forwarding(host, port, packet):
    log.info("proc_forwarding_enable: {}".format(PROC_FORWARDING_ENABLE))

    if not PROC_FORWARDING_ENABLE:
        return

    # socket_forward = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # scoket_forward.sendto(bytes(packet, encoding="utf-8"), (host, port))
    """
    Function used for enqueueing packets to be sent using the servers socket.
    @packet = packet.payload - formatted tuple (packet, destination)
    destination = (ip, port) *pack in tuple
    """
    # (_packet, _destination) = payload
    # self._server.socket.sendto(_packet, _destination)


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

def proc_toolchain(redis_server, mobile_id):
    for mobile_id in _client_registry:
        _client = _client_registry[mobile_id]
        # print(_client)
        # print("{}:{}".format(_client.packet.ip, _client.packet.port))
        print("proc_toolchain mobile_id: {}".format(mobile_id))

    return
    """ check for queued toochain messages """
    packet = redis_server.lrange(mobile_id, -1, -1)

    log.info("queue:peek mobile_id: {} packet: {}".format(mobile_id, packet))

    if (len(packet) > 0):
        data = redis_server.rpop(mobile_id)
        log.info("queue:pop {} mobile_id: {} data: {}".format(mobile_id, packet))

def proc_main():

    """ connect to redis """
    redis_server = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    """ register with pubsub """
    p = redis_server.pubsub()

    """ calculate channnel path """
    redis_channel_sub = "{}".format(REDIS_CHANNEL)
    redis_channel_pub = "{}".format(REDIS_CHANNEL_PUB)
    # redis_channel_client_cache = "{}".format(REDIS_CHANNEL_CLIENT_CACHE)

    """ subscribe to channel """
    p.subscribe(redis_channel_sub)


    log.info(" redis connection establised: ({}:{})".format(REDIS_HOST, REDIS_PORT))
    log.info(" - channel sub: {}".format(redis_channel_sub))
    log.info(" - channel pub: {}".format(redis_channel_pub))
    log.info(" - thread polling: {}".format(THREAD_POLLING))

    """ loop duh... """
    while True:
        """ listen for data """
        for buffer in p.listen():
        # buffer = p.get_message()

            proc_toolchain(None, None)
        # if buffer == None:
            # time.sleep(THREAD_POLLING)
            # continue

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
                # log.info("{}:{}".format(report.packet.ip, report.packet.port))

                """ register client """
                client = register_client(log, _client_registry, report.mobile_id)
                """ process adapter handler """
                client.adapter_handler(report)

                """ process toolchain messages """
                proc_toolchain(redis_server, report.mobile_id)

                """ forward message for further processing. """
                redis_server.publish(redis_channel_pub, report.packet.package_json)
                redis_server.set("{}:{}".format(redis_channel_pub, report.mobile_id), report.packet.to_str)

                """ uncomment below to log message to console """
                _log_debug(report)

            time.sleep(THREAD_POLLING)

