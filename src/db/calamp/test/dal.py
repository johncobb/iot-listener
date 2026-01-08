
import sys
import os
import sqlite3
import datetime

from devices.calamp.api import MessageTypes
from db import DatabaseProviders
from db import DatabaseFactory
from db import example_data as dat
from db.dal_device import db_log_device_meta
from db.dal_device import db_log_device_telem
from db.dal_device import db_log_device_telem_timescale
from db.dal_asset import db_log_asset_loc

""" generate tables: """
""" sqlite3 redskyapp < src/db/db_gen_schema.sql """

_sql_insert_device_logs = "INSERT INTO DeviceLogs (MobileId, Packet) VALUES ('{}', '{}');"

def exec_sql(conn, sql):
	cursor = conn.cursor()
	return cursor.execute(sql)

def db_log_packet(conn, mobile_id, packet):
	sql = _sql_insert_device_logs.format(mobile_id, packet)
	exec_sql(conn, sql)


def db_log_message(conn, msg):
	if (msg.message_type == MessageTypes.ID_REPORT):
		db_log_device_meta(conn, msg)

	if (msg.message_type == MessageTypes.EVENT_REPORT or msg.message_type == MessageTypes.MINI_EVENT_REPORT):
		db_log_device_telem(conn, msg)
		# db_log_device_telem_timescale(conn, msg)
		db_log_asset_loc(conn, msg)

