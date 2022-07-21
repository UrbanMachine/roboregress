from argparse import ArgumentParser
from pathlib import Path

from roboregress.robot.configuration import runtime_from_file
from roboregress.robot.reporting import render_stats


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("-v", "--visualize", action="store_true", default=False)
    parser.add_argument("-c", "--config", type=Path, required=True)
    parser.add_argument(
        "-s",
        "--save-to",
        type=Path,
        required=False,
        help="Where to save the report. Defaults to the name of the configuration file",
    )
    parser.add_argument(
        "-t",
        "--time",
        type=int,
        default=8 * 60 * 60,
        help="How long to run the simulation for. By default it will run for 8 hours",
    )
    args = parser.parse_args()

    runtime, stats = runtime_from_file(args.config)

    runtime.step_until(timestamp=args.time, visualization=args.visualize)

    save_to = args.save_to if args.save_to else args.config.with_suffix(".html")
    render_stats(stats, save_to=save_to, config_file=args.config)
    print("Finished Simulation!")


if __name__ == "__main__":
    main()
