# *****************************************************************************
# * | File        :	  epd2in13_V4.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2023-06-25
# # | Info        :   python demo
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
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


import logging
from time import sleep
from . import epdconfig
from .epdbase import EPDBase

# Display resolution
EPD_WIDTH       = 122
EPD_HEIGHT      = 250

logger = logging.getLogger(__name__)

class EPD(EPDBase):
    def __init__(self, up_cb, down_cb, select_cb):
        import gpiozero

        EPDBase.__init__(self, up_cb, down_cb, select_cb, EPD_WIDTH, EPD_HEIGHT, 3)
        self.reset_pin = epdconfig.RST_PIN
        self.dc_pin = epdconfig.DC_PIN
        self.busy_pin = epdconfig.BUSY_PIN
        self.cs_pin = epdconfig.CS_PIN
        self.sw_pin = 13
        self.dt_pin = 19
        self.clk_pin = 26

        self.GPIO_SW_PIN = gpiozero.Button(self.sw_pin)
        self.GPIO_DT_PIN = gpiozero.Button(self.dt_pin)
        self.GPIO_CLK_PIN = gpiozero.Button(self.clk_pin)
        self.clk_last_state = self.GPIO_CLK_PIN.is_pressed

    '''
    function :Hardware reset
    parameter:
    '''
    def reset(self):
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(20) 
        epdconfig.digital_write(self.reset_pin, 0)
        epdconfig.delay_ms(2)
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(20)   

    '''
    function :send command
    parameter:
     command : Command register
    '''
    def send_command(self, command):
        epdconfig.digital_write(self.dc_pin, 0)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([command])
        epdconfig.digital_write(self.cs_pin, 1)

    '''
    function :send data
    parameter:
     data : Write data
    '''
    def send_data(self, data):
        epdconfig.digital_write(self.dc_pin, 1)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([data])
        epdconfig.digital_write(self.cs_pin, 1)

    # send a lot of data   
    def send_data2(self, data):
        epdconfig.digital_write(self.dc_pin, 1)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte2(data)
        epdconfig.digital_write(self.cs_pin, 1)
    
    '''
    function :Wait until the busy_pin goes LOW
    parameter:
    '''
    def ReadBusy(self):
        logger.debug("e-Paper busy")
        while(epdconfig.digital_read(self.busy_pin) == 1):      # 0: idle, 1: busy
            epdconfig.delay_ms(10)  
        logger.debug("e-Paper busy release")

    '''
    function : Turn On Display
    parameter:
    '''
    def TurnOnDisplay(self):
        self.send_command(0x22) # Display Update Control
        self.send_data(0xf7)
        self.send_command(0x20) # Activate Display Update Sequence
        self.ReadBusy()

    '''
    function : Turn On Display Fast
    parameter:
    '''
    def TurnOnDisplay_Fast(self):
        self.send_command(0x22) # Display Update Control
        self.send_data(0xC7)    # fast:0x0c, quality:0x0f, 0xcf
        self.send_command(0x20) # Activate Display Update Sequence
        self.ReadBusy()
    
    '''
    function : Turn On Display Part
    parameter:
    '''
    def TurnOnDisplayPart(self):
        self.send_command(0x22) # Display Update Control
        self.send_data(0xff)    # fast:0x0c, quality:0x0f, 0xcf
        self.send_command(0x20) # Activate Display Update Sequence
        self.ReadBusy()


    '''
    function : Setting the display window
    parameter:
        xstart : X-axis starting position
        ystart : Y-axis starting position
        xend : End position of X-axis
        yend : End position of Y-axis
    '''
    def SetWindow(self, x_start, y_start, x_end, y_end):
        self.send_command(0x44) # SET_RAM_X_ADDRESS_START_END_POSITION
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data((x_start>>3) & 0xFF)
        self.send_data((x_end>>3) & 0xFF)
        
        self.send_command(0x45) # SET_RAM_Y_ADDRESS_START_END_POSITION
        self.send_data(y_start & 0xFF)
        self.send_data((y_start >> 8) & 0xFF)
        self.send_data(y_end & 0xFF)
        self.send_data((y_end >> 8) & 0xFF)

    '''
    function : Set Cursor
    parameter:
        x : X-axis starting position
        y : Y-axis starting position
    '''
    def SetCursor(self, x, y):
        self.send_command(0x4E) # SET_RAM_X_ADDRESS_COUNTER
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data(x & 0xFF)
        
        self.send_command(0x4F) # SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(y & 0xFF)
        self.send_data((y >> 8) & 0xFF)
    
    '''
    function : Initialize the e-Paper register
    parameter:
    '''
    def init(self, after):
        if (epdconfig.module_init() != 0):
            return -1
        # EPD hardware init start
        self.reset()
        
        self.ReadBusy()
        self.send_command(0x12)  #SWRESET
        self.ReadBusy() 

        self.send_command(0x01) #Driver output control      
        self.send_data(0xf9)
        self.send_data(0x00)
        self.send_data(0x00)
    
        self.send_command(0x11) #data entry mode       
        self.send_data(0x03)

        self.SetWindow(0, 0, self.width-1, self.height-1)
        self.SetCursor(0, 0)
        
        self.send_command(0x3c)
        self.send_data(0x05)

        self.send_command(0x21) #  Display update control
        self.send_data(0x00)
        self.send_data(0x80)
    
        self.send_command(0x18)
        self.send_data(0x80)
        
        self.ReadBusy()

        after()
        while True:
            clk_state = self.GPIO_CLK_PIN.is_pressed
            dt_state = self.GPIO_DT_PIN.is_pressed
            if clk_state != self.clk_last_state:
                if dt_state != clk_state:
                    print("up")
                    self.up_cb()
                    sleep(0.01)
                else:
                    print("down")
                    self.down_cb()
                    sleep(0.01)
            self.clk_last_state = clk_state
            if (self.GPIO_SW_PIN.is_pressed):
                print("pressed")
                self.select_cb()
                sleep(0.5)

    '''
    function : Initialize the e-Paper fast register
    parameter:
    '''
    def init_fast(self):
        if (epdconfig.module_init() != 0):
            return -1
        # EPD hardware init start
        self.reset()

        self.send_command(0x12)  #SWRESET
        self.ReadBusy() 

        self.send_command(0x18) # Read built-in temperature sensor
        self.send_command(0x80)

        self.send_command(0x11) # data entry mode       
        self.send_data(0x03)    

        self.SetWindow(0, 0, self.width-1, self.height-1)
        self.SetCursor(0, 0)
        
        self.send_command(0x22) # Load temperature value
        self.send_data(0xB1)	
        self.send_command(0x20)
        self.ReadBusy()

        self.send_command(0x1A) # Write to temperature register
        self.send_data(0x64)
        self.send_data(0x00)
                        
        self.send_command(0x22) # Load temperature value
        self.send_data(0x91)	
        self.send_command(0x20)
        self.ReadBusy()
        
        return 0
        
    '''
    function : Sends the image buffer in RAM to e-Paper and displays
    parameter:
        image : Image data
    '''
    def display(self, image):
        buf = self.getbuffer(image)
        self.send_command(0x24)
        self.send_data2(buf)
        self.TurnOnDisplay()
    
    '''
    function : Sends the image buffer in RAM to e-Paper and fast displays
    parameter:
        image : Image data
    '''
    def display_fast(self, image):
        buf = self.getbuffer(image)
        self.send_command(0x24)
        self.send_data2(buf)
        self.TurnOnDisplay_Fast()
    '''
    function : Sends the image buffer in RAM to e-Paper and partial refresh
    parameter:
        image : Image data
    '''
    def displayPartial(self, image):
        buf = self.getbuffer(image)
        epdconfig.digital_write(self.reset_pin, 0)
        epdconfig.delay_ms(1)
        epdconfig.digital_write(self.reset_pin, 1)  

        self.send_command(0x3C) # BorderWavefrom
        self.send_data(0x80)

        self.send_command(0x01) # Driver output control      
        self.send_data(0xF9) 
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x11) # data entry mode       
        self.send_data(0x03)

        self.SetWindow(0, 0, self.width - 1, self.height - 1)
        self.SetCursor(0, 0)
        
        self.send_command(0x24) # WRITE_RAM
        self.send_data2(buf)
        self.TurnOnDisplayPart()

    '''
    function : Refresh a base image
    parameter:
        image : Image data
    '''
    def displayPartBaseImage(self, image):
        buf = self.getbuffer(image)
        self.send_command(0x24)
        self.send_data2(buf)
                
        self.send_command(0x26)
        self.send_data2(buf)
        self.TurnOnDisplay()
    
    '''
    function : Clear screen
    parameter:
    '''
    def Clear(self, color=0xFF):
        if self.width%8 == 0:
            linewidth = int(self.width/8)
        else:
            linewidth = int(self.width/8) + 1
        # logger.debug(linewidth)
        
        self.send_command(0x24)
        self.send_data2([color] * int(self.height * linewidth))  
        self.TurnOnDisplay()

    '''
    function : Enter sleep mode
    parameter:
    '''
    def sleep(self):
        self.send_command(0x10) #enter deep sleep
        self.send_data(0x01)
        
        epdconfig.delay_ms(2000)
        epdconfig.module_exit()

### END OF FILE ###

