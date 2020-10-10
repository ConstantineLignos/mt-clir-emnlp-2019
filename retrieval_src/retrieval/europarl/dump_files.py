#! /usr/bin/env python
"""
Dumps europarl transcripts to a directory in JSON lines format.
"""

import argparse
import os
from typing import TextIO, Dict, Optional

import jsonlines

from retrieval.wiki.constants import ID


def main() -> None:
    """Parse arguments and call dump_articles."""
    parser = argparse.ArgumentParser()
    parser.add_argument('file_list', help='file containing paths to process')
    parser.add_argument('output', help='output file to write to')
    args = parser.parse_args()
    dump_files(args.file_list, args.output)


def dump_files(input_path: str, output_path: str) -> None:
    with open(input_path, encoding='utf8') as file_list_file:
        input_paths = [line.strip() for line in file_list_file]

    processed = 0
    skipped = 0
    with jsonlines.open(output_path, 'w') as output_file:
        for input_path in input_paths:
            file_id = os.path.splitext(os.path.basename(input_path))[0]
            with open(input_path, encoding='utf8') as input_file:
                parsed = parse_file(input_file, file_id)
                if parsed:
                    output_file.write(parsed)
                    processed += 1
                else:
                    skipped += 1

    print(f'Wrote {processed} and skipped {skipped} files')


def parse_file(input_file: TextIO, file_id: str) -> Optional[Dict]:
    output = {ID: file_id}
    paragraphs = []
    current_paragraph = []
    kept_lines = 0
    for line in input_file:
        line = line.strip()

        # Remove leading parentheticals
        if line.startswith('('):
            end_parens = line.find(')')
            if end_parens != -1:
                # If the parens are at the end, just skip
                if end_parens == len(line) - 1:
                    continue
                else:
                    line = line[end_parens + 1:].strip()

        # Remove <BRK>
        line = line.replace('<BRK>', '').strip()

        # Skip empty/bad lines
        if not line:
            continue

        if line.startswith('<') and line.endswith('>'):
            # XML should break paragraphs
            if current_paragraph:
                # Add it as a single sentence, even though it's probably more than that
                paragraphs.append([' '.join(current_paragraph)])
                current_paragraph = []
        else:
            if '<' in line or '>' in line:
                print(f'Possible XML in line from {file_id}: {repr(line)}')
            current_paragraph.append(line)
            kept_lines += 1

    # Add any remaining text
    paragraphs.append([' '.join(current_paragraph)])
    output['paragraphs'] = paragraphs

    # Return None for too-short documents
    if kept_lines < 3:
        return None
    else:
        return output


if __name__ == '__main__':
    main()
