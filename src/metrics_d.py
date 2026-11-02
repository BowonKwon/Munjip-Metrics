# -*- coding: utf-8 -*-
"""Series D — authors: dates, examination linkage, publication lag, translation and punctuation progress.

  python src/metrics_d.py [--derived data/derived]

Writes
  d_centuries.csv     per birth century: authors, birth/death completeness, lifespan median, munkwa link rate (M1/M2/M3), exam age median,
                      publication lag median, translation share (works), collections with no translated work, punctuation share
  d_authors.csv       authors.csv plus derived columns (lifespan, century, linked flag) for the site
  d_collections.csv   per collection: pub lag, translation share, punct share
"""
import argparse, sys
from pathlib import Path
import numpy as np
import pandas as pd


def century(y):
    return (int(y) - 1) // 100 + 1 if pd.notna(y) and str(y).strip().isdigit() else np.nan


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--derived", default="data/derived"); x = ap.parse_args()
    D = Path(x.derived)
    A = pd.read_csv(D / "authors.csv", dtype=str)
    C = pd.read_csv(D / "collections.csv", dtype=str).drop(columns=["n_works"]).set_index("collection_id")
    W = pd.read_csv(D / "works.csv", dtype={"is_author_work": "Int64"})
    A["century"] = A.birth.map(century).astype("Int64")   # from the string column, before the numeric cast
    for c in ("birth", "death", "exam_year", "exam_age"):
        A[c] = pd.to_numeric(A[c], errors="coerce")
    A["lifespan"] = A.death - A.birth
    A["linked"] = A.munkwa_rule.isin(["M1", "M1-first", "M2", "M3"]).astype(int)
    A["linked_strict"] = A.munkwa_rule.isin(["M1", "M1-first"]).astype(int)
    A.to_csv(D / "d_authors.csv", index=False, encoding="utf-8")
    cc = C.copy()
    cc["pub_year"] = pd.to_numeric(cc.pub_year, errors="coerce"); cc["death"] = pd.to_numeric(cc.death, errors="coerce")
    cc["pub_lag"] = cc.pub_year - cc.death
    tr = W.groupby("collection_id").agg(n_works=("work_id", "size"), n_translated=("has_translation", "sum"), n_punct=("has_punct", "sum"))
    cc = cc.join(tr)
    cc["translation_share"] = cc.n_translated / cc.n_works; cc["punct_share"] = cc.n_punct / cc.n_works
    cc["century"] = cc.birth.map(century).astype("Int64")
    cc[["title_ko", "author_ko", "birth", "death", "series", "pub_year", "pub_lag", "n_works", "n_translated", "translation_share", "n_punct", "punct_share", "century"]].to_csv(D / "d_collections.csv", encoding="utf-8")
    g = A.groupby("century").agg(n_authors=("author_id", "size"), birth_known=("birth", "count"), death_known=("death", "count"),
                                 lifespan_median=("lifespan", "median"), n_linked=("linked", "sum"), n_linked_strict=("linked_strict", "sum"),
                                 n_ambiguous=("munkwa_rule", lambda s: int((s == "AMB").sum())), exam_age_median=("exam_age", "median"),
                                 exam_age_p25=("exam_age", lambda s: s.quantile(.25)), exam_age_p75=("exam_age", lambda s: s.quantile(.75)))
    g["link_rate"] = g.n_linked / g.n_authors; g["link_rate_strict"] = g.n_linked_strict / g.n_authors
    h = cc.groupby("century").agg(n_collections=("title_ko", "size"), pub_year_known=("pub_year", "count"), pub_lag_median=("pub_lag", "median"),
                                  pub_lag_p25=("pub_lag", lambda s: s.quantile(.25)), pub_lag_p75=("pub_lag", lambda s: s.quantile(.75)),
                                  n_works=("n_works", "sum"), n_translated=("n_translated", "sum"), n_punct=("n_punct", "sum"),
                                  collections_no_translation=("n_translated", lambda s: int((s == 0).sum())), collections_full_translation=("translation_share", lambda s: int((s >= 0.999).sum())))
    h["translation_share"] = h.n_translated / h.n_works; h["punct_share"] = h.n_punct / h.n_works
    g = g.join(h)
    g.to_csv(D / "d_centuries.csv", encoding="utf-8")
    print(g[["n_authors", "lifespan_median", "n_linked", "link_rate", "exam_age_median", "pub_lag_median", "translation_share", "collections_no_translation"]].to_string())
    print(f"all: authors {len(A)} linked {A.linked.sum()} ({A.linked.mean():.1%}) strict {A.linked_strict.sum()} | collections no translation {int((cc.n_translated == 0).sum())}/{len(cc)}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
