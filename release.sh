#!/usr/bin/env bash

# Get the directory where this file is present (root directory)
DIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to root dir of project
cd "$DIR"

# Remove old build
rm -rf dist

# Package
python3 setup.py sdist bdist_wheel

# Publish
python3 -m twine upload dist/*
