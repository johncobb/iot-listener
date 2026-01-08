class MessgageAdapter:
	def __init__(self, events):
		self._events = events
		self._message = None

	def parse(self, msg):
		self._message = msg
		return msg.event_code in self._events

	@property
	def message(self):
		return self._message
	@property
	def events(self):
		return self._events
	@property
	def source(self):
		return self._source

	def transform(self):
		raise Exception("Sub-class must implement transform()")

