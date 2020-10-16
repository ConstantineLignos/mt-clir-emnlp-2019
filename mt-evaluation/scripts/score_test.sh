#!/usr/bin/env bash
set -euo pipefail

for d in "$@"; do
    echo -ne "$d \t"
    python sacreBLEU/sacrebleu.py -lc ${d}/ref.detok.txt < ${d}/sys.detok.txt
done
