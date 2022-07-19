from argparse import ArgumentParser
from pathlib import Path

from roboregress.robot.configuration import runtime_from_file


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("-v", "--visualize", action="store_true", default=False)
    parser.add_argument("-c", "--config", type=Path, required=True)
    args = parser.parse_args()

    runtime = runtime_from_file(args.config)

    runtime.step_until(timestamp=8 * 60 * 60, visualization=args.visualize)
    print("Finished Simulation!")


if __name__ == "__main__":
    main()
