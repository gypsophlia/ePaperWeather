# //*****************************************************************************
# * | File        :	  epd2in13.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * |	This version:   V3.0
# * | Date        :   2018-11-01
# * | Info        :   python2 demo
# * 1.Remove:
#   digital_write(self, pin, value)
#   digital_read(self, pin)
#   delay_ms(self, delaytime)
#   set_lut(self, lut)
#   self.lut = self.lut_full_update
# * 2.Change:
#   display_frame -> TurnOnDisplay
#   set_memory_area -> SetWindow
#   set_memory_pointer -> SetCursor
# * 3.How to use
#   epd = epd2in13.EPD()
#   epd.init(epd.lut_full_update)
#   image = Image.new('1', (epd2in13.EPD_WIDTH, epd2in13.EPD_HEIGHT), 255)
#   ...
#   drawing ......
#   ...
#   epd.display(getbuffer(image))
# ******************************************************************************//
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and//or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
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


import epdconfig
from PIL import Image
import RPi.GPIO as GPIO
# import numpy as np

# Display resolution
EPD_WIDTH       = 122
EPD_HEIGHT      = 250

class EPD:
    def __init__(self):
        self.reset_pin = epdconfig.RST_PIN
        self.dc_pin = epdconfig.DC_PIN
        self.busy_pin = epdconfig.BUSY_PIN
        self.cs_pin   = epdconfig.CS_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
    lut_full_update = [
        0x22, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x11,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x1E, 0x1E, 0x1E, 0x1E, 0x1E, 0x1E, 0x1E, 0x1E,
        0x01, 0x00, 0x00, 0x00, 0x00, 0x00
    ]

    lut_partial_update  = [
        0x18, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x0F, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]
        
    # Hardware reset
    def reset(self):
        epdconfig.digital_write(self.cs_pin, GPIO.LOW)
        epdconfig.digital_write(self.reset_pin, GPIO.HIGH)
        epdconfig.delay_ms(200) 
        epdconfig.digital_write(self.reset_pin, GPIO.LOW)         # module reset
        epdconfig.delay_ms(200)
        epdconfig.digital_write(self.reset_pin, GPIO.HIGH)
        epdconfig.delay_ms(200)   
        epdconfig.digital_write(self.cs_pin, GPIO.HIGH)

    def send_command(self, command):
        epdconfig.digital_write(self.cs_pin, GPIO.LOW)
        epdconfig.digital_write(self.dc_pin, GPIO.LOW)
        epdconfig.spi_writebyte([command])
        epdconfig.digital_write(self.cs_pin, GPIO.HIGH)

    def send_data(self, data):
        epdconfig.digital_write(self.cs_pin, GPIO.LOW)
        epdconfig.digital_write(self.dc_pin, GPIO.HIGH)
        epdconfig.spi_writebyte([data])
        epdconfig.digital_write(self.cs_pin, GPIO.HIGH)
        
    def wait_until_idle(self):
        while(epdconfig.digital_read(self.busy_pin) == 1):      # 0: idle, 1: busy
            epdconfig.delay_ms(100)    

    def TurnOnDisplay(self):
        # Fix
        #self.send_command(0xC4) # DISPLAY_UPDATE_CONTROL_2
        #self.send_data(0xC7)
        self.send_command(0x22) # DISPLAY_UPDATE_CONTROL_2
        self.send_data(0xC4)
        self.send_command(0x20) # MASTER_ACTIVATION
        self.send_command(0xFF) # TERMINATE_FRAME_READ_WRITE
        self.wait_until_idle()

    def init(self, lut):
        if (epdconfig.module_init() != 0):
            return -1
        # EPD hardware init start
        self.reset()
        self.send_command(0x01) # DRIVER_OUTPUT_CONTROL
        self.send_data((EPD_HEIGHT - 1) & 0xFF)
        self.send_data(((EPD_HEIGHT - 1) >> 8) & 0xFF)
        self.send_data(0x00) # GD = 0 SM = 0 TB = 0
        
        self.send_command(0x0C) # BOOSTER_SOFT_START_CONTROL
        self.send_data(0xD7)
        self.send_data(0xD6)
        self.send_data(0x9D)
        
        self.send_command(0x2C) # WRITE_VCOM_REGISTER
        self.send_data(0xA8) # VCOM 7C
        
        self.send_command(0x3A) # SET_DUMMY_LINE_PERIOD
        self.send_data(0x1A) # 4 dummy lines per gate
        
        self.send_command(0x3B) # SET_GATE_TIME
        self.send_data(0x08) # 2us per line
        
        self.send_command(0X3C) # BORDER_WAVEFORM_CONTROL
        self.send_data(0x03)      
        
        self.send_command(0X11) # DATA_ENTRY_MODE_SETTING
        self.send_data(0x03) # X increment; Y increment
        
        # WRITE_LUT_REGISTER
        self.send_command(0x32)
        for count in range(30):
            self.send_data(lut[count])

        return 0
        
