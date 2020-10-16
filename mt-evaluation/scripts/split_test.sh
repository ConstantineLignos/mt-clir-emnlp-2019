#!/usr/bin/env bash
set -euo pipefail

DETOKENIZE=mosesdecoder/scripts/tokenizer/detokenizer.perl
LOWERCASE=mosesdecoder/scripts/tokenizer/lowercase.perl
PROCESS="python scripts/process_tokens.py"
STEM="$PROCESS stem"
DEPUNC="$PROCESS depunc"

while read f; do
    dir=$(dirname ${f})
    sys=${dir}/sys
    ref=${dir}/ref
    grep ^H ${f} | cut -f 3 > ${sys}.txt
    grep ^T ${f} | cut -f 2 > ${ref}.txt
    for orig in ${sys} ${ref}; do
        lower=${orig}.lower
        depunc=${lower}.depunc
        stem=${lower}.stem
        stem_depunc=${stem}.depunc
        ${LOWERCASE} < ${orig}.txt > ${lower}.txt
        ${STEM} < ${lower}.txt > ${stem}.txt
        ${DEPUNC} < ${lower}.txt > ${depunc}.txt
        ${DEPUNC} < ${stem}.txt > ${stem_depunc}.txt
        for processed in ${lower} ${depunc} ${stem} ${stem_depunc}; do
            ${DETOKENIZE} -q < ${processed}.txt > ${processed}.detok.txt &
        done
        wait
    done
done
