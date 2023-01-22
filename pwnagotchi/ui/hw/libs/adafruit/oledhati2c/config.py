# /*****************************************************************************
# * | File        :	  config.py
# * | Author      :   Waveshare team
# * | Function    :   Hardware underlying interface,for Jetson nano
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2019-06-06
# * | Info        :
# ******************************************************************************/
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import RPi.GPIO as GPIO
import time
from smbus import SMBus
import ctypes

# Pin definition
RST_PIN = 24
address = 0x3C
bus = SMBus(1)
time.sleep(0.01)

def delay_ms(delaytime):
    time.sleep(delaytime / 1000.0)

def i2c_writebyte(reg, value):
    bus.write_byte_data(address, reg, value)
    time.sleep(0.01)

def module_init():
    print("module_init")

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(RST_PIN, GPIO.OUT)

    i2c_writebyte(0xff,0xff)
    return 0

def module_exit():
    bus.close()
    GPIO.output(RST_PIN, 0)
    GPIO.output(DC_PIN, 0)

### END OF FILE ###
