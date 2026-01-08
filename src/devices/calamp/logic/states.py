import datetime
import enum
from devices.calamp.logic import Timeouts
from devices.calamp.logic import DeviceStates
from devices.calamp.logic import Notify

from devices.calamp.config import CalampEvents

class StatesWrapper:
	def __init__(self, state=None, event=None, notification=None):
		self._state = state
		self._state_change = False
		self._state_prev = state
		self._event = event
		# self._event_handler = event_handler
		self._event_notify = False
		self._notification = notification
		self._timestamp = datetime.datetime.now()

	def __dict__(self):
		return {
			'state': self.current.name,
			'previous_state': self.prev.name ,
			'change': self.change,
			'timestamp': self.timestamp.timestamp(),
			'notify': self.note,
			'notification': self.notification.name
		}

	# def reg_event_handler(self, event_handler):
	# 	self._event_handler = event_handler

	def enter_state(self, new_state, timeout=None):
		if (self._state == None):
			self._state = DeviceStates.UNKNOWN
		self._state_prev = self._state
		self._state = new_state

		if (self._state_prev != self._state):
			self._state_change = True

		self._timestamp = datetime.datetime.now()
		if (timeout):
			self._timeout = datetime.datetime.now() + datetime.timedelta(seconds=timeout.value)

	def notify(self, event):
		self._event_notify = True
		self._notification = event

		# if (self._event_handler != None):
		# 	self._event_handler(event)

	@property
	def current(self):
		return self._state
	@property
	def event(self):
		return self._event
	# @property
	# def event_handler(self):
	# 	return self._event_handler
	@property
	def timestamp(self):
		return self._timestamp
	@property
	def change(self):
		return self._state_change
	@property
	def prev(self):
		return self._state_prev
	@property
	def note(self):
		return self._event_notify
	@property
	def notification(self):
		return self._notification

class DeviceState(StatesWrapper):
	def __init__(self, state=None, event=None, notification=None):
		StatesWrapper.__init__(self, state, event, notification)

	""" return True if state changes False if same. """
	def event_handler(self, event):

		""" reset the _state_change flag. """
		self._state_change = False

		""" reset the _event_notify flag. """
		self._event_notify = False
		if self._event_notify == False:
			self._notification = Notify.OK

		if (self.event == event):
			""" proc used for timeout handling. """
			self._proc()
			return

		if (event == CalampEvents.IGNITION_ON.value):
			self.enter_state(DeviceStates.IGNITION_ON, Timeouts.IGNITION_ON)
			return
		if (event == CalampEvents.IGNITION_OFF.value):
			self.enter_state(DeviceStates.IGNITION_OFF, Timeouts.IGNITION_OFF)
			return
		if (event == CalampEvents.PARKING_HEARTBEAT.value):
			self.enter_state(DeviceStates.PARKED)
			return
		if (event == CalampEvents.MOVING_POST_IG.value):
			self.enter_state(DeviceStates.MOVING)
			return
		if (event == CalampEvents.IDLE_END.value):
			self.enter_state(DeviceStates.MOVING)
			return
		if (event == CalampEvents.OVERSPEED.value):
			self.enter_state(DeviceStates.OVER_SPEED)
			return
		if (event == CalampEvents.IDLE.value):
			self.enter_state(DeviceStates.IDLE)
			return
		if (event == CalampEvents.OVERSPEED_END.value):
			self.enter_state(DeviceStates.MOVING)
			return
		if (event == CalampEvents.PARKING_HEARTBEAT.value):
			self.notify(CalampEvents.PARKING_HEARTBEAT)
			return
		if (event == CalampEvents.CALAMP_BATT_LOW.value):
			self.notify(CalampEvents.CALAMP_BATT_LOW)
			return
		if (event == CalampEvents.VBATT_LOW.value):
			self.notify(Notify.VEHICLE_BATT_LOW)
			return
		if (event == CalampEvents.CALAMP_BATT_LOW.value):
			self.notify(Notify.DEVICE_BATT_LOW)
			return
		if (event == CalampEvents.OTA_DOWNLOAD.value):
			self.notify(Notify.OTA_DOWNLOAD)
			return
		if (event == CalampEvents.OTA_COMPLETE.value):
			self.notify(Notify.OTA_COMPLETE)
			return
		if (event == CalampEvents.BATT_PWR.value):
			self.notify(CalampEvents.BATT_PWR)
			return
		if (event == CalampEvents.SRC_PWR.value):
			self.notify(CalampEvents.SRC_PWR)
			return
		if (event == CalampEvents.POWER_UP.value):
			self.notify(CalampEvents.POWER_UP)
			return
		if (event == CalampEvents.WAKE_UP.value):
			self.notify(CalampEvents.WAKE_UP)
			return
		if (event == CalampEvents.MOVING_POST_IG.value):
			self.notify(CalampEvents.MOVING_POST_IG)
			return
		if (event == CalampEvents.TEST_PING.value):
			self.notify(CalampEvents.TEST_PING)
			return
		if (event == CalampEvents.DEVICE_UNPLUGGED.value):
			self.notify(CalampEvents.DEVICE_UNPLUGGED)
			return
		if (event == CalampEvents.DEVICE_PLUGGED_IN.value):
			self.notify(CalampEvents.DEVICE_PLUGGED_IN)
			return
		if (event == CalampEvents.RESERVED_20.value):
			self.notify(CalampEvents.RESERVED_20)
			return
		if (event == CalampEvents.RESERVED_21.value):
			self.notify(CalampEvents.RESERVED_21)
			return
		if (event == CalampEvents.RESERVED_22.value):
			self.notify(CalampEvents.RESERVED_22)
			return
		if (event == CalampEvents.RESERVED_23.value):
			self.notify(CalampEvents.RESERVED_23)
			return
		if (event == CalampEvents.RESERVED_24.value):
			self.notify(CalampEvents.RESERVED_24)
			return

	def _proc(self):
		if (self.current == None):
			self.enter_state(DeviceStates.UNKNOWN)
			return
