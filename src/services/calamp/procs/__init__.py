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

from lib import MASK_BIT
from lib import MASK_NIBBLE
from lib import SHIFT_NIBBLE
from lib import ByteBuffer

from devices.calamp import OptionsHeader
from devices.calamp import MessageHeader
from devices.calamp import MessageTypes

from devices.calamp import MessageTypes
from devices.calamp.api import ServiceTypes
from devices.calamp.api import AckTypes

from devices.calamp.messages.ack import AckMessage
from devices.calamp.messages.id_report import IdReport
from devices.calamp.messages.event_report import EventReport
from devices.calamp.messages.event_report_mini import EventReportMini
from devices.calamp.messages.unit_request import UnitRequest
from devices.calamp.messages.undefined_report import UndefinedReport


from services.calamp.procs.ack import send_ack

from devices.calamp.logic import DeviceStates
from devices.calamp.logic.states import DeviceState

from devices.calamp.logic.adapter import DeviceAdapters
from devices.calamp.logic.odometer import DeviceOdometer
from devices.calamp.logic.acknowledgement import DeviceAcknowledgement
from devices.calamp.adapters.blackbird import BlackbirdMessage

from settings import CLIENT_DWELL_TIME
from settings import PROC_FORWARDING_ENABLE
from settings import PROC_ADAPTER_ENABLE
from settings import LOG_TRIP_DETAILS

from settings import BB_HOST
from settings import BB_PORT

def message_to_hex(msg):
    msg_buffer = None
    data = msg['data']
    if (isinstance(data, str)):
        msg_buffer = bytes.fromhex(data)

    return msg_buffer

class Packet:
    def __init__(self, data, source):
        self._source = source
        self._data = data
        self._last_update = time.time_ns()
        self._timestamp = datetime.datetime.now()

    def __dict__(self):
        return {
            'source': {
                'address': self.ip,
                'port': self.port
            },
            'payload':  str(binascii.hexlify(self.payload), 'utf-8'),
            'last_update': self.last_update,
            'timestamp': self.timestamp.timestamp()
        }


    @property
    def name(self):
        return type(self).__name__
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
    @property
    def last_update(self):
        return (self._last_update != None)
    @property
    def timestamp(self):
        return self._timestamp
    @property
    def package(self):
        return self.__dict__()
    @property
    def package_json(self):
        return json.dumps(self.__dict__())
    @property
    def to_str(self):
        return str(binascii.hexlify(self._data), 'utf-8')
    @property
    def to_byte_array(self):
        return bytearray.fromhex(self._data)


class Report:
    """
    Report class
    @log: the log
    @packet: Packet instance
    """
    # def __init__(self, log, packet):
    def __init__(self, packet):
        # self._log = log
        self._packet = packet
        self._id = packet.source
        self._message = None

    def __dict__(self):
        return {
            'report_id': self._id,
            'packet': self._packet.__dict__(),
            'message': self._message
        }

    @property
    def name(self):
        return type(self).__name__
    @property
    def packet(self):
        return self._packet
    @property
    def message(self):
        return self._message
    @property
    def id(self):
        return self._id
    @property
    def is_timeout(self):
        _time = (self._packet.timestamp + datetime.timedelta(seconds=REPORT_TIMEOUT))
        _timenow = datetime.datetime.now()
        _timeout = _timenow > _time
        # self._log.debug("client: {} report: timeout: {} > {} == ({})".format(self.id, _timenow, _time, _timeout))
        return _timeout and REPORT_TIMEOUT_ENABLE
    @property
    def package(self):
        return self.__dict__()
    @property
    def acknowledge(self):
        return self._message.message_header.service_type == ServiceTypes.ACKNOWLEDGED


class CalampPacket(Packet):
    def __init__(self, data, source):
        Packet.__init__(self, data, source)

    @property
    def to_str(self):
        return str(binascii.hexlify(self._data), 'utf-8')
    @property
    def to_byte_array(self):
        return bytearray.fromhex(self._data)


