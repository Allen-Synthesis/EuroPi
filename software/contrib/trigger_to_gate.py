from europi import oled, k1, k2, b1, b2, din, cv1, cv2
from europi_script import EuroPiScript
import machine
import utime

"""
Trigger to Gate
author: Andy Bulka (tcab) (github.com/abulka)
date: 2023-05-16
labels: trigger, gate, clock

Generates a gate on cv1 in response to a trigger on din.
Control the outgoing pulse width with k1. Control the delay between the trigger
and the gate starting with k2. Handy for converting short triggers (e.g. 1ms)
into longer gates (e.g. 10ms) as some eurorack modules don't like short
triggers.

See documentation in trigger_to_gate.md for more details.
"""

class Data:
    def __init__(self):
        # the default parameters controlled by the knobs
        self.gate_length = 10 # ms, generated pulse duration
        self.gate_delay = 0 # ms, delay between din trigger and gate start
        self.clock_period = 1000 # ms, time between generated clock pulses
        self.clock_length = 10 # ms, length of generated clock pulse

        # states controlled by the buttons
        self.mode = 'gate' # default mode
        self.gate_running = True
        self.clock_running = False

        # dynamically calculated values
        self.din_length = 0 # length of incoming trigger pulse (guess, calculated)
        self.din_period = 0 # time between incoming triggers (guess, calculated)

        # screen related
        self.updateUI = True

        # gate related
        self.din_state: bool = False
        self.gate_is_high: bool = False
        self.din_time_of_last_trigger = 0

        # knob choices
        self.knob_values = list(range(1, 201)) + list(range(201, 501, 5)) + list(range(501, 1600, 20)) # approx 315 values
        self.knob_values_gate_length = self.knob_values
        self.knob_values_gate_delay = [0] + self.knob_values
        self.knob_values_clock_period = self.knob_values
        self.knob_values_clock_length = self.knob_values

        # refresh rates
        self.frame_rate = 30 # for screen refresh
        self.schedule_resolution_ms = 1 # how often to check the schedule
        self.screen_refresh_rate_ms = 150 # int(1000 / self.frame_rate)
        self.knobs_read_interval_ms = int(1000 / self.frame_rate)

        # other
        self.after_off_settling_ms = 2 # time to wait after turning off gate or clock output, or it doesn't happen cleanly
        self.updateSavedState = False


class KnobWithHysteresis:
    """
    This is a class to cure the hysteresis problem with the rotary encoder.
    Documentation in tigger_to_gate.md
    """
    def __init__(self, knob, tolerance=0, lock_delay=1000, name=None) -> None:
        self.knob = knob
        self.tolerance = tolerance
        self.lock_delay = lock_delay
        self.lock_time = utime.ticks_ms() # initially locked
        self.name = name if name else "unnamed" # for debugging
        self.value = None  # cached value when locked, when None the first reading is used even when locked

    @property
    def locked(self):
        now = utime.ticks_ms()
        time_left = utime.ticks_diff(self.lock_time, now) # lock_time - now
        _time_expired = time_left <= 0
        return _time_expired
    
    def _update_value_if_allowed(self, new_value):
        if self.value is None or self._allow(self.value, new_value):
            self.value = new_value
        return self.value

    def _allow(self, old_value, new_value):
        if self.tolerance == 0:
            return True  # backwards compatibility
        if not self.locked:
            return True  # allow any value to get in
        
        # at this point the lock_time has expired
        big_enough_change = abs(old_value - new_value) >= self.tolerance
        if big_enough_change:
            now = utime.ticks_ms()
            self.lock_time = now + self.lock_delay
            self.locked_msg_shown_debug = False
            return True

        return False

    def choice(self, *args):
        new_value = self.knob.choice(*args)
        return self._update_value_if_allowed(new_value)


class KnobWithPassThrough:
    """
    Disable changing value till knob is moved and "passes-through" the current cached value.
    Documentation in tigger_to_gate.md
    """
    def __init__(self, knob, initial_value=50) -> None:
        self.knob = knob
        self.value = initial_value # cached value when locked
        self.locked = False # stay on value until the knob meets unlock condition
        self.unlock_condition = 'any change'  # '<' or '>' or 'any change'
        self.locked_on_knob_value = None # remember knob value we initially locked on when setting to 'any change'
        self.recalc_pending = False # unlock_condition needs recalculating

    def mode_changed(self):
        # call this when switching to a new mode that uses the same underlying knob
        self.recalc_pending = True

    def _recalc_pass_through_condition(self, current_knob_value):
        self.locked = True
        self.unlock_condition = '<' if current_knob_value > self.value else '>'

    def _has_passed_through(self, value):
        if self.unlock_condition == '<':
            return value <= self.value
        elif self.unlock_condition == '>':
            return value >= self.value
        elif self.unlock_condition == 'any change':
            return value != self.locked_on_knob_value
    
    def _update_pass_through(self, new_value):
        if self.recalc_pending:
            self._recalc_pass_through_condition(new_value)
            self.recalc_pending = False
        if self.locked_on_knob_value is None:
            self.locked_on_knob_value = new_value
            self.locked = True
            return self.value
        if self.locked and self._has_passed_through(new_value):
            self.locked = False

        if self.locked:
            # return the cached value
            return self.value
        else: 
            # pass through underlying knob new value, update cache
            self.value = new_value
            return self.value
    
    def choice(self, *args, **kwargs):
        new_value = self.knob.choice(*args)
        return self._update_pass_through(new_value)


