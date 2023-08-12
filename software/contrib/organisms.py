from time import sleep
from random import randint
from math import degrees, sin, cos, tan, atan, sqrt
from europi import *
from europi_script import EuroPiScript
from framebuf import FrameBuffer, MONO_HLSB

circle_bytearray = bytearray(b'\x07\x00\x18\xc0  @\x10@\x10\x80\x08\x80\x08\x80\x08@\x10@\x10  \x18\xc0\x07\x00')
circle_buffer = FrameBuffer(circle_bytearray,13,13, MONO_HLSB)

class Organism:
    def __init__(self, cv_out, starting_speed=1):
        self.x, self.y = self.generate_random_coordinates()
        self.destination = (self.x, self.y)
        self.size = 1
        self.walking = False
        self.boredom = 0
        self.speed = starting_speed
        self.maximum_speed = 6
        self.fighting = False
        self.last_opponent = None
        self.display_active = False

        self.cv_out = cv_out
        
    def set_fighting(self, value, opponent=None):
        self.fighting = value
        if opponent != None:
            self.last_opponent = opponent
            
    def set_display_active(self, value):
        self.display_active = value

    def generate_random_coordinates(self):
        return (randint(10, OLED_WIDTH - 11), randint(6, OLED_HEIGHT - 7))

    def calculate_boredom(self):
        if self.walking == False:  # If the organism is not walking it will get increasingly bored
            self.boredom += 1
        else:
            self.boredom -= 2  # If it is walking it will very quickly become not bored
        self.boredom = clamp(
            self.boredom, 0, 100
        )  # Boredom is a percentage so cannot go below 0 or above 100

    def calculate_hypotenuse(self, adjacent, opposite):
        return sqrt((adjacent**2) + (opposite**2))

    def choose_new_destination(self):
        self.destination = self.generate_random_coordinates()
        self.walking = True

    def alter_speed(self, amount):
        self.speed = clamp((self.speed + amount), 1, self.maximum_speed)
        
    def display(self):
        int_x, int_y = int(self.x), int(self.y)
        oled.pixel(int_x, int_y, 1)
        
        if self.speed >= 2:
            oled.pixel(int_x - 1, int_y, 1)
            oled.pixel(int_x + 1, int_y, 1)
            oled.pixel(int_x, int_y - 1, 1)
            oled.pixel(int_x, int_y + 1, 1)
        if self.speed >= 3:
            oled.pixel(int_x - 1, int_y - 1, 1)
            oled.pixel(int_x + 1, int_y - 1, 1)
            oled.pixel(int_x - 1, int_y + 1, 1)
            oled.pixel(int_x + 1, int_y + 1, 1)
        if self.speed >= 4:
            oled.pixel(int_x, int_y - 2, 1)
            oled.pixel(int_x, int_y + 2, 1)
            oled.pixel(int_x - 2, int_y, 1)
            oled.pixel(int_x + 2, int_y, 1)
        if self.speed >= 5:
            oled.pixel(int_x - 2, int_y + 1, 1)
            oled.pixel(int_x + 1, int_y + 2, 1)
            oled.pixel(int_x + 2, int_y - 1, 1)
            oled.pixel(int_x - 1, int_y - 2, 1)
        if self.speed >= 6:
            oled.pixel(int_x - 2, int_y - 1, 1)
            oled.pixel(int_x - 1, int_y + 2, 1)
            oled.pixel(int_x + 2, int_y + 1, 1)
            oled.pixel(int_x + 1, int_y - 2, 1)
            oled.pixel(int_x, int_y + 3, 1)
            oled.pixel(int_x, int_y - 3, 1)
            oled.pixel(int_x + 3, int_y, 1)
            oled.pixel(int_x - 3, int_y, 1)

    def tick(self):
        self.calculate_boredom()

        if self.boredom > randint(
            0, 99
        ):  # The organism gets so bored that it chooses a new destination and begins walking
            self.choose_new_destination()

        if self.walking:  # If the organism is walking
            adjacent = self.destination[0] - self.x
            opposite = self.destination[1] - self.y
            try:
                angle = abs(atan(opposite / adjacent))
            except ZeroDivisionError:
                angle = 0

            total_distance_remaining = self.calculate_hypotenuse(adjacent, opposite)
            if (
                abs(total_distance_remaining) <= self.speed
            ):  # The organism reaches its destination (or would exceed it in the next tick)
                self.x, self.y = self.destination[0], self.destination[1]
                self.walking = False

            distance_x = cos(angle) * self.speed * (1 if adjacent >= 0 else -1)
            self.x += distance_x

            distance_y = sin(angle) * self.speed * (1 if opposite >= 0 else -1)
            self.y += distance_y

        organism_location_value = self.calculate_hypotenuse(
            (self.x / OLED_WIDTH), (self.y / OLED_HEIGHT)
        )  # The total 'value' of the organism's location between 0 and square root of 2
        organism_location_voltage = organism_location_value * 7.07
        
        if self.display_active:
            self.display()
        
        self.cv_out.voltage(organism_location_voltage)
        
        self.fighting = False


