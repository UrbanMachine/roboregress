from typing import Optional


class RobotStats:
    """A stat tracker for a single robot cell side"""

    def __init__(self, name: str):
        self.name = name
        self.total_time_working: float = 0
        self.total_time_slacking: float = 0

        self._last_work_start: Optional[float] = None
        self._last_work_end: Optional[float] = None

    def start_working(self, time: float) -> None:
        if self._last_work_end is not None:
            slack_time = time - self._last_work_end
            assert slack_time >= 0, "It's okay to not take breaks"
            self.total_time_slacking += slack_time

        self._last_work_start = time

    def stop_working(self, time: float) -> None:
        assert self._last_work_start is not None
        assert time > self._last_work_start
        self._last_work_end = time
        work_time = time - self._last_work_start
        self.total_time_working += work_time


class OverallStats:
    def __init__(self) -> None:
        pass
