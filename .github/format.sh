#!/bin/bash
set -euxo pipefail

poetry run isort roboregression/ tests/
poetry run black roboregression/ tests/
