#
# Copyright (c) 2019, Pycom Limited.
#
# This software is licensed under the GNU GPL version 3 or any
# later version, with permitted additional terms. For more information
# see the Pycom Licence v1.0 document supplied with this file, or
# available at https://www.pycom.io/opensource/licensing
#
'''
This file is dedicated to manage the Bluetooth system feature
Note from Pycom :
At present, basic BLE functionality is available. More features will be
implemented in the near future, such as pairing. This page will be updated
in line with these features.

The library should be enhanced or a contribution shall be done here if
necessary
'''

from network import Sigfox
import time
import struct
import socket
import lib.others.logging as logging
from lib.others.tools import raise_error

class Csigfox(Sigfox):
    """
    Class dedicated to manage the BLE of the Pycom
    Attributes :
    Methods :

    """
    def __init__(self):
        super().__init__()
        self.pins = []
        self.log = logging.getLogger("CSigfox")
        self.log.info("CSigfox interfaces enabled")


    def conf_json(self, json):
        '''
        Init Sigfox Interface with json conf
        '''
        if json['mode'] == 'SIGFOX':
            from network import Sigfox
            if json['rcz'] == 'RCZ1':
                self.init(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)
            elif json['rcz'] == 'RCZ2':
                self.init(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)
            elif json['rcz'] == 'RCZ3':
                self.init(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)
            elif json['rcz'] == 'RCZ4':
                self.init(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)
            else:
                raise_error("Unkwown region {}, should be RCZ1, RCZ2, RCZ3 or RCZ4".format(json['mode']), fromWho="CSigfox")
                return
            self.configureSocket()
        elif json['mode'] == 'FSK':
            if 863000000 <= json['frequency'] <= 928000000:
                #TODO: not used and not tested, create specialized socket function if required (not calle for the moment)
                self.init(mode=Sigfox.FSK, rcz=json['frequency'])
            else:
                raise_error("Sigfox frequency should be between 863000000 <= {} <= 928000000".format(json['frequency']), fromWho="CSigfox")
        else:
            raise_error("Unkwown {}, should be FSK for device to device or SIGFOX for global network communication".format(json['mode']), fromWho="CSigfox")

    def __del__(self):
        super().__del__()
        self.s.close()

    def configureSocket(self):
        self.log.info("Socket configuration")
        self.s = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)
        # make the socket blocking
        self.s.setblocking(True)
        self.s.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, False)
        ## wait for a downlink after sending the uplink packet
        #s.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, True)

        ## make the socket uplink only
        #s.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, False)

        ## use the socket to send a Sigfox Out Of Band message
        #s.setsockopt(socket.SOL_SIGFOX, socket.SO_OOB, True)

        ## disable Out-Of-Band to use the socket normally
        #s.setsockopt(socket.SOL_SIGFOX, socket.SO_OOB, False)

        ## select the bit value when sending bit only packets
        ##s.setsockopt(socket.SOL_SIGFOX, socket.SO_BIT, False)
        # configure it as uplink only

    #First byte identification tram :
    # BME id always 0 and ruvi id ref to jsonconf
    # bit 0 / 1 : ID1
    # bit 2 / 3 :  ID2
    # bit 4 / 5 : ID3
    # bit 6 / 7 : 00 Not used
    #11bytes :
    # ID1 : Humidity : 0 -> 100 rounded without float -> 1 bytes (unsigned char : B)
    # ID1 : temperature (0-65 absolute) : -128 -> 128 rounded without float -> 1 bytes(unsigned char : b)
    # ID1 : presssure (300 to 1100 hPa) : rounded without float -> 2 bytes(short)
    # ID2 : Humidity : 0 -> 100 rounded without float -> 1 bytes (unsigned char : B)
    # ID2 : temperature (0-65 absolute) : -128 -> 128 rounded without float -> 1 bytes(unsigned char : b)
    # ID2 : presssure (300 to 1100 hPa) : rounded without float -> 2 bytes(short)
    # ID3 : Humidity : 0 -> 100 rounded without float -> 1 bytes (unsigned char : B)
    # ID3 : temperature (0-65 absolute) : -128 -> 128 rounded without float -> 1 bytes(unsigned char : b)
    # ID3 : presssure (300 to 1100 hPa) : rounded without float -> 2 bytes(short)
    def intToBytes(self, value, length):
        result = []
        for i in range(0, length):
            result.append(value >> (i * 8) & 0xff)

        result.reverse()
        return result

    def send_all_data(self, readers):
        self.log.debug("Sigfox Send all data")


    def sendDict(self, kwargs):
        self.log.info("Send Dictionary")
        payload = []
        deviceId = ''
        for data in kwargs:
            if data == "bme":
                deviceId = '00' + deviceId
                for bmeVal in kwargs[data]:
                    self.log.debug("Bme : {} : {}".format(bmeVal, int(kwargs[data][bmeVal])))
                    if bmeVal == "pres":
                        byteToAdd = self.intToBytes(int(kwargs[data][bmeVal]), 2)
                        payload.append(byteToAdd[0])
                        payload.append(byteToAdd[1])
                    else:
                        payload.append(int(kwargs[data][bmeVal]))
            elif data == "ruvi":
                for i, ruvi in enumerate(kwargs[data]):
                    for ruviData in ruvi:
                        val = int(kwargs[data][i][ruviData])
                        self.log.debug("Ruvi : {} : {}".format(ruviData, val))
                        if ruviData == "id":
                            deviceId = '{0:02b}'.format(val) + deviceId
                        elif ruviData == "pres":
                            byteToAdd = self.intToBytes(val,2)
                            payload.append(byteToAdd[0])
                            payload.append(byteToAdd[1])

                        else:
                            payload.append(val)

            else:
                raise_error("Unknown data to send ( {} ) shall be bme or ruvi".format(data), fromWho="CSigfox")
                return

        payload.insert(0, int(deviceId, 2))
        try:
            self.s.send(bytes(payload))
            self.log.info("Payload sent : {}.format(payload)")
        except OSError as ex:
            raise_error("Failed to sent payload {} error : {}".format(payload, ex), fromWho="CSigfox")

        return

