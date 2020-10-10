#! /usr/bin/env python

"""
# Translation probabilities
бани    entropy 1.632   nTrans 2761     sum 1.000000
  bathrooms: 0.413104
  baths: 0.278510
  bani: 0.157314
  bathroom: 0.054029
  bath: 0.029057
  wc: 0.009472
  bathing: 0.007966
  sunbaths: 0.007734
  wcs: 0.005974
  deck: 0.005971
  suite: 0.005435
  bedrooms: 0.004986
  sunbathing: 0.004352
  sunbathe: 0.003762
  rent: 0.002325
  applicable: 0.001989
  p3: 0.001926
  hostel: 0.001806
  wellness: 0.001740
  flooring: 0.001374
  cleaning: 0.000596
  construction: 0.000554
  yacht: 0.000013
  en: 0.000009
  spas: 0.000000
цикаранг        entropy 0       nTrans 94       sum 1.000000
  cikarang: 1.000000
"""
import csv
import re
from argparse import ArgumentParser
from typing import Dict, TextIO, Generator

from attr import attrs

START = "# Translation probabilities"
LINE_RE = re.compile(
    r"(?P<word>\S+)\tentropy (?P<entropy>\S+)\t+nTrans (?P<n_trans>\S+)\t+sum (?P<sum>\S+)"
)
ALIGNMENT_RE = re.compile(r"(?P<word>\S+): (?P<prob>[\d.]+)")


@attrs(auto_attribs=True)
class Alignment:
    word: str
    entropy: float
    n_trans: int
    sum: float
    alignments: Dict[str, float]


def extract_alignment_stats(alignment_file: TextIO) -> Generator[Alignment, None, None]:
    # Discard initial lines
    for line in alignment_file:
        if line.strip() == START:
            break

    alignment = None
    try:
        # Seed line with first word
        line = next(alignment_file)
        while True:
            line = line.strip()
            match = LINE_RE.match(line)
            if not match:
                raise ValueError(f"Couldn't match line: {repr(line)}")
            word = match.group("word")
            alignment = Alignment(
                word,
                float(match.group("entropy")),
                int(match.group("n_trans")),
                float(match.group("sum")),
                {},
            )
            while True:
                # Read more lines to fill in the alignments
                line = next(alignment_file)
                # If it doesn't start with spaces, it's a new entry
                if not line.startswith("  "):
                    break

                line = line.strip()
                match = ALIGNMENT_RE.match(line)
                if not match:
                    raise ValueError(
                        f"Couldn't match alignment line {repr(line)} for word {repr(word)}"
                    )
                alignment.alignments[match.group("word")] = float(match.group("prob"))

            if alignment.alignments:
                # Yield alignment and clear loop var
                yield alignment
                alignment = None
            else:
                raise ValueError(f"No alignments for word {repr(word)}")
    except StopIteration:
        if alignment and not alignment.alignments:
            raise ValueError(
                f"File ended while processing alignment for {repr(alignment.word)}"
            )


def main():
    parser = ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()

    with open(args.input, encoding="utf8") as input_file, open(
        args.output, "w", encoding="utf8"
    ) as output_file:
        writer = csv.writer(output_file)
        header = ["word", "entropy", "n_trans", "n_alignments"]
        writer.writerow(header)
        for alignment in extract_alignment_stats(input_file):
            row = [
                alignment.word,
                alignment.entropy,
                alignment.n_trans,
                len(alignment.alignments),
            ]
            writer.writerow(row)


if __name__ == "__main__":
    main()
