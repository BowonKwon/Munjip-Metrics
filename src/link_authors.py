# -*- coding: utf-8 -*-
"""Author table: one row per author (collections merged), linked to the AKS 문과급제자 and 역대인명 XML.

  python src/link_authors.py --derived data/derived --munkwa data/raw/aks/aks-2020-joseon-munkwa-geupjeja.xml \
                             --persons data/raw/aks/aks-2020-korean-historical-persons.xml

Pre-registered linkage rules (applied in order; the first that fires is recorded in munkwa_rule)
  M1  same 한자성명 and same 생년 (방목 생년 present)                               → match
  M2  same 한자성명, 방목 생년 absent/미상, and 자 or 호 identical                   → match
  M3  same 한자성명, exactly one candidate, 방목 생년 absent, 시험년 within [birth+15, death] (death absent: birth+70) → weak match
  AMB more than one candidate survives M1–M3                                        → ambiguous (not linked)
  none                                                                             → not linked (includes non-passers)
Persons: P1 same 한자성명 and same 생년; P2 same 한자성명, 호 identical; else none. Birth/death agreement is reported.
author_id = 한자성명 + '_' + 생년 (birth missing: '_x'). Collections of the same author_id are merged; n_collections kept.
"""
import argparse, csv, re, sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")


def hanja(s):
    m = re.search(r"\(([^)]+)\)", s or "")
    return m.group(1).strip() if m else ""


def load_munkwa(p):
    rows = []
    for e in ET.parse(p).getroot().iter("급제자"):
        if e.find("ID") is None:
            continue
        t = lambda k: (e.findtext(k) or "").strip()
        by = t("생년"); by = by if by.isdigit() else ""
        rows.append(dict(id=t("ID"), nm=hanja(t("급제자")), nm_ko=re.sub(r"\(.*", "", t("급제자")), by=by, yr=t("시험년"), bon=t("본관"),
                         ho=hanja(t("호")), ja=hanja(t("자")), grade=t("등급"), rank=t("등위"), exam=t("시험명"), king=t("왕대")))
    return rows


