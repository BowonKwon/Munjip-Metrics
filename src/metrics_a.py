# -*- coding: utf-8 -*-
"""Series A — size of the corpus.

  python src/metrics_a.py [--derived data/derived]

Reads works.csv, collections.csv, authors.csv; writes
  a_collections.csv   one row per collection: works, own works, characters (main/note), note share, volumes, century
  a_centuries.csv     one row per (author birth century, series): collections, authors, works, characters, per-work medians
  a_gwon_check.csv    collections where the 卷n headings in the table of contents can be compared with the 해제 「n권」
Definitions live in registry.py; this file only computes.
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
    W = pd.read_csv(D / "works.csv", dtype={"is_author_work": "Int64"})
    C = pd.read_csv(D / "collections.csv", dtype=str).drop(columns=["n_works"])
    W["chars"] = W.chars_main + W.chars_note
    W["own"] = W.is_author_work.fillna(0).astype(int)
    g = W.groupby("collection_id").agg(n_works=("work_id", "size"), n_own_works=("own", "sum"),
                                        chars_main=("chars_main", "sum"), chars_note=("chars_note", "sum"),
                                        chars_per_work_median=("chars", "median"), chars_per_work_mean=("chars", "mean"),
                                        n_volumes=("volume_id", "nunique"), n_translated=("has_translation", "sum"), n_punct=("has_punct", "sum"))
    A = C.set_index("collection_id").join(g)
    A["chars"] = A.chars_main + A.chars_note
    A["note_share"] = A.chars_note / A.chars
    A["own_share"] = A.n_own_works / A.n_works
    A["birth_century"] = A.birth.map(century).astype("Int64")
    A["n_gwon_titles"] = pd.to_numeric(A.n_gwon_titles)
    A["works_per_gwon"] = A.n_works / A.n_gwon_titles.replace(0, np.nan)
    cols = ["title_ko", "title_hj", "author_ko", "author_hj", "birth", "death", "birth_century", "series", "jip_start", "jip_end", "jip_count", "pub_year",
            "n_works", "n_own_works", "own_share", "chars_main", "chars_note", "chars", "note_share", "chars_per_work_median", "chars_per_work_mean",
            "n_volumes", "n_gwon_titles", "works_per_gwon", "haeje_gwon", "haeje_chaek", "n_translated", "n_punct"]
    A[cols].sort_values(["birth", "collection_id"]).to_csv(D / "a_collections.csv", encoding="utf-8")

    A["jip_count"] = pd.to_numeric(A.jip_count, errors="coerce")
    A["author_id"] = A.author_hj + "_" + A.birth.fillna("x")
    cen = A.groupby(["birth_century", "series"], dropna=False).agg(
        n_collections=("title_ko", "size"), n_authors=("author_id", "nunique"), n_works=("n_works", "sum"), n_own_works=("n_own_works", "sum"),
        chars_main=("chars_main", "sum"), chars_note=("chars_note", "sum"), jip_count=("jip_count", "sum"))
    cen["chars"] = cen.chars_main + cen.chars_note
    cen["note_share"] = cen.chars_note / cen.chars
    cen["own_share"] = cen.n_own_works / cen.n_works
    # per-work medians need the work rows
    W = W.merge(A[["birth_century", "series"]], left_on="collection_id", right_index=True, how="left")
    med = W.groupby(["birth_century", "series"], dropna=False).agg(chars_per_work_median=("chars", "median"), chars_per_work_mean=("chars", "mean"))
    cen = cen.join(med)
    tot = A.groupby("birth_century", dropna=False).agg(n_collections=("title_ko", "size"), n_authors=("author_id", "nunique"), n_works=("n_works", "sum"), n_own_works=("n_own_works", "sum"),
                                                        chars_main=("chars_main", "sum"), chars_note=("chars_note", "sum"), jip_count=("jip_count", "sum"))
    tot["series"] = "전체"; tot = tot.reset_index().set_index(["birth_century", "series"])
    tot["chars"] = tot.chars_main + tot.chars_note; tot["note_share"] = tot.chars_note / tot.chars; tot["own_share"] = tot.n_own_works / tot.n_works
    medt = W.groupby("birth_century", dropna=False).agg(chars_per_work_median=("chars", "median"), chars_per_work_mean=("chars", "mean"))
    medt["series"] = "전체"; medt = medt.reset_index().set_index(["birth_century", "series"])
    tot = tot.join(medt)
    cen = pd.concat([cen, tot]).sort_index()
    cen.to_csv(D / "a_centuries.csv", encoding="utf-8")

    chk = A[A.haeje_gwon.notna() & (A.haeje_gwon != "")][["title_ko", "n_gwon_titles", "n_volumes", "haeje_gwon", "haeje_chaek"]].copy()
    chk["haeje_gwon"] = pd.to_numeric(chk.haeje_gwon, errors="coerce")
    chk["match"] = (chk.n_gwon_titles == chk.haeje_gwon).astype(int)
    chk.to_csv(D / "a_gwon_check.csv", encoding="utf-8")
    print(f"collections {len(A):,} works {A.n_works.sum():,} own {A.n_own_works.sum():,} chars {A.chars.sum():,} (note {A.note_share.mean():.1%} mean share)")
    print(cen[["n_collections", "n_authors", "n_works", "chars", "chars_per_work_median"]].to_string())
    print(f"gwon check: {chk.match.sum()}/{len(chk)} match the 해제 (first-number rule)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
