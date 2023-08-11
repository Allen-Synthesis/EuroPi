from time import sleep
from random import randint
from math import degrees, sin, cos, tan, atan, sqrt
from europi import *
from europi_script import EuroPiScript


class Organism:
    def __init__(self, cv_out):
        self.x, self.y = self.generate_random_coordinates()
        self.destination = (self.x, self.y)
        self.size = 1
        self.walking = False
        self.boredom = 0
        self.speed = 1

        self.cv_out = cv_out

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
        print(self.destination)

    def alter_speed(self, amount):
        self.speed = clamp((self.speed + amount), 1, 10)
        
    def display(self):
        int_x, int_y = int(self.x), int(self.y)
        oled.pixel(int_x - 1, int_y, 1)
        oled.pixel(int_x, int_y, 1)
        oled.pixel(int_x + 1, int_y, 1)
        oled.pixel(int_x, int_y - 1, 1)
        oled.pixel(int_x, int_y + 1, 1)

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
        self.cv_out.voltage(organism_location_voltage)


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
            new_organism = Organism(cv_out)
            organisms.append(new_organism)

        return organisms

    def main(self):
        while True:
            if self.running:
                self.tick += 1

                oled.fill(0)

                for organism in self.organisms:
                    organism.tick()
                    organism.display()

                for index_1, organism_1 in enumerate(self.organisms):
                    for index_2, organism_2 in enumerate(self.organisms):
                        if (
                            abs(organism_1.x - organism_2.x) <= self.fight_radius
                            and abs(organism_1.y - organism_2.y) <= self.fight_radius
                            and organism_1 != organism_2
                        ):  # If the organisms are close enough to fight
                            oled.rect(0, 0, OLED_WIDTH - 1, OLED_HEIGHT - 1, 1)
                            if randint(0, 1) == 1:
                                organism_1.alter_speed(1)
                                organism_2.alter_speed(-1)
                            else:
                                organism_1.alter_speed(-1)
                                organism_2.alter_speed(1)

                oled.show()

                sleep(1 - k1.percent())


if __name__ == "__main__":
    Organisms().main()
