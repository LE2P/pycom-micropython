"""
Flavien BERNARD
stage LE2P LoRa 2019
"""


import machine
from machine import ADC
import math

class SCT013:
    '''
    L'objet SCT013 qui represente le capteur
    :calibre : correspond a l'amperage maximal du capteur (SCT013-0030 calibre = 30)
        type : int
    :pin : pin de lecture de la LoPy ('P18' adc classique)
        type : str
    :V_res : Tension sur le reseau (230 Volts)
        type : int
    '''

    def __init__(self, calibre, pin, V_res):

        self.calibre = calibre
        self.pin = pin
        self.V_res = V_res

        # conf de l'ADC LoPy
        self.adc = machine.ADC(0)
        self.analog_in = self.adc.channel(pin=self.pin, attn=ADC.ATTN_11DB)
        self.off_read = self.analog_in.voltage()/1000 # tension de reference sur entree adc

        # Definition de certaine constantes
        self.adc_res = 12 # resolution adc
        self.adc_range = 2**self.adc_res # nb de bits (= 4096 bits)
        self.N = 1000 # nb d'echantillons pour Methode R-M-S


    # methodes pour les calculs
    def calc_Vrms2(self):
        """
        Tension R-M-S
        """
        sum = 0
        carr = 0
        for i in range(self.N):
            V_im = self.analog_in.voltage() / 1000
            self.off_read = (self.off_read + (V_im - self.off_read) / self.adc_range) # filtrage de l'offset sur la lecture filtre digital
            V_filtre = V_im - self.off_read
            carr = V_filtre**2
            sum = sum + carr
        V_rms = math.sqrt(sum / self.N)
        return V_rms

    def calc_Irms2(self, V):
        """
        :V : tension R-M-S fourni par calc_Vrms2
            type : float
        """
        I_rms = V * self.calibre
        return I_rms

    def calc_Puiss2(self, I):
        """
        :I : Courant R-M-S fourni par calc_Irms2
            type : float
        """
        P = I * self.V_res
        return P
