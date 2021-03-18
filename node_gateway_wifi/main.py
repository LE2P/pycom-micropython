""" LoPy LoRaWAN Nano Gateway example usage """

import config
import pycom
from nanogateway import NanoGateway

pycom.heartbeat(False)


if __name__ == '__main__':
    nanogw = NanoGateway(
        config.GATEWAY_ID,
        config.LORA_FREQUENCY,
        config.LORA_GW_DR,
        config.WIFI_SSID,
        config.WIFI_PASS,
        config.SERVER,
        config.PORT,
        config.NTP,
        ntp_period = config.NTP_PERIOD_S
        )

    nanogw.start()
    pycom.rgbled(0xFFFFFF)
    nanogw._log('You may now press ENTER to enter the REPL')

    #nanogw._send_down_link('OK', 0,"SF7BW125", 868100000)
    input()
