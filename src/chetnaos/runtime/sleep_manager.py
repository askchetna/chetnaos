"""
Sleep Manager — Decides when to trigger sleep/consolidation cycles.
"""


class SleepManager:
    def __init__(self, sleep_every: int = 20):
        self._sleep_every = sleep_every
        self._last_sleep  = 0

    def should_sleep(self, cycle_count: int) -> bool:
        if cycle_count > 0 and (cycle_count - self._last_sleep) >= self._sleep_every:
            return True
        return False

    def mark_slept(self, cycle_count: int):
        self._last_sleep = cycle_count

    def cycles_until_sleep(self, cycle_count: int) -> int:
        return max(0, self._sleep_every - (cycle_count - self._last_sleep))
