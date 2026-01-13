import signal
import socket
import binascii
import time
import datetime
import threading
from queue import Queue
import binascii
import json
import redis
import logging
from threading import Lock
from logging.handlers import RotatingFileHandler

""" logging """
from settings import LOG_FORMAT
from settings import SERVICE_PROVIDER
from settings import SERVICE_TYPE
from settings import LOG_MAXBYTES
from settings import LOG_BACKUPS
from settings import LOG_LEVEL
from settings import LOG_FILE
from settings import THREAD_POLLING

from settings import HOST
from settings import PORT
# from settings import TOOLCHAIN_ENABLE
# from settings import TOOLCHAIN_PORT

""" redis host """
from settings import REDIS_HOST
from settings import REDIS_PORT
from settings import REDIS_DB
from settings import REDIS_CHANNEL
from settings import REDIS_CHANNEL_PUB

""" listeners """
from services.listener import UdpServer
from services.processor import ProcessorForwarder

""" packet/report handling """
from services.calamp.procs import CalampPacket
from services.calamp.procs import CalampReport
from services.toolchain import Toolchain
from services.redis import RedisQueue
from services.redis import RedisChannel

from services.calamp.procs.ack import send_ack
from settings import ACKBACK_ENABLE
from settings import ACK_BACK_TIMEOUT
from services import AckBack

from devices.calamp import parse_mobile_id

""" toolchain tester """
# . bin/launcher.sh --host localhost --esn 3271001574 id_report
""" listener tester """
# . bin/calamp_test_client data/id_report.dat

class SocketClient:
    def __init__(self, data, source):
        self._id = parse_mobile_id(data)
        self._source = source
        self._data = data
        self._report = None
        self._last_update = time.time_ns()
        self._timestamp = datetime.datetime.now()
        self._queue_outbox = Queue(100)
        self.ackback = AckBack(ACK_BACK_TIMEOUT)
        self._report = self.parse_message()

    def _hexlify(self, buffer):
        """ helper method to cut down code """
        return str(binascii.hexlify(buffer), 'utf-8')

    def enqueue_outbox(self, packet):
        self._queue_outbox.put(packet)

    def parse_message(self):
        packet = CalampPacket(self.payload, self.source)
        return CalampReport(packet)

    def encode_bin(self):
        """ ff:ff:ff:ff:00:00:00-NN """
        """ encode IotConnection to binary """
        """ ip to byte array """
        package = socket.inet_aton(self.ip)
        """ port to byte array """
        package += self.port.to_bytes(2, 'big')
        """ append payload """
        package += self.payload

        return package

    def encode_hex(self):
        """ encode IotConnection to hex """
        """ before encoding to hex we need to encode to binary """
        return self._hexlify(self.encode_bin())

    def encode_json(self):
        return {
            "ip": self.ip,
            "port": self.port,
            "payload": self._hexlify(self.payload),
            "last_update": self._last_update,
            "timestamp": self._timestamp.isoformat()
        }

    def shallow_copy(self, client):
        self._source = client.source
        self._data = client.payload
        self._report = client.report
        self._last_update = client.last_update
        self._timestamp = client.timestamp

    @property
    def queue_outbox(self):
        return self._queue_outbox
    @property
    def queue(self):
        return self._queue
    @property
    def id(self):
        return self._id
    @property
    def client_id(self):
        return self._id
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
    def report(self):
        return self._report
    @property
    def last_update(self):
        return (self._last_update != None)
    @property
    def timestamp(self):
        return self._timestamp

