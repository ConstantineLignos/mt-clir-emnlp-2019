import sys

import regex

REGEX_PUNC = regex.compile(r'\p{P}+$')


def main() -> None:
    verb=sys.argv[1]
    with open(sys.stdin.fileno(), encoding='utf-8') as sys.stdin, \
        open(sys.stdout.fileno(), 'w', encoding='utf-8') as sys.stdout:
        if verb == 'stem':
            # Lazy import due to heavy impact
            from nltk import PorterStemmer
            stemmer = PorterStemmer()
            processor = stemmer.stem
        elif verb == 'lower':
            processor = _lower
        elif verb == 'depunc':
            processor = _none_if_all_punc
        else:
            raise ValueError(f'Unsupported command: {repr(verb)}')

        for line in sys.stdin:
            tokens = (processor(tok) for tok in line.split())
            print(' '.join(token for token in tokens if token))


def _lower(s: str) -> str:
    return s.lower()


def _none_if_all_punc(s: str) -> str:
    return None if REGEX_PUNC.match(s) else s


if __name__ == '__main__':
    main()

