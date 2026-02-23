Keona Truitt & Lindsey Nielsen
Lab 3 – CS 423 read.md

# Shortest Counterexamples for Two Buggy Variants

We used a **bounded BFS** to test the lamp controller with all possible inputs `(press_raw, motion)`. This lets us find the **shortest input sequences** that break the safety properties.

## Buggy Variant 1 – Edge Detector Always Returns `press_raw`

**Bug:** `press_pulse` is always equal to `press_raw` instead of only when the button rises.

**Violated Property:** A3 – the pulse should only happen on the first tick of a press, not while holding the button.

**Shortest Counterexample (2 ticks):**

| k | press_raw | prev | press_pulse | mode | x | lamp | Explanation                            |
| - | --------- | ---- | ----------- | ---- | - | ---- | -------------------------------------- |
| 0 | 1         | 0    | 1           | OFF  | 0 | 0    | First rising edge, pulse is correct    |
| 1 | 1         | 1    | 1 ❌         | ON   | 0 | 1    | Button held, should be 0 → violates A3 |

**Why it fails:** The pulse repeats when the button is still held down, which breaks the rule that only the rising edge triggers a pulse.

## Buggy Variant 2 – Controller Doesn’t Turn OFF at Timer Limit

**Bug:** AUTO mode doesn’t turn OFF when the timer `x` reaches 10.

**Violated Property:** B3 – lamp should match the timer; B1 – OFF mode should have lamp = 0.

**Shortest Counterexample (12 ticks):**

| k  | press_raw | motion | mode     | x  | lamp | Explanation                         |
| -- | --------- | ------ | -------- | -- | ---- | ----------------------------------- |
| 0  | 1         | 0      | OFF → ON | 0  | 0    | Press turns OFF → ON                |
| 1  | 0         | 0      | ON       | 1  | 1    | Timer increments                    |
| 2  | 0         | 0      | ON       | 2  | 1    | Timer increments                    |
| 3  | 0         | 0      | ON       | 3  | 1    | Timer increments                    |
| 4  | 0         | 0      | ON       | 4  | 1    | Timer increments                    |
| 5  | 0         | 0      | ON       | 5  | 1    | Timer increments                    |
| 6  | 0         | 0      | ON       | 6  | 1    | Timer increments                    |
| 7  | 0         | 0      | ON       | 7  | 1    | Timer increments                    |
| 8  | 0         | 0      | ON       | 8  | 1    | Timer increments                    |
| 9  | 0         | 0      | ON       | 9  | 1    | Timer increments                    |
| 10 | 0         | 0      | ON       | 10 | 1    | Timer reaches max                   |
| 11 | 0         | 0      | ON ❌     | 10 | 1 ❌  | Should switch OFF; lamp should be 0 |

**Why it fails:** When the timer hits 10, the lamp stays ON instead of turning OFF. AUTO mode isn’t handling the timer limit correctly.

