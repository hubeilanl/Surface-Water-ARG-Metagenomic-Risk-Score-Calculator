#!/usr/bin/env python3
"""
Calculate the total ARG risk score for each metagenomic sample.

Usage:
    python calculate_sample_risk.py \
        --risk risk_scores.tsv \
        --abundance abundance_matrix.tsv \
        [--output output.tsv] \
        [--delimiter DELIM]
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Calculate the total ARG risk score for each sample."
    )
    parser.add_argument(
        "--risk",
        required=True,
        help=(
            "Risk-score file with a header. The first column contains ARG names "
            "and the second column contains risk scores."
        ),
    )
    parser.add_argument(
        "--abundance",
        required=True,
        help=(
            "ARG abundance matrix with a header. The first column contains ARG "
            "names and the remaining columns contain sample abundances."
        ),
    )
    parser.add_argument(
        "--output",
        help="Output file. Results are written to standard output if omitted.",
    )
    parser.add_argument(
        "--delimiter",
        default="\t",
        help="Field delimiter used in the input and output files (default: tab).",
    )
    args = parser.parse_args()

    delim = args.delimiter

    # Read the ARG risk-score file.
    risk_dict = {}
    try:
        with open(args.risk, "r") as f:
            f.readline()  # Skip the header row.
            for line_num, line in enumerate(f, start=2):
                line = line.rstrip("\n")
                if not line:  # Skip empty lines.
                    continue
                parts = line.split(delim)
                if len(parts) < 2:
                    sys.stderr.write(
                        f"Warning: line {line_num} of the risk-score file has "
                        f"too few columns and was skipped: {line}\n"
                    )
                    continue
                arg_name = parts[0].strip()
                try:
                    risk_score = float(parts[1].strip())
                except ValueError:
                    sys.stderr.write(
                        f"Warning: the risk score on line {line_num} is not "
                        f"numeric and was set to 0: {line}\n"
                    )
                    risk_score = 0.0
                risk_dict[arg_name] = risk_score
    except FileNotFoundError:
        sys.stderr.write(f"Error: risk-score file not found: {args.risk}\n")
        sys.exit(1)

    # Read the abundance matrix and calculate the total score for each sample.
    try:
        with open(args.abundance, "r") as f:
            # Read the header containing the sample names.
            header_line = f.readline().rstrip("\n")
            if not header_line:
                sys.stderr.write("Error: the abundance matrix is empty.\n")
                sys.exit(1)
            headers = header_line.split(delim)
            if len(headers) < 2:
                sys.stderr.write(
                    "Error: the abundance matrix must contain an ARG-name "
                    "column and at least one sample column.\n"
                )
                sys.exit(1)
            sample_names = headers[1:]  # First column: ARG name; others: samples.
            num_samples = len(sample_names)
            sample_scores = [0.0] * num_samples

            # Process the abundance matrix row by row.
            for line_num, line in enumerate(f, start=2):
                line = line.rstrip("\n")
                if not line:
                    continue
                parts = line.split(delim)
                if len(parts) < num_samples + 1:
                    sys.stderr.write(
                        f"Warning: line {line_num} of the abundance file has "
                        f"too few columns and was skipped: {line}\n"
                    )
                    continue
                arg_name = parts[0].strip()
                risk = risk_dict.get(arg_name, 0.0)

                # A zero risk score contributes zero to every sample total.
                if risk == 0.0:
                    continue

                # Add the abundance-weighted ARG risk score for each sample.
                for i in range(num_samples):
                    try:
                        abundance = float(parts[i + 1].strip())
                    except ValueError:
                        sys.stderr.write(
                            f"Warning: the abundance for sample "
                            f"{sample_names[i]} on line {line_num} is not "
                            "numeric and was treated as 0.\n"
                        )
                        abundance = 0.0
                    sample_scores[i] += abundance * risk

    except FileNotFoundError:
        sys.stderr.write(f"Error: abundance matrix not found: {args.abundance}\n")
        sys.exit(1)

    # Write the sample-level risk scores.
    out_fh = open(args.output, "w") if args.output else sys.stdout
    try:
        out_fh.write(f"Sample{delim}TotalRiskScore\n")
        for sample, score in zip(sample_names, sample_scores):
            out_fh.write(f"{sample}{delim}{score:.6f}\n")
    finally:
        if args.output:
            out_fh.close()


if __name__ == "__main__":
    main()
