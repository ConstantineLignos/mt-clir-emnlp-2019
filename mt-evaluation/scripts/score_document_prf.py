#! /usr/bin/env bash
"""
Score precision, recall, and F1 on translation at the document level.

Requires that the reference and system output consist of one document per
line. The line must begin with a document id, and the document must be
tokenized.
"""

import argparse
from typing import Dict, List, TextIO, Sequence, Tuple


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('reference')
    parser.add_argument('system')
    args = parser.parse_args()
    score(args.reference, args.system)


def score(ref_path: str, sys_path: str) -> None:
    with open(ref_path, encoding='utf8') as ref_file:
        ref_docs = _parse_file(ref_file)

    with open(sys_path, encoding='utf8') as sys_file:
        sys_docs = _parse_file(sys_file)

    # Iterate over sys docids since the reference may be a superset of the system output
    for docid in sorted(sys_docs):
        sys_tokens = sys_docs[docid]
        ref_tokens = ref_docs[docid]

    for ref_sent, hyp_sent in zip(ref_lines, hyp_lines):
        tp, fp, fn = tp_fp_fn(ref_sent, hyp_sent)
        true_positives += tp
        false_positives += fp
        false_negatives += fn

    precision = true_positives / (true_positives + false_positives)
    recall = true_positives / (true_positives + false_negatives)
    f1_score = 2 * precision * recall / (precision + recall)

    print("Precision: ", precision)
    print("Recall   : ", recall)
    print("F-1 score: ", f1_score)


def _parse_file(input_file: TextIO) -> Dict[str, List[str]]:
    docs = {}
    for line in input_file:
        splits = line.split()
        docs[splits[0]] = splits[1:]

    return docs


def tp_fp_fn(ref_words: Sequence[str], hyp_words: Sequence[str]) -> Tuple[int, int, int]:
    """

    Input:
    1. ref_sent (str): Reference sentence
    2. hyp_sent (str): Hypothesis sentence

    Description:
        -Calculates true positives, false positives and false negatives
        checking only for membership in the original class,without taking
        into account expected counts.

        -Example:
            Ref: the quick fox and the fast fox
            Hyp: the quick and the fast fox

    Output:
    1. tp_fp_fn (list): [true_positives, false_positives, false_negatives]

    """
    tp = 0
    fp = 0
    fn = 0

    for hyp_word in hyp_words:
        if hyp_word in ref_words:
            tp += 1
            ref_idx = ref_words.index(hyp_word)
            del ref_words[ref_idx]
    fp = len(hyp_words) - tp

    ref_words = ref_sent.rstrip().split()
    hyp_words = hyp_sent.rstrip().split()

    for ref_word in ref_words:
        if ref_word not in hyp_words:
            fn += 1
    return [tp, fp, fn]


if __name__ == '__main__':
    main()
