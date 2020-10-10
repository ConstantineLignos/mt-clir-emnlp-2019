#!/usr/bin/env bash
set -euxo pipefail

CORPUS=wiki

src=$1
size=$2
bpe_tokens=$3

dataset=data/${CORPUS}.${src}.tok.${size}.bpe${bpe_tokens}
jsonl_prefix=data/${CORPUS}.${src}-en.${size}.bpe${bpe_tokens}
badids_jsonl=${jsonl_prefix}.badids.jsonl

python retrieval/process_translation.py ${dataset}.trans.{${src},detok.en} data/en-de-cs.articles/${src}/articles.0.jsonl ${badids_jsonl}
python retrieval/wiki/remap_article_ids.py ${badids_jsonl} ${src} data/en-de-cs.titles.5000.ratio3.0.tsv ${jsonl_prefix}.jsonl
gzip -k ${jsonl_prefix}.jsonl
