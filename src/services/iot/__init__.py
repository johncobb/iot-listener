import threading
import binascii
import datetime
import time
import json
import traceback

from enum import Enum
from queue import Queue

from lib import ByteBuffer
from lib import IoThread

from services import Client
from services import Report
from services import Packet

from settings import PROC_ADAPTER_ENABLE

""" coap device api """
from devices.iot.api import AckTypes, ServiceTypes
from devices.iot.api import MessageTypes


class R3dSkyPacket(Packet):
    def __init__(self, data, source):
        Packet.__init__(self, data, source)

    @property
    def to_str(self):
        return str(binascii.hexlify(self._data), 'utf-8')
    @property
    def to_byte_array(self):
        return bytearray.fromhex(self._data)

class R3dSkyReport(Report):
    def __init__(self, log, packet):
        Report.__init__(self, log, packet)
        try:
            self._message = self._parse()
        except Exception as e:
            self._log.info(e)
            traceback.print_stack()
            raise e

    def _parse(self):
        iobuffer = ByteBuffer(self.packet.payload)
        """ todo:  """
        msg = None
        return msg

    def __dict__(self):
        return {
            'packet': self._packet.__dict__(),
            'message': self._message.__dict__() if self.message is not None else self.message
        }

    @property
    def mobile_id(self):
        return self._message.mobile_id
    @property
    def ver(self):
        if (hasattr(self._message, 'app_version')):
            return self._message.app_version
        else:
            return "??:??:??"

class R3dSkyClient():
    def __init__(self, client_id):
        self._client_id = client_id

    @property
    def client_id(self):
        return self._client_id

