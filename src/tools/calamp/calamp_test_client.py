f __name__ != "__main__":
    raise Exception("This is a shell script and cannot be imported")

import binascii
import os
import socket
import time
import argparse

from src.settings import HOST
from src.settings import PORT

DESC = "Sends a raw packet to the listener simulating a device. The data folder contains the preloaded .dat packet files."
EPILOG ="For development use only. It is HIGHLY discouraged to send a simulated packet to a production server."


MSG_HOST = "Listener host name or ip address to send to. (Default: {})".format(HOST)
MSG_PORT = "Port of listener server (Default: {})".format(PORT)
MSG_RAW = "Add this flag to pass in raw packet date instead of a file path. (Ex ./gin/calamp_test_client_new 83052..."
MSG_DATA = "Location of packet data file from the root of the repository. (Ex.  ./bin/calamp_test_client_new data/onerec.dat)"

parser = argparse.ArgumentParser(description=DESC, epilog=EPILOG)

parser.add_argument('--host', type=str, default=HOST, help=MSG_HOST)
parser.add_argument('--port', type=int, default=PORT, help=MSG_PORT)
parser.add_argument('--raw', action='store_const', const=True, help=MSG_RAW)
parser.add_argument('data', type=str, help=MSG_DATA)

args = parser.parse_args()

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
count  = 0

def send_data(data):
    try:
        packet = binascii.unhexlify(data.strip())
        socket.sendto(packet, (args.host, args.port))
        time.sleep(0.005)
    except Exception as e:
        print("Error: {}".format(e))
        pass

if (args.raw):
    count += 1
    send_data(args.data)

else:
    file   = open(os.getcwd() + "/%s" % args.data, "r")
    for line in file.readlines():
        count += 1
        send_data(line)

    file.close()

print("Sent {} packets to ({}, {})".format(count, args.host, args.port))

socket.close()
