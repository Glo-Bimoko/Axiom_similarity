#!/usr/bin/env python3
import sys
import pandas as pd
import re
import tempfile
from pathlib import Path

def main():
    if len(sys.argv) != 3:
        print("Usage: parse_axiom.py <input_file> <output_file>")
        sys.exit(1)

    infile = Path(sys.argv[1])
    outfile = Path(sys.argv[2])

    GENO_COL_RE = re.compile(r"^(.+?)\.CEL_call_code$", re.IGNORECASE)

    try:
        print(f"Processing file: {infile}")

        if infile.suffix.lower() in [".xlsx", ".xls"]:
            raw = pd.read_excel(infile, header=None, dtype=str)
        else:
            # For text files, read line by line to handle metadata lines
            with open(infile, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            print(f"File has {len(lines)} lines")

            # Find the data start (first line that doesn't start with ##)
            data_start = 0
            for i, line in enumerate(lines):
                if not line.strip().startswith('##'):
                    data_start = i
                    print(f"Data starts at line {i}: {line.strip()[:100]}...")
                    break

            if data_start >= len(lines) - 1:
                print("ERROR: No data found after metadata lines")
                sys.exit(1)

            # Write clean data to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
                # Write data lines (skip metadata)
                for line in lines[data_start:]:
                    tmp_file.write(line)
                tmp_filename = tmp_file.name

            try:
                # Read the cleaned data with pandas (compatible with older pandas versions)
                raw = pd.read_csv(tmp_filename, sep='\t', dtype=str, error_bad_lines=False, warn_bad_lines=False)
                print(f"Successfully read cleaned file with shape: {raw.shape}")
            except Exception as e:
                print(f"Error reading with pandas: {e}")
                print("Trying alternative approach...")
                # Fallback: read manually and create dataframe
                with open(tmp_filename, 'r') as f:
                    clean_lines = []
                    header = None
                    for line_num, line in enumerate(f):
                        line = line.strip()
                        if not line:
                            continue
                        parts = line.split('\t')
                        if header is None:
                            header = parts
                            expected_cols = len(parts)
                        elif len(parts) == expected_cols:
                            clean_lines.append(parts)
                        else:
                            print(f"Skipping malformed line {line_num + 1}: expected {expected_cols} fields, got {len(parts)}")
                
                if header and clean_lines:
                    raw = pd.DataFrame(clean_lines, columns=header)
                    print(f"Manually created dataframe with shape: {raw.shape}")
                else:
                    raise Exception("No valid data found")
            finally:
                # Clean up temporary file
                Path(tmp_filename).unlink()

        print(f"Data shape: {raw.shape}")
        print(f"Columns: {list(raw.columns)}")

        # Find genotype column
        geno_cols = [c for c in raw.columns if GENO_COL_RE.match(str(c))]

        if not geno_cols:
            print("ERROR: Could not find genotype column matching pattern '*.CEL_call_code'")
            print("Available columns:")
            for col in raw.columns:
                print(f"  - {col}")
            sys.exit(1)

        geno_col = geno_cols[0]
        print(f"Found genotype column: {geno_col}")

        # Extract sample ID
        match = GENO_COL_RE.match(geno_col)
        if match:
            sample_id = match.group(1)
        else:
            # Fallback: use filename without extension
            sample_id = infile.stem.replace('.CEL', '')

        print(f"Sample ID: {sample_id}")

        # Extract and rename column
        result_df = raw[[geno_col]].rename(columns={geno_col: sample_id}).copy()

        # Remove any rows with missing genotype calls
        initial_rows = len(result_df)
        result_df = result_df.dropna()
        final_rows = len(result_df)

        print(f"Rows: {initial_rows} -> {final_rows} (removed {initial_rows - final_rows} missing)")

        # Save result
        result_df.to_csv(outfile, sep="\t", index=False)
        print(f"Output saved to: {outfile}")
        if len(result_df) > 0:
            print(f"First few genotype calls: {result_df.iloc[:5, 0].tolist()}")

    except Exception as e:
        print(f"ERROR processing {infile}: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()