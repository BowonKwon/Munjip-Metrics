# -*- coding: utf-8 -*-
"""Series B — genre composition (ITKC 문체분류 as given in the XML).

  python src/metrics_b.py [--derived data/derived]

Own works only (is_author_work = 1) for the headline shares; the all-works variant is written alongside.
Writes
  b_centuries.csv      (birth century) × genre1: works, chars, share_works, share_chars — own works
  b_centuries_all.csv  same over all works (appendix by other writers included)
  b_collections.csv    per collection: genre1 shares (works and chars), 其他類 share, poem length median
  b_genre2.csv         (birth century) × genre2 counts
  b_poems.csv          per century: median/mean chars of a 詩類 work
"""
import argparse, sys
from pathlib import Path
import numpy as np
import pandas as pd

GENRES = ["詩類", "書簡類", "序跋類", "傳記類", "公車類", "哀祭類", "雜著類"]


def century(y):
    return (int(y) - 1) // 100 + 1 if pd.notna(y) and str(y).strip().isdigit() else np.nan


def comp(df, keys):
    g = df.groupby(keys + ["genre1"]).agg(n_works=("work_id", "size"), chars=("chars", "sum")).reset_index()
    tot = g.groupby(keys).agg(total_works=("n_works", "sum"), total_chars=("chars", "sum"))
    g = g.join(tot, on=keys)
    g["share_works"] = g.n_works / g.total_works; g["share_chars"] = g.chars / g.total_chars
    return g


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--derived", default="data/derived"); x = ap.parse_args()
    D = Path(x.derived)
    W = pd.read_csv(D / "works.csv", dtype={"is_author_work": "Int64"})
    C = pd.read_csv(D / "collections.csv", dtype=str).set_index("collection_id")
    W["chars"] = W.chars_main + W.chars_note
    W["century"] = W.collection_id.map(C.birth).map(century).astype("Int64")
    W["series"] = W.collection_id.map(C.series)
    own = W[W.is_author_work == 1]
    comp(own, ["century"]).to_csv(D / "b_centuries.csv", index=False, encoding="utf-8")
    comp(W, ["century"]).to_csv(D / "b_centuries_all.csv", index=False, encoding="utf-8")
    comp(own, ["century", "series"]).to_csv(D / "b_centuries_series.csv", index=False, encoding="utf-8")
    g2 = own.groupby(["century", "genre1", "genre2"]).agg(n_works=("work_id", "size"), chars=("chars", "sum")).reset_index()
    g2.to_csv(D / "b_genre2.csv", index=False, encoding="utf-8")
    # per collection
    pc = comp(own, ["collection_id"])
    wide = pc.pivot(index="collection_id", columns="genre1", values="share_works").reindex(columns=GENRES).fillna(0)
    wide.columns = [f"share_works_{g}" for g in GENRES]
    widec = pc.pivot(index="collection_id", columns="genre1", values="share_chars").reindex(columns=GENRES).fillna(0)
    widec.columns = [f"share_chars_{g}" for g in GENRES]
    other = own.assign(is_other=(own.genre2.str.contains("其他", na=False)).astype(int)).groupby("collection_id").agg(n_own_works=("work_id", "size"), other_share=("is_other", "mean"))
    poems = own[own.genre1 == "詩類"].groupby("collection_id").agg(poem_chars_median=("chars_main", "median"), n_poems=("work_id", "size"))
    B = C[["title_ko", "author_ko", "birth", "series"]].join(other).join(wide).join(widec).join(poems)
    B["century"] = B.birth.map(century)
    B.to_csv(D / "b_collections.csv", encoding="utf-8")
    po = own[own.genre1 == "詩類"].groupby("century").agg(n_poems=("work_id", "size"), poem_chars_median=("chars_main", "median"), poem_chars_mean=("chars_main", "mean"),
                                                        poem_chars_p25=("chars_main", lambda s: s.quantile(.25)), poem_chars_p75=("chars_main", lambda s: s.quantile(.75)))
    po.to_csv(D / "b_poems.csv", encoding="utf-8")
    other_c = own.assign(is_other=(own.genre2.str.contains("其他", na=False)).astype(int)).groupby("century").agg(n=("work_id", "size"), other_share=("is_other", "mean"))
    other_c.to_csv(D / "b_other_share.csv", encoding="utf-8")
    cen = comp(own, ["century"])
    print(cen[cen.genre1 == "詩類"][["century", "n_works", "total_works", "share_works", "share_chars"]].to_string(index=False))
    print("other share by century:\n" + other_c.to_string())


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
