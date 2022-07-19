import contextlib
from typing import Generator, Optional, Set, Tuple

from roboregress.engine import SimulationRuntime
from roboregress.wood import Surface, Wood

from .cell import BaseRobotCell


class RobotStats:
    """A stat tracker for a single robot cell side"""

    def __init__(
        self,
        robot_params: BaseRobotCell.Parameters,
        name: str,
        runtime: SimulationRuntime,
    ):
        """
        :param robot_params: The parameters the robot was configured with
        :param name: The type of robot (Rake, BigBird, etc)
        :param runtime: The runtime, for timestamp tracking
        """
        self.robot_params = robot_params
        self.name = name
        self.total_time_working: float = 0
        self.total_time_slacking: float = 0
        self.currently_working = False

        self._runtime = runtime
        self._last_work_start: Optional[float] = None
        self._last_work_end: Optional[float] = self._runtime.timestamp

    @property
    def total_time(self) -> float:
        return self.total_time_slacking + self.total_time_working

    @property
    def utilization_ratio(self) -> float:
        if self.total_time == 0:
            return 0
        else:
            return self.total_time_working / self.total_time

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


class StatsTracker:
    def __init__(self, runtime: SimulationRuntime, wood: Wood) -> None:
        self.robot_stats: Set[RobotStats] = set()
        self._runtime = runtime

    def create_robot_stats_tracker(self, robot: BaseRobotCell) -> RobotStats:
        def _get_key(stats: RobotStats) -> Tuple[float, float, Surface]:
            """Create a unique identifier"""
            return (
                stats.robot_params.end_pos,
                stats.robot_params.start_pos,
                stats.robot_params.pickable_surface,
            )

        stats = RobotStats(
            robot_params=robot.params,
            runtime=self._runtime,
            name=robot.__class__.__name__,
        )

        matching = any(_get_key(s) == _get_key(stats) for s in self.robot_stats)
        if matching:
            raise ValueError(f"Matching robot stats object was found: {robot}")

        self.robot_stats.add(stats)
        return stats
