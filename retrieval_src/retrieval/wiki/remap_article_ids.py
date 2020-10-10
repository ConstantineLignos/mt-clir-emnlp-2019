#! /usr/bin/env python
"""
Remap the IDs for wiki jsonlines using a table of parallel article titles.
"""
import argparse

from jsonlines import jsonlines

from retrieval.wiki.constants import ID


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('input_jsonl', help='input jsonlines')
    parser.add_argument('lang', help='language to use in table lookup')
    parser.add_argument('title_map', help='title mapping table')
    parser.add_argument('out_jsonl', help='output jsonlines')
    args = parser.parse_args()
    remap_ids(args.input_jsonl, args.lang, args.title_map, args.out_jsonl)


def remap_ids(input_jsonl_path: str, lang: str, title_map_path: str, output_jsonl_path) -> None:
    title_ids = {}
    with open(title_map_path, encoding='utf8') as title_map:
        # Parse header
        header = next(title_map).strip().split('\t')
        lang_idx = header.index(lang)

        # Make sure no one accidentally passed the ID field
        assert lang_idx != 0, 'Field for language is the same as the ID field'

        for line in title_map:
            fields = line.strip().split('\t')
            lang_title = fields[lang_idx]
            id_ = fields[0]

            if lang_title in title_ids:
                raise ValueError(f'Title f{repr(lang_title)} already in map')

            title_ids[lang_title] = id_

    with jsonlines.open(input_jsonl_path) as input_jsonl, \
            jsonlines.open(output_jsonl_path, 'w') as output_jsonl:
        for line in input_jsonl:
            line[ID] = title_ids[line[ID]]
            output_jsonl.write(line)


if __name__ == '__main__':
    main()
