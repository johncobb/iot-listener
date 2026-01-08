class Message:
	def __init__(self):
		self.speed = 234
		self.odometer = 1032
		self.heading = 32
		self.mobile_id = 'ghre34'

class Report:
	def __init__(self):
		self.mobile_id = 'ls74239'
		self.message = Message()
		self.accums = CalampAccumulators()


class CalampAccumulator():
	def __init__ (self, id, val):
		self._id = id
		self._val = val

	def to_json(self):
		return {"id": self.id, "val": self.val}

	@property
	def id(self):
		return self._id
	@property
	def val(self):
		return self._val


class CalampAccumulators():
	def __init__(self):

		self.accumulator_0 = 0
		self.accumulator_1 = 0
		self.accumulator_2 = 0
		self.accumulator_3 = 0
		self.accumulator_4 = 0
		self.accumulator_5 = 0
		self.accumulator_6 = 0
		self.accumulator_7 = 0
		self.accumulator_8 = 0
		self.accumulator_9 = 0
		self.accumulator_10 = 0
		self.accumulator_11 = 0
		self.accumulator_12 = 0
		self.accumulator_13 = 0
		self.accumulator_14 = 0
		self.accumulator_15 = 0

	def __call__(self, id):
		return getattr(self, 'accumulator_{}'.format(id))
	
	def set(self, accumulator):
		setattr(self, 'accumulator_{}'.format(accumulator.id), accumulator)

	

if __name__ == "__main__":
	report = Report()
	# print(report.message.speed)
	# print("MobileId={0.mobile_id}, Speed={0.message.speed}, Odometer={0.message.odometer}, Heading={0.message.heading}".format(report))

	report.accums.set(CalampAccumulator(0, 40))
	report.accums.set(CalampAccumulator(1, 50))
	report.accums.set(CalampAccumulator(2, 60))

	print("{report.accums.attrib('0').val}".format(report=report))