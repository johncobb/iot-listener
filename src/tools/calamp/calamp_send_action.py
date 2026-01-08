# ======================================================================================================================
# Copyright (c) 2013 Exzigo. All rights reserved.
#
# Author: Sean Kerr [sean@code-box.org]
# ======================================================================================================================

if __name__ != "__main__":
    raise Exception("This is a shell script and cannot be imported")

# from src.lib import ByteBuffer
from devices.calamp import CalampMessageHeader
from devices.calamp import CalampOptionsHeader
from devices.calamp import MessageHeader
from devices.calamp import OptionsHeader
from devices.calamp.messages.unit_request import UnitRequest
import enum

import socket
import struct
import sys

# class ActionCode(enum.Enum):
#     Reboot,
#     Version,
#     PegAction,
#     ChangePassword,
#     GpsStatusReport,
#     ClearPegEventList,
#     SetAuxSleepTime,
#     GeneratePegSpecialTrigger,
#     IdReport,
#     LocationReport,
#     MessageStatsReport,
#     ResetMessageStats,
#     ClearErrorFlags,
#     ForceInboundMaintenance
#     RequestStateReport,
#     UserFlagUpdate,
#     SetZoneCurrentLocation,
#     SetBatteryCapacity,
#     AccumulatorSchedule,
#     GeneratePegMdtTrigger,
#     SetBatteryUsage,
#     CheckSixByteDriverId,
#     Subscribe,
#     OneWireInterface,
#     DeviceControl,
#     CertificateInfoReport

# class UnitRequestMessage (Message):
#     def __init__ (self, action=None, byte8=0, byte16=0, byte32=0):
#         """
#         Create a new UnitRequestMessage instance.

#         @param action The action.
#         @param byte8  The 8 byte parameter.
#         @param byte16 The 16 byte parameter.
#         @param byte32 The 32 byte parameter.
#         """

#         # details
#         self.action = action
#         self.byte8  = byte8
#         self.byte16 = byte16
#         self.byte32 = byte32

#     def __str__ (self):
#         """
#         Retrieve the string representation of this object.
#         """
#         return struct.pack(">BBHI", self.action, self.byte8, self.byte16, self.byte32)

class MessageHeaderJig():
    def __init__(self, service_type, message_type, sqeuence_number):
        self._service_type = service_type
        self._message_type = message_type
        self._sequence_number = sqeuence_number

    @property
    def to_bytearray(self):
        return struct(">BBH", self._service_type, self._message_type, self._sequence_number)

class SendActionPacket():
    def __init__(self, mobile_id):
        """ bytes[0:1]: options_byte """
        """ bytes[1:1]: mobile_id_len """
        """ bytes[2:5]: mobile_id_len """
        """ bytes[7:1]: mobile_id_type_len """
        """ bytes[8:1]: mobile_id_type """
        """ bytes[9:1]: service_type """
        """ bytes[10:1]: message_type """
        """ bytes[11:2]: sequence_number """
        """ options header: 830546411433720101"""
        """ message header: 00070000 """
        """ unit request args <> : """
        """ unit request args > 4:  000000"""
        """ unit request args > 5:  00000000"""
        """ unit request args > 6:  0000000000"""
        self._bytes = "83054641143372010100070000"
        self._example_packet = "83054641143372010100070000"
        self._example_packet_byte8 = "8305464114337201010007000001FE"
        self._example_packet_byte16 = "83054641143372010100070000010000FE"
        self._example_packet_byte32 = "8305464114337201010007000001000000000000FE"
        # self._example_packet = "83054641143372000700"

    @property
    def payload(self):
        return self._example_packet_byte8

if len(sys.argv) < 4:
    print("Usage: ./calamp_send_action <CALAMP_HOST> <ESN> <ACTION> [byte8] [byte16] [byte32]")
    sys.exit(1)

MOBILE_ID_TYPE_ESN   = 1

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.bind(("0.0.0.0", 20599))

calamp_host     = sys.argv[1]
calamp_port     = 20500
mobile_id       = sys.argv[2]
action          = int(sys.argv[3])
byte8           = int(sys.argv[4])
byte16          = int(sys.argv[5])
byte32          = int(sys.argv[6])
print("\"{} {} {} {} {} {} {}\"".format(sys.argv[0], calamp_host, mobile_id, action, byte8, byte16, byte32 ))
# message_header = CalampMessageHeader(0, 7, 0)
# options_header = CalampOptionsHeader(mobile_id, MOBILE_ID_TYPE_ESN)
message_header = MessageHeader(0, 7, 0)
options_header = OptionsHeader(mobile_id, MOBILE_ID_TYPE_ESN)
unit_request = UnitRequest(options_header, message_header, action, byte8, byte16, byte32)
print("options_header: {}".format(bytes(options_header)))
print("message_header: {}".format(bytes(message_header)))
print("unit_request: {}".format(bytes(unit_request)))
print("Sending to %s:%d" % (calamp_host, calamp_port))
data = bytes(unit_request)
socket.sendto(data, (calamp_host, calamp_port))

# message_header = str(MessageHeader(0, 7, 0))
# options_header = str(OptionsHeader(sys.argv[2]))

# if len(sys.argv) > 6:
#     unit_request_message = UnitRequest(int(sys.argv[3], 16),
#                                               int(sys.argv[4], 16),
#                                               int(sys.argv[5], 16),
#                                               int(sys.argv[6], 16))
# elif len(sys.argv) > 5:
#     unit_request_message = UnitRequest(int(sys.argv[3], 16),
#                                               int(sys.argv[4], 16),
#                                               int(sys.argv[5], 16))

# elif len(sys.argv) > 4:
#     unit_request_message = UnitRequest(int(sys.argv[3], 16),
#                                               int(sys.argv[4], 16))

# else:
#     unit_request_message = UnitRequest(int(sys.argv[3], 16))

# data = str(options_header) + str(message_header) + str(unit_request_message)

# print("Sending to %s:%d" % (calamp_host, calamp_port))

# packet = SendActionPacket("1")
# data = bytearray.fromhex(packet.payload)

# socket.sendto(data, (calamp_host, calamp_port))
