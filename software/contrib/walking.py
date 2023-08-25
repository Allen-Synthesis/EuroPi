from time import sleep
from europi import *
from europi_script import EuroPiScript
from framebuf import FrameBuffer, MONO_HLSB
from random import randint, choice


def bytearray_to_framebuffer(b_array, x, y):
    "Convert a bytearray string to a FrameBuffer object"
    fb = bytearray(b_array)
    buf = FrameBuffer(fb, x, y, MONO_HLSB)
    return buf

PERCENT_IMAGE = bytearray_to_framebuffer(b'\xc8\xd0  X\x98', 5, 6)

# Images for numbers 0-9 with a font size of 5x6
NUMBER_IMAGES = [
    bytearray_to_framebuffer(b'p\x88\x88\x88\x88p', 5, 6),
    bytearray_to_framebuffer(b'`\xa0   \xf8', 5, 6),
    bytearray_to_framebuffer(b'p\x88\x080@\xf8', 5, 6),
    bytearray_to_framebuffer(b'p\x888\x08\x88p', 5, 6),
    bytearray_to_framebuffer(b'0P\x90\xf8\x10\x10', 5, 6),
    bytearray_to_framebuffer(b'\xf8\x80p\x08\x88p', 5, 6),
    bytearray_to_framebuffer(b'p\x80\xf0\x88\x88p', 5, 6),
    bytearray_to_framebuffer(b'\xf8\x08\x10 @\x80', 5, 6),
    bytearray_to_framebuffer(b'p\x88p\x88\x88p', 5, 6),
    bytearray_to_framebuffer(b'p\x88\x88x\x08p', 5, 6)
    ]

# A pattern which covers up the plants so they appear to fade out of view
DITHER_PATTERN = [
    (0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),
    (1,1),(1,2),(1,3),(1,4),(1,5),(1,6),
    (2,2),(2,3),(2,4),(2,5),(2,6),
    (3,3),(3,4),(3,5),(3,6),
    (4,4),(4,5),(4,6),
    (5,5),(5,6),
    (6,6)
    ]

def display_small_numbers(number, x, y, percent=False):
    "Display an integer in a small (5x6) font at given coordinates with an optional percentage sign"
    number = str(number)
    length = len(number)
    
    for index in range(length):
        oled.blit(NUMBER_IMAGES[int(number[index])], (x + (index * 6)), y)
        
    if percent:
        oled.blit(PERCENT_IMAGE, (x + (length * 6)), y)

def display_dither(x, y, colour=0):
    "Display the dither pattern at given coordinates with a given colour"
    for pixel in DITHER_PATTERN:
        oled.pixel(x + pixel[0], y - pixel[1], colour)

