#
# Copyright (c) 2019, Pycom Limited.
#
# This software is licensed under the GNU GPL version 3 or any
# later version, with permitted additional terms. For more information
# see the Pycom Licence v1.0 document supplied with this file, or
# available at https://www.pycom.io/opensource/licensing
#
'''
This file is dedicated to manage create a new interface on WLAN
This file overload the existing class WLAN
'''

import time
import lib.others.logging as logging
try:
    from pybytes import Pybytes
except:
    from _pybytes import Pybytes

class Cpybytes(Pybytes):
    """
    Class dedicated to manage the WLAN of the Pycom
    Attributes :
        wlan = pointer on WLAN class
        mode = current mode of the WLAN Pycom
    Methods :
        refreshMode = Methode dedicated to refresh the state mode WLAN info

    """

    def __init__(self, config, signals):
        """
        Overload the init class, call the WLAN initialization too
        """
        # Current automatically updated by pybytes_config.json
        # wait main.py befor init pybytes
        self.signals = {}
        self.pins = []
        self.log = logging.getLogger("CPybytes")
        self.log.info("CPybytes instance enabled")
        super().__init__(config)

    def conf_json(self, json):
        self.log.debug("Signals configuration {}".format(json))
        if "signals" in json:
            self.signals = json["signals"]
        else:
            self.log.warning("Error no signals definition in pybytes fsm conf")

    def update_wlan(self, wlan):
        self.__pybytes_connection.wlan = wlan

    def _return_data_from_readers(self, readers):
        data = {}
        for reader in readers:
            data[reader.device] = reader.data
        return data

    def send_all_data(self, readers):
        #data = self._return_data_from_readers(readers)
        data = readers
        #print("data : ",data)
        #print(self.signals)
        self.log.debug("Cpybyte Send all data {}".format(data))
        self.log.debug("Cpybyte Signals {}".format(self.signals))
        for signal in self.signals:
            try:
                device = self.signals[signal].split(".")[0]
                id = self.signals[signal].split(".")[1]
                value = self.signals[signal].split(".")[2]
                #print("Envoi Pybytes :", value)
                self.log.debug("Send signal : {}".format(self.signals[signal]))
                print("Send signal : {}".format(self.signals[signal]))
                self.send_signal(int(signal), data[device][id][value])
                time.sleep(1)
            except Exception as e:
                self.log.error("Error to send signal {} ".format(signal))

        self.send_battery_level(23)
