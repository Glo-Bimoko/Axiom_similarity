#!/usr/bin/env nextflow

nextflow.enable.dsl = 2

params.input = "./data/*.txt"
params.outdir = "./results"

workflow {
    input_files = Channel.fromPath(params.input)

    // Parse individual samples
    parsed = input_files.map { file ->
        tuple(file.getBaseName().replaceAll(/\..*/, ''), file)
    } | PARSE_SAMPLE

    // Collect all parsed TSV files and merge them
    all_tsvs = parsed.map { it[1] }.collect()
    merged = MERGE_ALL(all_tsvs)
    COMPARE(merged)
}

process PARSE_SAMPLE {
    tag "$sample_id"

    input:
    tuple val(sample_id), path(file)

    output:
    tuple val(sample_id), path("${sample_id}.tsv")

    script:
    """
    python3 ${projectDir}/bin/parse_axiom.py "$file" "${sample_id}.tsv"
    """
}

process MERGE_ALL {
    tag "merging"

    input:
    path(tsvs)

    output:
    path("merged_callcodes.tsv")

    script:
    """
    python3 -c '
import pandas as pd
import sys
import os

# Get all TSV files passed as input
tsv_files = [f for f in os.listdir(".") if f.endswith(".tsv")]
print(f"Found TSV files: {tsv_files}")

if not tsv_files:
    print("No TSV files found!")
    with open("merged_callcodes.tsv", "w") as f:
        f.write("")
    sys.exit(0)

# Read all TSV files and merge them
dfs = []
for tsv_file in sorted(tsv_files):
    print(f"Reading {tsv_file}")
    df = pd.read_csv(tsv_file, sep="\\t")
    print(f"Shape: {df.shape}, Columns: {list(df.columns)}")
    dfs.append(df)

if dfs:
    # Merge on index (assuming same number of rows)
    merged = pd.concat(dfs, axis=1)
    print(f"Merged shape: {merged.shape}")
    print(f"Merged columns: {list(merged.columns)}")
    merged.to_csv("merged_callcodes.tsv", sep="\\t", index=False)
else:
    with open("merged_callcodes.tsv", "w") as f:
        f.write("")
    '
    """
}

process COMPARE {
    tag "comparing"
    publishDir params.outdir, mode: 'copy'

    input:
    path("merged_callcodes.tsv")

    output:
    path("similarity_results.txt")

    script:
    """
    python3 -c '
import pandas as pd
import itertools
import sys

# Read the merged file
df = pd.read_csv("merged_callcodes.tsv", sep="\\t")
print(f"Comparison input shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

if df.empty or df.shape[1] < 2:
    print("Not enough data for comparison")
    with open("similarity_results.txt", "w") as f:
        f.write("No data available for comparison\\n")
    sys.exit(0)

results = []
for s1, s2 in itertools.combinations(df.columns, 2):
    # Remove rows where either column has NaN/missing values
    valid_mask = df[s1].notna() & df[s2].notna()
    col1_clean = df.loc[valid_mask, s1].astype(str)
    col2_clean = df.loc[valid_mask, s2].astype(str)

    total = len(col1_clean)
    if total == 0:
        similarity = 0.0
    else:
        matches = (col1_clean == col2_clean).sum()
        similarity = (matches / total) * 100

    result_line = f"{s1} vs {s2}: {similarity:.2f}% ({matches}/{total} matches)"
    results.append(result_line)
    print(result_line)

with open("similarity_results.txt", "w") as f:
    for line in results:
        f.write(line + "\\n")
    '
    """
}