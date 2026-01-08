from devices.calamp.logic import DeviceStates
from devices.calamp.logic import Timeouts
from devices.calamp.logic.states import DeviceState

class DummyCalampClient():
	def __init__(self, client_id, state=DeviceStates.Unknown):
		self._client_id = client_id
		self._state = DeviceState(state)
		self._last_update = time.time_ns()

	@property
	def notifications(self):
		return self.state.notifications
	@property
	def client_id(self):
		return self._client_id
	@property
	def state(self):
		return self._state
	@property
	def last_update(self):
		return (self._last_update != None)

import time
if __name__ == "__main__":
	client = DummyCalampClient("1337")

	client.state.enter_state(DeviceStates.IGNITION_ON, Timeouts.IGNITION_ON)

	while(True):
		client.state.proc()
		time.sleep(.025)