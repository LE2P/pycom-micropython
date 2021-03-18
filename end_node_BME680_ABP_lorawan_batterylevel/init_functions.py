from lib.drivers.bme680.bme680 import BME680
import lib.drivers.bme680.bme680_data
from lib.interfaces.ble import Cble
from lib.interfaces.i2C import Ci2c
#from lib.services.pybytes import Cpybytes
from network import Bluetooth




# Variables
i2c = {
    "_device": "undefined, bme680",
    "device": "bme",
    "_isMaster": "Not used shall be master !!",
    "isMaster": True,
    "_bus": "0, 1 ,2( withbit ranged software)  ",
    "bus": 0,
    "baud": 10000,
    "pSDA":"P9",
    "pSCL":"P10"
  }

ble = {
    "_device": "undefined, ruuvi",
    "device" : "ruuvi",
    "_antenna": "INT=INTERNAL or EXT=EXTERNAL",
    "antenna": "INT",
    "ruuvi": {
      "1": "ca:72:2b:29:53:a8",
      "2": "f5:0e:42:63:c5:1f"
    }
  }

bme_json=  {'0': {'humidite': 0, 'temperature': 0, 'pression': 0}}
bme_to_send = {'bme':{'0': {'humidite': 0, 'temperature': 0, 'pression': 0}}}

ruuvi_json ={'1':{'temperature':0,'humidite':0,'pression':0},'2':{'temperature':0,'humidite':0,'pression':0}}
ruuvi_to_send ={'ruuvi':{'1':{'temperature':0,'humidite':0,'pression':0},'2':{'temperature':0,'humidite':0,'pression':0}}}
pkt_to_send = {'ruuvi':{'1':{'temperature':0,'humidite':0,'pression':0},'2':{'temperature':0,'humidite':0,'pression':0}},'bme':{'0': {'humidite': 0, 'temperature': 0, 'pression': 0}}}

service ={"pybytes"}

pybytes_json =  {
    "signals": {
      "0": "bme.0.temperature",
      "1": "bme.0.humidite",
      "2": "bme.0.pression",
      "3": "ruuvi.1.temperature",
      "4": "ruuvi.1.humidite",
      "5": "ruuvi.1.pression",
      "6": "ruuvi.2.temperature",
      "7": "ruuvi.2.humidite",
      "8": "ruuvi.2.pression"
    }
  }

pybytesConf = None

def init_Pybytes(pybytes_json,pybytesConf):
     try:
         from _pybytes_config import PybytesConfig
         if pybytesConf is None:
             pybytesConf = PybytesConfig().read_config()
         else:
             print("Pybytes.pybytesconf is not None")
     except Exception as e:
         print("Exception during pybyte load configuration")


#def init_device_bme(i2c):
#    I2C = Ci2c()
#    I2C.conf_json(i2c,I2C.bme)

#def init_device_ble(ble):
#    BLE = Cble(Bluetooth)
#    BLE.conf_json(ble,BLE.ruuviScan)
def insert_MAC_ruuvi(ble,mac1,mac2):
    ble["ruuvi"]["1"] = mac1
    ble["ruuvi"]["2"] = mac2

def update_I2C(bme_json,I2C,bme_to_send):
    I2C.read_device(bme_json)
    bme_to_send['bme']['0']['temperature'] = I2C.bme.data.temperature
    bme_to_send['bme']['0']['humidite'] = I2C.bme.data.humidity
    bme_to_send['bme']['0']['pression'] = I2C.bme.data.pressure
    pkt_to_send['bme'] = bme_to_send['bme']

def update_BLE(ruuvi_json,BLE,ruuvi_to_send):
    BLE.read_device(ruuvi_json)
    print(ruuvi_json)
    ruuvi_to_send['ruuvi']['1']['temperature']= ruuvi_json['1']['temperature']
    ruuvi_to_send['ruuvi']['1']['humidite']= ruuvi_json['1']['humidite']
    ruuvi_to_send['ruuvi']['1']['pression']=ruuvi_json['1']['pression']
    ruuvi_to_send['ruuvi']['2']['temperature']=ruuvi_json['2']['temperature']
    ruuvi_to_send['ruuvi']['2']['humidite']=ruuvi_json['2']['humidite']
    ruuvi_to_send['ruuvi']['2']['pression']=ruuvi_json['2']['pression']
    pkt_to_send['ruuvi'] = ruuvi_to_send['ruuvi']
