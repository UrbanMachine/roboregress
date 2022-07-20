from pathlib import Path
from typing import List, Tuple, Union

import yaml
from pydantic import BaseModel

from roboregress.engine import SimulationRuntime
from roboregress.robot.cell import BaseRobotCell, BigBird, Rake
from roboregress.robot.cell.screw_manipulator import ScrewManipulator
from roboregress.robot.conveyor import DumbWoodConveyor, GreedyWoodConveyor
from roboregress.robot.statistics import StatsTracker
from roboregress.wood import Surface, Wood


class SimConfig(BaseModel):
    wood: Wood.Parameters

    rakes: List[Rake.Parameters]

    big_birds: List[BigBird.Parameters]

    screw_manipulators: List[ScrewManipulator.Parameters]

    conveyor: Union[DumbWoodConveyor.Parameters, GreedyWoodConveyor.Parameters]


CONVEYOR_MAPPING = {
    DumbWoodConveyor.Parameters: DumbWoodConveyor,
    GreedyWoodConveyor.Parameters: GreedyWoodConveyor,
}


def runtime_from_file(file: Path) -> Tuple[SimulationRuntime, StatsTracker]:
    with file.open() as f:
        config = SimConfig.parse_obj(yaml.safe_load(f))

    runtime = SimulationRuntime()

    wood = Wood(parameters=config.wood)
    stats = StatsTracker(runtime=runtime, wood=wood)

    cells: List[BaseRobotCell] = [
        *(
            Rake(r.copy(update={"pickable_surface": surface}), wood, stats)
            for surface in Surface
            for r in config.rakes
        ),
        *(
            BigBird(b.copy(update={"pickable_surface": surface}), wood, stats)
            for b in config.big_birds
            for surface in Surface
        ),
        *(
            ScrewManipulator(b.copy(update={"pickable_surface": surface}), wood, stats)
            for b in config.screw_manipulators
            for surface in Surface
        ),
    ]

    conveyor = CONVEYOR_MAPPING[type(config.conveyor)](
        params=config.conveyor, wood=wood, cells=cells
    )

    runtime.register(*cells, wood, conveyor)
    return runtime, stats
