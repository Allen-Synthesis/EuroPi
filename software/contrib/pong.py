"""
Pong
author: Igor Nawrocki (github.com/Bugari)
date: 2023-05-19
labels: game

EuroPi version of the classic Pong game.

digital_in: unused
analog_in: unused

knob_1: controls position of the left paddle
knob_2: controls position of the right paddle

button_1: start a new game
button_2: unused

output_1: trigger a sound for the ball hitting a wall
output_2: trigger a sound for the ball hitting a paddle
output_3: trigger a sound for scoring
output_4: unused
output_5: unused
output_6: unused

"""

import math
import time
import random
from time import sleep
from europi import oled, b1, k1, k2, Output, cv1, cv2, cv3
from europi_script import EuroPiScript


class Paddle:
    LEFT = -1
    RIGHT = 1
    NONE = 0

class SoundTrigger:
    def __init__(self, cv: Output):
        self.trigger_time_ms = 50
        self.cv = cv
        self.triggered = False
        self.last_trigger_time = 0


    def trigger(self):
        self.cv.on()
        self.triggered = True
        self.last_trigger_time = time.ticks_ms()

    def update(self):
        if self.triggered:
            if time.ticks_ms() - self.last_trigger_time > self.trigger_time_ms:
                self.cv.off()
                self.triggered = False

    def reset(self):
        self.cv.off()
        self.triggered = False


wall_sound = SoundTrigger(cv1)
paddle_sound = SoundTrigger(cv2)
score_sound = SoundTrigger(cv3)


sounds = [wall_sound, paddle_sound, score_sound]

class Ball:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.dx = 0
        self.dy = 0
        self.reset()
        [s.reset() for s in sounds]


    def randomize_direction(self):
        angle = random.randint(-45, 45)

        radians = angle * (math.pi / 180)

        self.dx = math.cos(radians) * random.choice([-1, 1]) * 1.4
        self.dy = math.sin(radians) * random.choice([-1, 1]) * 1.4

    def update(self, paddle_1_x, paddle_1_y, paddle_2_x, paddle_2_y, paddle_height):
        self.x += self.dx
        self.y += self.dy
        self.handle_bounce()
        self.handle_paddle_collision(paddle_1_x, paddle_1_y, paddle_height, Paddle.LEFT)
        self.handle_paddle_collision(paddle_2_x, paddle_2_y, paddle_height, Paddle.RIGHT)
        return self.handle_score()

    def handle_bounce(self):
        if self.y < 0:
            wall_sound.trigger()
            self.y *= -1
            self.dy *= -1
        elif self.y > oled.height-1:
            wall_sound.trigger()
            self.y = oled.height - (self.y - oled.height)
            self.dy *= -1

    def check_paddle_collision(self, paddle_x, paddle_y, paddle_height, dir: Paddle):
        if self.x < paddle_x and dir == Paddle.RIGHT:
            return False
        if self.x > paddle_x and dir == Paddle.LEFT:
            return False
        if self.y < paddle_y:
            return False
        if self.y > paddle_y + paddle_height:
            return False
        return True

    def handle_paddle_collision(self, paddle_x, paddle_y, paddle_height, dir):
        if self.check_paddle_collision(paddle_x, paddle_y, paddle_height, dir):
            paddle_sound.trigger()
            self.x = paddle_x - (self.x - paddle_x)
            self.dx *= -1
            self.dx += math.copysign(0.8, self.dx)

    def check_score(self) -> Paddle:
        if self.x < 0:
            return Paddle.RIGHT
        elif self.x > oled.width:
            return Paddle.LEFT
        else:
            return Paddle.NONE

    def handle_score(self):
        score = self.check_score()
        if score != 0:
            score_sound.trigger()
            self.reset()
            return score
        else:
            return 0

    def reset(self):
        self.x = oled.width // 2
        self.y = oled.height // 2
        self.randomize_direction()

    def draw(self):
        oled.rect(int(self.x), int(self.y), 1, 1, 1)


class Pong(EuroPiScript):
    def __init__(self):
        super().__init__()
        
        # used to avoid screen burn-in
        self.line_shift = False

        self.ball = Ball()
        self.ball.reset()
        self.paddle_height = oled.height // 4
        self.pad_pos = [0, 0]
        self.score = [0, 0]

    def draw_paddle(self, x, y):
        oled.vline(x, y, self.paddle_height, 1)

    def update_paddle_positions(self):
        self.pad_pos[0] = k1.read_position(oled.height - self.paddle_height)
        self.pad_pos[1] = k2.read_position(oled.height - self.paddle_height)

    def draw_midline(self):
        for i in range(self.line_shift * 2, oled.height, 4):
            oled.vline(oled.width // 2, i, 2, 1)

    def update_paddles(self):
        self.update_paddle_positions()
        self.draw_paddle(1, self.pad_pos[0])
        self.draw_paddle(oled.width - 1, self.pad_pos[1])

    def draw(self):
        oled.fill(0)
        self.draw_midline()
        self.update_paddles()
        scored = self.ball.update(1, self.pad_pos[0], oled.width-1, self.pad_pos[1], self.paddle_height)
        self.ball.draw()
        if scored != Paddle.NONE:
            self.score[scored-1] += 1
            self.animate_score()
        oled.show()

    def animate_score(self):
        self.line_shift = not self.line_shift
        for i in range(0, 3):
            self.display_score()
            [s.update() for s in sounds]
            sleep(0.2 * i)
            oled.fill(0)
            self.draw_midline()
            oled.show()
            [s.update() for s in sounds]
            sleep(0.2 * i)

    def display_score(self):
        oled.fill(0)
        oled.text(str(self.score[0]), oled.width // 4 - 10, oled.height // 2 - 4, 1)
        oled.text(str(self.score[1]), (oled.width // 4) * 3, oled.height // 2 - 4, 1)
        self.draw_midline()
        oled.show()

    @ classmethod
    def display_name(cls):
        return "Pong"

    def main(self):
        [s.reset() for s in sounds]
        
        @b1.handler
        def on_b1_press():
            self.score = [0, 0]
            self.ball.reset()
            self.animate_score()

        while True:
            self.draw() 
            [s.update() for s in sounds]
            sleep(0.05)


if __name__ == "__main__":
    Pong().main()
