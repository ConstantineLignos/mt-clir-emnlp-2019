import html
import sys

from pymongo import MongoClient

from retrieval.wiki.constants import DB, COLLECTION


def dump_ids(output_path: str) -> None:
    client = MongoClient()
    pages = client[DB][COLLECTION]
    cursor = pages.find({}, {"title": 1})

    with open(output_path, 'w', encoding='utf8') as output_file:
        for page in cursor:
            print(html.unescape(page["title"]), file=output_file)


if __name__ == '__main__':
    dump_ids(sys.argv[1])