class CalampReport(Report):
    # def __init__(self, log, packet):
    def __init__(self, packet):
        # Report.__init__(self, log, packet)
        Report.__init__(self, packet)
        try:
            self._message = self._parse()
        except Exception as e:
            # self._log.info(e)
            # traceback.print_stack()
            raise e

    def _parse(self):
        iobuffer = ByteBuffer(self.packet.payload)

        # server.log.info("iobuffer len: {}".format(iobuffer.length))
        opt_header = OptionsHeader()
        opt_header.parse(iobuffer)
        # opt_header.log(self._log)

        self._id = opt_header.mobile_id
        msg_header = MessageHeader()
        msg_header.parse(iobuffer)
        # msg_header.log(self._log)
        # server.log.info("iobuffer len: {}".format(iobuffer.length))

        msg = None

        if (msg_header.message_type == MessageTypes.NULL):
            msg = NullReport(opt_header, msg_header)
        # if (msg_header.message_type == MessageTypes.ACKNOWLEDGEMENT and msg_header.service_type == ServiceTypes.ACKNOWLEDGE_RESPONSE):
        if (msg_header.message_type == MessageTypes.ACKNOWLEDGEMENT):
            msg = AckMessage(opt_header, msg_header)
        if (msg_header.message_type == MessageTypes.EVENT_REPORT):
            msg = EventReport(opt_header, msg_header)
        if (msg_header.message_type == MessageTypes.MINI_EVENT_REPORT):
            msg = EventReportMini(opt_header, msg_header)
        # if (msg_header.message_type == MessageTypes.APPLICATION):
        #   msg = ApplicationMessage(opt_header, msg_header)
        if (msg_header.message_type == MessageTypes.ID_REPORT):
            msg = IdReport(opt_header, msg_header)
        if (msg_header.message_type == MessageTypes.UNIT_REQUEST):
            msg = UnitRequest(opt_header, msg_header)
        if (msg == None):
            msg = UndefinedReport(opt_header, msg_header)

        # if (msg_header.message_type == MessageTypes.ACKNOWLEDGEMENT):
        #   server.log.info("- - -")
        #   server.log.info("+ msg header service ack resp: {}".format(msg_header.service_type == ServiceTypes.ACKNOWLEDGE_RESPONSE))
        #   msg.log(server)
        #   server.log.info("- - -")



        if (msg is not None):
            msg.set_buffer(iobuffer)
            msg.parse(iobuffer)
            # msg.log(self._log)

        self._message = msg
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

    @property
    def message(self):
        return self._message

