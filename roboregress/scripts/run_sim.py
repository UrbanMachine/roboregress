from argparse import ArgumentParser

from roboregress.engine import EngineRuntime
from roboregress.robot.cell import BaseRobotCell
from roboregress.robot.planner import BaseWoodPlanner


def main() -> None:
    parser = ArgumentParser()
    args = parser.parse_args()

    print("Finished Simulation!")


if __name__ == "__main__":
    main()
