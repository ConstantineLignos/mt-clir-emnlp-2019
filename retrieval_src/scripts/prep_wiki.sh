#!/usr/bin/env bash
set -euxo pipefail

THREADS=2

lang=$1
data=$2

python retrieval/dump_paragraphs.py wiki ${data}/wiki.${lang}.jsonl ${data}/wiki.${lang}.txt
perl $MOSES/scripts/tokenizer/tokenizer.perl -q -threads $THREADS -a -l $lang -protected params/tokenizer_protected_patterns < ${data}/wiki.${lang}.sent.txt > ${data}/wiki.${lang}.tok.txt