class Walking(EuroPiScript):
    def __init__(self):
        super().__init__()
        
        self.increment_amount = 2
        
        self.walking_images = [
            bytearray_to_framebuffer(b'P\xf8\xd4\xfcp0000', 7, 9),
            bytearray_to_framebuffer(b'P\xf8\xd4\xfcp008l', 7, 9),
            bytearray_to_framebuffer(b'P\xf8\xd4\xfcp08l\xc6', 7, 9),
            bytearray_to_framebuffer(b'P\xf8\xd4\xfcp008l', 7, 9)
            ]
        
        self.number_of_walking_images = len(self.walking_images)
        self.walking_index = 0
        
        self.plant_text = bytearray_to_framebuffer(
            b'\xe4\x00\x00\x80\x00\x00\x00\x00\x00\x00\x01\xf0\x00\x00\x00\x00\x94\x1c9\xe3\x80\x00\x00\x00\x00\x00\x00DI\x1c\x00\x00\x94"D\x84\x00\x00\x00\x00\x00\x00\x00DV\xa2\x00\x00\xe4"D\x83\x00\x00\x00\x00\x00\x00\x00DP\xa2\x00\x00\x84\xa2D\x90\x80\x00\x00\x00\x00\x00\x00DP\xa2\x00\x00\x83\x1dDg\x00\x00\x00\x00\x00\x00\x01\x83\x90\xbc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
            128, 32)
        
        self.cloud_images = [
            bytearray_to_framebuffer(b'\x03\x1c\x00\xe00\x00\xce\x00', 14, 4),
            bytearray_to_framebuffer(b'X\xa4x', 6, 3),
            bytearray_to_framebuffer(b'\x1epa\x88\x90D\x88\x04@\x08?\xf0', 14, 6),
            bytearray_to_framebuffer(b'<xB\x86\x85\t\x88\x01\x80\x01@\x02?\xfc', 16, 7),
            ]
        
        self.clouds = []
        self.cloud_chance = 5
        
        self.plant_images = [
            bytearray_to_framebuffer(b'\x08\x14\x14P\xa4*(\x10\x10', 7, 9),
            bytearray_to_framebuffer(b' \xa0@P  \xa0@@', 4, 9),
            bytearray_to_framebuffer(b'H$\xc8(\x92J$(\x10', 7, 9),
            bytearray_to_framebuffer(b'\x00\x00\x00\x00\x00@$\xa8z', 7, 9),
            bytearray_to_framebuffer(b'\x00h\x94 \x10 \x10 \x10', 7, 9),
            bytearray_to_framebuffer(b'\x00\x00\x82\x94R\x8aRJ\x92', 7, 9),
            bytearray_to_framebuffer(b'\x00\x00\x00\x00\x00\x00\x10R\xac', 7, 9)
            ]
        self.plants = [[choice(self.plant_images), 0]]
        self.plant_collision = False
        self.update_plant_spawn_chance()
        
        self.left_limit = 0
        self.plant_despawn_x = OLED_WIDTH - self.left_limit
        
        self.character_x = 20
        self.character_y = OLED_HEIGHT - 11
        
        self.jumping_offsets = [
            [0],
            [0, 3],
            [0, 3, 2],
            [0, 3, 5, 2],
            [0, 4, 5, 5, 3],
            [0, 4, 5, 6, 4, 2],
            [0, 5, 6, 6, 5, 3, 1],
            [0, 5, 7, 8, 8, 6, 3, 0]
            ]
        
        self.jumping = False
        self.beginning_jump = False
        self.jumping_index = 0
        self.update_current_jumping_offsets()
        
        self.earth = []
        self.fill_earth()
        
        self.clocked_cvs = [cv1, cv2, cv3]
        
    @classmethod
    def display_name(cls):
        return "Walking"
    
    def initialise(self):
        "Initialise the display and handlers"
        oled.fill(0)
        for t in range(OLED_WIDTH):
            self.tick(False)
        oled.show()
        
        b1.handler(self.begin_jumping)
        din.handler(self.tick)
        din.handler_falling(self.un_tick)
        
    def read_k1(self):
        return k1.read_position(101)
        
    def read_k2(self):
        return k2.choice(self.jumping_offsets)
        
    def update_current_jumping_offsets(self):
        self.current_jumping_offsets = self.read_k2()
        self.jumping_index = clamp(self.jumping_index, 0, len(self.current_jumping_offsets) - 1)
        
    def update_plant_spawn_chance(self):
        self.plant_spawn_chance = self.read_k1()
    
    def update_outputs(self):
        cv1.on()
            
        if self.plant_collision:
            cv2.on()

        if self.beginning_jump:
            cv3.on()
            self.beginning_jump = False
            
        cv4.voltage(self.plant_spawn_chance / 10)
        
        cv5.voltage(k2.read_position() / 10)
            
        if self.jumping:
            cv6.on()
        else:
            cv6.off()
            
    def begin_jumping(self):
        self.update_current_jumping_offsets()
        self.walking_index = 0
        self.jumping = True
        self.beginning_jump = True
    
    def fill_earth(self):
        while len(self.earth) <= OLED_WIDTH:
            self.earth.append(randint(0, 1))
            
    def display_earth(self):
        y = OLED_HEIGHT - 1
        for x in range(OLED_WIDTH):
            oled.pixel(x, y, self.earth[x])
    
    def increment_plants(self):
        try:
            plant_too_close = False if self.plants[-1][1] >= self.increment_amount else True	# plant_too_close prevents overlapping plants that are closer than the width of one clock pulse
        except IndexError:
            plant_too_close = False
        
        if self.plant_spawn_chance > randint(0, 100) and not plant_too_close:
            self.plants.append([choice(self.plant_images), 0])	# Create a new plant with a random image
            
        self.plant_collision = False	# This variable determines if the player has hit a plant on the current tick
            
        plants_to_remove = []
            
        for plant in self.plants:
            plant[1] += self.increment_amount	# Move every plant one step to the left
            
            if OLED_WIDTH - plant[1] == self.character_x:	# If the plant is at the same location as the player
                self.plant_collision = True
                
            if plant[1] == self.plant_despawn_x:	# If the plant has got far enough to the left to despawn
                plants_to_remove.append(plant)
            else:
                oled.blit(plant[0], OLED_WIDTH - plant[1], self.character_y + 2)	# Draw the plant at its current location
            
        for dead_plant in plants_to_remove:
            self.plants.remove(dead_plant)
            
    def increment_clouds(self):
        clouds_to_remove = []
        if len(self.clouds) != 0:
            for cloud in self.clouds:
                cloud[1] -= cloud[3]
                if cloud[1] == -14:
                    clouds_to_remove.append(cloud)
                else:
                    oled.blit(cloud[0], int(cloud[1]), cloud[2])
        for dead_cloud in clouds_to_remove:
            self.clouds.remove(dead_cloud)

        if randint(0, 100) < self.cloud_chance:
            new_cloud_speed = randint(1, len(self.cloud_images))
            new_cloud_image = self.cloud_images[new_cloud_speed - 1]
            
            try:
                if (OLED_WIDTH - self.clouds[-1][1]) > 14:
                    self.clouds.append([new_cloud_image, OLED_WIDTH, randint(9, 16), (new_cloud_speed / len(self.cloud_images))])
            except IndexError:
                self.clouds.append([new_cloud_image, OLED_WIDTH, randint(9, 16), (new_cloud_speed / len(self.cloud_images))])
    
    def increment_earth(self):
        self.earth = self.earth[self.increment_amount:]
        self.fill_earth()
        self.display_earth()
    
    def increment_walking(self):
        if self.jumping:
            self.jumping_index += 1
            if self.jumping_index == len(self.current_jumping_offsets):
                self.jumping = False
                self.jumping_index = 0
        else:
            self.walking_index = (self.walking_index + 1) % self.number_of_walking_images
        oled.blit(self.walking_images[self.walking_index], self.character_x, (self.character_y - self.current_jumping_offsets[self.jumping_index]))
        
    def increment_variables(self):
        self.increment_earth()
        self.increment_plants()
        self.increment_clouds()
        self.increment_walking()
        
    def display_extras(self):
        oled.blit(self.plant_text, 0, 0)
        display_small_numbers(min(self.read_k1(), 100), 38, 0, True)
        display_small_numbers(len(self.read_k2()), 120, 0)

    def un_tick(self):
        for cv in self.clocked_cvs:
            cv.off()

    def tick(self, show=True):        
        if show:
            self.update_outputs()
            
        self.update_plant_spawn_chance()
        
        oled.fill(0)
        
        self.display_extras()
        self.increment_variables()
        
        display_dither(self.left_limit + 3, 28, 0)
        
        if show:
            oled.show()

    def main(self):
        self.initialise()
        while True:
            None

if __name__ == "__main__":
    Walking().main()

