""" LoPy LoRaWAN Nano Gateway configuration options """

import machine
import ubinascii

WIFI_MAC = ubinascii.hexlify(machine.unique_id()).upper()
# Set  the Gateway ID to be the first 3 bytes of MAC address + 'FFFE' + last 3 bytes of MAC address
GATEWAY_ID = WIFI_MAC[:6] + "FFFE" + WIFI_MAC[6:12]


SERVER ='router.eu.thethings.network' #adresse IP publique de The Things Network

PORT = 1700

NTP = "pool.ntp.org" # Réseau externe à la fac
NTP_PERIOD_S = 3600

# Remplir les champs avec le SSID et le mot de passe de la Wifi
WIFI_SSID = ''
WIFI_PASS = ''


# for EU868
# DR = 5 SF7 ; DR = 4 SF8 ; DR = 3 SF9 ; DR = 2 SF10 ; DR = 1 SF11 ;
LORA_FREQUENCY = 868100000
LORA_GW_DR = "SF7BW125"
LORA_NODE_DR = 5