class Scheduler:
    """
    A simple scheduler for running tasks at a given time in the future.
    Documentation in tigger_to_gate.md
    """

    def __init__(self):
        self.enabled = True
        self.schedule = [] # list of tuples (time, callback, callback_func_name)
        
    def add_task(self, callback, ms:int=0):
        self.schedule.append((utime.ticks_add(utime.ticks_ms(), ms), callback, callback.__name__))

    def remove_task(self, callback, must_be_found=False):
        to_remove = []
        found = False
        for scheduled_time, cb, callback_func_name in self.schedule:
            if callback_func_name == callback.__name__:
                to_remove.append((scheduled_time, cb, callback_func_name))
                found = True
        for item in to_remove:
            self.schedule.remove(item)
        if not found and must_be_found:
            print(f"cannot remove task {callback} viz. {callback.__name__} from schedule", len(self.schedule), "tasks in schedule")
            self.print_schedule()

    def run_once(self):
        now = utime.ticks_ms()
        for scheduled_time, callback, _ in self.schedule:
            if utime.ticks_diff(scheduled_time, now) <= 0:
                self.schedule.remove((scheduled_time, callback, _))
                callback()

    def stop(self):
        self.enabled = False

    def print_schedule(self):
        print('  Schedule:')
        for scheduled_time, callback, callback_func_name in self.schedule:
            print(f"  {callback_func_name} {scheduled_time}")


class Screen:
    """
    Show running status on 128x64 pixels OLED screen (text, x, y, color))
    """
    def __init__(self, data):
        self.data = data

    def draw(self, show=True):
        _ = self.data
        if _.mode == 'gate':
            line1 = f"din {_.din_length}ms {_.din_period}ms"
            line2 = f"1 gate_len {_.gate_length}ms"
            line3 = f"1 delay {_.gate_delay}ms"
            line1 += f" {'.' if _.gate_running else ''}"
        elif _.mode == 'clock':
            bpm = 60000 / _.clock_period
            line1 = f"clock {int(bpm)}bpm"
            line2 = f"2 clk_len {_.clock_length}ms"
            line3 = f"2 clk_pd {_.clock_period}ms"
            line1 += f" {'.' if _.clock_running else ''}"
        oled.fill(0)
        oled.text(line1, 0, 0, 1)
        oled.text(line2, 0, 12, 1)
        oled.text(line3, 0, 24, 1)
        if show:
            oled.show()

    def clear(self):
        oled.fill(0)
        oled.show()


