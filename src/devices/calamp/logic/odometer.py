from pyproj import Geod
import numpy

from devices.calamp.logic import DeviceStates
from devices.calamp import MessageTypes

FACTORMM = 1609

class DeviceOdometer:
	"""
	Accumulates Idle (sec), Engine Hours (sec), and Distance (Odometer) (Meters)
	A trip are the events between a Ignition On and Ignition Off.
	"""
	def __init__(self, state):
		self._state = state		
		self._trip_idle = 0
		self._total_idle = 0
		self._trip_hours = 0
		self._total_engine_hours = 0
		self._trip_odometer = 0
		self._total_odometer = 0
		self._trip_virtual_odometer = 0
		self._total_virtual_odometer = 0
		self._last_point = None
		self._report = None
  
	def __dict__(self):
		return {
			'trip_idle_hours': self.trip_idle,
			'total_idle_hours': self.total_idle,
			'current_idle_hours': self.current_idle,
			'trip_engine_hours': self.trip_engine_hours,
			'total_engine_hours': self.total_engine_hours,
			'current_engine_hours': self.current_engine_hours,
			'trip_odometer': self.trip_odometer,
			'total_odometer': self.total_odometer,
			'current_odometer': self.current_odometer,
			'trip_virtual_odometer': self.trip_virtual_odometer,
			'total_virtual_odometer': self.total_virtual_odometer,
			'current_virtual_odometer': self.current_virtual_odometer
		}
  
	def log_trip(self, log, report):
		if report.message.message_type != MessageTypes.EVENT_REPORT:
			return
  
		# on a state change and on the ignition off report -> end of trip totals else: current trip
		if self._state.change and self._state.current == DeviceStates.IGNITION_OFF:
			log.info("client: {} trip_totals: idle: {} engine_hours: {} odometer: {} virtual_odometer: {}".format(report.message.mobile_id, self.total_idle, self.total_engine_hours, self.total_odometer, self.total_virtual_odometer))
		else:
			log.info("client: {} trip: idle: {}({}) engine_hours: {}({}) odometer: {}({}) virtual_odometer: {}({})".format(report.message.mobile_id, self.trip_idle, self.total_idle, self.trip_engine_hours, self.total_engine_hours, self.trip_odometer, self.total_odometer, self.trip_virtual_odometer, self.total_virtual_odometer))
		
	def _check_sequence_number(self, last_sequence_number, sequence_number):
		"""If the sequence number increases, we can assume the message is newer. There are a bunch of
  			of caviats to that so we are going to wait for a watchdog or something.
     		TODO: Implement a watchdog to determine message ordering and sequence is okay."""
		pass
  
	def _check_trip(self, trip, accumulator):
		"""Generally a trips value will only increase. If it doesn't, somethings up.
  			Values might not accumulate due to older messages coming in before newer ones."""
     
		# if the old trip value is greater that the new accumulator value... something is wrong
		if trip > accumulator:
			return trip

		# if the old trip value is less than the accumulator value... business as usual
		elif trip < accumulator:
			return accumulator

		# if they equal each other... who cares (accumulator is certified fresh)
		else:
			return accumulator

	def _virtual_odometer_proc(self, current_location, current_altitude) -> int:
    
		# if no other points have been recorded -> short circuit
		if (self._last_point is None):
			self._last_point = (current_location, current_altitude)
			return 0

		geom = Geod(ellps='WGS84')
		last_location, last_altitude = self._last_point
  
		# calculate the 2d distance between points
		azimuth1, azimuth2, distance_2d = geom.inv(last_location[1], last_location[0], current_location[1], current_location[0])
  
		# calculates distance using delta height or altitude. This assumes the earth is flat. This might be a problem if the points are too far apart.
		distance_3d = numpy.hypot(distance_2d, abs(last_altitude - current_altitude)/100)

		# set the last point after finding the distance
		self._last_point = (current_location, current_altitude)
		return round(distance_3d)
		
	def handler(self, report): 
		
		# if there is an event report... 
		if report.message.message_type != MessageTypes.EVENT_REPORT:
			return

		self._trip_idle = self._check_trip(self._trip_idle,report.message.accumulators.idle)
		self._trip_hours = self._check_trip(self._trip_hours, report.message.accumulators.engine_hours)
		self._trip_odometer = self._check_trip(self._trip_odometer, report.message.accumulators.odometer)
		self._trip_virtual_odometer += self._virtual_odometer_proc((report.message.loc.latitude_radix, report.message.loc.longitude_radix), report.message.loc.altitude)
		
		
		# on a vehicle state change...
		if self._state.change:
			# reset all of the trips if the vehicle state changes to ignition on
			if self._state.current == DeviceStates.IGNITION_ON:
				self._trip_idle = 0
				self._trip_hours = 0
				self._trip_odometer = 0
				self._trip_virtual_odometer = 0

				# reset last point after ignition on
				self._last_point = None

			# add all of the trips to the total if the vehicle state changes to ignition off
			if self._state.current == DeviceStates.IGNITION_OFF:
				self._total_idle += self._trip_idle
				self._total_engine_hours += self._trip_hours
				self._total_odometer += self._trip_odometer
				self._total_virtual_odometer += self._trip_virtual_odometer
    
	@staticmethod
	def _meters2miles(meters):
		return meters/FACTORMM
	@property
	def trip_idle(self):
		"""The current trips idle time (sec), accumulated during the current trip."""
		return self._trip_idle    
	@property
	def total_idle(self):
		"""The total idle time (sec), accumulated since the device has connected. Not accounting for the current trip."""
		return self._total_idle    
	@property
	def current_idle(self):
		"""The absolute total idle time (sec), accumulated since the device connected and the current trip if there is one."""
		return self._trip_idle + self._total_idle
	@property
	def trip_engine_hours(self):
		"""The total idle time (sec) the engine has been ON, accumulated during the current trip."""
		return self._trip_hours
	@property
	def total_engine_hours(self):
		"""The total time (sec) the engine has been ON, accumulated since the device has connected. Not accounting for the current trip."""
		return self._total_engine_hours
	@property
	def current_engine_hours(self):
		"""The absolute total time (sec) the engine has been ON, accumulated since the device connected and the current trip if there is one."""
		return self._trip_hours + self._total_engine_hours
	@property
	def trip_odometer(self):
		"""The total trip distance (Meters), accumulated since the beginning of the trip."""
		return self._trip_odometer
	@property
	def total_odometer(self):
		"""The total distance (Meters), accumulated since the device has connected."""
		return self._total_odometer
	@property
	def current_odometer(self):
		"""The absolute total distance (Meters), accumulated since the beginning and current trip."""
		return self._trip_odometer + self._total_odometer
	@property
	def trip_virtual_odometer(self):
		"""The total trip distance (Meters), accumulated using dflp since the beginning of the trip."""
		return self._trip_virtual_odometer
	@property
	def total_virtual_odometer(self):
		"""The total distance (Meters), accumulated using dflp since the device has connected."""
		return self._total_virtual_odometer
	@property
	def current_virtual_odometer(self):
		"""The absolute total distance (Meters), accumulated using dflp since the beginning and current trip."""
		return self._trip_virtual_odometer + self._total_virtual_odometer
