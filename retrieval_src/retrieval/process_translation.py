#! /usr/bin/env python
"""
Process a translated europarl file in
"""


import argparse
import html
from itertools import zip_longest

import jsonlines

from retrieval.dump_paragraphs import ID_PREFIX
from retrieval.wiki.constants import ID


def process_translation(src_trans_path: str, tgt_trans_path: str,
                        src_jsonl_path: str, tgt_jsonl_path: str) -> None:
    with open(src_trans_path, encoding='utf8') as src_trans, \
            open(tgt_trans_path, encoding='utf8') as tgt_trans, \
            jsonlines.open(src_jsonl_path) as src_json, \
            jsonlines.open(tgt_jsonl_path, 'w') as tgt_json:

        # Get the first id
        src_id = _extract_id(next(src_trans).strip())
        # Discard the matching target line
        next(tgt_trans)

        for line in src_json:
            # Extract and check the id
            line_id = line[ID]
            sentences = []

            # Load the translated lines
            for src_sentence, tgt_sentence in zip_longest(src_trans, tgt_trans):
                # Ensure we haven't exhausted the lines
                assert src_trans is not None
                assert tgt_trans is not None

                # Always make sure IDs are matching, at least with some normalization
                assert html.unescape(src_id) == line_id.replace(' ', '_'), \
                    f'Source: f{repr(src_id)}, Translation: f{repr(line_id)}'

                if src_sentence.startswith(ID_PREFIX):
                    # Prepare for the next document
                    src_id = _extract_id(src_sentence.strip())
                    break

                sentences.append(tgt_sentence.strip())

            line['paragraphs'] = [sentences]
            tgt_json.write(line)


def _extract_id(line: str) -> str:
    assert line.startswith(ID_PREFIX)
    return line[len(ID_PREFIX):]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('src_trans', help='source translation file')
    parser.add_argument('tgt_trans', help='target translation file')
    parser.add_argument('src_jsonl', help='source jsonlines')
    parser.add_argument('out_jsonl', help='output jsonlines')
    args = parser.parse_args()
    process_translation(args.src_trans, args.tgt_trans, args.src_jsonl, args.out_jsonl)


if __name__ == '__main__':
    main()
