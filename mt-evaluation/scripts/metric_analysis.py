"""
Produce correlation analysis between metrics and test hypotheses regarding BPE.

Usage:
python scripts/metric_analysis.py output/mt_ir_scores_all.tsv output/mt_ir_scores_corr.tsv output/mt_ir_bpe_delta.tsv

Adapted from Metric Analysis.ipynb
"""

import argparse
from collections import defaultdict

import numpy as np
import pandas as pd
import scipy.stats as stats

# TODO: Change to MAP for the wilcoxon test results only
IR_METRIC = 'rbo'
MT_METRIC = 'bleu.lower'


def analyze(mt_ir_scores_path: str, corr_path: str, bpe_delta_path: str) -> None:
    # Load data
    scores = pd.read_table(mt_ir_scores_path)

    # Compute and write correlations
    corrs = compute_corrs(scores)
    corrs.to_csv(corr_path, sep='\t', index=False)

    # Compare BPE for each model and dataset
    compare_bpe_at_size(scores)

    bpe_comparison = compare_bpe_at_condition(scores)
    bpe_comparison.to_csv(bpe_delta_path, sep='\t', index=False)


def compare_bpe_at_condition(scores):
    bpe_comparison_dfs = []
    idx = 0
    for dataset in scores.dataset.unique():
        for lang in scores.lang.unique():
            for size in scores['size'].unique():
                # Models and datasets aren't fully crossed so we can't just take all unique
                for model in scores.model[scores.dataset == dataset].unique():
                    condition = scores[
                        (scores.lang == lang)
                        & (scores.dataset == dataset)
                        & (scores.model == model)
                        & (scores['size'] == size)
                        ]
                    condition_row = {
                        'dataset': dataset,
                        'lang': lang,
                        'model': model,
                        'size': size,
                    }
                    for _, row in condition.iterrows():
                        bpe_tokens = row['bpe.tokens']
                        condition_row[f"{IR_METRIC}.bpe{bpe_tokens}"] = row[IR_METRIC]
                        condition_row[f"{MT_METRIC}.bpe{bpe_tokens}"] = row[MT_METRIC]
                    bpe_comparison_dfs.append(pd.DataFrame(condition_row, index=[idx]))
                    idx += 1

    bpe_comparison = pd.concat(bpe_comparison_dfs, ignore_index=True, sort=False)
    for metric in (IR_METRIC, MT_METRIC):
        delta = bpe_comparison[f"{metric}.bpe32000"] - bpe_comparison[f"{metric}.bpe16000"]
        bpe_comparison[f"{metric}.delta"] = delta


    return bpe_comparison


def compare_bpe_at_size(scores):
    for dataset in scores.dataset.unique():
        dataset_scores = scores[scores.dataset == dataset]
        for model in dataset_scores.model.unique():
            condition_bpe_scores = defaultdict(dict)
            for _rownum, row in dataset_scores[dataset_scores.model == model].iterrows():
                key = condition_key_size(row)
                # Make sure we don't already have two values
                assert len(condition_bpe_scores[key]) < 2
                bpe_size = row['bpe.tokens']
                condition_bpe_scores[key][bpe_size] = row[IR_METRIC]

            bpe16k, bpe32k = zip(
                *((condition_scores[16000], condition_scores[32000]) for condition_scores in
                  condition_bpe_scores.values()))
            test = stats.wilcoxon(bpe32k, bpe16k)
            print(dataset, model, 'hypothesis: BPE 32k != BPE 16k')
            print('Mean 32k - 16k', mean_diff(bpe32k, bpe16k))
            print(test)
            print()


def compute_corrs(scores):
    # Compute pairwise metrics correlations
    corr_dfs = []
    for lang in scores.lang.unique():
        for dataset in scores.dataset.unique():
            dataset_scores = scores[(scores.lang == lang) & (scores.dataset == dataset)]
            for model in dataset_scores.model.unique():
                model_scores = dataset_scores[dataset_scores.model == model]
                common_fields = {'dataset': [dataset], 'lang': [lang], 'model': [model]}
                model_corr = model_scores.corr('kendall')
                for measure1, row in model_corr.items():
                    for measure2, value, in row.items():
                        if measure1 != measure2:
                            row_dict = dict(common_fields)
                            row_dict.update(
                                {'measure1': [measure1], 'measure2': [measure2], 'corr': [value]})
                            corr_dfs.append(pd.DataFrame(row_dict))
    corrs = pd.concat(corr_dfs, ignore_index=True)
    return corrs


def condition_key_size(row):
    return (row.model, row.lang, row['size'])


def mean_diff(seq1, seq2):
    assert len(seq1) == len(seq2)
    return sum(s1 - s2 for s1, s2 in zip(seq1, seq2)) / len(seq1)


def median_diff(seq1, seq2):
    assert len(seq1) == len(seq2)
    return np.median(seq1) - np.median(seq2)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'mt_ir_scores_path', help='path to input mt_ir scores TSV generated by analyze_mt.R'
    )
    parser.add_argument('corr_path', help='path to output correlation TSV')
    parser.add_argument('bpe_delta_path', help='path to output BPE delta TSV')
    args = parser.parse_args()
    analyze(args.mt_ir_scores_path, args.corr_path, args.bpe_delta_path)


if __name__ == '__main__':
    main()
