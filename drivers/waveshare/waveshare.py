import os
import sys

import PIL.ImageOps

from drivers.display import Display
from drivers.waveshare.models.waveshare_epd.epdbase import EPDBase

from drivers.waveshare.models.waveshare_epd.epdsoftware import EPD as EPDSOFTWARE

from PIL import Image,ImageDraw,ImageFont

picdir = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'waveshare'), 'pic')
libdir = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'waveshare'), 'models')

if os.path.exists(libdir):
    sys.path.append(libdir)

font12 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 15)
font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
font32 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 32)

class Waveshare(Display):
    def __init__(self, controller, model: str):
        self.controller = controller
        self.top_index = 0
        self.index = 0
        self.old_index = 0
        self.page = 'vms'
        self.epd = self.generateEpd(model)
        self.image = Image.new('1', (self.epd.height, self.epd.width), 255)
        self.draw = ImageDraw.Draw(self.image)
        self.vms = None
        self.vm = None
        self.status = None
        self.node = None
        self.id = None
        self.lines = []

    def generateEpd(self, model: str) -> EPDBase:
        match model.lower():
            case "epd2in13v4":
                try:
                    from drivers.waveshare.models.waveshare_epd.epd2in13_V4 import EPD as EPD2IN13V4
                    return EPD2IN13V4(lambda: self.go_up(), lambda: self.go_down(), lambda: self.select())
                except ImportError:
                    print("Cannot initialize e-Ink display. Reverting to software emulation.")
                    return EPDSOFTWARE(lambda: self.go_up(), lambda: self.go_down(), lambda: self.select())
            case _:
                return EPDSOFTWARE(lambda: self.go_up(), lambda: self.go_down(), lambda: self.select())

    def after(self):
        self.epd.Clear(0xFF)
        self.epd.display(self.image),
        print("end initialize")
        self.controller.launch()

    def go_up(self):
        self.old_index = self.index
        self.index = (self.index - 1)
        if self.page == 'vms':
            self.update_vm_selection()
        elif self.page == 'vm':
            self.update_vm_option_selection()

    def go_down(self):
        self.old_index = self.index
        self.index = (self.index + 1)
        if self.page == 'vms':
            self.update_vm_selection()
        elif self.page == 'vm':
            self.update_vm_option_selection()

    def select(self):
        if self.page == 'vms':
            return self.controller.display_vm(self.vms[self.index]["node"], self.vms[self.index]["vmid"])
        else:
            return self.run_option()

    def run_option(self):
        if self.status["status"] == "running":
            match self.index:
                case 0:
                    self.controller.shutdown_vm(self.node, self.id)
                case 1:
                    self.controller.reboot_vm(self.node, self.id)
                case 2:
                    self.controller.suspend_vm(self.node, self.id)
                case 3:
                    self.controller.suspend_vm(self.node, self.id)
                case 4:
                    self.controller.stop_vm(self.node, self.id)
                case 5:
                    self.controller.reset_vm(self.node, self.id)
                case 6:
                    self.controller.display_vm(self.node, self.id)
                case 7:
                    self.controller.display_vms()
                case _:
                    print("Invalid option")
        else:
            match self.index:
                case 0:
                    self.controller.start_vm(self.node, self.id)
                case 1:
                    self.controller.display_vm(self.node, self.id)
                case 2:
                    self.controller.display_vms()
                case _:
                    print("Invalid option")


    def initialize(self):
        print("begin initialize")
        self.epd.init(lambda: self.after())
        self.image = Image.new('1', (self.epd.height, self.epd.width), 255)
        self.draw = ImageDraw.Draw(self.image)
        self.draw_header()
        self.epd.displayPartBaseImage(self.image)

    def update_vm_selection(self):
        full_refresh = False
        if self.index > len(self.vms) - 1:
            self.index = 0
            self.top_index = 0
            full_refresh = True
        elif self.index < 0:
            self.index = len(self.vms) - 1
            self.top_index = len(self.vms) - 4
            full_refresh = True

        if self.index >= self.epd.lines + self.top_index:
            self.top_index = self.top_index + 1
            full_refresh = True
        elif self.index < self.top_index:
            self.top_index = self.top_index - 1
            full_refresh = True

        if full_refresh:
            self.refresh_vms()
        else:
            self.draw.polygon([(4, 63 + (20 * self.old_index)), (12, 67 + (20 * self.old_index)), (4, 71 + (20 * self.old_index))], fill=255)
            self.draw.polygon([(4, 63 + (20 * self.index)), (12, 67 + (20 * self.index)), (4, 71 + (20 * self.index))], fill=0)

        self.epd.displayPartial(self.image)

    def refresh_vms(self):
        self.draw.rectangle([(4, 63), (self.epd.height - 4, self.epd.width - 4)], fill=255)
        if len(self.vms) > self.epd.lines:
            self.draw_scrollbar(len(self.vms))
        for i in range(self.epd.lines):
            if i + self.top_index == self.index:
                self.draw.polygon([(4, 63 + (20 * i)),(12, 67 + (20 * i)), (4, 71 + (20 * i))], fill=0)
            self.draw.text((20, 60 + (20 * i)), get_vm_name(self.vms[i + self.top_index]), font=font12, fill=0)

    def display_vms(self, vms):
        self.draw.rectangle([(4, 40), (self.epd.width - 4, self.epd.height - 4)], fill=255)
        self.page = 'vms'
        self.vms = vms
        self.index = 0
        self.top_index = 0

        self.draw_header()
        self.draw.text((4, 40), "Current VMs:", font=font12, fill=0)
        self.draw.line(((4, 57), (self.epd.height - 5, 57)), fill=0)
        self.refresh_vms()

        self.epd.displayPartial(self.image)

    def display_vm(self, vm, status, node, id):
        self.draw.rectangle([(4, 40), (self.epd.width - 4, self.epd.height - 4)], fill=255)
        self.page = 'vm'
        self.vm = vm
        self.status = status
        self.node = node
        self.id = id
        self.index = 0
        self.top_index = 0

        self.draw_header()

        self.refresh_vm()

        self.epd.displayPartial(self.image)

    def refresh_vm(self):
        node_size = font12.getmask(f'Status: {self.status["status"]}').getbbox()[2]
        self.draw.rectangle([(4, 40), (self.epd.width - 4, self.epd.height - 4)], fill=255)
        self.draw.text((4, 40), get_vm_name(self.vm), font=font12, fill=0)
        self.draw.text((self.epd.height - node_size - 4, 40), f'Status: {self.status["status"]}', font=font12, fill=0)
        self.draw.line(((4, 57), (self.epd.height - 5, 57)), fill=0)
        if self.status["status"] == "running":
            self.lines = ["Shut Down VM", "Reboot VM", "Pause VM", "Hibernate VM", "Stop VM", "Reset VM", "Refresh", "Go Back"]
        else:
            self.lines = ["Start VM", "Refresh", "Go Back"]

        if len(self.lines) > self.epd.lines:
            self.draw_scrollbar(len(self.lines))
        for i in range(self.epd.lines):
            if i + self.top_index == self.index:
                self.draw.polygon([(4, 63 + (20 * i)), (12, 67 + (20 * i)), (4, 71 + (20 * i))], fill=0)
            self.draw.text((20, 60 + (20 * i)), self.lines[i + self.top_index], font=font12, fill=0)

    def update_vm_option_selection(self):
        full_refresh = False
        if self.index > len(self.lines) - 1:
            self.index = 0
            self.top_index = 0
            full_refresh = True
        elif self.index < 0:
            self.index = len(self.lines) - 1
            self.top_index = len(self.lines) - 4
            full_refresh = True

        if self.index >= self.epd.lines + self.top_index:
            self.top_index = self.top_index + 1
            full_refresh = True
        elif self.index < self.top_index:
            self.top_index = self.top_index - 1
            full_refresh = True

        if full_refresh:
            self.refresh_vm()
        else:
            self.draw.polygon([(4, 63 + (20 * self.old_index)), (12, 67 + (20 * self.old_index)), (4, 71 + (20 * self.old_index))], fill=255)
            self.draw.polygon([(4, 63 + (20 * self.index)), (12, 67 + (20 * self.index)), (4, 71 + (20 * self.index))], fill=0)

        self.epd.displayPartial(self.image)

    def draw_header(self):
        self.image = Image.new('1', (self.epd.height, self.epd.width), 255)
        self.draw = ImageDraw.Draw(self.image)
        bmp = Image.open(os.path.join(picdir, 'proxmox.bmp'))
        bmp = PIL.ImageOps.invert(bmp)
        self.draw.bitmap((4, 4), bmp)
        self.draw.text((40, 6), 'Proxmox Manager', font=font24, fill=0)

    def draw_scrollbar(self, num_vm):
        self.draw.rectangle([(self.epd.height - 8, 68), (self.epd.height - 6, self.epd.width - 12)], fill=255)
        self.draw.polygon([(self.epd.height - 7, 60), (self.epd.height - 4, 66), (self.epd.height - 10, 66)], fill=0)
        self.draw.polygon([(self.epd.height - 7, self.epd.width - 4), (self.epd.height - 4, self.epd.width - 10),
                           (self.epd.height - 10, self.epd.width - 10)], fill=0)
        tick = self.calc_tick(num_vm)
        self.draw.rectangle([(self.epd.height - 8, 68 + (tick * self.top_index)), (self.epd.height - 6, 68 + (tick * self.top_index) + (tick * self.epd.lines))], fill=0)

    def calc_tick(self, num_vm):
        height = self.epd.width - 80
        return height / num_vm

def get_vm_name(vm):
    try:
        name = vm["name"]
    except KeyError:
        name = "Unknown"
    return name
