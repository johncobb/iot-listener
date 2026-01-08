
""" DeviceLogs sql Table """
LOGS_SQL = "INSERT INTO DeviceLogs (MobileId, PacketData, PacketIp, PacketPort, CreatedDate) VALUES('{mobile_id}', '{packet_data}', '{packet_ip}', {packet_port}, UTC_TIMESTAMP(3));"

""" DeviceTelemetry sql Table"""
TELEM_SQL = """INSERT INTO DeviceTelemetry (MobileId, Latitude, Longitude, Speed,
                    Heading, Odometer, VirtualOdometer, EngineHours,
                    GPIO_01, GPIO_02, GPIO_03, GPIO_04, GPIO_05, GPIO_06, GPIO_07, GPIO_08,
                    Accumulator_01, Accumulator_02, Accumulator_03, Accumulator_04,
                    Accumulator_05, Accumulator_06, Accumulator_07, Accumulator_08,
                    Accumulator_09, Accumulator_10, Accumulator_11, Accumulator_12,
                    Accumulator_13, Accumulator_14, Accumulator_15, Accumulator_16,
                    CreatedDate)
                    VALUES(
                        '{mobile_id}', {latitude}, {longitude}, {speed}, {heading}, {odometer}, {virtual_odometer}, {engine_hours},
                        {gpio_1}, {gpio_2}, {gpio_3}, {gpio_4}, {gpio_5}, {gpio_6}, {gpio_7}, {gpio_8},
                        {accumulator_1}, {accumulator_2}, {accumulator_3}, {accumulator_4}, {accumulator_5}, {accumulator_6},
                        {accumulator_7}, {accumulator_8}, {accumulator_9}, {accumulator_10}, {accumulator_11}, {accumulator_12},
                        {accumulator_13}, {accumulator_14}, {accumulator_15}, {accumulator_16}, UTC_TIMESTAMP(3))
                    ON DUPLICATE KEY UPDATE RecordId=LAST_INSERT_ID(RecordId), Latitude={latitude}, Longitude={longitude},
                        Speed={speed}, Heading={heading}, Odometer={odometer}, VirtualOdometer={virtual_odometer}, EngineHours={engine_hours},
                        GPIO_01={gpio_1}, GPIO_02={gpio_2}, GPIO_03={gpio_3}, GPIO_04={gpio_4},
                        GPIO_05={gpio_5}, GPIO_06={gpio_6}, GPIO_07={gpio_7}, GPIO_08={gpio_8},
                        Accumulator_01={accumulator_1}, Accumulator_02={accumulator_2}, Accumulator_03={accumulator_3}, Accumulator_04={accumulator_4},
                        Accumulator_05={accumulator_5}, Accumulator_06={accumulator_6}, Accumulator_07={accumulator_7}, Accumulator_08={accumulator_8},
                        Accumulator_09={accumulator_9}, Accumulator_10={accumulator_10}, Accumulator_11={accumulator_11}, Accumulator_12={accumulator_12},
                        Accumulator_13={accumulator_13}, Accumulator_14={accumulator_14}, Accumulator_15={accumulator_15}, Accumulator_16={accumulator_16};"""

""" ActivityLog sql Table """
ACTIVITYLOG_SQL_INSERT = """INSERT INTO ActivityLog (MobileId, Activity, StartTime, EndTime, StartLatitude,
                                StartLongitude)
                                VALUES(
                                    '{}', {}, UTC_TIMESTAMP(3), FROM_UNIXTIME(1), {}, {});"""

ACTIVITYLOG_SQL_LOOKUP = """SELECT RecordId FROM ActivityLog WHERE MobileId = '{}' AND Activity = {} AND EndTime = FROM_UNIXTIME(1); """

ACTIVITYLOG_SQL_UPDATE = """UPDATE ActivityLog SET EndTime = UTC_TIMESTAMP(3), EndLatitude = {}, EndLongitude = {}
                            WHERE
                                MobileId = '{}' AND Activity = {} AND EndTime = FROM_UNIXTIME(1);"""

