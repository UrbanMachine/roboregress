import contextlib
from typing import Generator, List, Optional, Set, Tuple

from roboregress.engine import SimulationRuntime
from roboregress.wood import Surface, Wood

from .cell import BaseRobotCell

_FEET_PER_METER = 3.280839895


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
        self.n_picked_fasteners: int = 0
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
        self._wood = wood
        self._runtime = runtime

    @property
    def robots_by_cell(self) -> List[Tuple[int, RobotStats]]:
        """Iterate over the robots with their given 'cell id'"""
        cell_positions = self.cell_positions
        robots_by_cell: List[Tuple[int, RobotStats]] = []

        for robot in self.robot_stats:
            cell_id = cell_positions.index(robot.robot_params.end_pos)
            robots_by_cell.append((cell_id, robot))

        robots_by_cell.sort(key=lambda k: k[0])
        return robots_by_cell

    @property
    def cell_positions(self) -> List[float]:
        robot_centers = list(dict.fromkeys(r.robot_params.end_pos for r in self.robot_stats))
        robot_centers.sort()
        return robot_centers

    @property
    def missed_fasteners(self) -> int:
        """Return the number of fasteners after the final robot"""
        cell_positions = self.cell_positions
        furthest_pos = cell_positions[-1] if len(cell_positions) else 0
        return self._wood.missed_fasteners(furthest_pos)

    @property
    def total_time(self) -> float:
        return self._runtime.timestamp

    @property
    def total_picked_fasteners(self) -> int:
        return self._wood.total_picked_fasteners

    @property
    def total_meters_processed(self) -> float:
        return self._wood.processed_board

    @property
    def total_feet_processed(self) -> float:
        return self._wood.processed_board * _FEET_PER_METER

    @property
    def throughput_meters(self) -> float:
        return self.total_meters_processed / self.total_time

    @property
    def throughput_feet(self) -> float:
        return self.throughput_meters * _FEET_PER_METER

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
