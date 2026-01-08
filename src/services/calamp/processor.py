from services.processor import ProcessorForwarder

class CalampProcessorForwarder(ProcessorForwarder):
	def __init__(self, log, topic_prefix='calamp'):
		ProcessorForwarder.__init__(self, log, topic_prefix)