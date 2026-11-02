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
    ap = argparse.ArgumentParser(); ap.add_argument("--coding", default="data/coding"); ap.add_argument("--derived", default="data/derived")
    ap.add_argument("--munkwa", default="data/raw/aks/aks-2020-joseon-munkwa-geupjeja.xml"); x = ap.parse_args()
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
    if (C / "genre_recode_coded.csv").exists() and (C / "genre_coded.csv").exists():
        a = pd.read_csv(C / "genre_coded.csv", dtype=str).set_index("work_id"); b = pd.read_csv(C / "genre_recode_coded.csv", dtype=str).set_index("work_id")
        same = int(sum(a.loc[i, "fits"].strip().lower() == b.loc[i, "fits"].strip().lower() for i in b.index))
        out["genre_recode"] = dict(n=int(len(b)), same=same, agreement=same / len(b))
    # D2 stand-in: courtesy/pen-name agreement between the ITKC bibliographic record and the roster row linked (see codebook §4 note)
    if (D / "d_authors.csv").exists() and x.munkwa and Path(x.munkwa).exists():
        import re, xml.etree.ElementTree as ET
        hj = lambda s: (re.search(r"\(([^)]+)\)", s or "") or [None, ""])[1].strip() if re.search(r"\(([^)]+)\)", s or "") else ""
        mk = {}
        for e in ET.parse(x.munkwa).getroot().iter("급제자"):
            if e.find("ID") is not None:
                mk[(e.findtext("ID") or "").strip()] = (hj(e.findtext("자")), hj(e.findtext("호")))
        A = pd.read_csv(D / "d_authors.csv", dtype=str); L = A[A.linked == "1"]
        agree = dis = 0
        for _, r in L.iterrows():
            ja = set(filter(None, str(r.author_ja if pd.notna(r.author_ja) else "").split("|"))); ho = set(filter(None, str(r.author_ho if pd.notna(r.author_ho) else "").split("|")))
            mja, mho = mk.get(r.munkwa_id, ("", ""))
            if (ja and mja) or (ho and mho):
                if (mja and mja in ja) or (mho and mho in ho):
                    agree += 1
                else:
                    dis += 1
        out["munkwa_jaho"] = dict(n=agree + dis, agree=agree, rate=(agree / (agree + dis) if agree + dis else None))
    if (D / "works.csv").exists():
        w = pd.read_csv(D / "works.csv", dtype=str, usecols=["collection_id", "genre2"])
        n_blk = int(((w.collection_id == "ITKC_MO_0126A") & (w.genre2 == "冊文類")).sum())
        out["genre_block_note"] = dict(collection_id="ITKC_MO_0126A", title_ko="호음잡고", n_works=n_blk)
    (D / "reliability.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
