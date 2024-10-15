from drivers.waveshare.lib.waveshare_epd.epdbase import EPDBase
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image

class EPD(EPDBase):
    def __init__(self, up_cb, down_cb, select_cb):
        super(EPD, self).__init__(up_cb, down_cb, select_cb, 122, 250, 3)
        self.window = Tk()
        self.wait_state = False
        self.init_events()
        self.window.geometry(f'{self.height}x{self.width}')
        self.window.title('WaveShare Emulator')
        self.canvas = Canvas(self.window)
        # self.canvas.create_rectangle(0, 0, self.height, self.width, fill='white')
        self.canvas.pack(fill=BOTH, expand=True)

    def init_events(self):
        self.window.bind('<Key>', self.wait)
        self.window.bind('<Control-s>', self.switch_wait_state)

    def init(self, after):
        self.window.after(1, lambda: after())
        self.switch_wait_state()
        self.window.mainloop()

    def display(self, image):
        self.img = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, image=self.img, anchor=NW)

    def displayPartial(self, image):
        self.display(image)

    def displayPartBaseImage(self, image):
        self.display(image)

    def Clear(self, color):
        pass

    def switch_wait_state(self):
        self.wait_state = not self.wait_state

    def wait(self, event):
        if self.wait_state and any(key == event.keysym for key in ['Up']):
            self.up_cb()
        elif self.wait_state and any(key == event.keysym for key in ['Down']):
            self.down_cb()
        elif self.wait_state and any(key == event.keysym for key in ['Return']):
            self.select_cb()
        else:
            self.do_nhth()

    @staticmethod
    def do_nhth():
        pass