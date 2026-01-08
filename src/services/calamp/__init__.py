import binascii
import time
import datetime
import threading
import traceback
import json

from queue import Queue
from enum import Enum

from lib import IoThread
from lib import ByteBuffer

from settings import THREAD_POLLING
from settings import PROC_ADAPTER_ENABLE
from settings import LOG_TRIP_DETAILS

from services import ClientManager
from services import Client
from services import Report
from services import Packet

# from services.landmark import LandmarkManager

from services.calamp.toolchain import CalampToolchain
from services.calamp.processor import CalampProcessorForwarder

from devices.calamp import MessageTypes
from devices.calamp import ServiceTypes
from devices.calamp import OptionsHeader
from devices.calamp import MessageHeader

from devices.calamp.api import AckTypes
from devices.calamp.api import ServiceTypes
from devices.calamp.api import MessageTypes

from devices.calamp.messages.null_message import NullReport
from devices.calamp.messages.event_report import EventReport
from devices.calamp.messages.event_report_mini import EventReportMini
from devices.calamp.messages.id_report import IdReport
from devices.calamp.messages.ack import AckMessage
from devices.calamp.messages.unit_request import UnitRequest
from devices.calamp.messages.undefined_report import UndefinedReport
from devices.calamp.messages.application_message import ApplicationMessage


from devices.calamp.logic import DeviceStates
from devices.calamp.logic.states import DeviceState
from devices.calamp.logic.adapter import DeviceAdapters
# from devices.calamp.logic.odometer import DeviceOdometer
from devices.calamp.logic.acknowledgement import DeviceAcknowledgement

from devices.calamp.adapters.blackbird import BlackbirdMessage


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

        # server.log.info("iobuffer len: {}".format(iobuffer.length))
        opt_header = OptionsHeader()
        opt_header.parse(iobuffer)
        opt_header.log(self._log)

        self._id = opt_header.mobile_id
        msg_header = MessageHeader()
        msg_header.parse(iobuffer)
        msg_header.log(self._log)
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
            msg.log(self._log)

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

class CalampClient(Client):
    def __init__(self, client_manager, log, id):
        Client.__init__(self, client_manager, log, id)
        self._state = DeviceState(DeviceStates.UNKNOWN)
        self._odometer = DeviceOdometer(self._state)
        self._ack = DeviceAcknowledgement(ack_handler=self._ack_handler)
        self._adapter = DeviceAdapters(adapters={MessageTypes.EVENT_REPORT:BlackbirdMessage()}, adapter_handler=self._adapter_handler)
        self._report = None

    def _ack_handler(self, packet):
        payload = (packet, self._report.packet.source)
        self._client_manager.server_sendto(payload)
        self._log.debug("client: {} ack sent back".format(self._id))

    def _adapter_handler(self, payload):
        # payload = (packet, (BB_HOST, BB_PORT))
        if PROC_ADAPTER_ENABLE:
            self._client_manager.server_sendto(payload)
        self._log.debug("client: {} adapters handled".format(self._id))

    def _on_ack_message(self, message):
        if message.type == MessageTypes.UNIT_REQUEST:
            self.ackback.increment_ack()

    def _landmark_handler(self, message):
        if (message.message_type != MessageTypes.EVENT_REPORT and message.message_type != MessageTypes.MINI_EVENT_REPORT):
            return

        loc = (message.loc.latitude_radix, message.loc.longitude_radix)
        self._client_manager.enqueue_landmark_proc((self._id, loc))

    def _proc_message(self):
        message = self.report.message
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
            self._odometer.log_trip(self._log, self.report)

    def _proc_outbox(self):
        self._outbox.proc_backlog(self._report.packet.source)
        self._log.debug("client: {} proc_outbox".format(self._id))

    def _proc_db(self):
        db_report = (self._report, self._state.change, self._state.prev, self._state.current, self._odometer.total_odometer, self._odometer.total_virtual_odometer, self._odometer.total_engine_hours)
        self._client_manager.enqueue_db_report(db_report)

    def _inbox_handler(self, report):
        """called in Client run loop"""
        self._report = report
        self._ack.ack_handler(self._report.message.service_type, self._report.message.message_type, self._report.message.sequence_number)
        self._adapter.adapter_handler(self._report)

        self._state.event_handler(self._report.message.event_code)
        self._odometer.handler(self._report)

        self._proc_message()
        self._landmark_handler(self._report.message)
        self._proc_outbox()

        self._proc_db()

        self._state.event_handler(self._report.message.event_code)

        self._client_manager.publish_to_proc(self._id, json.dumps(self._asdict()))

    def _asdict(self):
        """package transforms/serializes the class into a dict for distribution"""
        return {
            'client_id': self._id,
            'report': self._report.__dict__(),
            'state': self._state.__dict__(),
            'odometer': self._odometer.__dict__()
        }

    @property
    def state(self):
        return self._state
    @property
    def notifications(self):
        return self.state.notifications

class CalampClientManager(ClientManager):
    def __init__(self, server, log):
        ClientManager.__init__(self, server, log, CalampToolchain, LandmarkManager, CalampProcessorForwarder, CalampClient, CalampReport, CalampPacket)

""" MQTT Service """

class IoEventTypes(Enum):
    ON_CONNECT = 1
    ON_DISCONNECT = 2
    ON_DATA = 3
    ON_ACK = 4

class IoEvent():
    def __init__(self, evt_type, evt_data):
        self.event_type = evt_type
        self.event_data = evt_data

class IoEventData():
    def __init__(self, id, data):
        self.id = id
        self.data = data
        self._timestamp = time.time_ns()

    @property
    def timestamp(self):
        return self._timestamp
