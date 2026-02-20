from enum import Enum
from selectors import SelectSelector
from unittest import expectedFailure

# CS 423/523 Lab 3
# Deliverable 1: Runtime monitors
# Lindsey Nielsen and Keona Truitt

INITIAL_TIMER_VALUE: int = 10

# class used to track current and previous values of a variable
class State:
    # initialize state with current and previous values
    def __init__(self, current, previous):
        self._current = current
        self._previous = previous

    # getter for current value
    @property
    def current(self):
        return self._current

    # getter for previous value
    @property
    def previous(self):
        return self._previous

    # setter for the current value
    # when updating the current, the old current is automatically stored into previous
    @current.setter
    def current(self, current):
        self._previous = self.current
        self._current = current

# define possible modes using Enum
class Mode (Enum):
    OFF = 0
    ON = 1
    AUTO = 2

# EDGE DETECTOR
def edge_detector(press_raw: bool, button_state: State):
    button_state.current = press_raw
    return press_raw and (not button_state.previous)  # return press_pulse

# MONITOR GROUP A: EDGE DETECTOR CORRECTNESS
def monitor_edge_detector(k: int, press_raw: bool, press_pulse: bool, button_state: State):
    """Check A1, A2, A3 for edge detection correctness."""
    # --- A1 ---
    expected_pulse = press_raw and (not button_state.previous)
    if press_pulse != expected_pulse:
        print(f"[A1 FAIL] Tick {k}: press_pulse={press_pulse}, expected {expected_pulse}")
    # --- A2 ---
    if k > 0:
        expected_prev = press_raw_history[k-1]
        if button_state.previous != expected_prev:
            print(f"[A2 FAIL] Tick {k}: prev={button_state.previous}, expected {expected_prev}")
    # --- A3 ---
    if k > 0 and press_raw_history[k-1] and press_raw:
        if press_pulse != False:
            print(f"[A3 FAIL] Tick {k}: press_pulse={press_pulse} while button held")

# MONITOR GROUP B: MODE/OUTPUT CONSISTENCY (INVARIANTS)
def monitor_output_consistency(k: int, mode: Mode, lamp: int, movement_timer: int):
    # --- B1 ---
    if mode == Mode.OFF and lamp != 0:
        print(f"[B1 FAIL] TICK {k}: mode=OFF, expected lamp=0, but observed lamp={lamp}\n")

    # --- B2 ---
    if mode == Mode.ON and lamp != 1:
        print(f"[B2 FAIL] TICK {k}: mode=ON, expected lamp=1, but observed lamp={lamp}\n")

    # --- B3 ---
    expected: int = 1 if movement_timer > 0 else 0
    if mode == Mode.AUTO and lamp != expected:
      print(f"[B3 FAIL] TICK {k}: mode=AUTO, movement_timer={movement_timer}, expected={expected}, but observed lamp={lamp}\n")

# MONITOR GROUP C: NUMERIC SAFETY (INVARIANTS)
def monitor_numeric_safety(k: int, movement_timer: int, mode: Mode):
    # --- C1 ---
    if movement_timer < 0 or  movement_timer > 10:
        print(f"[C1 FAIL] TICK {k}: expected movement_timer to be between 0 and 10, but observed movement_timer={movement_timer}\n")

    # --- C2 ---
    if mode == Mode.OFF and movement_timer != 0:
        print(f"[C2 FAIL] TICK {k}: mode=OFF, expected movement_timer=0, but observed movement_timer={movement_timer}\n")

# LAMP CONTROLLER HELPERS
def switch_mode_to_on(press_pulse: bool, lamp_state: State):
    if press_pulse:
        lamp_state.current = Mode.ON

def switch_mode_to_auto(press_pulse: bool, lamp_state: State):
    if press_pulse:
        lamp_state.current = Mode.AUTO

def switch_mode_to_off(press_pulse: bool, movement_timer, lamp_state: State):
    if press_pulse or movement_timer.current == 0:
        lamp_state.current = Mode.OFF

def set_movement_timer(motion, movement_timer):
    if motion:
        movement_timer.current = INITIAL_TIMER_VALUE
    else:
        movement_timer.current = max(movement_timer.current - 1, 0)

