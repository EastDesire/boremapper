#!/usr/bin/env python3

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from boremapper.app import App


def main():
    app = App()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()