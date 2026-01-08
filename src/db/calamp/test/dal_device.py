
import sys
import os
import sqlite3
import datetime

from devices.calamp.api import MessageTypes
from db import DatabaseProviders
from db import DatabaseFactory
from db.dal import dal

_odometer = 32875
_virtual_odometer = 33200
_engine_hours = 42782

_sql_device_lookup = "SELECT MobileId FROM DeviceMeta WHERE MobileId = '{}';"
_sql_meta_insert = """INSERT INTO DeviceMeta 
								(MobileId, ScriptVersion, ConfigVersion, AppId, AppVersion, 
								VehicleClass, HttpOtaUpdateStatusOk, GpsAntennaStatusOk, GpsReceiverTestOk, GpsReceiverTracking, 
								ModemSelection, MobileIdType, QueryId, 
								ESN, IMEI, IMSI, MobileIdentificationNumber, ICCID) 
							VALUES ('{}', {}, {}, {}, '{}', {}, {}, {}, {}, {}, {}, {}, {}, '{}', '{}', '{}', '{}', '{}');"""

_sql_meta_update = """UPDATE DeviceMeta SET 
								ScriptVersion = {}, ConfigVersion = {}, AppId = {}, AppVersion = '{}', 
								VehicleClass = {}, HttpOtaUpdateStatusOk = {}, GpsAntennaStatusOk = {}, GpsReceiverTestOk = {}, GpsReceiverTracking = {}, 
								ModemSelection = {}, MobileIdType = {}, QueryId = {}, 
								ESN = '{}', IMEI = '{}', IMSI = '{}', MobileIdentificationNumber = '{}', ICCID = '{}' 
								WHERE MobileId = '{}';"""
_sql_telem_insert = """INSERT INTO DeviceTelemetry 
						(DeviceId, MobileId, Latitude, Longitude, Speed, 
						Heading, Odometer, VirtualOdometer, EngineHours, 
						GPIO_01, GPIO_02, GPIO_03, GPIO_04, 
						Accumulator_01, Accumulator_02, Accumulator_03, Accumulator_04, 
						Accumulator_05, Accumulator_06, Accumulator_07, Accumulator_08) 
							VALUES 
						({}, '{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {});"""

_sql_telem_timescale_insert = "INSERT INTO {} {} VALUES {};"
_telem_fields = """(DeviceId, MobileId, Latitude, Longitude, Speed, 
								Heading, Odometer, VirtualOdometer, EngineHours, 
								GPIO_01, GPIO_02, GPIO_03, GPIO_04, 
								Accumulator_01, Accumulator_02, Accumulator_03, Accumulator_04, 
								Accumulator_05, Accumulator_06, Accumulator_07, Accumulator_08)"""
_telem_params = "({}, '{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})"

def _lookup(conn, mobile_id):
	sql = _sql_device_lookup.format(mobile_id)
	cursor = dal.exec_sql(conn, sql)
	row = cursor.fetchone()

	return row

def lookup(conn, mobile_id):
	return _lookup(conn, mobile_id)

def _add_meta(conn, msg):
	sql = _sql_meta_insert.format(msg.mobile_id, 
						msg.script_version, 
						msg.config_version, 
						msg.app_id, 
						msg.app_version, 
						msg.vehicle_class, 
						msg.gps_byte.http_ota_update_status_ok, 
						msg.gps_byte.gps_antenna_status_ok, 
						msg.gps_byte.gps_receiver_test_ok, 
						msg.gps_byte.gps_receiver_tracking, 
						msg.modem_selection, 
						msg.mobile_id_type, 
						msg.query_id, 
						msg.cell_info.esn, 
						msg.cell_info.imei, 
						msg.cell_info.imsi, 
						msg.cell_info.min, 
						msg.cell_info.iccid)

	dal.exec_sql(conn, sql)

def _update_meta(conn, msg):
	sql = _sql_meta_update.format(msg.script_version, 
						msg.config_version, 
						msg.app_id, 
						msg.app_version, 
						msg.vehicle_class, 
						msg.gps_byte.http_ota_update_status_ok, 
						msg.gps_byte.gps_antenna_status_ok, 
						msg.gps_byte.gps_receiver_test_ok, 
						msg.gps_byte.gps_receiver_tracking, 
						msg.modem_selection, 
						msg.mobile_id_type, 
						msg.query_id, 
						msg.cell_info.esn, 
						msg.cell_info.imei, 
						msg.cell_info.imsi, 
						msg.cell_info.min, 
						msg.cell_info.iccid,
						msg.mobile_id)

	dal.exec_sql(conn, sql)

def _insert_telem(conn, msg):
	row = _lookup(conn, msg.mobile_id)
	if (row == None):
		return
	_device_id = row[0]

	sql = _sql_telem_insert.format(_device_id, msg.mobile_id, msg.loc.latitude_radix, msg.loc.longitude_radix, msg.loc.speed, msg.loc.heading, _odometer, _virtual_odometer, _engine_hours, msg.gpio.bit_0, msg.gpio.bit_1, msg.gpio.bit_2, msg.gpio.bit_3, 0, 0, 0, 0, 0, 0, 0, 0)
	dal.exec_sql(conn, sql)

def _insert_telem_timescale(conn, msg):
	row = _lookup(conn, msg.mobile_id)
	if (row == None):
		return
	_device_id = row[0]

	_timescale_year = datetime.date.today().year
	_timescale_month = datetime.date.today().month
	_timescale_table = "TIMESCALE_TELEM_{}_{}".format(str(_timescale_month).zfill(2), _timescale_year)

	_params = _telem_params.format(_device_id, msg.mobile_id, msg.loc.latitude_radix, msg.loc.longitude_radix, msg.loc.speed, msg.loc.heading, _odometer, _virtual_odometer, _engine_hours, msg.gpio.bit_0, msg.gpio.bit_1, msg.gpio.bit_2, msg.gpio.bit_3, 0, 0, 0, 0, 0, 0, 0, 0)
	sql = _sql_telem_timescale_insert.format(_timescale_table, _telem_fields, _params)
	dal.exec_sql(conn, sql)

def db_log_device_meta(conn, msg):
	row = _lookup(conn, msg.mobile_id)
	if (row == None):
		_add_meta(conn, msg)
	else:
		_update_meta(conn, msg)

def db_log_device_telem(conn, msg):
	_insert_telem(conn, msg)

def db_log_device_telem_timescale(conn, msg):
	_insert_telem_timescale(conn, msg)