def load_persons(p):
    rows = []
    for e in ET.parse(p).getroot().iter("인물"):
        t = lambda k: (e.findtext(k) or "").strip()
        rows.append(dict(nm=hanja(t("TITLENAME")), by=t("LIVE_YEAR"), dy=t("DIE_YEAR"), ho=hanja(t("HO")), ja=hanja(t("JA")), bon=t("ORIGINNAME")))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--derived", default="data/derived"); ap.add_argument("--munkwa", required=True); ap.add_argument("--persons", required=True)
    x = ap.parse_args()
    d = Path(x.derived)
    colls = list(csv.DictReader(open(d / "collections.csv", encoding="utf-8")))
    works = list(csv.DictReader(open(d / "works.csv", encoding="utf-8")))
    mk = load_munkwa(x.munkwa); pr = load_persons(x.persons)
    mk_idx = defaultdict(list); [mk_idx[r["nm"]].append(r) for r in mk]
    pr_idx = defaultdict(list); [pr_idx[r["nm"]].append(r) for r in pr]
    per_coll = defaultdict(lambda: dict(n=0, own=0, main=0, note=0))
    for w in works:
        c = per_coll[w["collection_id"]]; c["n"] += 1; c["own"] += int(w["is_author_work"] or 0)
        c["main"] += int(w["chars_main"]); c["note"] += int(w["chars_note"])
    authors = {}
    for c in colls:
        aid = f"{c['author_hj']}_{c['birth'] or 'x'}"
        a = authors.setdefault(aid, dict(author_id=aid, author_hj=c["author_hj"], author_ko=c["author_ko"], author_ja=c["author_ja"], author_ho=c["author_ho"],
                                         author_si=c["author_si"], birth=c["birth"], death=c["death"], n_collections=0, collection_ids=[], series=set(),
                                         n_works=0, n_own_works=0, chars_main=0, chars_note=0, pub_years=[]))
        a["n_collections"] += 1; a["collection_ids"].append(c["collection_id"]); a["series"].add(c["series"])
        pc = per_coll[c["collection_id"]]; a["n_works"] += pc["n"]; a["n_own_works"] += pc["own"]; a["chars_main"] += pc["main"]; a["chars_note"] += pc["note"]
        if c["pub_year"]:
            a["pub_years"].append(c["pub_year"])
    stats = defaultdict(int)
    for a in authors.values():
        nm, by, dy = a["author_hj"], a["birth"], a["death"]
        ja = set(filter(None, a["author_ja"].split("|"))); ho = set(filter(None, a["author_ho"].split("|")))
        cands = mk_idx.get(nm, [])
        rule, hit = "none", None
        m1 = [r for r in cands if by and r["by"] == by]
        if len(m1) > 1 and len({r["bon"] for r in m1}) == 1:
            # one person listed for several examinations (문과 then 重試·拔英試 …): keep the earliest pass
            m1 = sorted(m1, key=lambda r: int(r["yr"]) if r["yr"].isdigit() else 9999)[:1]
            rule_note = "M1-first"
        if len(m1) == 1:
            rule, hit = (locals().get("rule_note") or "M1"), m1[0]
        elif len(m1) > 1:
            rule = "AMB"
        else:
            m2 = [r for r in cands if not r["by"] and ((r["ja"] and r["ja"] in ja) or (r["ho"] and r["ho"] in ho))]
            if len(m2) == 1:
                rule, hit = "M2", m2[0]
            elif len(m2) > 1:
                rule = "AMB"
            elif by:
                lo, hi = int(by) + 15, (int(dy) if dy.isdigit() else int(by) + 70)
                m3 = [r for r in cands if not r["by"] and r["yr"].isdigit() and lo <= int(r["yr"]) <= hi]
                if len(m3) == 1 and len(cands) == 1:
                    rule, hit = "M3", m3[0]
                elif len(m3) > 1:
                    rule = "AMB"
        a["munkwa_rule"] = rule; a["munkwa_candidates"] = len(cands)
        a["munkwa_id"] = hit["id"] if hit else ""; a["exam_year"] = hit["yr"] if hit else ""; a["exam_name"] = hit["exam"] if hit else ""
        a["munkwa_bon"] = hit["bon"] if hit else ""; a["munkwa_grade"] = hit["grade"] if hit else ""; a["munkwa_birth"] = hit["by"] if hit else ""
        a["exam_age"] = (int(hit["yr"]) - int(by) + 1) if hit and by and hit["yr"].isdigit() else ""  # 세는나이
        stats["munkwa_" + rule] += 1
        pc = pr_idx.get(nm, [])
        p1 = [r for r in pc if by and r["by"] == by]
        p2 = [r for r in pc if r["ho"] and r["ho"] in ho] if not p1 else []
        prule, ph = ("P1", p1[0]) if len(p1) == 1 else (("P2", p2[0]) if len(p2) == 1 else (("AMB", None) if len(p1) > 1 or len(p2) > 1 else ("none", None)))
        a["persons_rule"] = prule; a["persons_birth"] = ph["by"] if ph else ""; a["persons_death"] = ph["dy"] if ph else ""; a["persons_bon"] = ph["bon"] if ph else ""
        a["death_agrees"] = (int(ph["dy"] == dy) if ph and dy and ph["dy"].isdigit() else "")
        stats["persons_" + prule] += 1
        a["collection_ids"] = "|".join(a["collection_ids"]); a["series"] = "|".join(sorted(a["series"])); a["pub_years"] = "|".join(a["pub_years"])
        a["birth_century"] = (int(by) - 1) // 100 + 1 if by.isdigit() else ""
    rows = sorted(authors.values(), key=lambda r: (r["birth"] or "9999", r["author_hj"]))
    with open(d / "authors.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(f"authors {len(rows)} from collections {len(colls)} | " + " ".join(f"{k}={v}" for k, v in sorted(stats.items())))


if __name__ == "__main__":
    main()
