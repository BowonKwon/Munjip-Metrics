# -*- coding: utf-8 -*-
"""Collect the coded samples into data/derived/reliability.json (precision, Wilson 95% interval, recall where measured).

  python src/reliability.py [--coding data/coding] [--derived data/derived]

Expected coded files (coders fill the sample files and save them as *_coded.csv):
  genre_coded.csv     fits ∈ {yes, no, undecided}                      → key "genre": agreement = yes / n (undecided = no)
  letters_coded.csv   true_addressee (blank = no addressee in title)    → key "recipients": precision over parsed rows = parsed == true;
                                                                          recall over all rows = (parsed == true and true non-blank) / (true non-blank)
  epitaphs_coded.csv  true_subject                                      → key "epitaphs": same as letters
  munkwa_coded.csv    haeje_says_pass ∈ {yes, no, unclear}, haeje_exam_year → key "munkwa": precision over linked = exam_year agrees (±0) with haeje
                                                                          (haeje lacking a year: yes counts as agree); recall over unlinked = 1 − (haeje says yes)/n
"""
import argparse, json, math, sys
from pathlib import Path
import pandas as pd


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n; den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


def rec(k, n, extra=None):
    lo, hi = wilson(k, n)
    r = dict(n=int(n), yes=int(k), precision=(k / n if n else None), ci_lo=lo, ci_hi=hi)
    if extra:
        r.update(extra)
    return r


def norm(s):
    return "" if pd.isna(s) else str(s).strip().replace(" ", "")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--coding", default="data/coding"); ap.add_argument("--derived", default="data/derived"); x = ap.parse_args()
    C = Path(x.coding); D = Path(x.derived); out = {}
    if (C / "genre_coded.csv").exists():
        g = pd.read_csv(C / "genre_coded.csv", dtype=str); v = g.fits.str.strip().str.lower()
        out["genre"] = rec(int((v == "yes").sum()), len(g), dict(undecided=int((v == "undecided").sum())))
    for name, key, ans in (("letters", "recipients", "true_addressee"), ("epitaphs", "epitaphs", "true_subject")):
        if (C / f"{name}_coded.csv").exists():
            c = pd.read_csv(C / f"{name}_coded.csv", dtype=str); k = pd.read_csv(C / f"{name}_key.csv", dtype=str)
            m = c.merge(k, on="work_id"); parsed_col = "recipient_raw" if name == "letters" else "subject_raw"
            m["true"] = m[ans].map(norm); m["parsed"] = m[parsed_col].map(norm)
            P = m[m.pattern_ok == "1"]; prec_k = int((P.true == P.parsed).sum())
            has = m[m.true != ""]; rec_k = int((has.parsed == has.true).sum())
            out[key] = rec(prec_k, len(P), dict(recall=(rec_k / len(has) if len(has) else None), recall_n=int(len(has))))
    if (C / "munkwa_coded.csv").exists():
        c = pd.read_csv(C / "munkwa_coded.csv", dtype=str); k = pd.read_csv(C / "munkwa_key.csv", dtype=str); m = c.merge(k, on="author_id")
        L = m[m.group == "linked"]; U = m[m.group == "unlinked"]
        says = L.haeje_says_pass.str.strip().str.lower()
        agree = ((says == "yes") & ((L.haeje_exam_year.map(norm) == "") | (L.haeje_exam_year.map(norm) == L.exam_year.map(norm)))).sum()
        unclear = int((says == "unclear").sum())
        miss = int((U.haeje_says_pass.str.strip().str.lower() == "yes").sum())
        out["munkwa"] = rec(int(agree), len(L) - unclear, dict(unclear=unclear, recall=(1 - miss / len(U)) if len(U) else None, recall_n=int(len(U)), missed=miss))
    (D / "reliability.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
