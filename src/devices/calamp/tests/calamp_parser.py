import struct
from src.lib import ByteBuffer
from src.devices.calamp import OptionsByte
from src.devices.calamp.api import MessageTypes
from src.devices.calamp import ServiceTypes
from src.devices.calamp import OptionsHeader
from src.devices.calamp import MessageHeader
from src.devices.calamp.messages.event_report import EventReport
from src.devices.calamp.messages.event_report_mini import EventReportMini
from src.devices.calamp.messages.id_report import IdReport
from src.devices.calamp.messages.ack import AckMessage
from src.devices.calamp.messages.unit_request import UnitRequest
from src.devices.calamp.messages.adapters import BlackbirdMessage
from src.devices.calamp.tests import ServerFixture

from settings import LOG_FORMAT
from settings import LOG_MAXBYTES
from settings import LOG_BACKUPS
from settings import LOG_LEVEL
from settings import LOG_FILE
from settings import LOG_RAW

adapters = {}
adapters[MessageTypes.EVENT_REPORT] = BlackbirdMessage
adapters[MessageTypes.MINI_EVENT_REPORT] = BlackbirdMessage

class CalampPacket():
	def __init__(self, packet):
		self.__packet = packet
	
	@property
	def to_byte_array(self):
		return bytearray.fromhex(self.packet)

	@property
	def packet(self):
		return self.__packet

""" simulation data """
class SimData():
	opt_byte = CalampPacket("83")
	ext_byte = CalampPacket("00")
	opt_header = CalampPacket("830512750312690101")
	msg_header = CalampPacket("010a0007")
	accumulator = CalampPacket("03000000000100000002000000fe")
	evt_rpt_mini = CalampPacket("830512750312690101010a0007609d7dac169dd993cbe70fd10026010d0f8f0200")
	evt_rpt = CalampPacket("83051275031269010101020004609d584d609d584c169ddae4cbe70dbd000024f50000000801600e02019affb30f08cf00fffe0000")
	evt_ack = CalampPacket("8305127503126901010201000701020a0b0c")
	id_rpt = CalampPacket("8305327100161301010103000000032D2D2D000800FF01000001003271001613FFFFFF355144090097392F310410127813350F15253519119FFFFF890141042712781335064F54413A317C303B302C32322C31312C31387C32353B307C32363B30004F5441535441543A313632393339373637312C302C32322C362C31332C2222004C4D554150503A302C526576322C2C302C312E382E302E352E302E336362353430302C32322C504547325F4445565F302E362C31312C2C31382C004149443A3130303100564255533A32352C3130312C3030313738303164333433373531313233383337333733342C302C312E382E302E352E302E376334393661630056494E2D494E464F3A56494E3D3147314A433534343452373235323336372C4445562D5245474E3D3F3F2C535256522D5245474E3D3F3F00564255532D49443A32352C52657632424C453A32362C30004654424C3A302C32322C4141334200535256433A312C312C302CC2BF004D41433A3100415245563A3363623534303000")

def sim_opt_byte(server):
	iobuffer = ByteBuffer(SimData.opt_byte.to_byte_array)
	opt_byte = OptionsByte(iobuffer.read())
	opt_byte.log(server)

def sim_ext_byte(server):
	iobuffer = ByteBuffer(SimData.ext_byte.to_byte_array)
	opt_byte = OptionsByte(iobuffer.read())
	opt_byte.log(server)

def sim_opt_header(server):
	iobuffer = ByteBuffer(SimData.opt_header.to_byte_array)
	opt_header = OptionsHeader(iobuffer.read())
	opt_header.log(server)

def sim_msg_header(server):
	iobuffer = ByteBuffer(SimData.msg_header.to_byte_array)
	opt_byte = OptionsByte(iobuffer.read())
	opt_byte.log(server)

