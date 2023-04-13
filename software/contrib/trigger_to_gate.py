from europi import oled, k1, k2, b1, b2, din, cv1, cv2
from europi_script import EuroPiScript
import machine
import utime

"""
Trigger to Gate
author: Andy Bulka (tcab) (github.com/abulka)
date: 2023-05-13
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
        self.gate_length = 10 # generated pulse duration, will quickly get clobbered by k1 value 🗿
        self.gate_delay = 0 # 🗿
        self.clock_period = 1000 # ms, will quickly get clobbered by k2 value 🗿
        self.clock_length = 10 # ms 🗿

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


class KnobWithHysteresis:
    """
    This is a class to cure the hysteresis problem with the rotary encoder.
    Documentation in tigger_to_gate.md
    """
    DEBUG = False

    def __init__(self, knob, tolerance=0, delay=1000) -> None:
        self.knob = knob
        self.tolerance = tolerance
        self.delay_before_lock = delay
        self.value = 0  # cached value when locked
        self.lock_time = utime.ticks_ms()
        self.locked_debug = False # only print the locked message once when in debug mode

    # Wraps Knob so need to expose all Knob methods
    # and the methods of its superclass AnalogueReader.

    def set_samples(self, *args):
        return self.knob.set_samples(*args)
    
    def set_deadzone(self, *args):
        return self.knob.set_deadzone(*args)

    def range(self, *args):
        new_value = self.knob.range(*args)
        return self._update_value_if_allowed(new_value)
    
    def choice(self, *args):
        new_value = self.knob.choice(*args)
        return self._update_value_if_allowed(new_value)

    def percent(self, *args):
        new_value = self.knob.percent(*args)
        return self._update_value_if_allowed(new_value)

    def read_position(self, *args):
        new_value = self.knob.read_position(*args)
        return self._update_value_if_allowed(new_value)

    def _update_value_if_allowed(self, new_value):
        if self._allow(self.value, new_value):
            self.value = new_value
        return self.value

    def _allow(self, old_value, new_value):
        if self.tolerance == 0:
            return True
        now = utime.ticks_ms()
        time_expired = utime.ticks_diff(now, self.lock_time) > self.delay_before_lock
        if not time_expired:
            if self.DEBUG: print(f"{new_value} ", end="")
            return True  # allow any value to get in
        
        # at this point the lock_time has expired
        big_enough_change = abs(old_value - new_value) >= self.tolerance
        if big_enough_change:
            if self.DEBUG and self.locked_debug:
                print(f"{old_value} to {new_value} (resetting lock window cos big enough change)")
            self.lock_time = now + self.delay_before_lock
            self.locked_debug = False
            return True
        if self.DEBUG and time_expired and not self.locked_debug:
            print(f"LOCKED at {old_value} ignoring {new_value} (expired)")
            self.locked_debug = True
        return False


class KnobWithPassThrough:
    """
    Disable changing value till knob is moved and "passes-through" the current cached value.
    Documentation in tigger_to_gate.md
    """
    DEBUG = False

    def __init__(self, knob, initial=50) -> None:
        self.knob = knob
        self.cached_value = initial
        self.enabled = True
        self.enable_condition = '<'  # '<' or '>'
        self.recalc_pending = True

    def reactivate(self):
        self.recalc_pending = True

    def _recalc_pass_through_condition(self, current_knob_value):
        self.enabled = False
        self.enable_condition = '<' if current_knob_value > self.cached_value else '>'

    def _has_passed_through(self, value):
        if self.enable_condition == '<':
            return value <= self.cached_value
        elif self.enable_condition == '>':
            return value >= self.cached_value
    
    def _update_pass_through(self, new_value):
        if self.recalc_pending:
            self._recalc_pass_through_condition(new_value)
            self.recalc_pending = False
        if not self.enabled and self._has_passed_through(new_value):
            self.enabled = True
            self.cached_value = new_value
            if self.DEBUG: print(f"pass-through: {new_value}")
        if self.enabled:
            self.cached_value = new_value
        return self.cached_value
    
    def choice(self, *args):
        new_value = self.knob.choice(*args)
        return self._update_pass_through(new_value)
    
    # TODO more methods to wrap


class Scheduler:
    """
    A simple scheduler for running tasks at a given time in the future.
    Documentation in tigger_to_gate.md
    """
    DEBUG_COLLECT_STATS = True

    def __init__(self):
        self.enabled = True
        self.schedule = [] # list of tuples (time, callback, callback_func_name)
        self.stats = self.create_stats(scheduler=self) if self.DEBUG_COLLECT_STATS else None
        
    def add_task(self, callback, ms:int=0):
        self.schedule.append((utime.ticks_add(utime.ticks_ms(), ms), callback, callback.__name__))

    def remove_task(self, callback, must_be_found=False):
        found = False
        for scheduled_time, callback, callback_func_name in self.schedule:
            if callback_func_name == callback.__name__:
                self.schedule.remove((scheduled_time, callback, callback_func_name))
                found = True
        if not found and must_be_found:
            print(f"cannot remove task {callback} viz. {callback.__name__} from schedule", len(self.schedule), "tasks in schedule")
            self.print_schedule()

    def run_once(self):
        if self.stats:
            self.stats.record_run()
        now = utime.ticks_ms()
        for scheduled_time, callback, _ in self.schedule:
            if utime.ticks_diff(scheduled_time, now) <= 0:
                if self.stats:
                    self.stats.record_call(now, scheduled_time)
                self.schedule.remove((scheduled_time, callback, _))
                callback()

    def stop(self):
        self.enabled = False

    def print_schedule(self):
        print('  Schedule:')
        for scheduled_time, callback, callback_func_name in self.schedule:
            print(f"  {callback_func_name} {scheduled_time}")

    # Record Scheduler Statistics (optional)

    def create_stats(self, scheduler):
        class Stats:
            def __init__(self, scheduler):
                self.scheduler = scheduler
                self.schedule_loop_count = 0
                self.schedule_call_count = 0
                self.discrepancy_total = 0
                self.discrepancy_n = 0
                self.discrepancy_mean = 0

            def record_run(self):
                self.schedule_loop_count += 1

            def record_call(self, now, scheduled_time):
                self.schedule_call_count += 1
                discrepancy = utime.ticks_diff(now, scheduled_time)
                self.discrepancy_total += discrepancy
                self.discrepancy_n += 1
                self.discrepancy_mean = self.discrepancy_total / self.discrepancy_n

            def report(self):
                print(f"{self.schedule_call_count:,} calls / {self.schedule_loop_count:,} schedule loops ({self.discrepancy_mean}ms average scheduling discrepancy)")
                print(f"{len(self.scheduler.schedule)} unrun tasks remaining.")

        return Stats(scheduler)

    def print_stats(self):
        if self.stats:
            self.stats.report()


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
        self.data = Data()
        _ = self.data

        # Overclock the Pico for improved performance.
        machine.freq(250_000_000)

        # gate mode
        self.k1_gate_length = KnobWithPassThrough(KnobWithHysteresis(k1, tolerance=2), initial=_.gate_length)
        self.k2_gate_delay = KnobWithPassThrough(KnobWithHysteresis(k2, tolerance=2), initial=_.gate_delay)
        # clock mode
        self.k1_clock_length = KnobWithPassThrough(KnobWithHysteresis(k1, tolerance=2), initial=_.clock_length)
        self.k2_clock_period = KnobWithPassThrough(KnobWithHysteresis(k2, tolerance=2), initial=_.clock_period)

        self.scheduler = Scheduler()
        
        self.screen = Screen(self.data) # safest
        # self.screen = ScreenThreaded(self.data)
        # self.screen = ScreenOneShotThreaded(self.data)
        # self.screen = ScreenOneShotThreadedSmart(self.data)

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

        @b2.handler_falling
        def button2_click():
            _ = self.data
            if _.mode == 'gate':
                _.mode = 'clock'
                self.k1_clock_length.reactivate()
                self.k2_clock_period.reactivate()
            else:
                _.mode = 'gate'
                self.k1_gate_length.reactivate()
                self.k2_gate_delay.reactivate()
            _.updateUI = True

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
            
        self.scheduler.add_task(self.read_knobs_task, _.knobs_read_interval_ms)

    def update_screen_task(self):
        _ = self.data
        if _.updateUI:
            self.screen.draw()
            _.updateUI = False
        self.scheduler.add_task(self.update_screen_task, _.screen_refresh_rate_ms)

    def stop(self):
        _ = self.data
        self.scheduler.stop()
        self.screen.clear()
        cv1.off()
        cv2.off()
        _.gate_running = False
        _.clock_running = False

    def main(self):

        self.scheduler.add_task(self.read_knobs_task)
        self.scheduler.add_task(self.update_screen_task)

        try:
            while self.scheduler.enabled:
                self.scheduler.run_once()
                utime.sleep_ms(self.data.schedule_resolution_ms)
        except KeyboardInterrupt:
            print("Interrupted")
            self.stop()
            print('Shutdown complete')
            
        self.scheduler.print_stats()


if __name__ == "__main__":
    TriggerToGate().main()
