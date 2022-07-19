from abc import ABC, abstractmethod
from math import pi
from typing import Dict, Generic, List, Tuple, TypeVar

import numpy as np
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

BaseParams = TypeVar("BaseParams", bound="BaseRobotCell.Parameters")


class BaseRobotCell(BaseSimObject, ABC, Generic[BaseParams]):
    """An object in charge of doing _some_ work on some location along the wood axis"""

    class Parameters(BaseModel):
        start_pos: float
        end_pos: float
        pickable_surface: Surface
        pick_probabilities: Dict[Fastener, float]

    def __init__(self, wood: Wood, parameters: BaseParams):
        """
        :param parameters: The pydantic parameters for the robot cell.
        :param wood: The wood to pick from
        """
        super().__init__()
        self._params = parameters
        self._wood = wood

    def _loop(self) -> LoopGenerator:
        while True:
            try:
                with self._wood.work_lock():
                    _, pick_time = self._run_pick()
                    yield pick_time
            except MoveScheduled:
                # No new work is allowed, a wood movement has been scheduled
                yield None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._params.pickable_surface.value})"

    @property
    def width(self) -> float:
        return self._params.end_pos - self._params.start_pos

    @property
    def center(self) -> float:
        return self._params.start_pos + (self.width / 2)

    @property
    @abstractmethod
    def color(self) -> Tuple[float, float, float]:
        """The color to use when visualizing this robot cell"""

    @abstractmethod
    def _run_pick(self) -> Tuple[List[Fastener], float]:
        """Do the smallest amount of picking that this robot can do in a single unit,
        and return how many seconds it took to do it."""

    def draw(self) -> List[o3d.geometry.Geometry]:
        surface_dir = np.array(SURFACE_NORMALS[self._params.pickable_surface])
        position = surface_dir * ROBOT_DIST_FROM_CELL_CENTER
        position += (self.center, 0, 0)

        box: o3d.geometry.TriangleMesh = o3d.geometry.TriangleMesh.create_box(
            width=self.width, height=ROBOT_HEIGHT, depth=ROBOT_WIDTH
        )

        # Orient the rectangle to 'face' the surface it corresponds to
        if position[1] == 0:
            box.rotate(box.get_rotation_matrix_from_xyz((pi / 2, 0, 0)))

        box.translate(position - box.get_center())
        box.paint_uniform_color(self.color)
        return [box]
