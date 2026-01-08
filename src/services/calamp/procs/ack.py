import os
import struct
import socket
import redis
import socket
import binascii
import time
import datetime
import json
import traceback

from devices.calamp import MessageTypes
from devices.calamp.api import ServiceTypes
from devices.calamp.api import AckTypes

""" leaving commented for future reference """
# class DeviceAcknowledgement:
#     def __init__(self, service_type=ServiceTypes.UNACKNOWLEDGED, message_type=MessageTypes.NULL, sequence_number=0):
#         self._service_type = service_type
#         self._message_type = message_type
#         self._sequence_number = sequence_number

#     def _type(self, service_type):
#         if (service_type == ServiceTypes.UNACKNOWLEDGED):
#             return None # no ack
#         elif (service_type == ServiceTypes.ACKNOWLEDGED):
#             return ServiceTypes.ACKNOWLEDGE_RESPONSE.value
#         elif (service_type == ServiceTypes.ACKNOWLEDGE_RESPONSE):
#             return service_type == ServiceTypes.ACKNOWLEDGED.value
#         else:
#             return None # no ack

#     def _status(self, message_type):
#         return AckTypes.ACK_SUCCESSFUL.value

#         """ TODO: verify with CalAmp support that sending a not supported Message type is necessary """
#         if (MessageTypes.is_supported(message_type)):
#             return AckTypes.ACK_SUCCESSFUL.value
#         elif (MessageTypes(message_type)):
#             return AckTypes.NAK_NOT_SUPPORTED_MESSAGE_TYPE.value
#         else:
#             return AckTypes.NAK_NOT_SUPPORTED_OPERATION.value

#     def encode_ack(self):
#         """ handle ack types that need to be sent back to the device.
#             On a service requested ack it dispatches a ack worker to
#             monitor the client queue for a ack message
#         """

#         """ short circuit if ack is not needed """
#         if (self._service_type != ServiceTypes.ACKNOWLEDGED):
#             return


#         payload = struct.pack(">2bH6b", self._type(self._service_type),
#                                         MessageTypes.ACKNOWLEDGEMENT.value, self._sequence_number,
#                                         self._service_type.value,
#                                         self._status(self._message_type),
#                                         0,       # spare byte
#                                         0, 0, 0) # app version (3 bytes)
#         return payload

def _encode_service_type(service_type):
        if (service_type == ServiceTypes.ACKNOWLEDGED):
            return ServiceTypes.ACKNOWLEDGE_RESPONSE.value
        elif (service_type == ServiceTypes.ACKNOWLEDGE_RESPONSE):
            return ServiceTypes.ACKNOWLEDGED.value
        else:
            return ServiceTypes.UNACKNOWLEDGED

def _encode_ack(svc_type, msg_type, seq_number):

    payload = struct.pack(">2bH6b", _encode_service_type(svc_type),
                                    MessageTypes.ACKNOWLEDGEMENT.value,
                                    seq_number,
                                    svc_type.value,
                                    AckTypes.ACK_SUCCESSFUL.value,
                                    0,       # spare byte
                                    0, 0, 0) # app version (3 bytes)

    return payload

def send_ack(ip, port, msg, sequence_number=0):

    """ assign to local variables for convenience """
    service_type = msg.message_header.service_type
    message_type = msg.message_header.message_type

    """ short circuit if ack is not needed """
    if (service_type != ServiceTypes.ACKNOWLEDGED):
        return

    """ sequence is currently not implemented. default: 0 """
    packet = _encode_ack(service_type, message_type, sequence_number)

    try:
        socket_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if (packet != None):
            print("({0}:{1}) ACK".format(ip, port))
            socket_client.sendto(packet, (ip, port))
            """ following sleep could pose an issue with speed """
            # time.sleep(0.005)
    except Exception as e:
        print("Error: {}".format(e))
        pass

