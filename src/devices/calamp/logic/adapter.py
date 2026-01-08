class DeviceAdapters:
    def __init__(self, adapters, report=None, adapter_handler=None):
        self._adapters = adapters
        self._report = report
        self._adapter_handler = adapter_handler

    def reg_adapter_handler(self, handler):
        self._adapter_handler = handler

    def _dispatch_packet(self, payload):
        if(self._adapter_handler != None):
            self._adapter_handler(payload)

    def proc(self):
        # short circuit if adapters are disabled


        msg = self._report.message
        for msg_type in self._adapters:

            # check if the message type should be adapted
            if msg_type != msg.message_type:
                continue

            # get the adapter class to use
            adapter = self._adapters.get(msg_type)

            if not adapter.parse(msg):
                pass

            # transform the message to the adapters message
            packet = adapter.transform()

            self._dispatch_packet((bytes(packet, encoding='utf-8'), adapter.source))

    def adapter_handler(self, report):
        self._report = report
        self.proc()