""" DeviceMeta sql Table """
META_SQL = """INSERT INTO DeviceMeta (MobileId, ScriptVersion, AppId, AppVersion,
                    VehicleClass, HttpOtaUpdateStatusOk, GpsAntennaStatusOk, GpsReceiverTestOk, GpsReceiverTracking,
                    ModemSelection, MobileIdType, QueryId, ESN, IMEI, IMSI, MobileIdentificationNumber, ICCID, CreatedDate, LastUpdate)
                    VALUES (
                        '{mobile_id}', '{script_version}', {app_id}, '{app_version}', {vehicle_class}, {http_ota_update_status_ok},
                        {gps_antenna_status_ok}, {gps_receiver_test_ok}, {gps_receiver_tracking}, {modem_selection}, {mobile_id_type}, {query_id},
                        '{esn}', '{imei}', '{imsi}', '{mobile_identification_number}', '{iccid}', UTC_TIMESTAMP(3), UTC_TIMESTAMP(3))
                    ON DUPLICATE KEY UPDATE RecordId=LAST_INSERT_ID(RecordId), ScriptVersion='{script_version}', AppId={app_id},
                        AppVersion='{app_version}', VehicleClass={vehicle_class}, HttpOtaUpdateStatusOk={http_ota_update_status_ok},
                        GpsAntennaStatusOk={gps_antenna_status_ok}, GpsReceiverTestOk={gps_receiver_test_ok},
                        GpsReceiverTracking={gps_receiver_tracking}, ModemSelection={modem_selection}, MobileIdType={mobile_id_type},
                        QueryId={query_id}, ESN='{esn}', IMEI='{imei}', IMSI='{imsi}',
                        MobileIdentificationNumber='{mobile_identification_number}', ICCID='{iccid}', LastUpdate=UTC_TIMESTAMP(3);"""

""" Assets SQL Table """
ASSETS_SQL = """INSERT INTO Assets (MobileId, LastEpoch, LastState, LastEvent, LastLatitude, LastLongitude, LastSpeed, LastHeading, EngineHours, CreatedDate, LastUpdate)
                                VALUES ('{mobile_id}', {last_epoch}, {last_state}, {last_event}, {last_latitude}, {last_longitude}, {last_speed}, {last_heading}, {engine_hours}, UTC_TIMESTAMP(3), UTC_TIMESTAMP(3))
                ON DUPLICATE KEY UPDATE RecordId=LAST_INSERT_ID(RecordId), LastEpoch={last_epoch}, LastState={last_state}, LastEvent={last_event}, LastLatitude={last_latitude}, LastLongitude={last_longitude}, LastSpeed={last_speed}, LastHeading={last_heading},
                                EngineHours = {engine_hours}, LastUpdate = UTC_TIMESTAMP(3);"""

""" Devices SQL Table """
DEVICES_SQL = """INSERT INTO Devices (MobileId, IMEI, ICCID, Script, CreatedDate, LastUpdate)
                        VALUES ('{mobile_id}', '{imei}', '{iccid}', '{script}', UTC_TIMESTAMP(3), UTC_TIMESTAMP(3))
                        ON DUPLICATE KEY UPDATE RecordId=LAST_INSERT_ID(RecordId), IMEI='{imei}', ICCID='{iccid}', Script='{script}', LastUpdate=UTC_TIMESTAMP(3);"""

""" Landmarks SQL Table """
LANDMARKS_SQL_LOOKUP_ALL = "SELECT * FROM Landmarks WHERE Archived = 0;"

""" LandmarkLog SQL Table """
LANDMARKACTIVITY_SQL_INSERT = """INSERT INTO LandmarkActivity (LandmarkId, MobileId, ArrivalTime, StartLatitude, StartLongitude)
                            Values (
                                {}, '{}', FROM_UNIXTIME({}), {}, {});"""

LANDMARKACTIVITY_SQL_LOOKUP = "SELECT RecordId FROM LandmarkActivity WHERE LandmarkId = '{}' AND MobileId = '{}' AND DepartureTime IS NULL;"

LANDMARKACTIVITY_SQL_UPDATE = """UPDATE LandmarkActivity SET DepartureTime = FROM_UNIXTIME({}), EndLatitude = {}, EndLongitude = {}
                            WHERE
                                RecordId = '{}';"""

class Logs:
    def insert(self, report):
        mapping = {
            'mobile_id':report.mobile_id,
            'packet_data':report.packet.to_str,
            'packet_ip':report.packet.ip,
            'packet_port':report.packet.port
        }
        return LOGS_SQL.format_map(mapping)

