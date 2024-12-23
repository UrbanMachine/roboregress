from abc import ABC, abstractmethod
from math import pi
from typing import TYPE_CHECKING, Generic, TypeVar

import numpy as np
import numpy.typing as npt
import open3d as o3d
from pydantic import BaseModel

from roboregress.engine import BaseSimObject
from roboregress.engine.base_simulation_object import LoopGenerator
from roboregress.robot.vis_constants import (
    ROBOT_DIST_FROM_CELL_CENTER,
    ROBOT_HEIGHT,
    ROBOT_WIDTH,
)
from roboregress.wood import SURFACE_NORMALS, Fastener, MoveScheduled, Surface, Wood

if TYPE_CHECKING:
    from roboregress.robot.statistics import StatsTracker

BaseParams = TypeVar("BaseParams", bound="BaseRobotCell.Parameters")


class BaseRobotCell(BaseSimObject, ABC, Generic[BaseParams]):
    """An object in charge of doing _some_ work on some location along the wood axis"""

    class Parameters(BaseModel):
        pick_probabilities: dict[Fastener, float]

        # Prefill these with defaults since configuration will override them
        start_pos: float = -1.0
        working_width: float = -1.0

        pickable_surface: Surface = Surface.TOP
        """Defaults to top to simplify configuration"""

        @property
        def end_pos(self) -> float:
            return self.start_pos + self.working_width

    def __init__(
        self, parameters: BaseParams, wood: Wood, stats_tracker: "StatsTracker"
    ):
        """
        :param parameters: The pydantic parameters for the robot cell.
        :param wood: The wood to pick from
        :param stats_tracker: The global stats tracker object
        """
        super().__init__()
        self.params = parameters
        self._wood = wood
        self._stats = stats_tracker.create_robot_stats_tracker(self)

        assert all(
            p > 0 for p in self.params.pick_probabilities.values()
        ), "Pick probabilities must be nonzero!"

    def _loop(self) -> LoopGenerator:
        while True:
            try:
                with self._wood.work_lock():
                    fasteners, pick_time = self._run_pick()
                    assert pick_time >= 0

                    self._stats.n_picked_fasteners += len(fasteners)
                    if pick_time > 0:
                        with self._stats.work_timer.time():
                            yield pick_time

                # Since no work was done, yield (outside the work lock) to give
                # the conveyor the chance to move
                if pick_time == 0:
                    yield None
            except MoveScheduled:
                # No new work is allowed, a wood movement has been scheduled
                with self._stats.waiting_for_wood_timer.time():
                    yield None

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"center={round(self.center, 1)}, "
            f"surface={self.params.pickable_surface.value}"
            f")"
        )

    @property
    def width(self) -> float:
        return self.params.end_pos - self.params.start_pos

    @property
    def center(self) -> float:
        return self.params.start_pos + (self.width / 2)

    @property
    @abstractmethod
    def color(self) -> tuple[float, float, float]:
        """The color to use when visualizing this robot cell"""

    @abstractmethod
    def _run_pick(self) -> tuple[list[Fastener], float]:
        """Do the smallest amount of picking that this robot can do in a single unit,
        and return how many seconds it took to do it."""

    def _calculate_color(self) -> npt.NDArray[np.float64]:
        """Return the color that the geometry should be drawn as"""

        if self._stats.work_timer.currently_working:
            color = np.array(self.color)
        else:
            color = np.array(self.color, dtype=np.float64)
            color += (0.5, 0.5, 0.5)
            color = np.clip(color, a_min=0, a_max=1)
        return color

    def _calculate_position(self) -> npt.NDArray[np.float64]:
        surface_dir = np.array(SURFACE_NORMALS[self.params.pickable_surface])
        position = surface_dir * ROBOT_DIST_FROM_CELL_CENTER
        position += (self.center, 0, 0)
        return position

    def _calculate_workspace_box(self) -> o3d.geometry.TriangleMesh:
        box: o3d.geometry.TriangleMesh = o3d.geometry.TriangleMesh.create_box(
            width=self.width, height=ROBOT_HEIGHT, depth=ROBOT_WIDTH
        )
        position = self._calculate_position()

        # Orient the rectangle to 'face' the surface it corresponds to
        if position[1] == 0:
            box.rotate(box.get_rotation_matrix_from_xyz((pi / 2, 0, 0)))

        box.translate(position - box.get_center())

        box.paint_uniform_color(self._calculate_color())
        return box

    def draw(self) -> list[o3d.geometry.TriangleMesh]:
        """Returns the position and rotation of what the geometry should be drawn as"""
        return [self._calculate_workspace_box()]
