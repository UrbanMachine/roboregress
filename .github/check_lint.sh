#!/bin/bash
set -euxo pipefail

poetry run cruft check
poetry run mypy --ignore-missing-imports roboregression/
poetry run isort --check --diff roboregression/ tests/
poetry run black --check roboregression/ tests/
poetry run flake8 roboregression/ tests/
poetry run safety check -i 39462 -i 40291
poetry run bandit -r roboregression/
