import RPi.GPIO as GPIO  # import GPIO
from hx711 import HX711  # import the class HX711

import time

class loadcell():
    def __init__(self):
        GPIO.setmode(GPIO.BCM) # set GPIO pins to BCM numbering
        # create an hx711 object for each load cell 
        self.hx1 = HX711(dout_pin=6, pd_sck_pin=5)  #dout_pin is signal and sck is clock
        self.hx2 = HX711(dout_pin=13, pd_sck_pin=5)
        self.hx3 = HX711(dout_pin=19, pd_sck_pin=5)
        self.hx4 = HX711(dout_pin=26, pd_sck_pin=5)

        # ratio values are the ones obtained from the calibration code
        self.ratio1 = -203140
        self.hx1.set_scale_ratio(self.ratio1)
        self.ratio2 = -209464
        self.hx2.set_scale_ratio(self.ratio2)
        self.ratio3 = 211106
        self.hx3.set_scale_ratio(self.ratio3)
        self.ratio4 = -200515
        self.hx4.set_scale_ratio(self.ratio4)

        self.g= 9.81
        print('loadcell init complete')

    def tare(self):
        self.err1 = self.hx1.zero()
        self.err2 = self.hx2.zero()
        self.err3 = self.hx3.zero()
        self.err4 = self.hx4.zero()
        print('tare complete')

    def weigh(self):
        lc1=[]
        lc2=[]
        lc3=[]
        lc4=[]
        for i in range(5):
            loadcell1=self.hx1.get_weight_mean(5)
            lc1.append(loadcell1)
            loadcell2=self.hx2.get_weight_mean(5)
            lc2.append(loadcell2)
            loadcell3=self.hx3.get_weight_mean(5)
            lc3.append(loadcell3)
            loadcell4=self.hx4.get_weight_mean(5)
            lc4.append(loadcell4)
        self.weight= round(((sum(lc1)/len(lc1)) +(sum(lc2)/len(lc2)) + (sum(lc3)/len(lc3)) + (sum(lc4)/len(lc4)))*self.g,2)
        return self.weight

    def measure(self):
        self.loadcell1=self.hx1.get_weight_mean(2)*self.g
        self.loadcell2=self.hx2.get_weight_mean(2)*self.g
        self.loadcell3=self.hx3.get_weight_mean(2)*self.g
        self.loadcell4=self.hx4.get_weight_mean(2)*self.g
        return round(self.loadcell1,2), round(self.loadcell2,2),round(self.loadcell3,2), round(self.loadcell4,2)