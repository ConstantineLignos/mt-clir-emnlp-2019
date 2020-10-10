#!/usr/bin/env bash
import argparse

import jsonlines

from retrieval.wiki.constants import ID

ID_PREFIX = 'id__'
MODE_EUROPARL = 'europarl'
MODE_WIKI = 'wiki'
MODES = (MODE_EUROPARL, MODE_WIKI)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=MODES, help=f'type of input, one of {MODES}')
    parser.add_argument('input', help='input jsonl file')
    parser.add_argument('output', help='output text file')
    parser.add_argument('--single-sentence', action='store_true',
                        help='dump each document as a single sentence')
    args = parser.parse_args()
    dump_paragraphs(args.mode, args.input, args.output, single_sentence=args.single_sentence)


def dump_paragraphs(mode: str, input_path: str, output_path: str, *,
                    single_sentence: bool = False) -> None:
    with jsonlines.open(input_path) as json_input, \
            open(output_path, 'w', encoding='utf8') as out:
        # For single sentence output, use only a space between sentences
        sentence_sep = ' ' if single_sentence else '\n'

        for line in json_input:
            id_ = ID_PREFIX + line[ID]
            if mode == MODE_WIKI:
                id_ = id_.replace(' ', '_')
            elif mode == MODE_EUROPARL and not sentence_sep:
                # Extra newline to ensure a sentence break
                id_ += '\n'

            print(id_, file=out, end=sentence_sep)
            for paragraph in line['paragraphs']:
                for sentence in paragraph:
                    print(sentence, file=out, end=sentence_sep)

            # Extra newline to ensure sentence break for europarl, since it will be passed
            # through a sentence segmenter. (Wikipedia has sentence breaks, so it will not
            # need to be segmented.)
            # Also print a newline between documents if in single sentence mode, since each
            # sentence will end in a space, not newline
            if mode == MODE_EUROPARL or single_sentence:
                print(file=out)


if __name__ == '__main__':
    main()
