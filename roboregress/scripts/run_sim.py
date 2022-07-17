from argparse import ArgumentParser
from typing import List

from roboregress.engine import SimulationRuntime
from roboregress.robot.cell import BaseRobotCell, RakeCell
from roboregress.robot.planner import DumbWoodPlanner
from roboregress.robot.surfaces import Surface
from roboregress.robot.wood import InfinitePlank


def main() -> None:
    parser = ArgumentParser()
    args = parser.parse_args()

    print("Finished Simulation!")


if __name__ == "__main__":
    main()
