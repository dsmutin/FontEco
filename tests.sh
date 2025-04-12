#!/bin/bash

# Exit on error
set -e

# Install the package in development mode
pip install -e .

# Install test dependencies
pip install -e ".[test]"

# Run tests with coverage
pytest --cov=src tests/ -v 