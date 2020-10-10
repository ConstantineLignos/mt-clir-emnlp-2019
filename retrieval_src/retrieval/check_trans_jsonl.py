import sys

import jsonlines

from retrieval.wiki.constants import ID


def main() -> None:
    with jsonlines.open(sys.argv[1]) as left, jsonlines.open(sys.argv[2]) as right:
        for left_line, right_line in zip(left, right):
            left_id = left_line[ID]
            right_id = right_line[ID]
            assert left_id == right_id

            print(left_id)
            for paragraphs in (left_line['paragraphs'], right_line['paragraphs']):
                print(' '.join(sentence for paragraph in paragraphs for sentence in paragraph))
                print()
            print()


if __name__ == '__main__':
    main()
