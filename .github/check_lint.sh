#!/bin/bash
set -euxo pipefail

poetry run cruft check
poetry run mypy --ignore-missing-imports roboregress/
poetry run isort --check --diff roboregress/ tests/
poetry run black --check roboregress/ tests/
poetry run flake8 roboregress/ tests/
poetry run safety check -i 39462 -i 40291
poetry run bandit -r roboregress/
