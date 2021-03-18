#
# Copyright (c) 2019, Pycom Limited.
#
# This software is licensed under the GNU GPL version 3 or any
# later version, with permitted additional terms. For more information
# see the Pycom Licence v1.0 document supplied with this file, or
# available at https://www.pycom.io/opensource/licensing
#
'''
This file is dedicated to manage the weightless communication
Like the zigbee communication the weightless is not integrated into the PyCom
an I2C communication shall be established.
'''
from machine import I2C
import lib.others.logging as logging
from lib.others.tools import raise_error

class Ci2c(I2C):
    """
    Class dedicated to manage the Weightless communication
    Attributes :
    Methods :

    """
    def __str__(self):
        return "Ci2c interface"



    def __init__(self):
        super().__init__()
        self.log = logging.getLogger("CI2c")
        self.log.info("CI2c interfaces enabled")
        self.pins = []
        self.bme = None

    def conf_json(self, json, device):
        self.log.debug("conf_json called")
        if json['device'] == "undefined":
            self.log.info("CI2c configured with unedefined device")
            self.pins.append(json['pSDA'])
            self.pins.append(json['pSCL'])
            super().init(json['bus'], pins=(json['pSDA'], json['pSCL']), baudrate=json['baud'])
        elif json['device'] == "bme":
            from lib.drivers.bme680.bme680 import BME680
            import lib.drivers.bme680.bme680_data as BMEData


            self.log.info("CI2c configured with BME680 device")
            self.pins.append(json['pSDA'])
            self.pins.append(json['pSCL'])
            try:
                super().init(json['bus'], pins=(json['pSDA'], json['pSCL']), baudrate=json['baud'])
            except Exception as e:
                self.log.error("Error I2C init {}".format(e))
                raise(e)

            try:
                self.bme = BME680(i2c_device=self)
                # These oversampling settings can be tweaked to
                # change the balance between accuracy and noise in
                # the data.
                # TODO : BME Configuration here shall have better management
                self.bme.set_humidity_oversample(BMEData.OS_2X)
                self.bme.set_pressure_oversample(BMEData.OS_4X)
                self.bme.set_temperature_oversample(BMEData.OS_8X)
                self.bme.set_filter(BMEData.FILTER_SIZE_3)
            except Exception as e:
                self.log.error("Error BME init {}".format(e))
                raise(e)
        else:
            from lib.others.tools import raise_error
            raise_error("Unkwown device type in ScenarioConf ({}) should be \
                    undefined or bme680".format(
                        json['device']), fromWho="CI2c")

    def read_device(self, data):
        self.log.debug(data)
        if self.bme is not None:
            if self.bme.get_sensor_data():
                if '0' in data:
                    for feature in data['0']:
                        if feature == "temperature":
                            data['0'][feature] = self.bme.data.temperature
                            #print(self.bme.data.temperature)
                        elif feature == "humidite":
                            data['0'][feature] = self.bme.data.humidity
                            #print(self.bme.data.humidity)
                        elif feature == "pression":
                            data['0'][feature] = self.bme.data.pressure
                            #print(self.bme.data.pressure)
                        else:
                            raise_error("Unknown field (feature) to read with Bme {}".format(feature, data['0']))
                else:
                    raise_error("Unknown ID {}, BME id shall be 0".format(data))
            else:
                self.log.warning("Failed to retrieve BME sensor data")
        else:
            raise_error("self.i2c.bme should not be None in update_read ")



    def read_byte_data(self, addr, register):
        """ Read a single byte from register of device at addr
            Returns a single byte """
        return self.readfrom_mem(addr, register, 1)[0]

    def read_i2c_block_data(self, addr, register, length):
        """ Read a block of length from register of device at addr
            Returns a bytes object filled with whatever was read """
        return self.readfrom_mem(addr, register, length)

    def write_byte_data(self, addr, register, data):
        """ Write a single byte of data to register of device at addr
            Returns None """
        return self.writeto_mem(addr, register, data)

    def write_i2c_block_data(self, addr, register, data):
        """ Write multiple bytes of data to register of device at addr
            Returns None """
        return self.writeto_mem(addr, register, data)
