#!/bin/bash
isort -rc tests/ main.py
autoflake -r --in-place --remove-unused-variables tests/ main.py
black -l 120 tests/ main.py
flake8 --max-line-length 120 tests/ main.py
