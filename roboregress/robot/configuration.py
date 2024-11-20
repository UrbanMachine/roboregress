from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel

from roboregress.engine import SimulationRuntime
from roboregress.robot.cell import BaseRobotCell, BigBird, Rake, RollingRake
from roboregress.robot.cell.screw_manipulator import ScrewManipulator
from roboregress.robot.conveyor import (
    DumbWoodConveyor,
    GreedyBusynessWoodConveyor,
    GreedyDistanceWoodConveyor,
)
from roboregress.robot.statistics import StatsTracker
from roboregress.wood import Surface, Wood


class SimConfig(BaseModel):
    wood: Wood.Parameters

    conveyor: (
        GreedyBusynessWoodConveyor.Parameters
        | DumbWoodConveyor.Parameters
        | GreedyDistanceWoodConveyor.Parameters
    )

    default_cell_distance: float
    """Distance between robot cells"""

    default_cell_width: float
    """Workspace within a cell"""

    pickers: list[
        Rake.Parameters
        | BigBird.Parameters
        | ScrewManipulator.Parameters
        | RollingRake.Parameters
    ]


CONVEYOR_MAPPING = {
    DumbWoodConveyor.Parameters: DumbWoodConveyor,
    GreedyDistanceWoodConveyor.Parameters: GreedyDistanceWoodConveyor,
    GreedyBusynessWoodConveyor.Parameters: GreedyBusynessWoodConveyor,
}
ROBOT_MAPPING: dict[type[BaseModel], type[BaseRobotCell[Any]]] = {
    Rake.Parameters: Rake,
    RollingRake.Parameters: RollingRake,
    BigBird.Parameters: BigBird,
    ScrewManipulator.Parameters: ScrewManipulator,
}


def runtime_from_file(file: Path) -> tuple[SimulationRuntime, StatsTracker]:
    with file.open() as f:
        config = SimConfig.parse_obj(yaml.safe_load(f))

    runtime = SimulationRuntime()

    wood = Wood(parameters=config.wood)
    stats = StatsTracker(runtime=runtime, wood=wood)

    pos = 0.0
    cells = []
    for params in config.pickers:
        if params.start_pos == -1:
            # Don't autopopulate position, this one is manually configured
            params.start_pos = pos

        if params.working_width == -1:
            params.working_width = config.default_cell_width

        for surface in Surface:
            robot_type = ROBOT_MAPPING[type(params)]
            updated_surface_params = params.copy(update={"pickable_surface": surface})
            robot = robot_type(updated_surface_params, wood, stats)
            cells.append(robot)

        pos += config.default_cell_distance + params.working_width

    conveyor = CONVEYOR_MAPPING[type(config.conveyor)](
        params=config.conveyor, wood=wood, cells=cells, wood_stats=stats.wood
    )

    runtime.register(*cells, wood, conveyor)
    return runtime, stats
