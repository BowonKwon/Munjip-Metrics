# -*- coding: utf-8 -*-
"""Series C — relationship genres counted at the string level (no person identification in 1.0).

  python src/metrics_c.py [--derived data/derived]

Writes
  c_letters.csv         per collection (own letters): letters, parsed, unique recipient strings, top-1/top-3 share, HHI
  c_recipients.csv      per collection the ten most frequent recipient strings
  c_epitaphs.csv        per collection (own works): 碑誌·行狀 works, parsed, unique subject strings, by kind
  c_writers.csv         per collection: works by other writers, unique other writers, the five most frequent
  c_centuries.csv       per century: the same aggregates
"""
import argparse, sys
from pathlib import Path
import numpy as np
import pandas as pd


def century(y):
    return (int(y) - 1) // 100 + 1 if pd.notna(y) and str(y).strip().isdigit() else np.nan


def conc(s):
    """Top-1 share, top-3 share and Herfindahl index of a series of strings (blank excluded)."""
    s = s[s.notna() & (s != "")]
    if len(s) == 0:
        return pd.Series(dict(n_named=0, n_unique=0, top1_share=np.nan, top3_share=np.nan, hhi=np.nan))
    vc = s.value_counts(); p = vc / vc.sum()
    return pd.Series(dict(n_named=int(vc.sum()), n_unique=int(len(vc)), top1_share=float(p.iloc[0]), top3_share=float(p.iloc[:3].sum()), hhi=float((p ** 2).sum())))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--derived", default="data/derived"); x = ap.parse_args()
    D = Path(x.derived)
    C = pd.read_csv(D / "collections.csv", dtype=str).set_index("collection_id")
    L = pd.read_csv(D / "letters.csv", dtype={"is_author_work": "Int64"})
    E = pd.read_csv(D / "epitaphs.csv", dtype={"is_author_work": "Int64"})
    W = pd.read_csv(D / "works.csv", dtype={"is_author_work": "Int64"})
    for df in (L, E, W):
        df["century"] = df.collection_id.map(C.birth).map(century).astype("Int64")
    Lo = L[L.is_author_work == 1]
    cl = Lo.groupby("collection_id").agg(n_letters=("work_id", "size"), n_parsed=("pattern_ok", "sum"))
    cl = cl.join(Lo.groupby("collection_id").recipient_raw.apply(conc).unstack())
    cl["parse_rate"] = cl.n_parsed / cl.n_letters
    cl = C[["title_ko", "author_ko", "birth", "series"]].join(cl, how="inner")
    cl.to_csv(D / "c_letters.csv", encoding="utf-8")
    top = (Lo[Lo.recipient_raw.notna() & (Lo.recipient_raw != "")].groupby(["collection_id", "recipient_raw"]).size().rename("n").reset_index()
           .sort_values(["collection_id", "n"], ascending=[True, False]).groupby("collection_id").head(10))
    top.to_csv(D / "c_recipients.csv", index=False, encoding="utf-8")
    Eo = E[E.is_author_work == 1]
    ce = Eo.groupby("collection_id").agg(n_epitaphs=("work_id", "size"), n_parsed=("pattern_ok", "sum"))
    ce = ce.join(Eo.groupby("collection_id").subject_raw.apply(conc).unstack().add_prefix("subj_"))
    kinds = Eo.pivot_table(index="collection_id", columns="genre2", values="work_id", aggfunc="size", fill_value=0)
    ce = C[["title_ko", "author_ko", "birth", "series"]].join(ce, how="inner").join(kinds)
    ce.to_csv(D / "c_epitaphs.csv", encoding="utf-8")
    Wo = W[W.is_author_work == 0]
    cw = Wo.groupby("collection_id").agg(n_other_works=("work_id", "size"), n_other_writers=("writer_hj", "nunique"))
    cw["top_writers"] = Wo.groupby("collection_id").writer_hj.apply(lambda s: "|".join(f"{k}:{v}" for k, v in s.value_counts().head(5).items()))
    cw = C[["title_ko", "author_ko", "birth", "series"]].join(cw, how="inner")
    cw.to_csv(D / "c_writers.csv", encoding="utf-8")
    cc = Lo.groupby("century").agg(n_letters=("work_id", "size"), n_parsed=("pattern_ok", "sum")).join(Lo.groupby("century").recipient_raw.apply(conc).unstack())
    cc = cc.join(Eo.groupby("century").agg(n_epitaphs=("work_id", "size"), n_epitaphs_parsed=("pattern_ok", "sum")))
    cc = cc.join(Wo.groupby("century").agg(n_other_works=("work_id", "size"), n_other_writers=("writer_hj", "nunique")))
    cc.to_csv(D / "c_centuries.csv", encoding="utf-8")
    print(cc.to_string())


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
