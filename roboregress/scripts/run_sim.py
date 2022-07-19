from argparse import ArgumentParser
from typing import List

from roboregress.engine import SimulationRuntime
from roboregress.robot.cell import BaseRobotCell, BigBird, Rake
from roboregress.robot.conveyor import DumbWoodConveyor
from roboregress.wood import Fastener, Surface, Wood


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("-v", "--visualize", action="store_true", default=False)
    args = parser.parse_args()

    runtime = SimulationRuntime()

    wood = Wood(
        parameters=Wood.Parameters(
            fastener_densities={
                Fastener.STAPLE: 0.1,
                Fastener.FLUSH_NAIL: 5,
                Fastener.OFFSET_NAIL: 10,
                Fastener.SCREW: 0.01,
            }
        )
    )

    cells: List[BaseRobotCell] = [
        *(
            Rake(
                parameters=Rake.Parameters(
                    start_pos=0,
                    end_pos=1,
                    pickable_surface=surface,
                    rake_cycle_seconds=5.0,
                    pick_probabilities={Fastener.OFFSET_NAIL: 0.9},
                ),
                wood=wood,
            )
            for surface in Surface
        ),
        *(
            BigBird(
                parameters=BigBird.Parameters(
                    start_pos=1.1,
                    end_pos=2.1,
                    pickable_surface=surface,
                    pick_probabilities={
                        Fastener.OFFSET_NAIL: 0.8,
                        Fastener.FLUSH_NAIL: 0.7,
                        Fastener.STAPLE: 0.9,
                    },
                    big_bird_pick_seconds=4,
                ),
                wood=wood,
            )
            for surface in Surface
        ),
    ]
    planner = DumbWoodConveyor(
        cells=cells,
        wood=wood,
        params=DumbWoodConveyor.Parameters(move_increment=0.5, move_speed=0.25),
    )

    runtime.register(planner, wood, *cells)
    runtime.step_until(timestamp=10000, visualization=args.visualize)
    print("Finished Simulation!")


if __name__ == "__main__":
    main()