class TriggerToGate(EuroPiScript):
    def __init__(self):
        super().__init__()
        self.HYSTERESIS_KNOBS = True
        self.PASS_THROUGH_KNOBS = True
        self.data = Data()
        _ = self.data
        
        state = self.load_state_json()
        _.mode = state.get("mode", _.mode)
        _.gate_length = state.get("gate_length", _.gate_length)
        _.gate_delay = state.get("gate_delay", _.gate_delay)
        _.clock_length = state.get("clock_length", _.clock_length)
        _.clock_period = state.get("clock_period", _.clock_period)
        _.gate_running = state.get("gate_running", _.gate_running)
        _.clock_running = state.get("clock_running", _.clock_running)

        # Overclock the Pico for improved performance.
        machine.freq(250_000_000)

        # gate mode
        self.k1_gate_length = k1
        self.k2_gate_delay = k2
        # clock mode
        self.k1_clock_length = k1
        self.k2_clock_period = k2

        if self.HYSTERESIS_KNOBS:
            # Wrap knobs in KnobWithHysteresis to avoid jitter.
            self.k1_gate_length = KnobWithHysteresis(k1, tolerance=2, name="k1_gate_length")
            self.k2_gate_delay = KnobWithHysteresis(k2, tolerance=2, name="k2_gate_delay")
            self.k1_clock_length = KnobWithHysteresis(k1, tolerance=2, name="k1_clock_length")
            self.k2_clock_period = KnobWithHysteresis(k2, tolerance=2, name="k2_clock_period")

        if self.PASS_THROUGH_KNOBS:
            # Wrap knobs in KnobWithPassThrough to prevent values jumping when toggling modes.
            self.k1_gate_length = KnobWithPassThrough(self.k1_gate_length, initial_value=_.gate_length)
            self.k2_gate_delay = KnobWithPassThrough(self.k2_gate_delay, initial_value=_.gate_delay)
            self.k1_clock_length = KnobWithPassThrough(self.k1_clock_length, initial_value=_.clock_length)
            self.k2_clock_period = KnobWithPassThrough(self.k2_clock_period, initial_value=_.clock_period)

        self.scheduler = Scheduler()
        
        self.screen = Screen(self.data)

        @din.handler
        def din_rising():
            _ = self.data
            if not self.scheduler.enabled: return
            _.din_state = True

            now = utime.ticks_ms()
            _.din_period = utime.ticks_diff(now, _.din_time_of_last_trigger)
            _.din_time_of_last_trigger = now

            delay = _.gate_delay
            if _.gate_is_high:
                self.gate_off_task()
                self.scheduler.remove_task(self.gate_off_task, must_be_found=True) # cancel the existing gate_off task
                delay = max(_.gate_delay, _.after_off_settling_ms)
            self.scheduler.remove_task(self.gate_on_task, must_be_found=False) # cancel any existing gate_on task which had a long delay and hasn't run yet
            if _.gate_running:
                self.scheduler.add_task(self.gate_on_task, delay)

        @din.handler_falling
        def din_falling():
            _ = self.data
            _.din_state = False
            now = utime.ticks_ms()
            _.din_length = utime.ticks_diff(now, _.din_time_of_last_trigger)

        @b1.handler_falling
        def button1_click():
            _ = self.data
            if _.mode == 'gate':
                _.gate_running = not _.gate_running
            elif _.mode == 'clock':
                _.clock_running = not _.clock_running
                if _.clock_running:
                    self.clock_on_task()
            _.updateUI = True

            if _.updateUI:
                _.updateSavedState = True

        @b2.handler_falling
        def button2_click():
            _ = self.data
            if _.mode == 'gate':
                _.mode = 'clock'
                if self.PASS_THROUGH_KNOBS:
                    self.k1_clock_length.mode_changed()
                    self.k2_clock_period.mode_changed()
            else:
                _.mode = 'gate'
                if self.PASS_THROUGH_KNOBS:
                    self.k1_gate_length.mode_changed()
                    self.k2_gate_delay.mode_changed()
            _.updateUI = True
            _.updateSavedState = True

    def gate_on_task(self):
        _ = self.data
        cv1.on()
        _.gate_is_high = True
        self.scheduler.add_task(self.gate_off_task, _.gate_length)

    def gate_off_task(self):
        _ = self.data
        cv1.off()
        _.gate_is_high = False

    def clock_on_task(self):
        _ = self.data
        cv2.on()
         # don't let clock_length be longer than clock_period
        in_how_long = min(_.clock_length, _.clock_period - _.after_off_settling_ms)
        self.scheduler.add_task(self.clock_off_task, in_how_long)
        if _.clock_running:
            self.scheduler.add_task(self.clock_on_task, _.clock_period)

    def clock_off_task(self):
        cv2.off()

    def read_knobs_task(self):
        _ = self.data

        if _.mode == 'gate':

            new_value = self.k1_gate_length.choice(_.knob_values_gate_length)
            if new_value != _.gate_length:
                _.gate_length = new_value
                _.updateUI = True

            new_value = self.k2_gate_delay.choice(_.knob_values_gate_delay)
            if new_value != _.gate_delay:
                _.gate_delay = new_value
                _.updateUI = True                

        elif _.mode == 'clock':

            new_value = self.k1_clock_length.choice(_.knob_values_clock_length)
            if new_value != _.clock_length:
                _.clock_length = new_value
                _.updateUI = True

            new_value = self.k2_clock_period.choice(_.knob_values_clock_period)
            if new_value != _.clock_period:
                _.clock_period = new_value
                _.updateUI = True
            
        if _.updateUI:
            _.updateSavedState = True

        self.scheduler.add_task(self.read_knobs_task, _.knobs_read_interval_ms)

    def update_screen_task(self):
        _ = self.data
        if _.updateUI:
            self.screen.draw()
            _.updateUI = False
        self.scheduler.add_task(self.update_screen_task, _.screen_refresh_rate_ms)

    def save_state_task(self):
        _ = self.data
        if _.updateSavedState:
            _.updateSavedState = False
            self.save_state()
        self.scheduler.add_task(self.save_state_task, 5000)

    def stop(self):
        _ = self.data
        self.scheduler.stop()
        self.screen.clear()
        cv1.off()
        cv2.off()
        _.gate_running = False
        _.clock_running = False

    def save_state(self):
        """Save the current state variables as JSON."""
        # Don't save if it has been less than 5 seconds since last save.
        if self.last_saved() < 5000:
            return
        
        _ = self.data
        state = {
            'mode': _.mode,
            'gate_length': _.gate_length,
            'gate_delay': _.gate_delay,
            'clock_length': _.clock_length,
            'clock_period': _.clock_period,
            'gate_running': _.gate_running,
            'clock_running': _.clock_running,
        }
        self.save_state_json(state)

    def main(self):

        self.scheduler.add_task(self.read_knobs_task)
        self.scheduler.add_task(self.update_screen_task)
        self.scheduler.add_task(self.save_state_task)

        try:
            while self.scheduler.enabled:
                self.scheduler.run_once()
                utime.sleep_ms(self.data.schedule_resolution_ms)
        except KeyboardInterrupt:
            print("Interrupted")
            self.stop()
            print('Shutdown complete')
            raise
            
if __name__ == "__main__":
    TriggerToGate().main()
