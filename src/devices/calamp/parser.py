
import sys
import struct
import logging
from devices.calamp.messages.application_message import ApplicationMessage

from lib import ByteBuffer
from devices.calamp import MessageTypes
from devices.calamp import ServiceTypes
from devices.calamp import OptionsHeader
from devices.calamp import MessageHeader
from devices.calamp.messages.event_report import EventReport
from devices.calamp.messages.event_report_mini import EventReportMini
from devices.calamp.messages.id_report import IdReport
from devices.calamp.messages.ack import AckMessage
from devices.calamp.messages.unit_request import UnitRequest
from devices.calamp.messages.undefined_report import UndefinedReport

from lib import ByteBuffer
from devices.calamp.api import MessageTypes
from devices.calamp.api import ServiceTypes
from devices.calamp.config import peg
from devices.calamp.config import service
from devices.calamp.tests import ServerFixture
from devices.calamp.messages.adapters import BlackbirdMessage

adapters = {}
adapters[MessageTypes.EVENT_REPORT] = BlackbirdMessage
#adapters[MessageTypes.MINI_EVENT_REPORT] = BlackbirdMessage

class CalampPacket:
	def __init__(self, packet):
		self._packet = packet
	
	@property
	def to_byte_array(self):
		return bytearray.fromhex(self.packet)

	@property
	def packet(self):
		return self._packet

class SimData:
	id_rpt = CalampPacket("8305327100161301010103000000032D2D2D000800FF01000001003271001613FFFFFF355144090097392F310410127813350F15253519119FFFFF890141042712781335064F54413A317C303B302C32322C31312C31387C32353B307C32363B30004F5441535441543A313632393339373637312C302C32322C362C31332C2222004C4D554150503A302C526576322C2C302C312E382E302E352E302E336362353430302C32322C504547325F4445565F302E362C31312C2C31382C004149443A3130303100564255533A32352C3130312C3030313738303164333433373531313233383337333733342C302C312E382E302E352E302E376334393661630056494E2D494E464F3A56494E3D3147314A433534343452373235323336372C4445562D5245474E3D3F3F2C535256522D5245474E3D3F3F00564255532D49443A32352C52657632424C453A32362C30004654424C3A302C32322C4141334200535256433A312C312C302CC2BF004D41433A3100415245563A3363623534303000")
	evt_rpt_mini = CalampPacket("830512750312690101010a0007609d7dac169dd993cbe70fd10026010d0f8f0200")
	evt_rpt = CalampPacket("83051275031269010101020004609d584d609d584c169ddae4cbe70dbd000024f50000000801600e02019affb30f08cf00fffe0000")


def parse(server, packet):
	iobuffer = ByteBuffer(packet)

	# server.log.info("iobuffer len: {}".format(iobuffer.length))
	opt_header = OptionsHeader()
	opt_header.parse(iobuffer)
	opt_header.log(server)
	
	msg_header = MessageHeader()
	msg_header.parse(iobuffer)
	msg_header.log(server)
	# server.log.info("iobuffer len: {}".format(iobuffer.length))


	msg = None

	if (msg_header.message_type == MessageTypes.NULL):
		server.log.info("NULL MESSAGE")
	# if (msg_header.message_type == MessageTypes.ACKNOWLEDGEMENT and msg_header.service_type == ServiceTypes.ACKNOWLEDGE_RESPONSE):
	if (msg_header.message_type == MessageTypes.ACKNOWLEDGEMENT):
		msg = AckMessage(opt_header, msg_header)
	if (msg_header.message_type == MessageTypes.EVENT_REPORT):
		msg = EventReport(opt_header, msg_header)
	if (msg_header.message_type == MessageTypes.MINI_EVENT_REPORT):
		msg = EventReportMini(opt_header, msg_header)
	# if (msg_header.message_type == MessageTypes.APPLICATION):
	# 	msg = ApplicationMessage(opt_header, msg_header)
	if (msg_header.message_type == MessageTypes.ID_REPORT):
		msg = IdReport(opt_header, msg_header)
	if (msg_header.message_type == MessageTypes.UNIT_REQUEST):
		msg = UnitRequest(opt_header, msg_header)
	if (msg == None):
		msg = UndefinedReport(opt_header, msg_header)
  
	# if (msg_header.message_type == MessageTypes.ACKNOWLEDGEMENT):
	# 	server.log.info("- - -")
	# 	server.log.info("+ msg header service ack resp: {}".format(msg_header.service_type == ServiceTypes.ACKNOWLEDGE_RESPONSE))
	# 	msg.log(server)
	# 	server.log.info("- - -")

	

	if (msg is not None):
		msg.set_buffer(iobuffer)
		msg.parse(iobuffer)
		msg.log(server)

	return msg


# class ForwardingHandler:
# 	def __init__(self, endpoint, *events):
# 		self.endpoint = endpoint
# 		self.__events = {}
# 		for event in events:
# 			self.__events[event] = endpoint

# 	@property
# 	def events(self):
# 		return self.__events

# 	def send(self):
# 		print("forwarding: {}".format(self.endpoint))

# def example_forwarding_event(self):

# 	forwarding_handlers = {}

# 	forwarding_handlers[0] = ForwardingHandler("10.0.0.1", get_event_def("EVENT", "IGNITION_ON", "IGNITION_OFF", "TIME_DISTANCE", "IDLE_RECEIPT", "PARKING_HEARTBEAT"))
# 	example_event = 1
# 	for f_key in forwarding_handlers:
# 		handler = forwarding_handlers[f_key]
# 		_evt = handler.events.get(example_event)
# 		if _evt is not None:
# 			handler.send()


def main():
	server = ServerFixture("CALAMP")

	sim_messages = {}
	sim_messages[0] = SimData.id_rpt
	sim_messages[1] = SimData.evt_rpt
	sim_messages[2] = SimData.evt_rpt_mini

	for key in sim_messages:
		msg = parse(server, sim_messages.get(key).to_byte_array)

		""" loop through adapters to handler conversions of data. """
		for evt_key in adapters:
			if (evt_key == msg.message_header.message_type):
				if server.get_event_def(msg.event_code, "IGNITION_ON", "IGNITION_OFF", "TIME_DISTANCE", "IDLE_RECEIPT", "PARKING_HEARTBEAT"):
					""" we have a match, create the class. """
					adapter = adapters.get(evt_key)(msg)
					""" call the transform method and print. """
					""" TODO: replace print with sending to endpoint. """
					packet = adapter.transform()
					server.log.debug(packet)

if __name__ == "__main__":
	main()



