#! /usr/bin/env python
"""
Collect MT scores from the output of score_test.sh.
"""

import csv
import re
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path
from typing import Dict, Tuple, Sequence

FIELD_BLEU = 'bleu'
FIELD_PREC1 = 'prec1'
FIELD_PREC2 = 'prec2'
FIELD_PREC3 = 'prec3'
FIELD_PREC4 = 'prec4'
FIELD_LANG = 'lang'
FIELD_SIZE = 'size'
FIELD_BPE_TOKENS = 'bpe.tokens'
PREC_FIELDS = [FIELD_PREC1, FIELD_PREC2, FIELD_PREC3, FIELD_PREC4]

CONDITIONS = ('lower', 'lower.stem', 'lower.depunc', 'lower.stem.depunc')
FIELDS = ([FIELD_LANG, FIELD_SIZE, FIELD_BPE_TOKENS]
          + [field + '.' + condition
             for field in [FIELD_BLEU] + PREC_FIELDS
             for condition in CONDITIONS])

BLEU_RE = re.compile(r'= (?P<bleu>[\d.]+) '
    + r'(?P<prec1>[\d.]+)/(?P<prec2>[\d.]+)/(?P<prec3>[\d.]+)/(?P<prec4>[\d.]+)')


def collect_scores(root: str, output_path: str) -> None:
    all_args = []
    for subdir in Path(root).iterdir():
        splits = subdir.name.split('.')
        # Last two chars is source lang
        src = splits[1][-2:]
        size = int(splits[2])
        # If specified, BPE is given as bpeXXX for XXX tokens. Otherwise, it's 1600.
        bpe_tokens = int(splits[3][3:]) if splits[3].startswith('bpe') else 16000

        all_args.append((subdir, src, size, bpe_tokens, CONDITIONS))

    with Pool() as pool:
        results = pool.starmap(_compute_scores, all_args, 1)

    with open(output_path, 'w', encoding='utf8') as output:
        writer = csv.DictWriter(output, FIELDS, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for result in results:
            writer.writerow(result)


def _compute_scores(subdir: Path, lang: str, size: int, bpe_tokens: int,
                    conditions: Sequence[str]) -> Dict[str, float]:
    scores = {
        FIELD_LANG: lang,
        FIELD_SIZE: size,
        FIELD_BPE_TOKENS: bpe_tokens
    }
    for condition in conditions:
        ref_detok = subdir / dotjoin('ref', condition, 'detok', 'txt')
        sys_detok = subdir / dotjoin('sys', condition, 'detok', 'txt')
        bleu, precisions = compute_bleu_prec1(ref_detok, sys_detok)
        scores[dotjoin(FIELD_BLEU, condition)] = bleu
        for prec_field, prec in zip(PREC_FIELDS, precisions):
            scores[dotjoin(prec_field, condition)] = prec

    return scores


def compute_bleu_prec1(ref_path: Path, sys_path: Path) \
        -> Tuple[float, Tuple[float, float, float, float]]:
    cmd = [
        'python',
        'sacreBLEU/sacrebleu.py',
        '-lc',
        '--smooth',
        'none',
        ref_path,
        '-i',
        sys_path
    ]
    result = subprocess.check_output(cmd).decode('utf8')
    match = BLEU_RE.search(result)
    return float(match.group('bleu')), \
           tuple(float(match.group('prec' + str(n)))for n in (1, 2, 3, 4))


def dotjoin(*args: str) -> str:
    return '.'.join(args)


if __name__ == '__main__':
    collect_scores(sys.argv[1], sys.argv[2])