class Organisms(EuroPiScript):
    def __init__(self):
        super().__init__()

        self.tick = 0

        self.organisms = self.generate_organisms()

        self.fight_radius = 5
        
        self.running = True
        
        b1.handler(self.start_stop)

    @classmethod
    def display_name(cls):
        return "Life"
    
    def start_stop(self):
        self.running = not self.running

    def generate_organisms(self, start_population=6):
        organisms = []
        for organism_index in range(start_population):
            cv_out = cvs[organism_index]
            new_organism = Organism(cv_out, organism_index+1)
            organisms.append(new_organism)

        return organisms
    
    
    def begin_simulation(self):
        text = 'birthing organisms'
        letters = []
        for letter in text:
            letters.append([letter,0])
        x_offsets = [8, 8, 8, 8, 6, 6, 6, 6, 5, 5, 5, 5, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 6, 6, 6, 6, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8]
        start_x = OLED_WIDTH

        for offset_index, offset in enumerate(x_offsets):
            oled.fill(0)
            
            if offset_index == 10:
                self.organisms[0].set_display_active(True)
            elif offset_index == 20:
                self.organisms[1].set_display_active(True)
            elif offset_index == 30:
                self.organisms[2].set_display_active(True)
            elif offset_index == 40:
                self.organisms[3].set_display_active(True)
            elif offset_index == 50:
                self.organisms[4].set_display_active(True)
            elif offset_index == 60:
                self.organisms[5].set_display_active(True)
                
            for organism in self.organisms:
                organism.tick()
            
            oled.fill_rect(0, 12, max((start_x - letters[-1][1]) + (8 * 18), 0), 10, 0)
            
            for letter_index, letter in enumerate(letters):
                letter[1] += offset
                oled.text(letter[0], int((start_x - letter[1]) + (8 * letter_index)), 14)
            oled.show()
            sleep(0.01)

    def main(self):
        
        self.begin_simulation()
        
        while True:
            if self.running:
                self.tick += 1

                oled.fill(0)

                for index_1, organism_1 in enumerate(self.organisms):
                    if organism_1.fighting == False:	#If the organism is already fighting, reduce calculation effort by skipping fight calculations
                        for index_2, organism_2 in enumerate(self.organisms):
                            if organism_2.fighting == False and organism_2.last_opponent != organism_1:
                                if (
                                    abs(organism_1.x - organism_2.x) <= self.fight_radius
                                    and abs(organism_1.y - organism_2.y) <= self.fight_radius
                                    and organism_1 != organism_2
                                ):  # If the organisms are close enough to fight
                                    organism_1.set_fighting(True, organism_2)
                                    organism_2.set_fighting(True, organism_1)
                                    midpoint = (int(organism_1.x + ((organism_2.x - organism_1.x) / 2)), int(organism_1.y + ((organism_2.y - organism_1.y) / 2)))
                                    oled.blit(circle_buffer, midpoint[0]-6, midpoint[1]-6)
                                    if randint(0, 1) == 1 and organism_2.speed > 1 and organism_1.speed < 6:	#As all energy must be reserved, organism_2 must have a speed of at least 2 to be able to 'give' 1 to organism_1
                                        organism_1.alter_speed(1)
                                        organism_2.alter_speed(-1)
                                    elif organism_1.speed > 1 and organism_2.speed < 6:
                                        organism_1.alter_speed(-1)
                                        organism_2.alter_speed(1)
                                    else:
                                        None	#Neither organism has any speed to 'give' so nothing happens
                                        
                for organism in self.organisms:
                    organism.tick()

                oled.show()

                sleep(1 - k1.percent())


if __name__ == "__main__":
    Organisms().main()
