#!/usr/bin/env python3

import unittest
import sys
import os


def main():
    app_root_dir = os.path.dirname(os.path.realpath(__file__)) + '/../'
    sys.path.insert(0, app_root_dir)

    test_dir = 'unit'
    test_pattern = 'test*.py'

    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, test_pattern, app_root_dir)

    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    
    sys.exit(0 if result.wasSuccessful() else 1)

if __name__ == '__main__':
    main()