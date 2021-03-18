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

data_to_send = "TEST"

while (True):
    s.send(data_to_send) # Envoi d'une donnée en LORAWAN
    pycom.rgbled(0x7f7f00) # Led jaune
    time.sleep(2)
    pycom.rgbled(0x000000) #led éteinte
    print("Data send :", data_to_send)
    time.sleep(10) # Pause de 10 secondes avant le prochain envoi
