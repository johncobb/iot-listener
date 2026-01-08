
import sys
import os
import sqlite3
import datetime
from devices.calamp.api import MessageTypes
from db import DatabaseProviders
from db import DatabaseFactory
from db.dal import dal

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

""" example data """
_mobile_id = "4641143372"
_packet = "8305464114337201010102002452d0c1ca52d0c1ca1820fe44cecce3a4000081a90000000500fc08220015ffbb0f0d07002f0a100000002ee8000142440000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"



_sql_insert_device = "INSERT INTO Devices (AccountId, MobileId, IMEI, ICCID, Firmware, Script, Notes) VALUES ({}, '{}', '{}', '{}', '{}', '{}', '{}');"
_sql_insert_asset = "INSERT INTO Assets (AccountId, GroupId, DeviceId, VIN, Name, Label, MiniLabel) VALUES ({}, {}, {}, '{}', '{}', '{}', '{}');"

def db_insert_device(conn):
	""" cell fields intentionally left blank, allow to populate on first id report. """
	sql = _sql_insert_device.format(_account_id, _mobile_id, "", "", "", "", _notes)
	dal.exec_sql(conn, sql)

def db_insert_asset(conn):
	sql = _sql_insert_asset.format(_account_id, _group_id, _device_id, _vin, _name, _label, _label_mini)
	dal.exec_sql(conn, sql)
