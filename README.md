# Surface-Water-ARG-Metagenomic-Risk-Score-Calculator
This tool is designed to calculate the total risk score of antibiotic resistance genes (ARGs) in surface water metagenomic samples, using ARG abundance data and a precomputed risk score map.

For each sample:
Sample total risk score = Σ (ARG abundance × ARG risk score)

# Background
Risk score file: Risk_score_map.txt is a pre‑generated risk score map whose scores were derived from an ecological risk assessment model specifically calibrated for surface water environments. Therefore, these scores are environment‑specific and may not be directly applicable to other environments (e.g., soil, sediment, human gut). 

Abundance matrix: The tool is designed to work with the output format of ARGs_OAP v3.2.4. The abundance values produced by ARGs_OAP are in copies per cell. If you use other software or different abundance units (e.g., RPKM, TPM, relative abundance), make sure all samples share the same unit; otherwise, comparisons of total risk scores across samples will not be valid.

# Requirements
Python 3.6 or higher
No external libraries required (only the Python standard library)

# Usage
```
python calculate_sample_risk.py --risk RISK_FILE --abundance ABUNDANCE_FILE [--output OUTPUT_FILE] [--delimiter DELIMITER]
```

# Arguments
|Argument|Short|Required|Description|
| ------------- | ------------- |------------- | ------------- |
|--risk|-r|Yes|Path to the risk score file (format described below)|
|--abundance|-a|Yes|Path to the ARG abundance matrix file (format described below)|
|--output|-o|No|Output file path. If not provided, results are printed to standard output|
|--delimiter|-d|No|Field delimiter used in all files (default: tab \t). Can be set to e.g. , for CSV|

# Input File Formats
# Risk Score File (Risk_score_map.txt)
Tab‑separated (or using the delimiter specified by --delimiter).
First column: ARG name (must match exactly with the names in the abundance matrix, including case).
Second column: risk score (floating point number).
# ARG Abundance Matrix
Tab‑separated (or using the delimiter specified by --delimiter).
First row contains sample names: The first column is a fixed label (e.g., ARG_name), and the remaining columns are sample identifiers.
First column contains ARG names, the subsequent columns contain the abundance of that ARG in each sample (numeric values, expected unit: copies per cell).
Example:
```
ARG_name	Sample1	Sample2	Sample3
ARG1	10	20	30
ARG2	5	15	25
ARG4	100	200	300
```
# Output Format
Two columns: sample name and total risk score.
The delimiter is the same as the input files (default tab).
Risk scores are printed with six decimal places.
Example:
```
Sample	TotalRiskScore
Sample1	11.0
Sample2	28.0
Sample3	45.0
```
# Examples
```
# Basic usage
python calculate_sample_risk.py \
    --risk Risk_score_map.txt \
    --abundance abundance_matrix.tsv \
    --output sample_risk_scores.tsv

# Using comma‑separated files
python calculate_sample_risk.py \
    -r Risk_score_map.csv \
    -a abundance_matrix.csv \
    -d ',' \
    -o sample_risk.csv
```

# Citation
If you use this tool and the associated risk score file in your research, please cite:

