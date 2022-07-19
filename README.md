# roboregress
A system for numerical modeling different configurations of a lumber processing robot.

_________________

[![PyPI version](https://badge.fury.io/py/roboregress.svg)](http://badge.fury.io/py/roboregress)
[![Test Status](https://github.com/urbanmachine/roboregress/workflows/Test/badge.svg?branch=main)](https://github.com/urbanmachine/roboregress/actions?query=workflow%3ATest)
[![Lint Status](https://github.com/urbanmachine/roboregress/workflows/Lint/badge.svg?branch=main)](https://github.com/urbanmachine/roboregress/actions?query=workflow%3ALint)
[![codecov](https://codecov.io/gh/urbanmachine/roboregress/branch/main/graph/badge.svg)](https://codecov.io/gh/urbanmachine/roboregress)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://timothycrosley.github.io/isort/)
_________________

[Read Latest Documentation](https://urbanmachine.github.io/roboregress/) - [Browse GitHub Code Repository](https://github.com/urbanmachine/roboregress/)
_________________

## Development

### Installing python dependencies
```shell
poetry install
```

### Running Tests
```shell
pytest .
```

### Formatting Code
```shell
bash .github/format.sh
```

### Linting
```shell
bash .github/check_lint.sh
```

## Running the Sim
After running `poetry install`, the script can be run via:

```
run_sim --visualize --config experiments/basic.yml
```