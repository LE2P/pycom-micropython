import time
import machine
import struct
import binascii
import socket
import json
import pycom
from network import WLAN, LoRa, Bluetooth
#from lib.services.pybytes import Cpybytes
from init_functions import *
from lib.interfaces.i2c import Ci2c
from machine import ADC

pycom.heartbeat(False)
I2C = Ci2c()
I2C.conf_json(i2c,I2C.bme)
state = bytes([0]) #1 = état allumé et 0 = état éteint
# conf de l'ADC LoPy pour une lecture de tension de batterie
pin_batt = 'P16';
adc = machine.ADC(0);
analog_batt =adc.channel(pin=pin_batt, attn=ADC.ATTN_6DB);

# Europe = LoRa.EU868, setup pour la communication
lora = LoRa(mode=LoRa.LORAWAN, tx_iq=True,region=LoRa.EU868) # tx_iq activer pour eviter les redondances

# Parametres pour ABP (authetification par personalisation)
dev_addr = struct.unpack(">l", binascii.unhexlify('2601126E'))[0] # a changer selon noeud
nwk_swkey = binascii.unhexlify('1A89E8BF1264C10A514A921C74FA06C3') # a changer selon application
app_swkey = binascii.unhexlify('CB828B81441CC0AA995C019CAB614E18') # a changer selon application

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

def formatage(temp,hum,pres): # Fonction qui permet de formater les données mesurées par le BME680 en bytes pour un envoi LoRaWAN
        # Multiplication par 1000 pour obtenir des nombres entiers
        T = int(round(temp, 2) * 1000)
        H = int(round(hum, 2) * 1000)
        P = int(round((pres/6),2)*1000)

        nT = '{:06d}'.format(T) # Température
        avT = int(''.join([nT[i] for i in range(0,3)])) # Avant la virgule
        apT = int(''.join([nT[j] for j in range(3, len(nT)-1)])) # Après la virgule
        nP = '{:06d}'.format(P) # Pression
        avP = int(''.join([nP[i] for i in range(0,3)]))
        apP = int(''.join([nP[j] for j in range(3, len(nP)-1)]))
        nH = '{:06d}'.format(H) # Humidité
        avH = int(''.join([nH[i] for i in range(0,3)]))
        apH = int(''.join([nH[j] for j in range(3, len(nH)-1)]))
        pkt = bytes([avT]) + bytes([apT])+ bytes([avH]) + bytes([apH])+ bytes([avP]) + bytes([apP])
        return pkt

def get_batt(): # Fonction qui récupère le niveau de batterie du noeud
    Vbat = 0; mVbat = 0;
    combi_resistance = 3.05357143
    Moy = []
    for i in range(20):
        Vbat = analog_batt.voltage() / 1000;
        Moy.append(Vbat)
        mVbat = sum(Moy) / len(Moy)
    Vbat =  mVbat * combi_resistance
    print("Niveau de batterie (V) : ",Vbat)
    # formatage du nombre flottant en nombre entier pour un envoi en bytes
    Vbat = 100 * (Vbat / 2)
    print("Niveau de batterie formaté:",Vbat)
    return int(Vbat)

while(True):
    # Configuration I2C
    update_I2C(bme_json,I2C,bme_to_send)
    print(bme_to_send)
    # Récupération des données du capteur
    temp = I2C.bme.data.temperature
    hum = I2C.bme.data.humidity
    pres = I2C.bme.data.pressure
    # Formatage des données BME680 en trame de bytes
    pkt = formatage(temp, hum, pres)
    print("LoRa packet :",pkt)
    # Récupération du niveau de batterie
    battery = get_batt()
    print("Battery level :",battery)
    battery_level = bytes([battery])
    # Envoi des données en LoRaWAN
    s.send(pkt+battery_level)
    time.sleep(20)
