from abc import abstractmethod


class EPDBase:
    def __init__(self, up_cb, down_cb, select_cb, width, height, lines):
        self.up_cb = up_cb
        self.down_cb = down_cb
        self.select_cb = select_cb
        self.width = width
        self.height = height
        self.lines = lines

    @abstractmethod
    def init(self, after):
        pass

    def getbuffer(self, image):
        img = image
        imwidth, imheight = img.size
        if imwidth == self.width and imheight == self.height:
            img = img.convert('1')
        elif imwidth == self.height and imheight == self.width:
            # image has correct dimensions, but needs to be rotated
            img = img.rotate(90, expand=True).convert('1')
        else:
            # return a blank buffer
            return [0x00] * (int(self.width / 8) * self.height)

        buf = bytearray(img.tobytes('raw'))
        return buf

    @abstractmethod
    def display(self, image):
        pass

    @abstractmethod
    def displayPartial(self, image):
        pass

    @abstractmethod
    def displayPartBaseImage(self, image):
        pass

    @abstractmethod
    def Clear(self, color):
        pass