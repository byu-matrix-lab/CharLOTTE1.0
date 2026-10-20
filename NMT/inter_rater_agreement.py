import csv
from statsmodels.stats.inter_rater import fleiss_kappa, aggregate_raters
import argparse


def calc_fleiss_kappa(csv_file):
    with open(csv_file, newline="") as f:
        data = [[int(x) if x.strip().lstrip('-').isdigit() else x for x in row]
                for row in csv.reader(f)]

    table, categories = aggregate_raters(data)
    print(categories)
    print(table)
    kappa = fleiss_kappa(table, method='fleiss')
    print(kappa)

def get_args():
    parser = argparse.ArgumentParser(description="Calculate Fleiss' Kappa")
    parser.add_argument("--csv_file", "-f")

    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    calc_fleiss_kappa(args.csv_file)

