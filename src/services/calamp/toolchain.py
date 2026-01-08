from services.toolchain import Toolchain

class CalampToolchain(Toolchain):
	def __init__(self, client_manager, log, handler=None):
		Toolchain.__init__(self, client_manager, log, handler)