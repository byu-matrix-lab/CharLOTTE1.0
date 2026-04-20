import difflib
import argparse

def calc_diff(file1, file2):
    print(f"Getting diff between:\n\t-`{file1}`\n\t-`{file2}`\n\n")
    with open(file1) as f1, open(file2) as f2:
        diff = difflib.unified_diff(
            f1.readlines(),
            f2.readlines(),
            fromfile=file1,
            tofile=file2
        )
        for line in diff:
            print(line)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file1", "-f1")
    parser.add_argument("--file2", "-f2")
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    calc_diff(args.file1, args.file2)
