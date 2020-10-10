"""
Dumps wikipedia articles to a directory in JSON lines format.
"""

import argparse
import os
from multiprocessing import Process, JoinableQueue
from typing import List

import jsonlines
from pymongo import MongoClient

from retrieval.wiki.constants import COLLECTION, ID

_DEFAULT_BATCH_SIZE = 100_000


def main() -> None:
    """Parse arguments and call dump_articles."""
    parser = argparse.ArgumentParser()
    parser.add_argument('id_file', help='file with wikipedia article IDs, one per line')
    parser.add_argument('language', help='wiki language')
    parser.add_argument('output_dir', help='output directory to write dump files to')
    parser.add_argument('num_workers', type=int, help='number of parallel workers to use')
    args = parser.parse_args()
    dump_articles(args.id_file, args.output_dir, args.language, args.num_workers, _DEFAULT_BATCH_SIZE)


def dump_articles(id_path: str, output_dir: str, lang: str,  n_workers: int, batch_size: int):
    """Dump wikipedia articles to a directory in JSON Lines format."""
    os.makedirs(output_dir, exist_ok=True)

    # Create a queue for batches of IDs
    queue: JoinableQueue = JoinableQueue()

    workers = [Process(target=_work, args=(output_dir, lang, queue, i)) for i in range(n_workers)]
    for worker in workers:
        worker.daemon = True
        worker.start()

    print(f'Loading IDs from {id_path}')
    article_count = 0
    batch_count = 0
    with open(id_path, encoding='utf8') as id_file:
        batch = []
        for line in id_file:
            batch.append(line.strip())
            article_count += 1
            if len(batch) == batch_size:
                queue.put((batch_count, batch))
                batch_count += 1
                batch = []

        # Add final batch
        if batch:
            queue.put((batch_count, batch))
            batch_count += 1

    print(f'Added {article_count} articles to queue in {batch_count} batches')
    queue.join()
    print('All queue tasks complete')


def _work(output_dir: str, lang: str, queue: JoinableQueue, worker_id: int) -> None:
    print(f'Starting worker {worker_id}')
    client = MongoClient()
    collection = client[lang + 'wiki'][COLLECTION]
    while True:
        i, batch = queue.get()
        output_path = os.path.join(output_dir, f'articles.{i}.jsonl')
        # Encoding is always forced by jsonlines, no need to set it
        with jsonlines.open(output_path, 'w') as output_file:
            # Doing a batch find is much faster than one query per article
            articles = collection.find({ID: {'$in': batch}})
            for article in articles:
                paragraphs = get_paragraphs(article)
                line = {ID: article[ID], 'paragraphs': paragraphs}
                output_file.write(line)

        queue.task_done()


def get_paragraphs(article: dict) -> List[List[str]]:
    paragraphs = []
    for section in article['sections']:
        for paragraph in section['paragraphs']:
            sentences = [sentence['text'] for sentence in paragraph['sentences']]
            if sentences:
                paragraphs.append(sentences)

    return paragraphs


if __name__ == '__main__':
    main()
