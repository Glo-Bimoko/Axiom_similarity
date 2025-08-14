# Axiom Match/Similarity

A Nextflow-based pipeline for processing and comparing genetic genotype data from Axiom microarray chips. This pipeline extracts genotype call codes from multiple sample files and calculates pairwise similarity percentages between samples.

## Overview

The Axiom Match pipeline is designed to:
- Process Axiom genotype files (`.txt` or `.xlsx` format)
- Extract genotype call codes from the `*.CEL_call_code` columns
- Merge multiple samples into a single matrix
- Calculate pairwise similarity percentages between all sample pairs
- Generate comprehensive similarity reports

## Requirements

- **Nextflow**: 25.04.4 or higher
- **Python**: 3.8.1 or higher
- **Python packages**: pandas, openpyxl (for Excel files)

## Installation

1. **Clone or download** this repository to your local machine
2. **Ensure Nextflow is installed** and accessible in your PATH
3. **Install Python dependencies**:
   ```bash
   pip install pandas openpyxl
   ```

## Project Structure

```
axiom_match/
├── main.nf                 # Main Nextflow pipeline
├── bin/
│   ├── parse_axiom.py     # Script to parse Axiom genotype files
│   └── compare_genos.py   # Script to compare genotypes (legacy)
└── results/               # Output directory (created after running)
```

## Input File Format

Your input files should be Axiom genotype files with the following characteristics:

- **File naming**: `YYYYMMDD_SAMPLEID.CEL.txt` (e.g., `20250604_GX094.CEL.txt`)
- **Format**: Tab-separated text files or Excel files
- **Required columns**:
  - `probeset_id`: Unique identifier for each genetic probe
  - `SAMPLEID.CEL_call_code`: Genotype call codes (e.g., `G/G`, `C/G`, `A/T`)
  - Additional metadata columns (Strand, Allele_A, Allele_B, etc.)

## Usage

### Basic Usage

```bash
nextflow run main.nf --input './path/to/your/files/*.txt' --outdir './results'
```

### Parameters

- `--input`: Glob pattern for input files (e.g., `./data/*.txt`)
- `--outdir`: Output directory for results (default: `./results`)

### Example

```bash
# Process all .txt files in the testing_data directory
nextflow run main.nf --input './testing_data/*.txt' --outdir './results'

# Process files from a different directory
nextflow run main.nf --input './batch19/*.CEL.txt' --outdir './batch19_results'
```

## Pipeline Workflow

1. **PARSE_SAMPLE**: 
   - Processes each input file
   - Extracts the `*.CEL_call_code` column
   - Outputs a TSV file with sample ID as column name

2. **MERGE_ALL**: 
   - Combines all sample TSV files
   - Creates a merged matrix with samples as columns and genotypes as rows

3. **COMPARE**: 
   - Calculates pairwise similarity between all samples
   - Outputs similarity percentages to `similarity_results.txt`

## Output

### Files Generated

- `merged_callcodes.tsv`: Combined matrix of all sample genotypes
- `similarity_results.txt`: Pairwise similarity comparisons

### Similarity Results Format

```
GX094 vs GX095: 98.23%
GX094 vs TY010519967: 97.56%
GX095 vs TY010519967: 99.01%
```

## Configuration

The pipeline uses a local executor by default. You can modify `nextflow.config` to:
- Change resource allocation (CPU, memory, time)
- Switch to different executors (SLURM, PBS, etc.)
- Adjust process-specific settings

## Troubleshooting

### Common Issues

1. **File parsing errors**: Ensure input files are properly formatted tab-separated files
2. **Missing genotype columns**: Verify that your files contain `*.CEL_call_code` columns
3. **Memory issues**: Adjust memory settings in `nextflow.config` for large datasets

### Debug Mode

To see detailed processing information, check the Nextflow work directories:
```bash
cd work/
# Look for process-specific directories with detailed logs
```

## Example Data

The `testing_data/` directory contains example files:
- `20250604_GX094.CEL.txt`
- `20250604_GX095.CEL.txt` 
- `20250604_TY010519967.CEL.txt`

## Citation

If you use this pipeline in your research, please cite:
- Nextflow: Di Tommaso, P. et al. (2017). Nextflow enables reproducible computational workflows. Nature Biotechnology, 35(4), 316-319.


## License

GNU General Public License V3

