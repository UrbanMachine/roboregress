#!/bin/bash
set -euxo pipefail

poetry run isort roboregress/ tests/
poetry run black roboregress/ tests/
