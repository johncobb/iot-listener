
import sys
import os
import sqlite3
import datetime

from devices.calamp.api import MessageTypes
from db import DatabaseProviders
from db import DatabaseFactory
from db.dal import dal
from db.dal import dal_device

_sql_update = "UPDATE Assets SET LastPing = DATETIME(), LastLatitude = {}, LastLongitude = {}, LastSpeed = {}, LastHeading = {}, Odometer = {}, EngineHours = {}, LastUpdate = DATETIME() WHERE DeviceId = {};"

_odometer = 32875
_virtual_odometer = 33200
_engine_hours = 42782
def db_log_asset_loc(conn, msg):
	row = dal_device.lookup(conn, msg.mobile_id)
	if (row == None):
		return
	_device_id = row[0]

	sql = _sql_update.format(msg.loc.latitude_radix, msg.loc.longitude_radix, msg.loc.speed, msg.loc.heading, _odometer, _engine_hours, _device_id)
	dal.exec_sql(conn, sql)