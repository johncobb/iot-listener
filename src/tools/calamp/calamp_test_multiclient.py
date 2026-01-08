import binascii
import os
import socket
import argparse
import time
import datetime
# import logging
import threading
from multiprocessing import Pool
from multiprocessing import cpu_count


from src.settings import HOST
from src.settings import PORT

# from settings import LOG_ENABLE
# from settings import LOG_FILE
# from settings import LOG_FORMAT

# logger = logging.getLogger("multiproc")
# logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)

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

class RedskyClient():
    def __init__(self, socket):
        self.socket = socket
    def send(self, data):
        packet = binascii.unhexlify(data.strip())
        socket.sendto(packet, (args.host, args.port))

def send_data(data):
    """ instantiate our clinet """
    redsky_client = RedskyClient(socket)

    try:
        redsky_client.send(data)
        """ negligible but nonetheless """
        time.sleep(0.0001)
    except Exception as e:
        print("Error: {}".format(e))
        pass

""" burn baby burn """
def multicore_proc():
    count = 0
    num_cores = cpu_count()
    pool = Pool(processes=num_cores)

    file   = open(os.getcwd() + "/%s" % args.data, "r")
    for line in file.readlines():
        count += 1
        pool.apply_async(send_data, args=(line,))

    file.close()

    pool.close()
    pool.join()
    print("Sent {} packets to ({}, {})".format(count, args.host, args.port))


def main():
    print("cores: {}".format(cpu_count()))
    start = time.time()
    multicore_proc()
    end = time.time()
    print("elapsed time: {}s".format((end-start)))


if __name__ == "__main__":
    main()
