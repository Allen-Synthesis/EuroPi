SET_CONTRAST = const(0x81)
SET_ENTIRE_ON = const(0xA4)
SET_NORM_INV = const(0xA6)
SET_DISP = const(0xAE)
SET_MEM_ADDR = const(0x20)
SET_COL_ADDR = const(0x21)
SET_PAGE_ADDR = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP = const(0xA0)
SET_MUX_RATIO = const(0xA8)
SET_COM_OUT_DIR = const(0xC0)
SET_DISP_OFFSET = const(0xD3)
SET_COM_PIN_CFG = const(0xDA)
SET_DISP_CLK_DIV = const(0xD5)
SET_PRECHARGE = const(0xD9)
SET_VCOM_DESEL = const(0xDB)
SET_CHARGE_PUMP = const(0x8D)

class SSD1306_I2C:
    def __init__(self, *args):
        pass

    def contrast(self, *args):
        pass

    def fill(self, *args):
        pass

    def fill_rect(self, *args):
        pass

    def rect(self, *args):
        pass

    def text(self, *args):
        pass

    def show(self, *args):
        pass

    def blit(self, *args):
        pass

    def hline(self, *args):
        pass

    def write_cmd(self, *args):
        pass
