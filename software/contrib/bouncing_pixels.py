# Copyright 2025 Allen Synthesis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
A bunch of pixels bouncing around, inspired by the beloved bouncing DVD logo.
A gate is triggered each time a wall is hit. See `bouncing_pixels.md` for more information.

@author  Jorin (jorin.se)
@year    2025
"""

from europi import *
from europi_script import EuroPiScript

from experimental.math_extras import rescale
from experimental.knobs import KnobBank
import configuration

from _thread import start_new_thread
from cmath import phase, polar, rect
from math import degrees, e, inf, log, pi, radians
from random import uniform
from time import sleep_ms, ticks_ms, ticks_diff

tau = pi * 2

ARENA_HEIGHT = 480

COLLISION_ID_UP = 0
COLLISION_ID_LEFT = 1
COLLISION_ID_RIGHT = 2
COLLISION_ID_DOWN = 3
COLLISION_ID_ANY = 4
COLLISION_ID_CORNER = 5

def exponential_interpolation(a, b, t):
    """Exponentially interpolate between a and b by t, where t=0 gives a and t=1 gives b.
    This function uses e as the base which hopefully gives a "natural" feeling curve.
    """
    return e ** (t * log(b + 1 - a)) - 1 + a


class Event():
    """A simple, synchronous event implementation. Handlers can be added either when instantiating,
    or by using the += operator. The event is then emitted using the emit function.
    """
    def __init__(self, *handlers):
        # *handlers is a tuple, so we must explicitly create a mutable list to add given handlers to.
        self.handlers = []
        self.handlers.extend(handlers)
        
    def __iadd__(self, handler):
        self.handlers.append(handler)
        return self
        
    def emit(self, *args, **kwargs):
        """Emit the event, calling each handler synchronously in the order they were added.
        Arguments are passed through to each handler, so it is up to the user to ensure that
        the arguments match up.
        """
        for handler in self.handlers:
            handler(*args, **kwargs)


class Arena():
    def __init__(self, config):
        self.config = config
        self.on_width_changed = Event()
        
        # Height is constant
        self.height = ARENA_HEIGHT # Simulated size
        self.display_height = oled.height # Displayed arena height
        self.draw_y_min = 0 # First y coordinate for the displayed arena
        self.draw_y_max = self.draw_y_min + self.display_height # Last y coordinate for the displayed arena
        
        # Width is variable, but we initialise its variables here to ensure it can be referenced.
        self.width = oled.width * self.height / oled.height
        self.display_width = oled.width
        self.draw_x_min = 0
        self.draw_x_max = oled.width
        
    def update_width(self, aspect_ratio):
        """Set the arena's width according to given aspect ratio.
        """
        prev_width = self.width
        self.width = int(self.height * aspect_ratio)
        self.display_width = int(self.display_height * aspect_ratio)
        self.draw_x_min = int(oled.width / 2 - self.display_width / 2)
        self.draw_x_max = self.draw_x_min + self.display_width
        self.on_width_changed.emit(prev_width, self.width)
        
    def draw_boundary(self):
        """Draw the boundaries of the arena, one pixel outside of draw_x_min and draw_x_max.
        This will fall outside of the bounds of the display when the arena covers the full screen, which is intentional.
        """
        oled.vline(self.draw_x_min - 1, 0, oled.height, 1)
        oled.vline(self.draw_x_max + 1, 0, oled.height, 1)


class Ball():
    def __init__(self, arena, config):
        self.config = config
        self.bounce_angle_deviation_max = radians(config.bounce_angle_deviation_max)
        self.impulse_speed_multiplier = 1.0
        self.arena = arena
        
        self.on_over_speed = Event(getattr(self, config.over_speed_behaviour))
        self.on_under_speed = Event(getattr(self, config.under_speed_behaviour))
        self.on_collide = Event()
        arena.on_width_changed += self.translate_x
        
        self.reset()
        
    def __repr__(self):
        speed, direction = polar(self.velocity)
        return f"Ball at ({self.pos.real}, {self.pos.imag}), velocity {speed}/s {int(degrees(direction))}°"
    
    def if_active(fn):
        """Functions wrapped with this function will only run if self.active is true.
        This is needed to avoid processing when over/under speed behaviour is set to deactivate.
        """
        def inner(self, *args, **kwargs):
            if not self.active:
                return
            fn(self, *args, **kwargs)
        return inner

    @if_active
    def draw(self):
        arena = self.arena
        x = int(rescale(
            self.pos.real,
            0, arena.width,
            arena.draw_x_min, arena.draw_x_max
        ))
        
        y = int(rescale(
            self.pos.imag,
            0, arena.height,
            arena.draw_y_min, arena.draw_y_max
        ))
        
        oled.pixel(x, y, 1)
                
    def translate_x(self, old_width: float, new_width: float):
        """Translate the pixel's x so that it's the same relative distance from the edges with new_width as it was with old_width.
        """
        new_x = new_width * self.pos.real / old_width
        self.pos = complex(new_x, self.pos.imag)
        
    def reset(self):
        """Reset the pixel, randomising its position, velocity, bounciness, acceleration, and marking it as active.
        """
        self.pos = complex(
            uniform(0, self.arena.width),
            uniform(0, self.arena.height)
        )
        self.velocity = rect(
            uniform(self.config.start_speed_min, self.config.start_speed_max),
            uniform(0, tau)
        )
        self.bounciness = uniform(self.config.bounciness_min, self.config.bounciness_max)
        self.acceleration = uniform(self.config.accel_min, self.config.accel_max)
        self.active = True

    @if_active
    def impulse(self):
        """Apply an impulse of speed in a random direction to the pixel.
        """
        self.velocity += rect(
            uniform(self.config.impulse_speed_variation_min, self.config.impulse_speed_variation_max) * self.impulse_speed,
            uniform(0, tau)
        )
        
    def deactivate(self):
        """Set the pixel to inactive, meaning it won't be processed by functions that are wrapped by @if_active.
        """
        self.active = False
    
    def noop(self):
        """Do nothing. This is used as a possible under speed behaviour.
        """
        pass
    
    @if_active
    def tick(self, delta: float):
        # Apply acceleration
        delta_v = rect(self.acceleration * delta, phase(self.velocity))
        self.velocity += delta_v
                
        # Grab the speed and direction of the resulting velocity for later use
        speed, direction = polar(self.velocity)
        
        # Apply velocity and check whether collisions happened
        delta_x = self.velocity.real * delta
        delta_y = self.velocity.imag * delta
        
        collide_x = (self.pos.real + delta_x) // self.arena.width
        collide_y = (self.pos.imag + delta_y) // self.arena.height
        
        self.pos += complex(
            delta_x - delta_x * abs(collide_x) * 2,
            delta_y - delta_y * abs(collide_y) * 2,
        )

        if collide_x != 0:
            if collide_x != 1: # Left
                self.on_collide.emit(COLLISION_ID_LEFT)
            if collide_x != -1: # Right
                self.on_collide.emit(COLLISION_ID_RIGHT)
            if self.pos.imag < self.config.corner_collision_margin or self.arena.height - self.pos.imag < self.config.corner_collision_margin:
                self.on_collide.emit(COLLISION_ID_CORNER)
            
            speed *= self.bounciness
            direction = pi - direction + uniform(-self.bounce_angle_deviation_max, self.bounce_angle_deviation_max)
        
        if collide_y != 0:
            if collide_y != 1: # Up
                self.on_collide.emit(COLLISION_ID_UP)
            if collide_y != -1: # Down
                self.on_collide.emit(COLLISION_ID_DOWN)
            
            speed *= self.bounciness
            direction = -direction + uniform(-self.bounce_angle_deviation_max, self.bounce_angle_deviation_max)
        
        # Update velocity based on changes to speed and direction stemming from collisions
        self.velocity = rect(speed, direction)
            
        # Travelled more than one width or height in one tick.
        # TODO: we should be able to account for multiple collisions in one tick and not need this check
        if abs(collide_x) > 1 or abs(collide_y) > 1 or speed > self.config.over_speed_threshold:
            self.on_over_speed.emit()
            
        # Speed too low
        if speed < self.config.under_speed_threshold:
            self.on_under_speed.emit()

        
class Gate():
    def __init__(self, cv, gate_hold_length):
        self.cv = cv
        self.gate_hold_length = gate_hold_length
        self.opened = None
        
    def on(self):
        self.cv.on()
        self.opened = ticks_ms()
        
    def off(self):
        self.cv.off()
        self.opened = None
        
    def tick(self, delta: float):
        if self.opened is None:
            return
        if ticks_diff(ticks_ms(), self.opened) >= self.gate_hold_length:
            self.off()


class BouncingPixels(EuroPiScript):
    def __init__(self):
        super().__init__()
        saved_state = self.load_state_json()
        self.state_saved = False
        self.k1_bank = (
            KnobBank.builder(k1)
            .with_locked_knob('speed', initial_percentage_value=saved_state.get('speed', 0.5))
            .with_locked_knob('ball_count', initial_percentage_value=saved_state.get('ball_count', 0.0))
            # .with_locked_knob('gravity_magnitude', initial_percentage_value=0.0)
            .build()
        )
        
        self.k2_bank = (
            KnobBank.builder(k2)
            .with_locked_knob('aspect_ratio', initial_percentage_value=saved_state.get('aspect_ratio', 1.0))
            .with_locked_knob('impulse_speed', initial_percentage_value=saved_state.get('impulse_speed', 0.5))
            # .with_locked_knob('gravity_direction', initial_percentage_value=0.0)
            .build()
        )

        # Initialise some internal state variables
        self.b1_pressed = None
        self.b2_pressed = None
        self.ball_count = 1
        self.time_factor = 1
        
        # Trackers of inputs
        # -1 as a starting value means they always get updated on first poll.
        self.speed_input = -1.0
        self.aspect_ratio_input = -1.0
        self.ball_count_input = -1.0
        self.impulse_speed_input = -1.0
        self.ain_input = -1.0
        
        # We store analogue input values in these. Although we only change change one as determined by
        # config.ain_function, we do need to reference them all when their respective knobs change.
        self.speed_ain_term = 0.0
        self.aspect_ratio_ain_term = 0.0
        self.ball_count_ain_term = 0.0
        self.impulse_speed_ain_term = 0.0
        
        # Initialise input events
        self.on_speed_input = Event(self.mark_state_unsaved, self.apply_speed)
        self.on_aspect_ratio_input = Event(self.mark_state_unsaved, self.apply_aspect_ratio)
        self.on_ball_count_input = Event(self.mark_state_unsaved, self.apply_ball_count)
        self.on_impulse_speed_input = Event(self.mark_state_unsaved, self.apply_impulse_speed)
        self.on_ain_input = Event(
            # To avoid excess compute spent on string formatting or dict lookups in the main loop, we keep an assortment of
            # set and apply functions so that we can assign them once and for all here.
            getattr(self, f'update_{self.config.ain_function}_ain_term'),
            getattr(self, f'apply_{self.config.ain_function}'),
        )
        
        # Create the playing field and gate abstractions
        self.arena = Arena(self.config)
        self.balls = [Ball(arena=self.arena, config=self.config) for _ in range(self.config.ball_count_max)]
        hold_lengths = [
            self.config.gate_hold_length_top,
            self.config.gate_hold_length_left,
            self.config.gate_hold_length_right,
            self.config.gate_hold_length_bottom,
            self.config.gate_hold_length_any,
            self.config.gate_hold_length_corner,
        ]
        self.gates = [Gate(cv, hold_length) for cv, hold_length in zip(cvs, hold_lengths)]
        
        # Register external event handlers.
        b1.handler(self.b1_rising)
        b1.handler_falling(self.b1_falling)
        b2.handler(self.b2_rising)
        b2.handler_falling(self.b2_falling)
        din.handler(getattr(self, self.config.din_function))
        
        for ball in self.balls:
            ball.on_collide += self.report_collision
            
    @classmethod
    def display_name(cls):
        return "Bouncing Pixels"
    
    @classmethod
    def config_points(cls):
        return [
            configuration.floatingPoint('aspect_ratio_min',
                minimum=2.0 / oled.height,
                maximum=oled.width / oled.height,
                default=4.0 / oled.height
            ),
            configuration.floatingPoint('aspect_ratio_max',
                minimum=2.0 / oled.height,
                maximum=oled.width / oled.height,
                default=oled.width / oled.height
            ),
            configuration.floatingPoint('poll_frequency', minimum=5.0, maximum=120.0, default=20.0, danger=True),
            configuration.floatingPoint('save_period', minimum=0.0, maximum=inf, default=5000.0, danger=True),
            configuration.floatingPoint('render_frequency', minimum=1.0, maximum=inf, default=30.0, danger=True),
            configuration.floatingPoint('long_press_length', minimum=0.0, maximum=inf, default=500.0),
            configuration.floatingPoint('timescale_min', minimum=-inf, maximum=inf, default=0.0),
            configuration.floatingPoint('timescale_max', minimum=-inf, maximum=inf, default=100.0),
            configuration.floatingPoint('knob_change_threshold', minimum=0.0, maximum=0.1, default=0.01),
            configuration.choice('din_function', choices=['impulse', 'reset'], default='impulse'),
            configuration.choice('ain_function', choices=['speed', 'aspect_ratio', 'ball_count', 'impulse_speed'], default='speed'),
            configuration.floatingPoint('gate_hold_length_top', minimum=1.0, maximum=10_000.0, default=25.0),
            configuration.floatingPoint('gate_hold_length_left', minimum=1.0, maximum=10_000.0, default=25.0),
            configuration.floatingPoint('gate_hold_length_right', minimum=1.0, maximum=10_000.0, default=25.0),
            configuration.floatingPoint('gate_hold_length_bottom', minimum=1.0, maximum=10_000.0, default=25.0),
            configuration.floatingPoint('gate_hold_length_any', minimum=1.0, maximum=10_000.0, default=10.0),
            configuration.floatingPoint('gate_hold_length_corner', minimum=1.0, maximum=10_000.0, default=100.0),
            configuration.integer('ball_count_max', minimum=1, maximum=inf, default=100),
            configuration.integer('ball_count_min', minimum=1, maximum=inf, default=1),
            configuration.floatingPoint('corner_collision_margin', minimum=0.0, maximum=ARENA_HEIGHT / 2.0, default=ARENA_HEIGHT / oled.height),
            configuration.floatingPoint('start_speed_min', minimum=0.0, maximum=inf, default=10.0),
            configuration.floatingPoint('start_speed_max', minimum=0.0, maximum=inf, default=100.0),
            configuration.floatingPoint('accel_min', minimum=-inf, maximum=inf, default=-5.0),
            configuration.floatingPoint('accel_max', minimum=-inf, maximum=inf, default=5.0),
            configuration.floatingPoint('bounciness_min', minimum=0.0001, maximum=inf, default=0.8),
            configuration.floatingPoint('bounciness_max', minimum=0.0001, maximum=inf, default=1.2),
            configuration.floatingPoint('bounce_angle_deviation_max', minimum=0.0, maximum=180.0, default=15.0),
            configuration.choice('under_speed_behaviour', choices=['impulse', 'reset', 'deactivate', 'noop'], default='reset'),
            configuration.choice('over_speed_behaviour', choices=['reset', 'deactivate'], default='reset'),
            configuration.floatingPoint('under_speed_threshold', minimum=0.0, maximum=inf, default=5.0),
            configuration.floatingPoint('over_speed_threshold', minimum=0.0, maximum=inf, default=1.0e6),
            configuration.floatingPoint('impulse_speed_min', minimum=0.0, maximum=inf, default=10.0),
            configuration.floatingPoint('impulse_speed_max', minimum=0.0, maximum=inf, default=1000.0),
            configuration.floatingPoint('impulse_speed_variation_min', minimum=0.0, maximum=inf, default=0.5),
            configuration.floatingPoint('impulse_speed_variation_max', minimum=0.0, maximum=inf, default=2.0),
        ]
    
    # Button handlers
    def b1_rising(self):
        self.k1_bank.set_current('ball_count')
        self.k2_bank.set_current('impulse_speed')
        self.b1_pressed = ticks_ms()
    
    def b1_falling(self):
        self.k1_bank.set_current('speed')
        self.k2_bank.set_current('aspect_ratio')
        
        delta = ticks_diff(ticks_ms(), self.b1_pressed)
        if delta <= self.config.long_press_length:
            self.reset()
            
        self.b1_pressed = None
    
    def b2_rising(self):
        # self.k1_bank.set_current('gravity_magnitude')
        # self.k2_bank.set_current('gravity_direction')
        self.k1_bank.set_current('ball_count')
        self.k2_bank.set_current('impulse_speed')
        self.b2_pressed = ticks_ms()
    
    def b2_falling(self):
        self.k1_bank.set_current('speed')
        self.k2_bank.set_current('aspect_ratio')
        
        delta = ticks_diff(ticks_ms(), self.b2_pressed)
        if delta <= self.config.long_press_length:
            self.impulse()
            
        self.b2_pressed = None
        
    def mark_state_unsaved(self):
        """Denote that the state saved onto storage does not match current knob state.
        """
        self.state_saved = False
        
    def save_state(self):
        """Save knob states to storage and denote that storage matches current knob state.
        """
        self.save_state_json({
            'speed': self.speed_input,
            'aspect_ratio': self.aspect_ratio_input,
            'ball_count': self.ball_count_input,
            'impulse_speed': self.impulse_speed_input
        })
        self.state_saved = True
        
    # Event handlers to save analogue input into respective variables
    def update_speed_ain_term(self):
        self.speed_ain_term = ain.percent()
    
    def update_aspect_ratio_ain_term(self):
        self.aspect_ratio_ain_term = ain.percent()
        
    def update_ball_count_ain_term(self):
        self.ball_count_ain_term = ain.percent()
        
    def update_impulse_speed_ain_term(self):
        self.impulse_speed_ain_term = ain.percent()
        
    # Event handlers to apply knob and analogue input values
    def apply_speed(self):
        # Time factor is calibrated so that an input of 0 stops time, an input of 0.5 runs at 1x speed,
        # and an input of 1.0 gives the configured max speed.
        # https://math.stackexchange.com/questions/3311614/find-the-exponential-curve-through-three-data-points
        input_sum = self.speed_input + self.speed_ain_term
        # self.time_factor = (
            # (
                # e ** (2 * log(self.config.timescale_max - 1) * input_sum
                      # ) / (self.config.timescale_max - 2)
            # ) -1 / (self.config.timescale_max - 2)
        # )
        self.time_factor = exponential_interpolation(self.config.timescale_min, self.config.timescale_max, input_sum)
        
    def apply_aspect_ratio(self):
        input_sum = self.aspect_ratio_input + self.aspect_ratio_ain_term
        aspect_ratio = rescale(input_sum, 0.0, 1.0, self.config.aspect_ratio_min, self.config.aspect_ratio_max)
        self.arena.update_width(aspect_ratio)
        
    def apply_ball_count(self):
        input_sum = self.ball_count_input + self.ball_count_ain_term
        self.ball_count = int(exponential_interpolation(self.config.ball_count_min, self.config.ball_count_max, input_sum))
        
    def apply_impulse_speed(self):
        # Impulse strength is calibrated so that an input of 0 gives 0.1 and an input of 1 gives 100.
        input_sum = self.impulse_speed_input + self.impulse_speed_ain_term
        impulse_speed = exponential_interpolation(self.config.impulse_speed_min, self.config.impulse_speed_max, input_sum)
        for ball in self.balls:
            ball.impulse_speed = impulse_speed
    
    def report_collision(self, collision_id: int):
        """Open the gate corresponding to the given collision ID, as well as the any gate.
        """
        self.gates[COLLISION_ID_ANY].on()
        self.gates[collision_id].on()

    def reset(self):
        """Reset all balls and gates.
        """
        for ball in self.balls:
            ball.reset()
        for gate in self.gates:
            gate.off()
        
    def impulse(self):
        """Apply an impulse to all balls currently in play.
        """
        for i in range(self.ball_count):
            self.balls[i].impulse()

    def poll(self):
        """Poll for input and emit corresponding events when changes are detected
        """
        new_speed_input = self.k1_bank.speed.percent()
        new_aspect_ratio_input = self.k2_bank.aspect_ratio.percent()
        new_ball_count_input = self.k1_bank.ball_count.percent()
        new_impulse_speed_input = self.k2_bank.impulse_speed.percent()
        new_ain_input = ain.percent()
        
        # The difference between the new and registered input must exceed the threshold in order to trigger a change.
        # This reduces jitter, which can in particular be visible in the aspect ratio.
        if abs(new_speed_input - self.speed_input) > self.config.knob_change_threshold:
            self.speed_input = new_speed_input
            self.on_speed_input.emit()
            
        if abs(new_aspect_ratio_input - self.aspect_ratio_input) > self.config.knob_change_threshold:
            self.aspect_ratio_input = new_aspect_ratio_input
            self.on_aspect_ratio_input.emit()
            
        # Since the rest of the parameters require a button to be held, they will not jitter once the button is released
        # and no threshold check should be needed.
        if new_ball_count_input != self.ball_count_input:            
            self.ball_count_input = new_ball_count_input
            self.on_ball_count_input.emit()
            
        if new_impulse_speed_input != self.impulse_speed_input:
            self.impulse_speed_input = new_impulse_speed_input
            self.on_impulse_speed_input.emit()
            
        if new_ain_input != self.ain_input:
            self.ain_input = new_ain_input
            self.on_ain_input.emit()

    def tick(self, delta: float):
        """Process a tick in the simulation.
        Delta should already include any time scaling, meaning that this function is
        naive to any time scale.
        """
        any_active = False
        for i in range(self.ball_count):
            self.balls[i].tick(delta)
            any_active = any_active or self.balls[i].active
        for gate in self.gates:
            gate.tick(delta)
        if not any_active:
            self.reset()
        
    def render(self):
        """Render the simulation. This is the only function that should call any drawing commands.
        """
        oled.fill(0)
        self.arena.draw_boundary()
        for i in range(self.ball_count):
            if not self.balls[i].active:
                continue
            self.balls[i].draw()
        oled.show()
        
    def main(self):
        """Start the application.
        """
        # Per chrisib's recommendation after some display-related errors,
        # the render thread specifically runs on cpu0 as this might be the
        # cpu that handles i2c communication with the display.
        proc_thread = start_new_thread(self.proc_thread, ())
        self.render_thread()

    def proc_thread(self):
        """Run the simulation, poll inputs, and save state as necessary.
        """
        prev_cycle = None
        last_poll = None
        poll_period = 1000.0 / self.config.poll_frequency
        while True:
            cycle_start = ticks_ms()
            delta = ticks_diff(cycle_start, prev_cycle) / 1000
            
            # Poll inputs at limited frequency
            time_since_poll = ticks_diff(cycle_start, last_poll)
            if time_since_poll > poll_period:
                self.poll()
                last_poll = cycle_start
                
            # Save at limited frequency
            if not self.state_saved and self.last_saved() > self.config.save_period:
                self.save_state()
            
            self.tick(delta * self.time_factor)            
            prev_cycle = cycle_start
            
    def render_thread(self):
        """Render at limited frequency.
        """
        prev_cycle = None
        render_period = 1000.0 / self.config.render_frequency
        while True:
            cycle_start = ticks_ms()
            self.render()
            cycle_finish = ticks_ms()
            time_taken = ticks_diff(cycle_finish, cycle_start)
            wait = int(max(0.0, render_period - time_taken))
            sleep_ms(wait)


if __name__ == '__main__':
    BouncingPixels().main()