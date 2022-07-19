import contextlib
from typing import Generator, Optional, Set, Tuple

from roboregress.engine import SimulationRuntime
from roboregress.wood import Surface

from .cell import BaseRobotCell


class RobotStats:
    """A stat tracker for a single robot cell side"""

    def __init__(self, robot_params: BaseRobotCell.Parameters, runtime: SimulationRuntime):
        self.robot_params = robot_params
        self.total_time_working: float = 0
        self.total_time_slacking: float = 0
        self.currently_working = False

        self._runtime = runtime
        self._last_work_start: Optional[float] = None
        self._last_work_end: Optional[float] = None

    @property
    def total_time(self) -> float:
        return self.total_time_slacking + self.total_time_working

    @contextlib.contextmanager
    def track_work_time(self) -> Generator[None, None, None]:
        """A context manager for tracking utilization of a robot"""

        self.start_working()
        self.currently_working = True
        yield
        self.stop_working()
        self.currently_working = False

    def start_working(self) -> None:
        time = self._runtime.timestamp

        if self._last_work_end is not None:
            slack_time = time - self._last_work_end
            assert slack_time >= 0, "It's okay to not take breaks"
            self.total_time_slacking += slack_time

        self._last_work_start = time

    def stop_working(self) -> None:
        time = self._runtime.timestamp

        assert self._last_work_start is not None
        assert time > self._last_work_start
        self._last_work_end = time
        work_time = time - self._last_work_start
        self.total_time_working += work_time


class OverallStats:
    def __init__(self) -> None:
        pass
