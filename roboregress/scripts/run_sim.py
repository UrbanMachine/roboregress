import logging
from argparse import ArgumentParser
from pathlib import Path

from roboregress.engine import Visualizer
from roboregress.robot.configuration import runtime_from_file
from roboregress.robot.reporting import render_stats


def main() -> None:
    logging.basicConfig(level=logging.INFO)

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

    visualizer = Visualizer(statistics=stats) if args.visualize else None
    runtime.step_until(timestamp=args.time, visualizer=visualizer)

    save_to = args.save_to if args.save_to else args.config.with_suffix(".html")
    render_stats(stats, save_to=save_to, config_file=args.config)
    logging.info("Finished Simulation!")


if __name__ == "__main__":
    main()
