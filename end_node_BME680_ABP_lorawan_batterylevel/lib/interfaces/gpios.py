#
# Copyright (c) 2019, Pycom Limited.
#
# This software is licensed under the GNU GPL version 3 or any
# later version, with permitted additional terms. For more information
# see the Pycom Licence v1.0 document supplied with this file, or
# available at https://www.pycom.io/opensource/licensing
#
'''
This file is dedicated to manage the ADC protocol
This class is build on top
'''
from machine import Pin, ADC
import ujson
import pycom
import time
from lib.others.tools import raise_error
import lib.others.logging as logging


class Cpin():
    """
    Class dedicated to manage the ADC protocol
    Attributes :
    Methods :
    """
    def __init__(self):
        self.log = logging.getLogger("Cpin")
        self.pin = None
        self.type = ""
        self.id = ""
        self.deviceId = ""
        self.pins = []

    def conf_json(self, json, device):
        #Manage pin id of the alternate function
        self.log.debug(json)
        for pinId in json:
            if "device" in json[pinId]:
                if json[pinId]['device'] == device:
                    if self.pin is None:
                        if "type" in json[pinId]:
                            if "deviceId" in json[pinId]:
                                self.deviceId = json[pinId]["deviceId"]
                            else:
                                raise_error("ERROR : Device id shall be defined")

                            if json[pinId]["type"] == "ANALOG":
                                self.pins.append(pinId)
                                self.id = pinId
                                self.log.info("Configure pin {} in Analog mode".format(pinId))
                                self.adc = ADC()
                                self.log.debug("pinId {} ".format(pinId))
                                self.type = "ANALOG"
                            elif json[pinId]["type"] == "DIGITAL":
                                self.pins.append(pinId)
                                self.id = pinId
                                self.log.info("Configure pin {} in DIGITAL mode".format(pinId))
                                if json[pinId]["alt"] != "None":
                                    talt = json[pinId]["alt"]
                                else:
                                    talt = -1

                                try:
                                    self.pin = Pin(pinId, alt=talt)
                                    self.type = "DIGITAL"
                                    #Manage pin mode, ADC(
                                    if "mode" in json[pinId]:
                                        if json[pinId]["mode"] == "IN":
                                            self.pin.mode(Pin.IN)
                                        elif json[pinId]["mode"] == "OUT":
                                            self.pin.mode(Pin.OUT)
                                        elif json[pinId]["mode"] == "OPENDRAIN":
                                            self.pin.mode(Pin.OPEN_DRAIN)
                                        else:
                                            raise_error("ERROR : pin configuration unknown mode ")
                                    else:
                                        raise_error("ERROR : Mode is not defined in json configuration")

                                    ##Manage pin pull type

                                    if "pull" in json[pinId]:
                                        if json[pinId]["pull"] == "None":
                                            self.pin.pull(None)
                                        elif json[pinId]["pull"] == "PULLUP":
                                            self.pin.pull(Pin.PULL_UP)
                                        elif json[pinId]["pull"] == "PULLDOWN":
                                            self.pin.pull(Pin.PULL_DOWN)
                                        else:
                                            raise_error("ERROR : pin configuration unknown pull ")
                                    else:
                                        raise_error("ERROR : Mode is not defined in json configuration")


                                    if "pull" in json[pinId]:
                                        if json[pinId]["val"] == "0":
                                            self.pin(0)
                                        elif json[pinId]["val"] == "1":
                                            self.pin(1)
                                    else:
                                        raise_error("ERROR : pull is not defined in json configuration")


                                    #Manage pin Interrupt
                                    if "callback" in json[pinId]:
                                        if json[pinId]["callback"] == "IRQFALLING":
                                            irq = Pin.IRQ_FALING
                                        elif json[pinId]["callback"] == "IRQRISING":
                                            irq = Pin.IRQ_RISNG
                                        elif json[pinId]["callback"] == "IRQLOW":
                                            irq = Pin.IRQ_LOW
                                        elif json[pinId]["callback"] == "IRQHIGH":
                                            irq = Pin.IRQ_HIGH
                                        elif json[pinId]["callback"] == "None":
                                            irq = None
                                        else:
                                            raise_error("ERROR : pin configuration unknown init value ")
                                            irq = None
                                    else:
                                        raise_error("ERROR : callback is not defined in json configuration")


                                    if "handler" in json[pinId]:
                                        if json[pinId]["handler"] != "None":
                                            irqFct = json[pinId]["handler"]
                                            self.pin.callback(irq, globals()[irqFct])
                                        else:
                                            irqFct = None
                                    else:
                                        raise_error("ERROR : handler is not defined in json configuration")


                                except OSError as ex:
                                    raise_error(ex)
                                    self.adc = None

                            else:
                                self.log.warning("Pin type is unknown, {}, should be ANALOG or DIGITAL".format(json[pinId]['type']))

                        else:
                            self.log.warning("PIN id : {} has no type field in json".format(pinId))
                    else:
                        self.log.warning("PIN already defined {}".format(self.pin))
                    self.pin
                else:
                    self.log.warning("PIN id : {} with device {} not match with {}".format(pinId, json[pinId].device, device))
            else:
                self.config.warning("device for pin is not defined in json scenario")
        return

    def read_device(self, data):
        self.log.debug(data)
        if self.pin is None:
            if self.type == "ANALOG":
                if self.adc is not None:
                    self.pin = self.adc.channel(pin=self.id)
                else:
                    self.log.warning("Self.adc should not be none in read_device ")
            else:
                self.log.warning("Self.pin should not be none in read_device ")

        if self.pin is not None:
            if self.deviceId in data:
                for feature in data[self.deviceId]:
                    if feature == "humidite":
                        data[self.deviceId][feature] = self.pin()
                        self.log.debug("Pin read humidity : {}".format(data))
                    else:
                        raise_error("Unknown field (feature) to read with Bme {}".format(feature, data['0']))
            else:
                raise_error("Unknown ID {}, device Id not match with data id ({})".format(data, self.deviceId))
        else:
            self.log.warning("Failed to retrieve pin elemen impossible to read")



