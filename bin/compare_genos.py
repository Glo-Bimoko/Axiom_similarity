#!/usr/bin/env python3
import sys
import pandas as pd
import itertools

matrix_file = sys.argv[1]
output_file = sys.argv[2]

df = pd.read_csv(matrix_file, sep="\t", index_col=0)

results = []

for s1, s2 in itertools.combinations(df.columns, 2):
    sub_df = df[[s1, s2]].dropna()
    total = len(sub_df)
    if total == 0:
        similarity = 0.0
    else:
        matches = (sub_df[s1] == sub_df[s2]).sum()
        similarity = matches / total * 100
    results.append(f"{s1} vs {s2} similarity={similarity:.0f}%")

with open(output_file, 'w') as f:
    for line in results:
        f.write(line + '\n')
