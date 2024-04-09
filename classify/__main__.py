# SPDX-FileCopyrightText: 2024 Sascha Brawer <sascha@brawer.ch>
# SPDX-License-Identifier: MIT

import argparse
import zipfile

from .classify import classify


def read_zip(path):
    with zipfile.ZipFile(args.corpus) as zf:
        for name in sorted(zf.namelist()):
            if "__MACOS" in name or not name.endswith(".png"):
                continue
            parts = name.split("/")
            with zf.open(name, mode="r") as f:
                png = zf.read(name)
            yield parts[-2], parts[-1], png


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="classify",
        description="Classify corpus images, report precision and recall",
    )
    parser.add_argument("corpus")
    args = parser.parse_args()
    num, true_positive, false_positive = {}, {}, {}
    for cat, name, png in read_zip(args.corpus):
        num[cat] = num.get(cat, 0) + 1
        got = classify(png) or "other"
        if got == cat:
            true_positive[got] = true_positive.get(got, 0) + 1
        else:
            false_positive[got] = false_positive.get(got, 0) + 1
    print("Symbol Class          Precision Recall")
    print("--------------------------------------")
    for cat in sorted(num.keys()):
        # For some classes, we have too few test cases to tell anything.
        if num[cat] < 50:
            continue
        true_pos = true_positive.get(cat, 0)
        false_pos = false_positive.get(cat, 0)
        n = true_pos + false_pos
        precision = float(true_pos / n if n > 0 else 0)
        recall = true_pos / num[cat]
        prec = f"{precision * 100:.1f}"
        rec = f"{recall * 100:.1f}"
        print("%-25s %5s  %5s" % (cat, prec, rec))
