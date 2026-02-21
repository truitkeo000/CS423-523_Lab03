from collections import deque

from monitors import State, Mode, INITIAL_TIMER_VALUE, simulate_tick

HORIZON = INITIAL_TIMER_VALUE + 5


# creates and returns initial BFS node
# - empty input trace
# - initial lamp state (OFF, timer initialized, prev=false)
# - last_press_raw = None (no previous input yet)
def make_initial_state():
    button_state = State(False, False)                  # aka prev
    movement_timer = State(INITIAL_TIMER_VALUE, INITIAL_TIMER_VALUE)    # aka x
    lamp_state = State(Mode.OFF, Mode.OFF)                              # aka mode

    state = {
        "button_state": button_state,
        "movement_timer": movement_timer,
        "lamp_state": lamp_state
    }

    trace = []
    last_press_raw = None

    return trace, state, last_press_raw


# generates the 4 possible input combinations for one tick:
# (press_raw, motion) ∈ {(0,0),(0,1),(1,0),(1,1)}
def next_inputs():
    for press_raw in [False, True]:
        for motion in [False, True]:
            yield press_raw, motion


# make an independent copy of state (deepcopy too slow)
def copy_state(state):
    button_state = state["button_state"]
    movement_timer = state["movement_timer"]
    lamp_state = state["lamp_state"]

    state_copy = {
        "button_state": State(button_state.current, button_state.previous),
        "movement_timer": State(movement_timer.current, movement_timer.previous),
        "lamp_state": State(lamp_state.current, lamp_state.previous),
    }
    return state_copy


# creates a hashable key for visited-state pruning
# include BOTH current and previous fields to avoid incorrect merging
def state_key(state):
    button_state = state["button_state"]
    movement_timer = state["movement_timer"]
    lamp_state = state["lamp_state"]

    return (
        button_state.current, button_state.previous,
        movement_timer.current, movement_timer.previous,
        lamp_state.current, lamp_state.previous
    )


# build a minimal press_raw_history list
# it only needs press_raw_history[k-1] to be correct
def build_press_raw_history(k: int, last_press_raw, press_raw):
    if k == 0:
        return [press_raw]
    # length must be at least k so index k-1 exists
    press_raw_history = [False] * (k + 1)
    press_raw_history[k - 1] = last_press_raw
    press_raw_history[k] = press_raw
    return press_raw_history


# performs BFS over input traces up to HORIZON with state-pruning
# returns the shortest counterexample if one is found
def bfs_find_cex():
    q = deque()
    q.append(make_initial_state())

    # visited[key] = smallest depth at which we've reached this state
    visited = {}

    while q:
        trace, state, last_press_raw = q.popleft()

        # stop expanding beyond horizon
        if len(trace) >= HORIZON:
            continue

        k = len(trace)

        for press_raw, motion in next_inputs():
            state_copy = copy_state(state)

            # build minimal history list just for your monitor A3 line:
            # if k>0 and press_raw_history[k-1] and press_raw: ...
            press_raw_history = build_press_raw_history(k, last_press_raw, press_raw)

            # run one tick
            state_copy, press_pulse, violation = simulate_tick(
                state_copy, k, press_raw, motion, press_raw_history
            )

            new_trace = trace + [(press_raw, motion)]

            # If monitor reports a violation, stop immediately (shortest trace)
            if violation is not None:
                return new_trace, violation

            # prune repeated states (don’t re-explore same state at >= depth)
            key = state_key(state_copy)
            depth = len(new_trace)

            if key in visited and visited[key] <= depth:
                continue
            visited[key] = depth

            # enqueue next node; last_press_raw for next tick becomes this tick's press_raw
            q.append((new_trace, state_copy, press_raw))

    return None, None


# prints violation information
def print_violation(trace, violation):
    property_id, bad_k, explanation = violation
    print(f"VIOLATION: {property_id}")
    print(f"first_bad_tick: k={bad_k}")
    print(f"inputs[0..k]: {trace[:bad_k+1]}")
    print(f"explanation: {explanation}")


# runs BFS and prints either the shortest counterexample
# or a bounded "no counterexample found" message
def main():
    trace, violation = bfs_find_cex()

    if violation is None:
        print(f"NO COUNTEREXAMPLE FOUND up to H={HORIZON} for properties A1,A2,A3,B1,B2,B3,C1,C2")
        print("bounded result; not a proof beyond H.")
        return

    print_violation(trace, violation)


if __name__ == "__main__":
    main()