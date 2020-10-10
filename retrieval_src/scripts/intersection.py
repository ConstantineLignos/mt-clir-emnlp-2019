#! /usr/bin/env python
"""
Output the intersection of all lines in the specified files.
"""

import argparse
from typing import Sequence


def intersect(paths: Sequence[str]):
    lines = None
    for path in paths:
        with open(path, encoding='utf8') as input_file:
            new_lines = set(line.strip() for line in input_file)
            if lines is None:
                lines = new_lines
            else:
                lines = lines & new_lines

    for line in lines:
        print(line)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', nargs='+', help='files to process')
    args = parser.parse_args()
    intersect(args.file)


if __name__ == '__main__':
    main()
