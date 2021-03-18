"""Code envoi d'une donnée en LoRaWAN ABP vers une application
"""

# Import pour communication LoRa
from network import LoRa
from network import Bluetooth
from network import WLAN
import socket
import binascii
import struct
import math
import time
import machine
import uos
import config
import pycom
import uos
import machine




pycom.heartbeat(False) # Désactiver la led par défaut
bt = Bluetooth()
bt.deinit() # Désactiver le bluetooth
wlan = WLAN()
wlan.deinit() # Désactiver la Wifi


# Europe = LoRa.EU868, setup pour la communication
lora = LoRa(mode=LoRa.LORAWAN, tx_iq=True,region=LoRa.EU868) # tx_iq activer pour eviter les redondances

# Parametres pour ABP (authetification par personalisation)
dev_addr = struct.unpack(">l", binascii.unhexlify('26013901'))[0] # a changer selon noeud
nwk_swkey = binascii.unhexlify('0FCD30ED67F8937967D6A7A099024644') # a changer selon application
app_swkey = binascii.unhexlify('9134CB1A0709E39FCD2EA10A6176F479') # a changer selon application

# Rejoindre le reseau avec l'authetification ABP
lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))

# remove all the non-default channels
for i in range(8, 16):
    lora.remove_channel(i)

# set the 3 default channels to the same frequency
lora.add_channel(0, frequency=868100000, dr_min=0, dr_max=5)
lora.add_channel(1, frequency=868100000, dr_min=0, dr_max=5)
lora.add_channel(2, frequency=868100000, dr_min=0, dr_max=5)

# Creation LoRa socket pour la com RF + configuration
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5) # ajustement Data Rate
s.setblocking(False) # socket non bloquant

data_to_send = bytes([2]) # état neutre
led_color = 0x0000ff # led yellow
pycom.rgbled(led_color)

while (True):

    # Contrôle pour vérifier si l'on a un message
    message = s.recv(256)
    print("Message :", message)
    time.sleep(5)

    if message: # Le noeud a reçu une information de la passerelle
        if message == bytes([0]):
            print("Message extinction reçu :",message)
            time.sleep(1)
            data_to_send = bytes([0])
            led_color = 0x000000  # Led éteinte
            s.send(data_to_send) # Envoi d'une donnée en LORAWAN
            pycom.rgbled(0x7f7f00) # Led jaune = envoi d'une donnée
            time.sleep(3)
            pycom.rgbled(led_color)
        elif message == bytes([1]):
            print("Message allumage reçu :",message)
            time.sleep(1)
            data_to_send = bytes([1])
            led_color = 0x007f00 # Led verte
            s.send(data_to_send) # Envoi d'une donnée en LORAWAN
            pycom.rgbled(0x7f7f00) # Led jaune = envoi d'une donnée
            time.sleep(3)
            pycom.rgbled(led_color)
        elif message == bytes([2]):
            print("Message neutre reçu :",message)
            time.sleep(1)
            data_to_send = bytes([2])
            led_color = 0x0000ff
            s.send(data_to_send) # Envoi d'une donnée en LORAWAN
            pycom.rgbled(0x7f7f00) # Led jaune = envoi d'une donnée
            time.sleep(3)
            pycom.rgbled(led_color)
    else:
        s.send(data_to_send)
        pycom.rgbled(0x7f7f00) # Led jaune = envoi d'une donnée
        time.sleep(3)
        pycom.rgbled(led_color)
