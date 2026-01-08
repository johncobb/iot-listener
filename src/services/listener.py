import socket
import threading
import time
import binascii
import logging
import traceback
from queue import  Queue

""" import frameworks """
from redis import Redis

""" import libs """
from lib.socket import InterruptableUdpSocket
from lib.socket import SocketInterruption

""" import settings """
from settings import THREAD_POLLING
from settings import HOST
from settings import PORT
from settings import SEND_ACK
from settings import REDIS_HOST
from settings import REDIS_PORT
from settings import REDIS_DB
from settings import REDIS_CHANNEL
from settings import LOG_FILE
from settings import LOG_RAW
from settings import LOG_LEVEL
from settings import LOG_FILE
from settings import LOG_RAW

""" constants """
UDP_PACKET_SIZE = 512

class UdpServer(threading.Thread):
    # def __init__(self, log, socket_data_recv, host=HOST, port=PORT):
    def __init__(self, log, socket_data_recv, host, port):
        threading.Thread.__init__(self)
        self._host = host
        self._port = port
        self._log = log
        self.evt_socket_data_recv = socket_data_recv
        self._log_raw = LOG_RAW
        self._shutdown_flag = threading.Event()
        self._lock = threading.Lock()
        self._is_shutdown = False
        self._shutdown = False
        self._packet_counter = 0
        self._send_ack = SEND_ACK
        """ _label_ip_port used for logging (ip:port) """
        self._label_ip_port = "({}:{})".format(HOST, PORT)
        self._inbox = Queue()

        try:
            self._socket = InterruptableUdpSocket(socket.AF_INET, socket.SOCK_DGRAM)
            # self._socket.bind((HOST , PORT))
            self._socket.bind((self._host , self._port))

        except Exception as e:
            self._log.critical("{}({}) failed to bind {}:{}: {}".format(self.name, self.ident, HOST, PORT, e))
            raise e

        self._log_startup()

    def run(self):
        self._log.info("{} {} started.".format(self.name, self._label_ip_port))

        while True:
            time.sleep(THREAD_POLLING)
            if self._shutdown_flag.is_set() and self._inbox.qsize() == 0:
                self.log.info("{} {} shutdown initiated.".format(self.name, self._label_ip_port))
                break
            try:
                packet = self._socket.interruptable_recvfrom(UDP_PACKET_SIZE)
                self.evt_socket_data_recv(packet)
                self._log_raw_packet(packet)
                self._packet_counter += 1
                while self._inbox.qsize() > 0:
                    report = self._inbox.get()

            # socket recvfrom was interrupted
            except SocketInterruption:
                continue

            except Exception as e:
                """TODO: see socket.py for todo on fixing [Error 9] Bad File Descriptor"""
                self._log.error("{}({}) Exception: {}".format(self.name, self.ident, e))
                traceback.print_exc()
                continue

        """ close the socket. """
        self._socket.close()
        """ log info. """
        self._log.info("{} {} packets: {}.".format(self.name, self._label_ip_port, self.packet_counter))
        self.log.info("{} {} shutdown complete.".format(self.name, self._label_ip_port))

    def _log_raw_packet(self, packet):
        if (self._log_raw == True):
            raw_log = open(LOG_FILE + ".raw", "a+")
            raw_log.write(str(binascii.hexlify(packet[0]), 'utf-8')+ "\n")
            raw_log.flush()
            raw_log.close()

    def _log_startup(self):
        self._log.info("{} initializing.".format(self.name))
        self._log.info(" - host: {}:{}".format(HOST, PORT))
        self._log.info(" - log_level: {}".format(logging.getLevelName(LOG_LEVEL)))
        self._log.info(" - log_file: {}".format(LOG_FILE))
        self._log.info(" - log_raw: {}".format(LOG_RAW))
        self._log.info(" - send_ack: {}".format(SEND_ACK))

    def enqueue_inbox(self, packet):
        self._inbox.put(packet)

    def shutdown(self):
        self._shutdown_flag.set()
        self._socket.interrupt()
        self._is_shutdown = True

    @property
    def name(self):
        return type(self).__name__
    @property
    def send_ack(self):
        return self._send_ack
    @property
    def is_shutdown(self):
        return self._is_shutdown
    @property
    def log(self):
        return self._log
    @property
    def socket(self):
        return self._socket
    @property
    def packet_counter(self):
        return self._packet_counter
