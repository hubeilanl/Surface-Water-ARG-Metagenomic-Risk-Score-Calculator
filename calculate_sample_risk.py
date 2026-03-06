#!/usr/bin/env python3
"""
calculate_sample_risk.py



用法：
    python calculate_sample_risk.py --risk risk_scores.tsv --abundance abundance_matrix.tsv [--output output.tsv] [--delimiter DELIM]
"""

import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description='计算每个样本的ARG总风险得分')
    parser.add_argument('--risk', required=True, help='风险得分文件（制表符分隔，有表头，第一列ARG名称，第二列风险得分）')
    parser.add_argument('--abundance', required=True, help='丰度矩阵文件（制表符分隔，第一列ARG名称，第一行样本名）')
    parser.add_argument('--output', help='输出文件（默认输出到标准输出）')
    parser.add_argument('--delimiter', default='\t', help='文件分隔符（默认为制表符）')
    args = parser.parse_args()

    delim = args.delimiter

    # ---------- 读取风险得分文件 ----------
    risk_dict = {}
    try:
        with open(args.risk, 'r') as f:
            header = f.readline()  # 跳过表头
            for line_num, line in enumerate(f, start=2):
                line = line.rstrip('\n')
                if not line:  # 跳过空行
                    continue
                parts = line.split(delim)
                if len(parts) < 2:
                    sys.stderr.write(f"警告：风险文件第{line_num}行列数不足，已忽略：{line}\n")
                    continue
                arg_name = parts[0].strip()
                try:
                    risk_score = float(parts[1].strip())
                except ValueError:
                    sys.stderr.write(f"警告：风险文件第{line_num}行风险得分不是数值，已设为0：{line}\n")
                    risk_score = 0.0
                risk_dict[arg_name] = risk_score
    except FileNotFoundError:
        sys.stderr.write(f"错误：风险文件 {args.risk} 不存在\n")
        sys.exit(1)

    # ---------- 读取丰度矩阵，计算每个样本的总分 ----------
    try:
        with open(args.abundance, 'r') as f:
            # 读取样本名称行
            header_line = f.readline().rstrip('\n')
            if not header_line:
                sys.stderr.write("错误：丰度矩阵文件为空\n")
                sys.exit(1)
            headers = header_line.split(delim)
            if len(headers) < 2:
                sys.stderr.write("错误：丰度矩阵至少需要一列ARG名称和一列样本数据\n")
                sys.exit(1)
            sample_names = headers[1:]  # 第一列是ARG名称，其余是样本名
            num_samples = len(sample_names)
            sample_scores = [0.0] * num_samples

            # 逐行处理丰度数据
            for line_num, line in enumerate(f, start=2):
                line = line.rstrip('\n')
                if not line:
                    continue
                parts = line.split(delim)
                if len(parts) < num_samples + 1:  # 至少要有ARG名称和所有样本的列
                    sys.stderr.write(f"警告：丰度文件第{line_num}行列数不足，已忽略：{line}\n")
                    continue
                arg_name = parts[0].strip()
                risk = risk_dict.get(arg_name, 0.0)  # 如果不存在风险得分，默认为0

                # 如果风险得分为0，可以跳过该ARG以节省计算（但为了完整性，我们仍累加0）
                # 但即使风险为0，乘以丰度还是0，所以可以跳过
                if risk == 0.0:
                    continue

                # 遍历每个样本的丰度
                for i in range(num_samples):
                    try:
                        abundance = float(parts[i+1].strip())
                    except ValueError:
                        sys.stderr.write(f"警告：丰度文件第{line_num}行，样本{sample_names[i]}丰度不是数值，视为0\n")
                        abundance = 0.0
                    sample_scores[i] += abundance * risk

    except FileNotFoundError:
        sys.stderr.write(f"错误：丰度矩阵文件 {args.abundance} 不存在\n")
        sys.exit(1)

    # ---------- 输出结果 ----------
    out_fh = open(args.output, 'w') if args.output else sys.stdout
    try:
        out_fh.write(f"Sample{delim}TotalRiskScore\n")
        for sample, score in zip(sample_names, sample_scores):
            out_fh.write(f"{sample}{delim}{score:.6f}\n")
    finally:
        if args.output:
            out_fh.close()

if __name__ == '__main__':
    main()
