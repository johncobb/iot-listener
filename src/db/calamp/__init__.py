from db import Database
from db import DbManager
from db.calamp.connection import Device
from devices.calamp.api import MessageTypes
# from db.logic.landmark_proccessor import LandmarksProcessor
from devices.calamp.logic.landmark import LandmarksProcessor

class CalampDatabase(Database):
    def __init__(self, log):
        Database.__init__(self, log)

    def device_logs(self, report):
        self.enqueue(Device.logs.insert(report))

    def device_telemetry(self, report, odometer, virtual_odometer, engine_hours):
        self.enqueue(Device.telemetry.insert(report, odometer, virtual_odometer, engine_hours))

    def device_meta(self, report):
        self.enqueue(Device.meta.insert(report))

    def assets(self, report, state):
        self.enqueue(Device.assets.insert(report, state))

    def devices(self, report):
        self.enqueue(Device.devices.insert(report))

    def activitylog(self, report, last_state, state):
        def callback(response):
            if last_state == state:
                return

            self.enqueue(Device.activitylog.update(report, last_state))

        self.enqueue(Device.activitylog.insert(report, state), callback)

    def get_landmarks(self):
        return self.db.lookup_all(Device.landmarks.lookup_all())

    def landmarklactivity(self, report, landmark_id):
        record_id = self.db.lookup(Device.landmarkactivity.lookup(report, landmark_id))
        if (record_id == None):
            self.db.exec_sql(Device.landmarkactivity.insert(report, landmark_id))
        else:
            self.db.exec_sql(Device.landmarkactivity.update(report, record_id[0]))
            self.db.exec_sql(Device.landmarkactivity.insert(report,landmark_id))

class CalampDbManager(DbManager):
    def __init__(self, log):
        DbManager.__init__(self, log, database=CalampDatabase)

    def _handle_db(self, db_report):
        (report, state_change, last_state, current_state, odometer, virtual_odometer, engine_hours) = db_report
        self._db.device_logs(report)
        message = report.message

        if (message.message_type == MessageTypes.EVENT_REPORT or message.message_type == MessageTypes.MINI_EVENT_REPORT):
            self._db.device_telemetry(report, odometer, virtual_odometer, engine_hours)
            self._db.assets(report, current_state)
            if (state_change):
                self._db.activitylog(report, last_state, current_state)
        elif (message.message_type == MessageTypes.ID_REPORT):
            self._db.device_meta(report)
            self._db.devices(report)

