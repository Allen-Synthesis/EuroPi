SET_CONTRAST = 0x81
SET_ENTIRE_ON = 0xA4
SET_NORM_INV = 0xA6
SET_DISP = 0xAE
SET_MEM_ADDR = 0x20
SET_COL_ADDR = 0x21
SET_PAGE_ADDR = 0x22
SET_DISP_START_LINE = 0x40
SET_SEG_REMAP = 0xA0
SET_MUX_RATIO = 0xA8
SET_COM_OUT_DIR = 0xC0
SET_DISP_OFFSET = 0xD3
SET_COM_PIN_CFG = 0xDA
SET_DISP_CLK_DIV = 0xD5
SET_PRECHARGE = 0xD9
SET_VCOM_DESEL = 0xDB
SET_CHARGE_PUMP = 0x8D


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
