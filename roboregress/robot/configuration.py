from pathlib import Path
from typing import List, Union

import yaml
from pydantic import BaseModel

from roboregress.engine import SimulationRuntime
from roboregress.robot.cell import BaseRobotCell, BigBird, Rake
from roboregress.robot.conveyor import DumbWoodConveyor
from roboregress.wood import Surface, Wood


class SimConfig(BaseModel):
    wood: Wood.Parameters

    rakes: List[Rake.Parameters]

    big_birds: List[BigBird.Parameters]

    conveyor: Union[DumbWoodConveyor.Parameters]


def runtime_from_file(file: Path):
    with file.open() as f:
        config = SimConfig.parse_obj(yaml.safe_load(f))

    wood = Wood(parameters=config.wood)
    cells: List[BaseRobotCell] = [
        *(
            Rake(parameters=r.copy(update={"pickable_surface": surface}), wood=wood)
            for surface in Surface
            for r in config.rakes
        ),
        *(
            BigBird(parameters=b.copy(update={"pickable_surface": surface}), wood=wood)
            for b in config.big_birds
            for surface in Surface
        ),
    ]

    conveyor = DumbWoodConveyor(params=config.conveyor, wood=wood, cells=cells)

    runtime = SimulationRuntime()
    runtime.register(conveyor, wood, *cells)
    return runtime
