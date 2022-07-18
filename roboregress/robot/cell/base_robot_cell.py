from abc import ABC, abstractmethod
from typing import Dict, Generic, List, Tuple, TypeVar

from pydantic import BaseModel

from roboregress.engine import BaseSimObject
from roboregress.engine.base_simulation_object import LoopGenerator
from roboregress.robot.fasteners import Fastener
from roboregress.robot.surfaces import Surface
from roboregress.robot.wood import MoveScheduled, Wood

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
                    print(_)
                    yield pick_time
            except MoveScheduled:
                # No new work is allowed, a wood movement has been scheduled
                yield None

    @abstractmethod
    def _run_pick(self) -> Tuple[List[Fastener], float]:
        """Do the smallest amount of picking that this robot can do in a single unit,
        and return how many seconds it took to do it."""
