#!/bin/bash
set -euxo pipefail

poetry run cruft check
poetry run mypy --ignore-missing-imports roboregress/
poetry run isort --check --diff roboregress/ tests/
poetry run black --check roboregress/ tests/
poetry run flake8 roboregress/ tests/
poetry run bandit -r -c pyproject.toml roboregress/ tests/
poetry run vulture --min-confidence 100 roboregress/ tests/
echo "Lint successful!"