#! /usr/bin/env python
"""
Extract test BLEU scores from fairseq output.
"""

import re
import subprocess
import sys

RE_SCORE = re.compile(
    'BLEU4 = '
    + r'(?P<bleu>[\d.]+), (?P<bleu1>[\d.]+)/(?P<bleu2>[\d.]+)/(?P<bleu3>[\d.]+)/(?P<bleu4>[\d.]+)'
)


def main():
    test_files_path = sys.argv[1]
    with open(test_files_path, encoding='utf8') as test_files:
        for line in test_files:
            test_file = line.strip()
            output = subprocess.check_output(['tail', '-n', '1', test_file]).decode('utf8')
            print(test_file, RE_SCORE.search(output).groupdict())


if __name__ == '__main__':
    main()
