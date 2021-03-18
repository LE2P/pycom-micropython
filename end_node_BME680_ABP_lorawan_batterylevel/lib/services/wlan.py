# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 schade <schade@schadelin-System>
#
'''
wlan.py :
    wlan is a service class of wlan !
    This file overload the existing class WLAN
    WARNING : NOT IMPLEMENTED : OVERWRITTEN by pybytes
    SHALL IMPLEMENT SEND_ALL_SIGNALS and SEND_SIGNAL

'''
from network import WLAN
import machine
import lib.others.logging as logging

class CWlan(WLAN):
    """
    Class dedicated to manage the WLAN of the Pycom
    Attributes :
        wlan = pointer on WLAN class
        mode = current mode of the WLAN Pycom
    Methods :
        refreshMode = Methode dedicated to refresh the state mode WLAN info

    """

    def __init__(self):
        """
        Overload the init class, call the WLAN initialization too
        """

        super().init(mode=WLAN.STA)
        self._ssid = ""
        self._pwd = ""
        self.log = logging.getLogger("CWlan")
        self.log.info("Wlan instance enabled")

        return

    def updateConnectInfo(self, ssid, pwd):
        """
        Update SSID to connect
        """
        if ssid == "":
            self.requestInput()
        else:
            self._ssid = ssid
            if pwd == "":
                self.requestInput()
            else:
                self._pwd = pwd
        return

    def connect(self):
        """
        Overload connect function in order to use class variable
        """
        # TODO: pass authentifacation parameter to
        self.log.info("Try to connect to {} with {}".format(self._ssid, self._pwd))
        super().connect(self._ssid, auth=(WLAN.WPA2, self._pwd), timeout=5000)
        self.waitForConnection()
        return

    def waitForConnection(self):
        """
        Wait for connection
        """
        while not super().isconnected():
            machine.idle()  # save power while waiting
        if super().isconnected():
            self.log.info("Connected to {}".format(self._ssid))
        else:
            self.log.info("Connection to {} failed".format(self._ssid))
        return

    def requestInput(self):
        """
        Request user SSID and PWD
        """

        self._ssid = input("Connection WLAN : Définir le SSID du point \
                           d'accés ? --> ")
        self._pwd = input("Connection WLAN : Définir le mot de pass de \
                          {} ? --> ".format(self._ssid))
        return
