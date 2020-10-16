#! /usr/bin/env python
"""
Collect IR scores.
"""

import csv
import sys
from multiprocessing import Pool
from pathlib import Path
from typing import Dict, List

# Wiki fields
# map                   	all	0.4342
# rbo	all	0.21848273082018374
# gm_map                	all	0.0252
# P_5                   	all	0.1016
# P_10                  	all	0.0558
# recall_10             	all	0.5576
# ndcg                  	all	0.4994

# Europarl fields
# map                   	all	0.4342
# rbo	all	0.21848273082018374
# gm_map                	all	0.0252
# P_5                   	all	0.1016
# P_10                  	all	0.0558
# recall_10             	all	0.5576
# ndcg                  	all	0.4994

QUERY_ALL = 'all'

FIELD_LANG = 'lang'
FIELD_SIZE = 'size'
FIELD_BPE_TOKENS = 'bpe.tokens'
FIELD_DATASET = 'dataset'
FIELD_MODEL = 'model'
FIELD_QUERY = 'query'

FIELD_MAP = 'map'
FIELD_RBO = 'rbo'
FIELD_MAP_GM = 'map.gm'
FIELD_P5 = 'p.5'
FIELD_P10 = 'p.10'
FIELD_R10 = 'r.10'
FIELD_NDCG = 'ndcg'

FIELD_NAME_MAPPING = {
    'map': FIELD_MAP,
    'rbo': FIELD_RBO,
    'gm_map': FIELD_MAP_GM,
    'P_5': FIELD_P5,
    'P_10': FIELD_P10,
    'recall_10': FIELD_R10,
    'ndcg': FIELD_NDCG
}

MEASURES = [FIELD_MAP, FIELD_MAP_GM, FIELD_P5, FIELD_P10, FIELD_R10, FIELD_RBO, FIELD_NDCG]
FIELDS = ([FIELD_DATASET, FIELD_LANG, FIELD_SIZE, FIELD_BPE_TOKENS, FIELD_MODEL, FIELD_QUERY]
          + MEASURES)

DATASET_DIRS = (
    ('europarl', Path('evals_ones_qrel')),
    ('wiki', Path('wiki_evals', 'onehotR')),
    ('wiki', Path('wiki_evals', 'onehotR-glove')),
)


def collect_scores(root: str, output_path: str) -> None:
    all_args = []
    for dataset, dataset_path in DATASET_DIRS:
        dataset_dir = Path(root) / dataset_path
        for eval_path in dataset_dir.iterdir():
            splits = eval_path.name.split('.')
            # Skip control results
            if '-' not in splits[1]:
                continue

            # First two chars is source lang
            src = splits[1][:2]
            size = int(splits[2])
            # If specified, BPE is given as bpeXXX for XXX tokens. Otherwise, it's 16000.
            bpe_tokens = int(splits[3][3:]) if splits[3].startswith('bpe') else 16000
            if splits[-1] == 'bm25eval':
                model = 'bm25'
            elif splits[-1] == 'jsonleval':
                if dataset_dir.name == 'onehotR':
                    model = 'neural'
                elif dataset_dir.name == 'onehotR-glove':
                    model = 'neural.glove'
                else:
                    raise ValueError(f'Could not identify neural model dir {dataset_dir}')
            else:
                raise ValueError(f'Could not identify model type from {splits[-1]}')

            all_args.append((eval_path, dataset, src, size, bpe_tokens, model, FIELD_NAME_MAPPING))

    with Pool() as pool:
        results = pool.starmap(_extract_scores, all_args, 1)

    with open(output_path, 'w', encoding='utf8') as output:
        writer = csv.DictWriter(output, FIELDS, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for result in results:
            writer.writerows(result)


def _extract_scores(input_path: Path, dataset: str, lang: str, size: int, bpe_tokens: int,
                    model: str, field_mapping: Dict[str, str]) -> List[Dict[str, float]]:
    common_fields = {
        FIELD_DATASET: dataset,
        FIELD_LANG: lang,
        FIELD_SIZE: size,
        FIELD_BPE_TOKENS: bpe_tokens,
        FIELD_MODEL: model
    }

    all_scores = []
    with input_path.open(encoding='utf8') as input_file:
        query = None
        row_scores = None
        for line in input_file:
            fields = line.split()
            new_query = fields[1]

            # Set up for new query if needed
            if new_query != query:
                # Save old query scores if needed
                if query:
                    all_scores.append(row_scores)
                row_scores = dict(common_fields)
                row_scores[FIELD_QUERY] = query = new_query

            measure, value = fields[0], float(fields[2])
            row_scores[field_mapping[measure]] = value

    # Write out last entry
    assert row_scores
    all_scores.append(row_scores)

    return all_scores


def dotjoin(*args: str) -> str:
    return '.'.join(args)


if __name__ == '__main__':
    collect_scores(sys.argv[1], sys.argv[2])
