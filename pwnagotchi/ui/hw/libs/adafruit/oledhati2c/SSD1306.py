from . import config
import RPi.GPIO as GPIO
import time

Device_SPI = config.Device_SPI
Device_I2C = config.Device_I2C

LCD_WIDTH   = 128 #LCD width
LCD_HEIGHT  = 64  #LCD height

# Constants
SSD1306_I2C_ADDRESS = 0x3C    # 011110+SA0+RW - 0x3C or 0x3D
SSD1306_SETCONTRAST = 0x81
SSD1306_DISPLAYALLON_RESUME = 0xA4
SSD1306_DISPLAYALLON = 0xA5
SSD1306_NORMALDISPLAY = 0xA6
SSD1306_INVERTDISPLAY = 0xA7
SSD1306_DISPLAYOFF = 0xAE
SSD1306_DISPLAYON = 0xAF
SSD1306_SETDISPLAYOFFSET = 0xD3
SSD1306_SETCOMPINS = 0xDA
SSD1306_SETVCOMDETECT = 0xDB
SSD1306_SETDISPLAYCLOCKDIV = 0xD5
SSD1306_SETPRECHARGE = 0xD9
SSD1306_SETMULTIPLEX = 0xA8
SSD1306_SETLOWCOLUMN = 0x00
SSD1306_SETHIGHCOLUMN = 0x10
SSD1306_SETSTARTLINE = 0x40
SSD1306_MEMORYMODE = 0x20
SSD1306_COLUMNADDR = 0x21
SSD1306_PAGEADDR = 0x22
SSD1306_COMSCANINC = 0xC0
SSD1306_COMSCANDEC = 0xC8
SSD1306_SEGREMAP = 0xA0
SSD1306_CHARGEPUMP = 0x8D
SSD1306_EXTERNALVCC = 0x1
SSD1306_SWITCHCAPVCC = 0x2

# Scrolling constants
SSD1306_ACTIVATE_SCROLL = 0x2F
SSD1306_DEACTIVATE_SCROLL = 0x2E
SSD1306_SET_VERTICAL_SCROLL_AREA = 0xA3
SSD1306_RIGHT_HORIZONTAL_SCROLL = 0x26
SSD1306_LEFT_HORIZONTAL_SCROLL = 0x27
SSD1306_VERTICAL_AND_RIGHT_HORIZONTAL_SCROLL = 0x29
SSD1306_VERTICAL_AND_LEFT_HORIZONTAL_SCROLL = 0x2A

class SSD1306(object):
    def __init__(self):
        self.width = LCD_WIDTH
        self.height = LCD_HEIGHT
        #Initialize DC RST pin
        self._dc = config.DC_PIN
        self._rst = config.RST_PIN
        self._bl = config.BL_PIN
        self.Device = config.Device
        self._vccstate = SSD1306_SWITCHCAPVCC


    """    Write register address and data     """
    def command(self, cmd):
        if(self.Device == Device_SPI):
            GPIO.output(self._dc, GPIO.LOW)
            config.spi_writebyte([cmd])
        else:
            config.i2c_writebyte(0x00, cmd)

    # def data(self, val):
        # GPIO.output(self._dc, GPIO.HIGH)
        # config.spi_writebyte([val]) 

    def Init(self):
        if (config.module_init() != 0):
            return -1
        """Initialize display"""
        self.reset()
        # 128x64 pixel specific initialization.
        self.command(SSD1306_DISPLAYOFF)                    # 0xAE
        self.command(SSD1306_SETDISPLAYCLOCKDIV)            # 0xD5
        self.command(0x80)                                  # the suggested ratio 0x80
        self.command(SSD1306_SETMULTIPLEX)                  # 0xA8
        self.command(0x3F)
        self.command(SSD1306_SETDISPLAYOFFSET)              # 0xD3
        self.command(0x0)                                   # no offset
        self.command(SSD1306_SETSTARTLINE | 0x0)            # line #0
        self.command(SSD1306_CHARGEPUMP)                    # 0x8D
        if self._vccstate == SSD1306_EXTERNALVCC:
            self.command(0x10)
        else:
            self.command(0x14)
        self.command(SSD1306_MEMORYMODE)                    # 0x20
        self.command(0x00)                                  # 0x0 act like ks0108
        self.command(SSD1306_SEGREMAP | 0x1)
        self.command(SSD1306_COMSCANDEC)
        self.command(SSD1306_SETCOMPINS)                    # 0xDA
        self.command(0x12)
        self.command(SSD1306_SETCONTRAST)                   # 0x81
        if self._vccstate == SSD1306_EXTERNALVCC:
            self.command(0x9F)
        else:
            self.command(0xCF)
        self.command(SSD1306_SETPRECHARGE)                  # 0xd9
        if self._vccstate == SSD1306_EXTERNALVCC:
            self.command(0x22)
        else:
            self.command(0xF1)
        self.command(SSD1306_SETVCOMDETECT)                 # 0xDB
        self.command(0x40)
        self.command(SSD1306_DISPLAYALLON_RESUME)           # 0xA4
        self.command(SSD1306_NORMALDISPLAY)                 # 0xA6
        time.sleep(0.1)
        self.command(0xAF);#--turn on oled panel


    def reset(self):
        """Reset the display"""
        GPIO.output(self._rst,GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(self._rst,GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(self._rst,GPIO.HIGH)
        time.sleep(0.1)

    def getbuffer(self, image):
        # print "bufsiz = ",(self.width/8) * self.height
        buf = [0xFF] * ((self.width//8) * self.height)
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size
        pixels = image_monocolor.load()
        # print "imwidth = %d, imheight = %d",imwidth,imheight
        if(imwidth == self.width and imheight == self.height):
            #print ("Vertical")
            for y in range(imheight):
                for x in range(imwidth):
                    # Set the bits for the column of pixels at the current position.
                    if pixels[x, y] == 0:
                        buf[x + (y // 8) * self.width] &= ~(1 << (y % 8))
                        # print x,y,x + (y * self.width)/8,buf[(x + y * self.width) / 8]

        elif(imwidth == self.height and imheight == self.width):
            #print ("Vertical")
            for y in range(imheight):
                for x in range(imwidth):
                    newx = y
                    newy = self.height - x - 1
                    if pixels[x, y] == 0:
                        buf[(newx + (newy // 8 )*self.width) ] &= ~(1 << (y % 8))
        return buf


    # def ShowImage(self,Image):
        # self.SetWindows()
        # GPIO.output(self._dc, GPIO.HIGH);
        # for i in range(0,self.width * self.height/8):
            # config.spi_writebyte([~Image[i]])

    def ShowImage(self, pBuf):
        for page in range(0,8):
            # set page address #
            self.command(SSD1306_PAGEADDR + page);
            # set low column address #
            self.command(SSD1306_SETLOWCOLUMN);
            # set high column address #
            self.command(SSD1306_SETHIGHCOLUMN);
            # write data #
            time.sleep(0.01)
            if(self.Device == Device_SPI):
                GPIO.output(self._dc, GPIO.HIGH);
            for i in range(0,self.width):#for(int i=0;i<self.width; i++)
                if(self.Device == Device_SPI):
                    config.spi_writebyte([~pBuf[i + self.width * page]]);
                else :
                    config.i2c_writebyte(0x40, ~pBuf[i + self.width * page])





    def clear(self):
        """Clear contents of image buffer"""
        _buffer = [0xff]*(self.width * self.height//8)
        self.ShowImage(_buffer)
            #print "%d",_buffer[i:i+4096]
