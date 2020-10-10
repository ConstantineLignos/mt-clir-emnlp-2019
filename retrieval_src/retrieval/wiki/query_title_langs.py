#! /usr/bin/env python
"""
Query wikidata using English article names to get names of articles in other languages.
"""

import argparse
import concurrent.futures
from itertools import islice
from multiprocessing import Pool
from typing import Sequence, Tuple, Optional

import requests


QUERY_URL = 'https://www.wikidata.org/w/api.php'
QUERY_TITLES_LIMIT = 50

FIELD_SITELINKS = 'sitelinks'
FIELD_TITLE = 'title'


def query_title_langs(titles_path: str, output_path: str, langs: Sequence[str], workers: int):
    with open(titles_path, encoding='utf8') as title_file:
        title_count = 0
        batches = []
        while True:
            # Read in the next set of titles
            batch = [line.strip() for line in islice(title_file, QUERY_TITLES_LIMIT)]
            if batch:
                title_count += len(batch)
                batches.append(batch)
            else:
                break

    all_wikis = [lang + 'wiki' for lang in langs]
    print(f'Querying {title_count} titles in {len(batches)} batches from wikis {all_wikis}')

    with open(output_path, 'w', encoding='utf8') as out:
        # Write header
        print('\t'.join(['id'] + langs), file=out)

        errors = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            # Start the load operations and mark each future with its URL
            futures = [executor.submit(_process_batch, batch, all_wikis) for batch in batches]
            for future in concurrent.futures.as_completed(futures):
                results = future.result()
                if results is not None:
                    for result in results:
                        print('\t'.join(result), file=out)
                else:
                    errors += 1

        if errors:
            print(f'{errors} batches encountered errors')


def _process_batch(titles: Sequence[str], wikis: Sequence[str]) \
        -> Optional[Sequence[Sequence[str]]]:
    query_params = _query_params(titles)
    req = requests.get(QUERY_URL, query_params)

    if req.status_code != requests.codes.ok:
        print(f'Received status {req.status_code} for request: {req.request}')
        return None

    json = req.json()
    all_results = []
    for id_, fields in json['entities'].items():
        # Missing entry
        if id_ == '-1':
            print(f'Missing: {repr(fields[FIELD_TITLE])}')
        elif FIELD_SITELINKS not in fields:
            # Nothing to do, move on
            continue
        else:
            sitelinks = fields[FIELD_SITELINKS]
            result = [id_]
            for wiki in wikis:
                if wiki in sitelinks:
                    result.append(sitelinks[wiki][FIELD_TITLE])
                else:
                    break
            else:
                # If we made it to the end of the loop, the results were good
                all_results.append(result)

    return all_results


def _query_params(ids: Sequence[str]) -> dict:
    return {
        'format': 'json',
        'action': 'wbgetentities',
        'sites': 'enwiki',
        'props': 'sitelinks',
        'titles': '|'.join(ids)
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('titles', help='file containing titles to query')
    parser.add_argument('output', help='output file')
    parser.add_argument('langs', nargs='+', help='languages to retrieve titles for')
    parser.add_argument('--workers', '-w', type=int, default=2,
                        help='number of parallel workers (default 2)')
    args = parser.parse_args()
    query_title_langs(args.titles, args.output, args.langs, args.workers)


if __name__ == '__main__':
    main()
