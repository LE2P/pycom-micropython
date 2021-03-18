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

from network import Bluetooth
import binascii
import time
from lib.others.tools import raise_error
import lib.others.logging as logging

class Cble(Bluetooth):
    """
    Class dedicated to manage the BLE of the Pycom
    Attributes :
    Methods :

    """
    def __str__(self):
        return "Cble interface"


    def __init__(self):
        """
        Interface class init
        """
        super().init()
        self.antenna = Bluetooth.INT_ANT
        self.pins = []
        self.ruuviScan = None

        self.log = logging.getLogger("Cble")
        self.log.info("Cble interfaces enabled")

    def conf_json(self, json, device):
        '''
        Init BLE Interface with device
        '''
        self.log.debug("Conf JSon")
        returnDict = {}
        gpios = []
        if json["device"] == "undefined":
            if json['antenna'] == "EXT":
                self.device = "undefined"
                self.updateAntenna(json['antenna'])
                # P12 shall be reserved for external antenna
                self.pins.append('P12')
        elif json["device"] == "ruuvi":
            self.device = "ruuvi"
            if self.device in json:
                self.ruuvi_id = json[self.device]
            from lib.drivers.ruuvitag.scanner import RuuviTagScanner

            # TODO: pass antena argument if required
            self.ruuviScan = RuuviTagScanner()
        else:
            raise_error("Unkwown device type in ScenarioConf ({}) should be undefined or ruuvitag".format(json['device']), fromWho="CBle")

    def updateAntenna(self, antenna):
        # TODO :
        # P12 should be output pin if external antenna set !!
        self.log.info("Update CWlan with {} antenna".format(antenna))
        if antenna == "INT":
            self.antenna = Bluetooth.INT_ANT
            super().deinit()
            super().init(antenna=Bluetooth.INT_ANT)
        elif antenna == "EXT":
            super().deinit()
            self.antenna = Bluetooth.EXT_ANT
            super().init(antenna=Bluetooth.EXT_ANT)
        else:
            raise_error("Unkwown antenna type", fromWho="CBle")

    def findDevice(self, timeout=5):
        """
        Find device at proximity
        """
        bt = super()
        self.log.info("Search for ble devices...")
        deviceFound = []
        deviceFoundMac = []
        bt.start_scan(timeout)
        while bt.isscanning():
            adv = bt.get_adv()
            if adv:
                if adv[0] not in deviceFoundMac:
                    deviceFound.append(adv)
                    deviceFoundMac.append(adv[0])
            else:
                time.sleep(0.050)

        self.log.info("{} devices found ".format(len(deviceFound)))

        return deviceFound

    def read_device(self, data):
        if self.device == "ruuvi":
            if self.ruuviScan is not None:
                for ruuvitag in self.ruuviScan.find_ruuvitags(timeout=10):
                    if ruuvitag is not None:
                        id = self.check_ruuvi_id(ruuvitag[0])
                        if id in data and int(id) > 0:
                            for feature in data[id]:
                                if feature == "temperature":
                                    data[id][feature] = ruuvitag[4]
                                elif feature == "humidite":
                                    data[id][feature] = ruuvitag[3]
                                elif feature == "pression":
                                    data[id][feature] = ruuvitag[5] / 100
                                else:
                                    raise_error("Unknown field to read with ruuvi")
                        else:
                            raise_error("update read i2C : id error {} > 0 or defined into self.read".format(id))
                    else:
                        self.log.debug("update read ruuvitag is None")
            else:
                raise_error("self.ble.ruuviscan should not be None in update_read ")
        elif self.device == "undefined":
            self.log.warning("Read unknown device not implemented", fromWho="CBle")
        else:
            raise_error("Unkwown read device {}".format(self.device), fromWho="CBle")

    def check_ruuvi_id(self, mac):
        for ruuvi in self.ruuvi_id:
            if self.ruuvi_id[ruuvi] == mac:
                return str(ruuvi)
        return 0
