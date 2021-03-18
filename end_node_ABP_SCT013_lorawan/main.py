

# Import pour communication LoRa
from network import LoRa
from network import WLAN
from network import Bluetooth
#from network import LTE

import socket
import binascii
import struct
import math
import time
import machine
import pycom
from machine import ADC, DAC

# On désactive tout ce qui consomme
pycom.heartbeat(False)
bt = Bluetooth()
bt.deinit()
wlan = WLAN()
wlan.deinit()
#lte = LTE()
#lte.deinit()
# import pour le Capteur
import sct013_libv2


# configuration capteur

calibre = 15 # calibre du capteur [5, 15, 30, 100]
SCT013_100 = sct013_libv2.SCT013(calibre, 'P16', 230)# fontion d'initalisation du capteur

dac = DAC('P22')

type_cap = [5, 15, 30, 100] # correspondant au SCT013 5, 15,30 et 100 A



def formatage_4(val):
        I = int(round(val, 2) * 1000)
        nI = '{:06d}'.format(I)
        av = int(''.join([nI[i] for i in range(0,3)]))
        ap = int(''.join([nI[j] for j in range(3, len(nI)-1)]))

        pkt = bytes([2]) + bytes([av]) + bytes([ap])
        return pkt

def treat_tab(tab, min, max,moy):
    min = tab[0]
    max = tab[0]
    for i in range(0,len(tab)):
        if min > tab[i]:
            min = tab[i]
        elif max < tab[i]:
            max = tab[i]

# Europe = LoRa.EU868, setup pour la communication
lora = LoRa(mode=LoRa.LORAWAN, tx_iq=True, region=LoRa.EU868) # tx_iq activer pour eviter les redondances

dev_addr = struct.unpack(">l", binascii.unhexlify('260111BB'))[0] # a changer selon noeud
nwk_swkey = binascii.unhexlify('3B84B57D3CB94B00B4F48190A81029C2') # a changer selon application
app_swkey = binascii.unhexlify('5C4EFB6E3C8803419B903C1FAEEAB4F5') # a changer selon application


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

# Routine principal pour l'envoi des donnees Courant
while(True):
    #calibre = 100
    V = SCT013_100.calc_Vrms2()
    I = SCT013_100.calc_Irms2(V)
    P = SCT013_100.calc_Puiss2(I)
    pkt = formatage_4(I)

    print("Tension image = %.3f en V" %V)
    print("Courant = %.3f en A" %I)
    print("LoRa send pkt : ", pkt)

    s.send(pkt)

    time.sleep(15)
