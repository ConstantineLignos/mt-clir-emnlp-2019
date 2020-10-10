#! /usr/bin/env python
"""
Select parallel wikipedia articles from a TSV.
"""

import argparse
import random
import re
import sys
from typing import Tuple, Dict, Sequence

from pymongo import MongoClient
from pymongo.collection import Collection

from retrieval.wiki.constants import COLLECTION
from retrieval.wiki.dump_articles import get_paragraphs

RE_PARENTHETICAL = re.compile(r'\(.+?\)')


def select_parallel_articles(input_path: str, output_path: str, select: int, seed: int) -> None:

    with open(input_path, encoding='utf8') as input_file:
        random.seed(seed)

        # Parse header
        langs = next(input_file).strip().split('\t')[1:]

        entries: Dict[str, Tuple[str, ...]] = {}
        skip_count = 0
        keep_count = 0
        for line in input_file:
            fields = line.strip().split('\t')
            id_ = fields[0]
            titles = fields[1:]

            # Check titles
            if any(_is_bad_title(title) for title in titles):
                skip_count += 1
                continue

            entries[id_] = tuple(titles)
            keep_count += 1

    print(f'Kept {keep_count} entries, discarded {skip_count} entries')

    # Subselect as needed
    do_selection = select != -1
    if do_selection:
        ids = list(entries.keys())
        random.shuffle(ids)
    else:
        ids = entries.keys()


    # Set up for mongo
    client = MongoClient()
    collections = [client[lang + 'wiki'][COLLECTION] for lang in langs]

    keep_count = 0
    skip_count = 0
    with open(output_path, 'w', encoding='utf8') as output:
        # Write header
        print('\t'.join(['id'] + langs), file=output)
        for id_ in ids:
            if do_selection and keep_count >= select:
                break

            titles = entries[id_]
            if _keep_titles(titles, collections):
                print('\t'.join([id_] + list(titles)), file=output)
                keep_count += 1
                if not keep_count % 100:
                    print(keep_count)
            else:
                skip_count += 1

    print(f'Wrote {keep_count} entries, discarded {skip_count} entries')
    if do_selection and keep_count < select:
        print('ERROR: Did not return requested number of entries')
        sys.exit(1)


def _is_bad_title(title: str) -> bool:
    title_no_parens = RE_PARENTHETICAL.sub('', title).strip()
    if any(c.isalpha() for c in title_no_parens):
        return False
    else:
        return True


def _keep_titles(titles: Sequence[str], collections: Sequence[Collection]) -> bool:
    title_words = [_article_words(title, collection) for title, collection in zip(titles, collections)]
    if (all(words > 500 for words in title_words)
            and max(title_words) <= 3 * min(title_words)):
        return True
    else:
        return False


def _article_words(title: str, collection: Collection) -> int:
    article = collection.find_one(title)
    if not article:
        return 0

    word_count = 0
    for paragraph in get_paragraphs(article):
        for sentence in paragraph:
            word_count += len(sentence.split())

    return word_count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('input_tsv',
                        help='Input TSV file with an id column and a column per-langauge')
    parser.add_argument('output_tsv',
                        help='output file')
    parser.add_argument('--select', type=int, default=-1,
                        help='number of entries to select')
    parser.add_argument('--seed', type=int, default=0,
                        help='random seed to use')
    args = parser.parse_args()
    select_parallel_articles(args.input_tsv, args.output_tsv, args.select, args.seed)


if __name__ == '__main__':
    main()