##
 #  @brief: specify the memory area for data R//W
 ##
    def SetWindows(self, x_start, y_start, x_end, y_end):
        self.send_command(0x44) # SET_RAM_X_ADDRESS_START_END_POSITION
        self.send_data((x_start >> 3) & 0xFF)
        self.send_data((x_end >> 3) & 0xFF)
        self.send_command(0x45) # SET_RAM_Y_ADDRESS_START_END_POSITION
        self.send_data(y_start & 0xFF)
        self.send_data((y_start >> 8) & 0xFF)
        self.send_data(y_end & 0xFF)
        self.send_data((y_end >> 8) & 0xFF)

##
 #  @brief: specify the start point for data R//W
 ##
    def SetCursor(self, x, y):
        self.send_command(0x4E) # SET_RAM_X_ADDRESS_COUNTER
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data((x >> 3) & 0xFF)
        self.send_command(0x4F) # SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(y & 0xFF)
        self.send_data((y >> 8) & 0xFF)
        self.wait_until_idle()
        
    def getbuffer(self, image):
        if self.width%8 == 0:
            linewidth = self.width//8
        else:
            linewidth = self.width//8 + 1
         
        buf = [0xFF] * (linewidth * self.height)
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size
        pixels = image_monocolor.load()
        
        if(imwidth == self.width and imheight == self.height):
            print("Vertical")
            for y in range(imheight):
                for x in range(imwidth):                    
                    if pixels[x, y] == 0:
                        # x = imwidth - x
                        buf[x // 8 + y * linewidth] &= ~(0x80 >> (x % 8))
        elif(imwidth == self.height and imheight == self.width):
            print("Horizontal")
            for y in range(imheight):
                for x in range(imwidth):
                    newx = y
                    newy = self.height - x - 1
                    if pixels[x, y] == 0:
                        # newy = imwidth - newy - 1
                        buf[newx // 8 + newy*linewidth] &= ~(0x80 >> (y % 8))
        return buf   

        
    def display(self, image):
        if self.width%8 == 0:
            linewidth = self.width//8
        else:
            linewidth = self.width//8 + 1

        self.SetWindows(0, 0, EPD_WIDTH, EPD_HEIGHT);
        for j in range(0, self.height):
            self.SetCursor(0, j);
            self.send_command(0x24);
            for i in range(0, linewidth):
                self.send_data(image[i + j * linewidth])   
        self.TurnOnDisplay()
    
    def Clear(self, color):
        if self.width%8 == 0:
            linewidth = self.width//8
        else:
            linewidth = self.width//8 + 1

        self.SetWindows(0, 0, EPD_WIDTH, EPD_HEIGHT);
        for j in range(0, self.height):
            self.SetCursor(0, j);
            self.send_command(0x24);
            for i in range(0, linewidth):
                self.send_data(color)   
        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0x10) #enter deep sleep
        self.send_data(0x01)
        epdconfig.delay_ms(100)    

### END OF FILE ###