# return lamp[k] as 0/1 based on mode and timer
def compute_lamp_output(mode: Mode, movement_timer: int):
    match mode:
        case Mode.OFF:
            return 0
        case Mode.ON:
            return 1
        case Mode.AUTO:
                return 1 if movement_timer > 0 else 0

# LAMP CONTROLLER
def lamp_controller(press_pulse: bool, motion: bool, movement_timer: State, lamp_state: State):
    match lamp_state.current:
        case Mode.OFF:
            # turns on if press_pulse is enabled, otherwise, remains off
            switch_mode_to_on(press_pulse, lamp_state)
            movement_timer.current = 0

        case Mode.ON:
            # switches to auto if press_pulse is enabled, otherwise, remains on
            switch_mode_to_auto(press_pulse, lamp_state)

        case Mode.AUTO:
            # updates movement timer
            set_movement_timer(motion, movement_timer)

            # turns off if press_pulse is enabled OR movement_timer reaches 0, otherwise, remains on auto
            switch_mode_to_off(press_pulse, movement_timer, lamp_state)

# SIMULATE LAMP CONTROLLER WITH GIVEN INPUT
def run_lamp_trace(press_raw: list[bool], motion: list[bool]):

    # declare variables & states
    press_pulse: bool | None = None
    button_state = State(False, False)                   # aka prev
    movement_timer = State(INITIAL_TIMER_VALUE, INITIAL_TIMER_VALUE)    # aka x
    lamp_state = State(Mode.OFF, Mode.OFF)                              # aka mode

    global press_raw_history
    press_raw_history = press_raw.copy()  # needed for monitor checks

    for k in range(len(press_raw)):
        print(f"Tick: {k}")
        # compute press pulse
        press_pulse = edge_detector(press_raw[k], button_state)

        # --- MONITOR GROUP A ---
        monitor_edge_detector(k, press_raw[k], press_pulse, button_state)

        # update lamp mode and movement timer
        lamp_controller(press_pulse, motion[k], movement_timer, lamp_state)
        lamp_output: int = compute_lamp_output(lamp_state.current, movement_timer.current)

        # --- MONITOR GROUP B ---
        monitor_output_consistency(k, lamp_state.current, lamp_output, movement_timer.current)

        # --- MONITOR GROUP C ---
        monitor_numeric_safety(k, movement_timer.current, lamp_state.current)

        # print out variable and states
        print(f"- Press pulse: {press_pulse}\n- Timer: {movement_timer.current}\n- Lamp: {lamp_state.current.name}\n")

# DEFINE INPUTS AND RUN TRACES
def main() -> None:

    # input examples modified from lab 2

    # T1: turn on then timeout
    # input length = 14
    t1_press_raw: list[bool] = [
        True,           # first press → lamp ON
        False,          # button released
        True,           # second press → switch ON → AUTO
    ] + [False] * 11    # button released
    t1_motion: list[bool] = [False] * 14

    print("Trace T1: turn on then timeout ----------------------------------------------------------\n")
    run_lamp_trace(t1_press_raw, t1_motion)

    # T2: turn off early via press
    # input length = 6
    t2_press_raw: list[bool] = [
        True,       # first press → lamp ON
        False,      # button release
        True,       # second press → switch ON → AUTO
        False,      # release
        True,       # third press → lamp OFF
        False       # button released
    ]
    t2_motion: list[bool] = [False] * 8

    print("Trace T2: turn off via early press -------------------------------------------------------\n")
    run_lamp_trace(t2_press_raw, t2_motion)

    # T3: button held high (edge detector contract)
    # input length = 6
    t3_press_raw: list[bool] = [True] * 3 + [False] * 3  # only one press at k = 0
    t3_motion: list[bool] = [False] * 6

    print("Trace T3: button held high -------------------------------------------------------\n")
    run_lamp_trace(t3_press_raw, t3_motion)

    # T4: motion resets timer
    # input length = 18
    t4_press_raw: list[bool] = [
        True,        # first press → lamp ON
        False,       # button release
        True,        # second press → switch ON → AUTO
    ] + [False] * 15 # button released
    t4_motion: list[bool] = [False] * 7 + [True] + [False] * 10

    print("Trace T4: motion resets timer -------------------------------------------------------\n")
    run_lamp_trace(t4_press_raw, t4_motion)

# execute main function
if __name__ == "__main__":
    main()