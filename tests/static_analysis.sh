#!/bin/bash

# TODO: make runnable from anywhere, e.g. from test/
python -m pylint ./ --errors-only --init-hook='import sys; sys.path.insert(0, "./")' --extension-pkg-whitelist=PySide6