class Telemetry:
    def insert(self, report, odometer, virtual_odometer, engine_hours):
        mapping = {
                        'mobile_id':report.mobile_id,
                        'latitude':report.message.loc.latitude_radix,
                        'longitude':report.message.loc.longitude_radix,
                        'speed':report.message.loc.speed_mph,
                        'heading':report.message.loc.heading,
                        'odometer':odometer,
                        'virtual_odometer':virtual_odometer,
                        'engine_hours':engine_hours,
                        'gpio_1':report.message.gpio.bit_0,
                        'gpio_2':report.message.gpio.bit_1,
                        'gpio_3':report.message.gpio.bit_2,
                        'gpio_4':report.message.gpio.bit_3,
                        'gpio_5':report.message.gpio.bit_4,
                        'gpio_6':report.message.gpio.bit_5,
                        'gpio_7':report.message.gpio.bit_6,
                        'gpio_8':report.message.gpio.bit_7,
                        'accumulator_1':report.message.accumulators(0).val,
                        'accumulator_2':report.message.accumulators(1).val,
                        'accumulator_3':report.message.accumulators(2).val,
                        'accumulator_4':report.message.accumulators(3).val,
                        'accumulator_5':report.message.accumulators(4).val,
                        'accumulator_6':report.message.accumulators(5).val,
                        'accumulator_7':report.message.accumulators(6).val,
                        'accumulator_8':report.message.accumulators(7).val,
                        'accumulator_9':report.message.accumulators(8).val,
                        'accumulator_10':report.message.accumulators(9).val,
                        'accumulator_11':report.message.accumulators(10).val,
                        'accumulator_12':report.message.accumulators(11).val,
                        'accumulator_13':report.message.accumulators(12).val,
                        'accumulator_14':report.message.accumulators(13).val,
                        'accumulator_15':report.message.accumulators(14).val,
                        'accumulator_16':report.message.accumulators(15).val
        }
        return TELEM_SQL.format_map(mapping)

class Meta:
    def insert(self, report):
        mapping = {
            'mobile_id':report.mobile_id,
            'script_version':report.message.script,
            'app_id':report.message.app_id,
            'app_version':report.message.app_version,
            'vehicle_class':report.message.vehicle_class,
            'http_ota_update_status_ok':report.message.gps_byte.http_ota_update_status_ok,
            'gps_antenna_status_ok':report.message.gps_byte.gps_antenna_status_ok,
            'gps_receiver_test_ok':report.message.gps_byte.gps_receiver_test_ok,
            'gps_receiver_tracking':report.message.gps_byte.gps_receiver_tracking,
            'modem_selection':report.message.modem_selection,
            'mobile_id_type':report.message.mobile_id_type,
            'query_id':report.message.query_id,
            'esn':report.message.cell_info.esn,
            'imei':report.message.cell_info.imei,
            'imsi':report.message.cell_info.imsi,
            'mobile_identification_number':report.message.cell_info.min,
            'iccid':report.message.cell_info.iccid
        }
        return META_SQL.format_map(mapping)

class Assets:
    def insert(self, report, state):
        mapping = {
            'mobile_id':report.mobile_id,
            'last_epoch':report.message.update_time,
            'last_state':state.value,
            'last_event':report.message.event_code,
            'last_latitude':report.message.loc.latitude_radix,
            'last_longitude':report.message.loc.longitude_radix,
            'last_speed':report.message.loc.speed_mph,
            'last_heading':report.message.loc.heading,
            'engine_hours':report.message.accumulators.engine_hours
        }
        return ASSETS_SQL.format_map(mapping)

class Devices:
    def insert(self, report):
        mapping = {
            'mobile_id':report.mobile_id,
            'imei':report.message.cell_info.imei,
            'iccid':report.message.cell_info.iccid,
            'script':report.message.script
        }
        return DEVICES_SQL.format_map(mapping)

class ActivityLog:
    def insert(self, report, state):
        return ACTIVITYLOG_SQL_INSERT.format(
            report.mobile_id,
            state.value,
            report.message.loc.latitude_radix,
            report.message.loc.longitude_radix
        )

    def update(self, report, last_state):
        return ACTIVITYLOG_SQL_UPDATE.format(
            report.message.loc.latitude_radix,
            report.message.loc.longitude_radix,
            report.mobile_id,
            last_state.value
            )

    def lookup(self, report, last_state):
        return ACTIVITYLOG_SQL_LOOKUP.format(
            report.mobile_id,
            last_state.value
            )

class LandmarkActivity:
    def insert(self, report, landmark_id):
        return LANDMARKACTIVITY_SQL_INSERT.format(landmark_id,
                       report.mobile_id, report.message.update_time,
                       report.message.loc.latitude_radix, report.message.loc.longitude_radix)

    def lookup(self, report, landmark_id):
        return LANDMARKACTIVITY_SQL_LOOKUP.format(landmark_id, report.mobile_id)

    def update(self, report, landmarklog_id):
        return LANDMARKACTIVITY_SQL_UPDATE.format(report.message.update_time,
                       report.message.loc.latitude_radix,
                       report.loc.longitude_radix,
                       landmarklog_id)

class Landmarks:
    def lookup_all(self):
        return LANDMARKS_SQL_LOOKUP_ALL

class Device:
    logs = Logs()
    telemetry = Telemetry()
    meta = Meta()
    assets = Assets()
    devices = Devices()
    activitylog = ActivityLog()
    landmarks = Landmarks()
    landmarkactivity = LandmarkActivity()
