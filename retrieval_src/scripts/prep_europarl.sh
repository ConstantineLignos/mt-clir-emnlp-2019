#!/usr/bin/env bash
set -euxo pipefail

THREADS=2

lang=$1
data=$2

python retrieval/dump_paragraphs.py europarl $data/europarl.${lang}.jsonl $data/europarl.${lang}.txt
perl $MOSES/scripts/ems/support/split-sentences.perl -q -l $lang < data/europarl.${lang}.txt > data/europarl.${lang}.sent.txt
# Delete <P> lines
sed -i '/<P>/d' $data/europarl.${lang}.sent.txt
perl $MOSES/scripts/tokenizer/tokenizer.perl -q -threads $THREADS -a -l $lang -protected params/tokenizer_protected_patterns < $data/europarl.${lang}.sent.txt > $data/europarl.${lang}.tok.txt
