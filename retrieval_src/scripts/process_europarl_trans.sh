#!/usr/bin/env bash
set -euxo pipefail

CORPUS=europarl

src=$1
size=$2
bpe_tokens=$3

dataset=data/${CORPUS}.${src}.tok.${size}.bpe${bpe_tokens}
output=data/${CORPUS}.${src}-en.${size}.bpe${bpe_tokens}.jsonl

python retrieval/process_translation.py ${dataset}.trans.{${src},detok.en} data/europarl.${src}.jsonl ${output}
gzip -k ${output}
