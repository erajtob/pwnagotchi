from . import SSD1306
from . import config

disp = SSD1306.SSD1306()

class EPD(object):

    def __init__(self):
        self.reset_pin = config.RST_PIN
        self.dc_pin = config.DC_PIN
        self.busy_pin = config.BUSY_PIN
        self.cs_pin = config.CS_PIN
        self.width = disp.width
        self.height = disp.height

    def init(self):
        disp.Init()

    def Clear(self):
        disp.clear()

    def display(self, image):
        disp.ShowImage(disp.getbuffer(image))
