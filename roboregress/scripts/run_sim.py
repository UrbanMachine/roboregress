from argparse import ArgumentParser
from pathlib import Path

from roboregress.robot.configuration import runtime_from_file


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("-v", "--visualize", action="store_true", default=False)
    parser.add_argument("-c", "--config", type=Path, required=True)
    parser.add_argument(
        "-t",
        "--time",
        type=int,
        default=8 * 60 * 60,
        help="How long to run the simulation for. By default it will run for 8 hours",
    )
    args = parser.parse_args()

    runtime = runtime_from_file(args.config)

    runtime.step_until(timestamp=args.time, visualization=args.visualize)
    print("Finished Simulation!")


if __name__ == "__main__":
    main()
