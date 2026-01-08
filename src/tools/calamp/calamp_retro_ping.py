# ======================================================================================================================
# Copyright (c) 2013 Exzigo. All rights reserved.
#
# Author: Sean Kerr [sean@code-box.org]
# ======================================================================================================================

if __name__ != "__main__":
    raise Exception("This is a shell script and cannot be imported")

from devices.calamp import MessageHeader
from devices.calamp import OptionsHeader
from devices.calamp.api import MessageTypes

from settings import PRODUCTION_IP
from settings import PORT

import binascii
import os
import socket
import sys
import time

if len(sys.argv) < 2:
    raise Exception("Enter one or more job clock ids")

sys.argv.pop()

count         = 0
job_clocks    = sys.argv
matched_count = 0
socket        = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
file          = open("/tmp/calamp.log.raw", "r")

for line in file.readlines():
    count += 1

    if count % 10000 == 0:
        print("Processed %d packets" % count)

    try:
        data = binascii.unhexlify(line.strip())

        options_header = OptionsHeader()
        options_header.parse(data)

        message_header = MessageHeader()
        message_header.parse(options_header.get_data())

        if options_header.mobile_id is None:
            # not a valid packet
            continue

        if message_header.message_type != MessageTypes.EVENT_REPORT:
            # don't care about this message
            continue

        message = calamp.EventReportMessage(options_header.mobile_id)
        message.parse(message_header.get_data())

        if message.mobile_id.upper() in job_clocks:
            matched_count += 1
            socket.sendto(data, (PRODUCTION_IP, CALAMP_PORT))

            time.sleep(0.01)

    except:
        pass

print("Processed %d packets" % count)
print("Matched %d packets" % matched_count)