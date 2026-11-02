# -*- coding: utf-8 -*-
"""Draw the stratified samples for the reliability cards (stage 3) and write coder bundles.

  python src/export_coding_input.py [--derived data/derived] [--out data/coding] [--seed 20261103]

Bundles (pre-registered sizes)
  genre_sample.csv     300 own works, stratified by (genre1 × birth century), ≤ 6 per cell then filled at random:
                       coder judges whether the ITKC genre1 fits the title (and, where needed, the first 200 characters)
  letters_sample.csv   300 own letters with pattern_ok = 1 (parsed) + 60 with pattern_ok = 0 (unparsed, for recall):
                       coder writes the true addressee string from the title; precision = parsed == true
  epitaphs_sample.csv  200 own 碑誌·行狀 works: coder writes the true subject string
  munkwa_sample.csv    200 linked authors (precision: does the short introduction confirm the examination year / clan seat?)
                       + 100 unlinked authors with a birth year (recall: does the introduction mention a 문과 pass?)
Each coder bundle carries only ids, titles and (for munkwa) the introduction text — never the parsed answer,
which stays in the *_key.csv files kept out of the bundles.
"""
import argparse, csv, json, random, re, sys
from pathlib import Path
import pandas as pd


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--derived", default="data/derived"); ap.add_argument("--out", default="data/coding"); ap.add_argument("--seed", type=int, default=20261103)
    x = ap.parse_args(); rng = random.Random(x.seed)
    D = Path(x.derived); O = Path(x.out); O.mkdir(parents=True, exist_ok=True)
    W = pd.read_csv(D / "works.csv", dtype={"is_author_work": "Int64"})
    C = pd.read_csv(D / "collections.csv", dtype=str).set_index("collection_id")
    W["century"] = W.collection_id.map(C.birth).map(lambda y: (int(y) - 1) // 100 + 1 if isinstance(y, str) and y.isdigit() else -1)
    own = W[W.is_author_work == 1]
    # genre
    cells = own.groupby(["genre1", "century"])
    picked = []
    for key, g in cells:
        ids = list(g.work_id); rng.shuffle(ids); picked += ids[:6]
    rest = [i for i in own.work_id if i not in set(picked)]; rng.shuffle(rest)
    picked = (picked + rest)[:300]; rng.shuffle(picked)
    gs = own.set_index("work_id").loc[picked].reset_index()
    gs[["work_id", "collection_id", "title", "genre1", "genre2"]].assign(fits="", note="").to_csv(O / "genre_sample.csv", index=False, encoding="utf-8")
    # letters
    L = pd.read_csv(D / "letters.csv", dtype={"is_author_work": "Int64"}); Lo = L[L.is_author_work == 1]
    ok = list(Lo[Lo.pattern_ok == 1].work_id); no = list(Lo[Lo.pattern_ok == 0].work_id); rng.shuffle(ok); rng.shuffle(no)
    ls = Lo.set_index("work_id").loc[ok[:300] + no[:60]].reset_index()
    ls[["work_id", "collection_id", "title"]].assign(true_addressee="", note="").to_csv(O / "letters_sample.csv", index=False, encoding="utf-8")
    ls[["work_id", "recipient_raw", "pattern_ok"]].to_csv(O / "letters_key.csv", index=False, encoding="utf-8")
    # epitaphs
    E = pd.read_csv(D / "epitaphs.csv", dtype={"is_author_work": "Int64"}); Eo = E[E.is_author_work == 1]
    ids = list(Eo.work_id); rng.shuffle(ids)
    es = Eo.set_index("work_id").loc[ids[:200]].reset_index()
    es[["work_id", "collection_id", "genre2", "title"]].assign(true_subject="", note="").to_csv(O / "epitaphs_sample.csv", index=False, encoding="utf-8")
    es[["work_id", "subject_raw", "kind", "pattern_ok"]].to_csv(O / "epitaphs_key.csv", index=False, encoding="utf-8")
    # munkwa
    A = pd.read_csv(D / "d_authors.csv", dtype=str)
    H = {json.loads(l)["collection_id"]: json.loads(l)["haeje"] for l in open(D / "haeje_private.jsonl", encoding="utf-8")}
    A["haeje"] = A.collection_ids.str.split("|").str[0].map(H).fillna("")
    linked = A[A.linked == "1"]; unlinked = A[(A.linked != "1") & A.birth.notna() & (A.birth != "")]
    li = list(linked.index); ui = list(unlinked.index); rng.shuffle(li); rng.shuffle(ui)
    ms = pd.concat([linked.loc[li[:200]].assign(group="linked"), unlinked.loc[ui[:100]].assign(group="unlinked")])
    ms = ms.sample(frac=1, random_state=x.seed)
    ms[["author_id", "author_hj", "author_ko", "birth", "death", "group", "haeje"]].assign(haeje_says_pass="", haeje_exam_year="", haeje_bon="", note="").to_csv(O / "munkwa_sample.csv", index=False, encoding="utf-8")
    ms[["author_id", "munkwa_rule", "exam_year", "munkwa_bon", "exam_name"]].to_csv(O / "munkwa_key.csv", index=False, encoding="utf-8")
    print(f"genre {len(gs)} | letters {len(ls)} (parsed {int(ls.pattern_ok.sum())}) | epitaphs {len(es)} | munkwa {len(ms)} (linked {int((ms.group == 'linked').sum())})")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
