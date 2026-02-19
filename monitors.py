from enum import Enum

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

# LAMP CONTROLLER
def lamp_controller(press_pulse: bool, motion: bool, movement_timer: State, lamp_state: State):
    match lamp_state.current:
        case Mode.OFF:
            # turns on if press_pulse is enabled, otherwise, remains off
            switch_mode_to_on(press_pulse, lamp_state)
            movement_timer.current = INITIAL_TIMER_VALUE

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

    for k in range(len(press_raw)):
        print(f"Tick: {k}")
        press_pulse = edge_detector(press_raw[k], button_state)

        # update lamp mode and movement timer based on press_pulse and motion inputs
        lamp_controller(press_pulse, motion[k], movement_timer, lamp_state)

        # print out variable and states for debugging purposes
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