""" semaphores, mutexes, and sentinels all keep us from getting our wires crossed. """
class SocketListener:
    def __init__(self):
        """ logging init"""
        logging.basicConfig(format=LOG_FORMAT)
        self.formatter = logging.Formatter(LOG_FORMAT)
        self.log_handler = RotatingFileHandler(LOG_FILE, maxBytes=LOG_MAXBYTES, backupCount=LOG_BACKUPS)
        self.log_handler.setFormatter(self.formatter)
        """ locking """
        self._mutex = Lock()
        """ main udp socket listener """
        self.server = None
        """ toolchain listener """
        self.server_toolchain = None
        self._inbox = Queue()

        """ logging config"""
        self.log = logging.getLogger('calamp_listener')
        self.log.addHandler(self.log_handler)
        self.log.setLevel(LOG_LEVEL)

        """ instantiate redis services """
        self._redis_queue = RedisQueue(REDIS_CHANNEL, REDIS_HOST, REDIS_PORT, REDIS_DB)
        self._redis_channel_live = RedisChannel(REDIS_CHANNEL_PUB, REDIS_HOST, REDIS_PORT, REDIS_DB)
        # self._redis_server = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        # self._redis_server = None
        # self._redis_channel_live = REDIS_CHANNEL_PUB
        # self._redis_channel = REDIS_CHANNEL

        """ socket client registry """
        self._client_registry = {}

        """ todo: """
        # self._queue_toolkit = Queue()

    def enqueue_toolbokit_packet(self, packet):
        self._queue_tooklit.put(packet)
        self._log.debug("client: {} outbox: size {} backlog: size: {}".format(self._id, self._queue.qsize(), self._backlog_queue.qsize()))


    def client_register(self, client_id, client):
        self._client_registry[client_id] = client
        return client

    def client_unregister(self, client_id):
        self._client_registry.pop(client_id)

    def client_lookup(self, client_id):
        client = self._client_registry.get(client_id)
        return client

    def socket_ack_handler(self, client, report):
        self.log.info(" - socket_ack_handler:")

        self.log.debug(" - iot_message: {}".format(report.packet.package_json))

        """ determine if we need to ack the message """
        if (report.acknowledge):
            # send_ack(iot_conn.ip, iot_conn.port, report.message)
            send_ack(client.ip, client.port, report.message, report.message.sequence_number)

    def socket_data_recv(self, packet):
        self.log.info(" - socket_data_recv:")

        """ create the connection helper """
        _client = SocketClient(packet[0], packet[1])

        """ parse the message """
        report = _client.parse_message()

        """ check if client has previously registered """
        client = self.client_lookup(_client.client_id)

        """ register client connection if not registered"""
        if (client == None):
            client = self.client_register(_client.client_id, _client)
        else:
            """ shallow copy new info to previosly registered client """
            self.log.info(" - shallow_copy:")
            self.log.info("  - client_id: {}".format(_client.client_id))
            self.log.info("  - source: ({}:{}) -> ({}:{})".format(client.ip, client.port, _client.ip, _client.port))
            self.log.info("  - timestamp: {} -> {}".format(client.timestamp, _client.timestamp))
            self.log.info("  - ackback: {} -> {}".format(client.ackback.count, _client.ackback.count))
            client.shallow_copy(_client)


        """ logging """
        self.log.info("({}:{}):{}".format(client.ip, client.port, client.id))

        """ process acknowledgement """
        self.socket_ack_handler(client, report)

        """ encode the message to hex """
        client_payload = _client.encode_hex()

        """ publish to redis (subscribers)"""
        """ todo: refactor using RedisQueue class """
        # self.redis_server.publish(self._redis_channel_live, report.packet.package_json)
        # self.redis_queue_pub.pub(json.dumps(_client.encode_json()))

        """ add to redis channel """
        self.redis_queue.enqueue(json.dumps(_client.encode_json()))

        """ log info """
        self.log.info(" - {}:{}".format(client.client_id, client_payload))

    # . bin/launcher.sh --host localhost --esn 3271001574 id_report
    def socket_toolchain_recv(self, packet):
        self.log.info(" - socket_toolchain_recv:")

        """ create the connection helper """
        # _client = R3dSkyClient(packet[0], packet[1])
        _client = SocketClient(packet[0], packet[1])

        """ push toolchain message to queue """
        self._redis_server.lpush(_client.client_id, _client.payload)

        self.log.info(" - mobile_id: {} payload: {}".format(_client.client_id, _client.payload))

        return

        """ *** todo: refactor following to queue handling *** """
        """ check to see if client previously registered """
        client = self.client_lookup(_client.client_id)
        if(client == None):
            return

        client.ackback.increment_ack()
        self.log.info(" - mobile_id: {} ackback.count: {}".format(client.client_id, client.ackback.count))

    def start(self):

        self.log.info("Starting SocketClient services...")
        self.log.info(" - test: . bin/calamp_test_client data/id_report.dat ")
        self.log.info(" Redis connection established: ({}:{})".format(REDIS_HOST, REDIS_PORT))
        self.log.info(" - queue: {}".format(self.redis_queue.queue_name))
        self.log.info(" - channel: {}".format(self.redis_channel_live.channel_name))

        # if (self._redis_server.exists(self._redis_channel_live) == False):
            # self.log.info(" - Redis creating channel live: {}".format(self._redis_channel_live))
            # self._redis_ts.create(self._redis_channel_live)


        signal.signal(signal.SIGTERM, self.service_shutdown)
        signal.signal(signal.SIGINT, self.service_shutdown)

        self.server = UdpServer(self.log, self.socket_data_recv, HOST, PORT)
        self.server.start()

        self.server_toolchain = Toolchain(self.log, self.socket_toolchain_recv)
        self.server_toolchain.start()

        try:
            while(True):
                # if (self.server.shutdown):
                if (self.server.is_shutdown):
                    break

                """ todo: needs rework to use RedisQueue class """
                # self.proc_outbox()
                # self.loop_clients()

                time.sleep(THREAD_POLLING)

        except KeyboardInterrupt:
            pass
            # self.server.shutdown_thread()
            # self.server_toolchain.shutdown_thread()

    def loop_clients(self):
        """  *** todo: refactor to separate method *** """
        for client_id in self._client_registry:
            """ reference the client """
            client = self._client_registry[client_id]

            """ skip if this devices has not been registered """
            if (client != None):
                if (client.queue_outbox.qsize() > 0):
                    _packet = client.queue_outbox.get()
                    # payload_bytes = bytes.fromhex(payload)
                    self.log.info(" - client send-toolkit-msg: ({}:{}) {}".format(client.ip, client.port, _packet))
                    self.server.socket.sendto(_packet, (client.ip, client.port))
                    self.log.info(" - client: {} queue_outbox: {} packet: {}".format(client.client_id, client.queue_outbox.qsize(), _packet))
        """  *** todo: end refactor to separate method *** """

    def proc_outbox(self):
        # return

        """ acquire lock """
        self.mutex.acquire()

        for client_id in self._client_registry:
            """ reference the client """
            client = self._client_registry[client_id]

            """ skip if this devices has not been registered """
            if (client == None):
                continue

            """ check redis for packets waiting for this client """
            while (True):

                """ queue peek """
                _packet = self._redis_server.lrange(client_id, -1, -1)

                """ check for packet """
                if (len(_packet) == 0):
                    break

                """ we have data so pop the message from the queue """
                packet = self._redis_server.rpop(client_id)
                # payload_bytes = bytes.fromhex(payload)
                """ enqueue to the client's outbox """
                client.enqueue_outbox(packet)
                """ increment ack count """
                client.ackback.increment_ack()
                """ logging """
                self.log.info("queue.pop mobile_id: {} packet: {} count: {}".format(client_id, packet, client.ackback.count))


        """ release lock """
        self.mutex.release()

    def service_shutdown(self, signum, frame):
        signame = signal.Signals(signum).name
        self.log.info("{} service_shutdown signal caught: {}({}) threads: {}".format(self.name, signame, signal.strsignal(signum), threading.active_count()))

        # shutdown and wait for the server
        self.server.shutdown()
        self.server_toolchain.shutdown()

        self.server.join()
        self.server_toolchain.join()

        # if there somehow are any threads left alive we want to know about it (for debugging)
        if any(thread.is_alive() for thread in threading.enumerate()):
            self.log.info("Waiting on {}".format([(thread.name, thread.ident) for thread in threading.enumerate() if thread.is_alive()]))
        self.log.info("Goodbye!")

    @property
    def mutex(self):
        return self._mutex
    @property
    def name(self):
        return type(self).__name__
    @property
    def redis_server(self):
        return self._redis_server
    @property
    def redis_queue(self):
        return self._redis_queue
    @property
    def redis_channel_live(self):
        return self._redis_channel_live

def main():
    service = SocketListener()
    service.start()

""" Handy terminal command in the event the threads runaway. """
""" ps aux | grep """
""" kill -9 <process-id> """
if __name__ == "__main__":
    main()
