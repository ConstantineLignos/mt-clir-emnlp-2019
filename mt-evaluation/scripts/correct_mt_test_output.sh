#!/usr/bin/env bash
set -euo pipefail

# Creates corrected versions of the original MT output

DATA=../mt_data
ORIG_DIR=../mt_test_output
CORRECTED_DIR=../mt_test_output_corrected
mkdir -p "$CORRECTED_DIR"

TEST="test.txt"

function decompress_if_needed {
  path=$1
  if [ ! -f "$path" ]; then
    path_gz=$path.gz
    echo "Decompressing $path_gz to $path"
    gunzip -c "$path_gz" > "$path"
  fi
}

for orig in "$ORIG_DIR/"*; do
  # Set up paths
  config=$(basename "$orig")
  corrected="$CORRECTED_DIR/$config"
  mkdir -p "$corrected"
  orig_test="$orig/$TEST"
  corrected_test="$corrected/$TEST"

  # To get the name of the reference we need to get the first two fields of the config
  # nc.en-de.150000.bpe32000.fconv -> nc.en-de
  ref_name=$(echo "$config" | cut -d . -f 1-2)
  # We are always testing in en
  ref="$DATA/$ref_name.test.en"

  # Decompress reference and test output if needed
  decompress_if_needed "$ref"
  decompress_if_needed "$orig_test"

  # Copy over the reference
  cp "$ref" "$corrected/ref.txt"

  # Run the new splitter in the background, we'll wait for all jobs at the end
  ./scripts/split_test_corrected.sh "$orig_test" "$corrected" &
done
wait
