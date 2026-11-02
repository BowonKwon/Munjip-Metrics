# -*- coding: utf-8 -*-
"""Recount characters straight from the raw XML and compare with works.csv; other integrity checks.

  python src/check_works.py --src data/raw/itkc [--src more] --derived data/derived

Checks
  1. per collection: CJK count over every <내용>…</내용> in the 권차 files (regex on the raw string after entity
     decoding, tags stripped) == sum(chars_main + chars_note) in works.csv. Any difference is listed.
  2. residual '&#' after decoding (double-escaped characters), per zip.
  3. work_id uniqueness; collection_id uniqueness; works without 문체분류; 서지 files without author/birth.
  4. zip inventory: every zip in --src has a collections.csv row.
Exit code 1 on any failure of 1–3.
"""
import argparse, csv, glob, html, re, sys, zipfile
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HAN = re.compile(r"[㐀-䶿一-鿿豈-﫿\U00020000-\U0003134f]")
TAG = re.compile(r"<[^>]+>")


def read_xml(zf, name):
    """Same decoding rule as build_works: UTF-8 with optional BOM, UTF-16 when a BOM says so."""
    b = zf.read(name)
    if b[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return b.decode("utf-16")
    return b.decode("utf-8-sig")


def selftest_split():
    """Minimal case from the Codex review: <내용>甲<원주>乙<line/>丙</원주>丁</내용> must give main 2, note 2."""
    import xml.etree.ElementTree as ET
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from build_works import itertext_split
    m, n = itertext_split(ET.fromstring("<내용>甲<원주>乙<line/>丙</원주>丁</내용>"))
    assert (len(HAN.findall(m)), len(HAN.findall(n))) == (2, 2), (m, n)


def main():
    selftest_split()
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", action="append", required=True); ap.add_argument("--derived", default="data/derived")
    x = ap.parse_args()
    d = Path(x.derived)
    colls = list(csv.DictReader(open(d / "collections.csv", encoding="utf-8")))
    works = list(csv.DictReader(open(d / "works.csv", encoding="utf-8")))
    by_zip = {c["zip"]: c for c in colls}
    sums = defaultdict(int)
    for w in works:
        sums[w["collection_id"]] += int(w["chars_main"]) + int(w["chars_note"])
    fails = []
    zips = sorted(set(z for s in x.src for z in glob.glob(str(Path(s) / "*.zip"))))
    n_ok = 0; residue = []
    for z in zips:
        name = Path(z).name
        c = by_zip.get(name)
        if c is None:
            fails.append(("inventory", name, "collections.csv 에 없음")); continue
        zf = zipfile.ZipFile(z); raw_total = 0
        for n in zf.namelist():
            if not n.lower().endswith(".xml"):
                continue
            s = read_xml(zf, n)
            if "<레벨2 " not in s:  # 서지 file: 해제 is not part of the work count
                continue
            s = re.sub(r"<!--.*?-->", "", s, flags=re.S)   # commented-out fragments (e.g. 지봉집 권36) are not content; ElementTree drops them too
            for m in re.finditer(r"<내용>(.*?)</내용>", s, re.S):
                t = html.unescape(TAG.sub("", m.group(1)))
                raw_total += len(HAN.findall(t))
                if "&#" in t:
                    residue.append((name, n))
        if raw_total != sums[c["collection_id"]]:
            fails.append(("chars", name, f"raw {raw_total} vs works {sums[c['collection_id']]}"))
        else:
            n_ok += 1
    ids = [w["work_id"] for w in works]
    if len(ids) != len(set(ids)):
        fails.append(("ids", "", f"work_id 중복 {len(ids) - len(set(ids))}"))
    cids = [c["collection_id"] for c in colls]
    if len(cids) != len(set(cids)):
        fails.append(("ids", "", f"collection_id 중복 {len(cids) - len(set(cids))}"))
    nocls = sum(1 for w in works if not w["genre1"])
    noauth = [c["zip"] for c in colls if not c["author_hj"]]
    nobirth = [c["zip"] for c in colls if not c["birth"]]
    print(f"zips {len(zips)} | chars match {n_ok} | residue '&#' {len(residue)} | works {len(works):,} | no genre {nocls} | no author {len(noauth)} | no birth {len(nobirth)}")
    for f in fails[:50]:
        print("  FAIL", f)
    for r in residue[:10]:
        print("  residue", r)
    for n in noauth[:10]:
        print("  no author:", n)
    (d / "check_report.txt").write_text(
        f"zips {len(zips)}\nchars match {n_ok}\nresidue {len(residue)}\nworks {len(works)}\nno genre {nocls}\nno author {len(noauth)}\nno birth {len(nobirth)}\n"
        + "\n".join("FAIL\t" + "\t".join(f) for f in fails) + "\n" + "\n".join("RESIDUE\t" + "\t".join(r) for r in residue) + "\n"
        + "\n".join("NOAUTH\t" + n for n in noauth) + "\n" + "\n".join("NOBIRTH\t" + n for n in nobirth) + "\n", encoding="utf-8")
    sys.exit(1 if fails or residue or nocls else 0)


if __name__ == "__main__":
    main()
