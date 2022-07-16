#!/bin/bash
set -euxo pipefail

poetry run cruft check
poetry run mypy --ignore-missing-imports roboregress/
poetry run isort --check --diff roboregress/ tests/
poetry run black --check roboregress/ tests/
poetry run flake8 roboregress/ tests/
poetry run bandit -r roboregress/
poetry run vulture roboregress/
echo "Lint successful!"