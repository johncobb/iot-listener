import struct

from lib import IoByte
from lib import IoByteUtil
from devices.calamp.api import CalampScriptInfo, FixByteMini
from devices.calamp.api import CommByteMini
from devices.calamp.api import GpsByte
from devices.calamp.api import CalampAppVersion
from devices.calamp.api import CalampCellInfo
from devices.calamp.api import CalampMessageBase

from devices.calamp.messages.schema import MessageConfig as cf

class IdReport(CalampMessageBase):
	def __init__ (self, options_header, message_header):
		CalampMessageBase.__init__(self, options_header, message_header)
		self.script_version = None
		self.config_version = None
		self.script = CalampScriptInfo(0, 0)
		self.app_version = CalampAppVersion(0, 0, 0)

		self.vehicle_class = None
		self.modem_selection = None
		self.app_id = None
		self.mobile_id_type = None
		self.cell_info = CalampCellInfo()

		""" TODO: extensions not yet implemented. """
		# self.extensions = None in calampbase
  
	def __dict__(self):
		return {
			'options_header': self.options_header.__dict__(),
			'message_header': self.message_header.__dict__(),
			'script': str(self.script),
			'app_version': str(self.app_version),
			'vehicle_class': self.vehicle_class,
			'gps': self.gps_byte.__dict__(),
			'modem_selection': self.modem_selection,
			'app_id': self.app_id,
			'mobile_id_type': self.mobile_id_type,
			'query_id': self.query_id,
			'cell_info': self.cell_info.__dict__()
		}

	@property
	def satellites(self):
		""" IdReport does not have satellite attribute but inherits """
		""" from CalampMessageBase. Return None in this case. """
		return None

	def parse(self, buffer):
		self.script.script_version = self.buffer.read(cf.SCRIPT_VERSION_LEN)
		self.script.config_version = self.buffer.read(cf.CONFIG_VERSION_LEN)

		self.app_version.byte_0 = self.buffer.read()
		self.app_version.byte_1 = self.buffer.read()
		self.app_version.byte_2 = self.buffer.read()

		self.vehicle_class = self.buffer.read(cf.VEHICLE_CLASS_LEN)
		self.gps_byte = GpsByte(self.buffer.read(cf.GPS_BYTE_LEN))
		self.modem_selection = self.buffer.read(cf.MODEM_SELECTION_LEN)
		self.app_id = self.buffer.read(cf.APP_ID_LEN)
		self.mobile_id_type = self.buffer.read(cf.MOBILEID_TYPE_LEN)
		self.query_id = struct.unpack(">i", self.buffer.read(cf.QUERY_ID_LEN))[0]
		self.cell_info.esn = IoByteUtil.bcd_unpack(self.buffer, cf.CELL_ESN_LEN)
		self.cell_info.imei = IoByteUtil.bcd_unpack(self.buffer, cf.CELL_IMEI_LEN)
		self.cell_info.imsi = IoByteUtil.bcd_unpack(self.buffer, cf.CELL_IMSI_LEN)
		self.cell_info.min = IoByteUtil.bcd_unpack(self.buffer, cf.CELL_MIN_LEN)
		self.cell_info.iccid = IoByteUtil.bcd_unpack(self.buffer, cf.CELL_ICCID_LEN)

		""" TODO: extensions not yet implemented. """
		# self.extensions = self.parse_extension_strings(self.buffer)
	
	def log(self, log):	
		log.debug("id report:")
		log.debug("script_version: {}".format(self.script.script_version))
		log.debug("config_version: {}".format(self.script.config_version))
		log.debug("app_id: {}".format(self.app_id))
		log.debug("app_version: ({}, {}, {})".format(self.app_version.byte_0, self.app_version.byte_1, self.app_version.byte_2))
		log.debug("vehicle_class: {}".format(self.vehicle_class))
		log.debug("gps_byte: {}".format(hex(self.gps_byte.byte_val)))
		log.debug(" - http_ota_update_status_ok: {}".format(self.gps_byte.http_ota_update_status_ok))
		log.debug(" - gps_status_ok: {}".format(self.gps_byte.gps_antenna_status_ok))
		log.debug(" - gps_receiver_test: {}".format(self.gps_byte.gps_receiver_test_ok))
		log.debug(" - gps_receiver_tracking: {}".format(self.gps_byte.gps_receiver_tracking))
		log.debug("modem_selection: {}".format(self.modem_selection))
		log.debug("query_id: {}".format(self.query_id))
		log.debug("cell_info:")
		log.debug(" - esn: {}".format(self.cell_info.esn))
		log.debug(" - imei: {}".format(self.cell_info.imei))
		log.debug(" - imsi: {}".format(self.cell_info.imsi))
		log.debug(" - min: {}".format(self.cell_info.min))
		log.debug(" - iccid: {}".format(self.cell_info.iccid))
		""" TODO: extensions not yet implemented. """
		# log.debug("extension_strings:")
		# if (self.extensions != None):
		# 	for i in self.extensions:
		# 		log.debug(" - ext[{}]: {}".format(self.extension_strings.tag , self.extension_strings.data))