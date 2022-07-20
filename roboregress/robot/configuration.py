from pathlib import Path
from typing import List, Tuple, Union

import yaml
from pydantic import BaseModel

from roboregress.engine import SimulationRuntime
from roboregress.robot.cell import BigBird, Rake
from roboregress.robot.cell.screw_manipulator import ScrewManipulator
from roboregress.robot.conveyor import DumbWoodConveyor, GreedyWoodConveyor
from roboregress.robot.statistics import StatsTracker
from roboregress.wood import Surface, Wood


class SimConfig(BaseModel):
    wood: Wood.Parameters

    conveyor: Union[DumbWoodConveyor.Parameters, GreedyWoodConveyor.Parameters]

    cell_distance: float
    """Distance between robot cells"""

    cell_width: float
    """Workspace within a cell"""

    pickers: List[Union[Rake.Parameters, BigBird.Parameters, ScrewManipulator.Parameters]]


CONVEYOR_MAPPING = {
    DumbWoodConveyor.Parameters: DumbWoodConveyor,
    GreedyWoodConveyor.Parameters: GreedyWoodConveyor,
}
ROBOT_MAPPING = {
    Rake.Parameters: Rake,
    BigBird.Parameters: BigBird,
    ScrewManipulator.Parameters: ScrewManipulator,
}


def runtime_from_file(file: Path) -> Tuple[SimulationRuntime, StatsTracker]:
    with file.open() as f:
        config = SimConfig.parse_obj(yaml.safe_load(f))

    runtime = SimulationRuntime()

    wood = Wood(parameters=config.wood)
    stats = StatsTracker(runtime=runtime, wood=wood)

    pos = 0.0
    cells = []
    for params in config.pickers:
        for surface in Surface:
            robot_type = ROBOT_MAPPING[type(params)]
            fixed_params = params.copy(
                update={
                    "pickable_surface": surface,
                    "start_pos": pos,
                    "end_pos": pos + config.cell_width,
                }
            )
            robot = robot_type(fixed_params, wood, stats)
            cells.append(robot)

        pos += config.cell_distance + config.cell_width

    conveyor = CONVEYOR_MAPPING[type(config.conveyor)](
        params=config.conveyor, wood=wood, cells=cells
    )

    runtime.register(*cells, wood, conveyor)
    return runtime, stats
