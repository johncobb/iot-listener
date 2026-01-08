
import sys
import os
# import core_config
import src.settings as core_config
from src.db import DatabaseProviders
from src.db import DatabaseFactory
from src.devices.calamp.tests import ServerFixture
from src.db import dal

_server = None
_db = None
_conn = None


MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
MYSQLITE_DATABASE = os.getenv('MYSQLITE_DATABASE')

""" example data """
_packet = "8305464114337201010102002452d0c1ca52d0c1ca1820fe44cecce3a4000081a90000000500fc08220015ffbb0f0d07002f0a100000002ee8000142440000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
_mobile_id = "4641143372"
_account_id = 1
_group_id = 1
_device_id = 1
_vin = "4VG7DARJ6XN765691"
_name = "hack3d"
_label = "My Label"
_label_mini = "My Mini Label"

_latitude = 40.4815428
_longitude = -82.543318
_speed = 5
_heading = 252
_odometer = 32875
_virtual_odometer = 33200
_engine_hours = 42782
_imei = "357805023984942"
_iccid = "891004234814455936F"
_firmware = "1.0.1"
_script = "rs.beta.01"
_notes = "I like to move it move it..."



""" don't forget to generate tables: """
""" sqlite3 redskyapp < src/db/db_gen_schema.sql """

if __name__ == "__main__":

	_db = DatabaseFactory.get_database(DatabaseProviders.MySqlite)
	_conn = _db.connect()

	row = dal.db_lookup_device(_conn, "4641143372")
	print("RecordId: {}".format(row[0]))



	print(_db)