def sim_accumulator(server):
	iobuffer = ByteBuffer(SimData.accumulator.to_byte_array)
	count = iobuffer.read() & 0xFFFFFF
	spare_byte = iobuffer.read()

	accum_list = {}

	for i in range(0, count):
		accum_list[i] = CalampAccumulator(i, struct.unpack(">i", iobuffer.read(4))[0])

	server.log.debug("accumulators: {}".format(count))
	for key in accum_list:
		accum = accum_list.get(key)
		server.log.debug(" - accum[{}]: {}".format(accum.id, accum.val))

def sim_evt_ack(server):
	iobuffer = ByteBuffer(SimData.evt_ack.to_byte_array)
	evt_ack = AckMessage(iobuffer)
	evt_ack.log(server)

def sim_evt_report(server):
	server.log.debug("*** SIM EVT REPORT ***")
	iobuffer = ByteBuffer(SimData.evt_rpt.to_byte_array)
	opt_header = OptionsHeader(iobuffer)
	opt_header.parse()
	opt_header.log(server)
	
	msg_header = MessageHeader(iobuffer)
	msg_header.parse()
	msg_header.log(server)

	evt_report = EventReport(iobuffer, opt_header, msg_header)
	evt_report.parse()
	evt_report.log(server)
	server.log.debug("*** END ***")

def packet_handler(server, packet):

	iobuffer = ByteBuffer(packet.to_byte_array)
	opt_header = OptionsHeader(iobuffer)
	opt_header.parse()
	opt_header.log(server)
	
	msg_header = MessageHeader(iobuffer)
	msg_header.parse()
	msg_header.log(server)

	msg = None

	if (msg_header.message_type == MessageTypes.NULL):
		server.log.debug("NULL MESSAGE")
	if (msg_header.message_type == MessageTypes.ACKNOWLEDGEMENT and msg_header.service_type == ServiceTypes.ACKNOWLEDGE_RESPONSE):
		msg = AckMessage(iobuffer, opt_header, msg_header)
	if (msg_header.message_type == MessageTypes.EVENT_REPORT):
		msg = EventReport(iobuffer, opt_header, msg_header)
	if (msg_header.message_type == MessageTypes.MINI_EVENT_REPORT):
		msg = EventReportMini(iobuffer, opt_header, msg_header)
	if (msg_header.message_type == MessageTypes.ID_REPORT):
		msg = IdReport(iobuffer, opt_header, msg_header)
	
	if (msg is not None):
		msg.parse()
		msg.log(server)

		""" loop through adapters to handler conversions of data. """
		for evt_key in adapters:
			if (evt_key == msg.message_header.message_type):
				if server.get_event_def(msg.event_code, "IGNITION_ON", "IGNITION_OFF", "TIME_DISTANCE", "IDLE_RECEIPT", "PARKING_HEARTBEAT"):
					""" we have a match, create the class. """
					adapter = adapters.get(evt_key)(msg)
					""" call the transform method and print. """
					""" TODO: replace print with sending to endpoint. """
					server.log.debug(adapter.transform())	

logging.basicConfig(format=LOG_FORMAT)
log = logging.getLogger(__name__)
log.setLevel(LOG_LEVEL)
log.addHandler(RotatingFileHandler(LOG_FILE, maxBytes=LOG_MAXBYTES, backupCount=LOG_BACKUPS))

def main():



	server = ServerFixture("CALAMP", log)
	""" uncomment individual methods below to test discrete components. """
	# sim_opt_byte()
	# sim_ext_byte()
	# sim_msg_header()
	# sim_opt_header()
	# return
	# sim_evt_ack()
	# sim_evt_report()

	# packet_handler(server, SimData.evt_rpt_mini)
	# return

	sim_messages = {}
	sim_messages[0] = SimData.evt_ack
	sim_messages[1] = SimData.evt_rpt
	sim_messages[2] = SimData.evt_rpt_mini
	sim_messages[3] = SimData.id_rpt

	for key in sim_messages:
		packet_handler(server, sim_messages.get(key))


if __name__ == "__main__":
	main()

