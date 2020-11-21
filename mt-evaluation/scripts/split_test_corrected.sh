#!/usr/bin/env bash
set -euo pipefail

DETOKENIZE=mosesdecoder/scripts/tokenizer/detokenizer.perl
LOWERCASE=mosesdecoder/scripts/tokenizer/lowercase.perl
PROCESS="python scripts/process_tokens.py"
STEM="$PROCESS stem"
DEPUNC="$PROCESS depunc"

f=$1
dir=$2
sys=${dir}/sys
ref=${dir}/ref
# We rely on the calling script to set up the reference, we just extract system output.
# We do the following:
# 1. Extract the hypotheses via grep, which are formatted like H-<line number> (0-indexed) for example:
# H-1	-0.494432270526886	This is the addictive side of our warlors, as if the humiliation of these posters must be offset by our joy to its demise.
# 2. Use sed to remove the H- prefix so we can sort numerically
# 3. Use sort with the numeric flag to get them in the original order
# 4. Use cut to remove the line number and score
grep "^H-" "$f" | sed 's/^H-//' | sort -n | cut -f 3 > "${sys}.txt"
for orig in $sys $ref; do
    lower=${orig}.lower
    ${LOWERCASE} < "${orig}.txt" > "${lower}.txt"
    # Only detokenize sys
    if [ "$orig" == "$sys" ]; then
      for processed in ${orig} ${lower}; do
          ${DETOKENIZE} -q < "${processed}.txt" > "${processed}.detok.txt"
      done
    fi
done
