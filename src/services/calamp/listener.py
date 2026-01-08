import logging

from services.listener import UdpServer
from services.calamp import CalampClientManager
from db.calamp import CalampDbManager

from settings import PROC_ADAPTER_ENABLE
from settings import BB_HOST
from settings import BB_PORT
from settings import BB_LOGINFO

from settings import HOST
from settings import PORT
from settings import COPY_TO_PRODUCTION
from settings import PL_HOST
from settings import PL_PORT
from settings import REMOTE_HOST
from settings import REMOTE_PORT

from settings import LOG_LEVEL
from settings import LOG_FILE
from settings import LOG_RAW

from settings import SEND_ACK

from settings import PROC_DB_ENABLE

class CalampUdpServer(UdpServer):
	def __init__(self, log):
		UdpServer.__init__(self, log, CalampClientManager, CalampDbManager)

	def _log_startup(self):
		self._log.info("{}({}) starting.".format(self.name, self.ident))
		self._log.debug(" - host: {}:{}".format(HOST, PORT))
		self._log.info(" - log_level: {}".format(logging.getLevelName(LOG_LEVEL)))
		self._log.info(" - log_file: {}".format(LOG_FILE))
		self._log.info(" - log_raw: {}".format(LOG_RAW))
		self._log.info(" - send_ack: {}".format(SEND_ACK))
		self._log.info(" - copy to production: {}".format(COPY_TO_PRODUCTION))
		self._log.debug("  - remote_host: {}:{}".format(REMOTE_HOST, REMOTE_PORT))
		self._log.info(" - proc_adapter_enable: {}".format(PROC_ADAPTER_ENABLE))
		self._log.debug("  - bb_host: {}:{}".format(BB_HOST, BB_PORT))
		self._log.info("  - bb_logging: {}".format(BB_LOGINFO))
		self._log.info(" - proc_db_enable: {}".format(PROC_DB_ENABLE))