class CalampClient():
    # def __init__(self, log, id):
    def __init__(self, log, packet):
        self._state = DeviceState(DeviceStates.UNKNOWN)
        self._odometer = DeviceOdometer(self._state)
        self._log = log
        self._id = id
        self._instance_time = datetime.datetime.now()
        self._ack = DeviceAcknowledgement(ack_handler=self._ack_handler)
        self._adapter = DeviceAdapters(adapters={MessageTypes.EVENT_REPORT:BlackbirdMessage()}, adapter_handler=self._adapter_handler)
        # self._shutdown_flag = threading.Event()
        # self._sleep = threading.Event()
        # self._sleep.set()
        # self.ackback = AckBack(ACK_BACK_TIMEOUT)

        # self._log.debug("client: {} client_type: {}({}) client created".format(self._id, self.name, self.ident))

    def proc_message(self, report):
        message = report.message
        if (message.message_type == MessageTypes.EVENT_REPORT or message.message_type == MessageTypes.MINI_EVENT_REPORT):
            self._log.info("client: {} type: {}({}) sequence_number: {} event: {} time: {} lat: {} lon: {} hdg: {} vel: {} vel_unit: 0".format(message.mobile_id, message.message_type.value, message.message_type.name, message.sequence_number, message.event_code, message.update_time, message.loc.latitude_radix, message.loc.longitude_radix, message.loc.heading, message.loc.speed_mph))
        elif (message.message_type == MessageTypes.MINI_EVENT_REPORT):
            self._log.info("client: {} type: {}({}) sequence_number: {} event: {} time: {} lat: {} lon: {} hdg: {} vel: {} vels_unit: 0".format(message.mobile_id, message.message_type.value, message.message_type.name, message.sequence_number, message.event_code, message.update_time, message.loc.latitude_radix, message.loc.longitude_radix, message.loc.heading, message.loc.speed_mph))
        elif (message.message_type == MessageTypes.ID_REPORT):
            self._log.info("client: {} type: {}({}) sequence_number: {} script: {} app: \"{}\" app_id: {} esn: {} imei: {} imsi: {} min: {} iccid: {}".format(message.mobile_id, message.message_type.value, message.message_type.name, message.sequence_number, message.script.ver, message.app_version.ver, message.app_id, message.cell_info.esn, message.cell_info.imei, message.cell_info.imsi, message.cell_info.min, message.cell_info.iccid))
        elif (message.message_type == MessageTypes.UNIT_REQUEST):
            self._log.info("client: {} type: {}({}) sequence_number: {} action: {} byte8: {} byte16: {} byte32: {}".format(message.mobile_id, message.message_type.value, message.message_type.name, message.sequence_number, message.action, message.byte8, message.byte16, message.byte32))
        elif (message.message_type == MessageTypes.ACKNOWLEDGEMENT):
            self._log.info("client: {} type: {}({}) sequence_number: {} ack_message_type: {}({}) ack_type: {}({}) app_version: {}".format(message.mobile_id, message.message_type.value, message.message_type.name, message.sequence_number, message.type.value, message.type.name, message.ack.value, message.ack.name, message.app_version.ver))
            self._on_ack_message(message)
        # elif (message.message_type == MessageTypes.APPLICATION):
        #   self._log.info("client: {} type: {} time: {} app_message_type: {} app_message: {}".format(message.mobile_id, message.message_type, message.update_time, message.app_message_type, message.app_message))
        else:
            self._log.info("client: {} type: {}({}) sequence_number: {} status: message type unhandled!".format(message.mobile_id, message.message_type.value, message.message_type.name, message.sequence_number))

        if (self._state.change):
            self._log.info("client: {} state_change: {}({}) -> {}({})".format(message.mobile_id, self._state.prev.value, self._state.prev.name, self._state.current.value, self._state.current.name))

        if (self._state.note):
            self._log.info("client: {} event_notification: {}({})".format(message.mobile_id, self._state.notification.value, self._state.notification.name))

        if LOG_TRIP_DETAILS:
            self._odometer.log_trip(self._log, report)


    def state_handler(self, event_code):
        self._state.event_handler(event_code)

    def odometer_handler(self, report):
        self._odometer.handler(report)

    def adapter_handler(self, report):
        self._adapter.adapter_handler(report)

    def _adapter_handler(self, payload):
        socket_adapter = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_adapter.sendto(bytes(str(payload), encoding="utf-8"), (BB_HOST, BB_PORT))

    def _ack_handler(self, report):
        """ assign to local variables for convenience """
        service_type = report._message.message_header.service_type
        message_type = report._message.message_header.message_type

        if (service_type != ServiceTypes.ACKNOWLEDGED):
            return

        sequence_number = report.message.sequence_number

        self._ack.ack_handler(service_type, message_type, sequence_number)

    def landmark_handler(self, message):
        if (message.message_type != MessageTypes.EVENT_REPORT and message.message_type != MessageTypes.MINI_EVENT_REPORT):
            return

        loc = (message.loc.latitude_radix, message.loc.longitude_radix)
        # self._client_manager.enqueue_landmark_proc((self._id, loc))

    def acknowledgement_handler(self, report):
        self._ack_handler(report)
    @property
    def name(self):
        return type(self).__name__
    @property
    def id(self):
        return (self._id, self.ident)
    @property
    def state(self):
        return self._state
    @property
    def log(self):
        return self._log
    @property
    def is_timeout(self):
        _dwell_offset = self._instance_time + datetime.timedelta(seconds=CLIENT_DWELL_TIME)
        # if self._report == None:
        #   _dwell_offset = self._instance_time + datetime.timedelta(seconds=CLIENT_DWELL_TIME)
        # else:
        #   _dwell_offset = self._report.packet.timestamp + datetime.timedelta(seconds=CLIENT_DWELL_TIME)

        _timenow = datetime.datetime.now()
        _timeout = _timenow > _dwell_offset
        # self._log.debug("client: {} dwell: {} > {} == {}".format(self.id, _timenow, _dwell_offset, _timeout))
        return _timeout

    @property
    def package(self):
        return self._asdict()


""" pulled from src/services/__init__.py """
""" look to see if the client is in the current registry """
def _client_lookup(client_registry, client_id):
    client =client_registry.get(client_id)
    return client

""" register a client """
def register_client(log, client_registry, client_id):
    """ add client to registry if not already registered. """
    client = _client_lookup(client_registry, client_id)
    if (client == None):
        client = CalampClient(log, client_id)
        client_registry[client_id] = client
        log.info("client: {} registered.".format(client_id))

    return client

def _unregister_client(client_registry, client_id):
    client_registry.pop(client_id)

