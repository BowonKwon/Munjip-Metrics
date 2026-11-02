# -*- coding: utf-8 -*-
"""Build the work-level tables from the 한국문집총간 XML zips.

  python src/build_works.py --src data/raw/itkc [--src more/dir] --out data/derived

Outputs (UTF-8 CSV):
  collections.csv  one row per collection (레벨1 서지): ids, titles, author, series a/b, volumes, publication year, haeje summary
  works.csv        one row per final item (레벨3/4 type="최종정보"): ids, volume, genre, title, writer, chars main/note, links
  letters.csv      書簡類 works with the recipient string parsed from the title
  epitaphs.csv     碑誌類·行狀類 works with the subject string parsed from the title
  haeje_private.jsonl  the full 간략해제 text per collection (kept for linkage checks; not exported)

Counting rule: characters are CJK code points (U+3400–4DBF, 4E00–9FFF, F900–FAFF, U+20000–3134F) in the text of
<내용> after tag removal and entity decoding. Text inside <원주> or <주석> (교감주·난외주·협주) is counted as
chars_note, everything else as chars_main. check_works.py recounts the same code points straight from the raw XML.
"""
import argparse, csv, glob, json, re, sys, unicodedata, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HAN = re.compile(r"[㐀-䶿一-鿿豈-﫿\U00020000-\U0003134f]")
NOTE_TAGS = {"원주", "주석"}
LETTER_VERB = re.compile(r"^(?:又|再|三|四|五|復)?(答|與|上|寄|復|報|奉|呈|贈|簡|謝|擬|代)")
LETTER_TAIL = re.compile(r"(書|簡|問目|別紙|狀|札|啓|帖|疏|牘|函|書牘|詩)(?:[^書簡]*)$")
EPITAPH_KIND = re.compile(r"(神道碑銘|神道碑|墓誌銘|墓碣銘|墓碣|墓表|墓誌|墓碑|碑銘|碑文|壙誌|壙銘|壙記|墓記|阡表|行狀|諡狀|行錄|行蹟|遺事|家狀|言行錄|事狀|實紀)")
CJK_PUNCT = "。，、：；！？「」『』（）〔〕《》〈〉○　 "


def han_count(s):
    return len(HAN.findall(s))


def read_xml(zf, name):
    """Decode an archive member: UTF-8 (BOM allowed); a few files are UTF-16 with a BOM."""
    b = zf.read(name)
    if b[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return b.decode("utf-16")
    return b.decode("utf-8-sig")


def itertext_split(elem):
    """Return (main_text, note_text) for an element, note = text inside 원주/주석 at any depth."""
    main, note = [], []

    def walk(e, in_note):
        here = in_note or e.tag in NOTE_TAGS
        (note if here else main).append(e.text or "")
        for c in e:
            walk(c, here)
            (note if in_note else main).append(c.tail or "")  # tail belongs to the parent's context
    walk(elem, False)
    return "".join(main), "".join(note)


def plain(elem):
    return "".join(elem.itertext()) if elem is not None else ""


def parse_level1(root):
    """Collection-level metadata from the 서지 file."""
    lv1 = root.find("레벨1")
    meta = lv1.find("메타정보")
    g = lambda path: plain(meta.find(path)).strip() if meta.find(path) is not None else ""
    titles = {t.get("type"): plain(t).strip() for t in meta.findall("제목정보/제목")}
    au = meta.find("저자정보[@type='저자']/저자")
    author = {}
    if au is not None:
        author = {"ko": plain(au.find("한글성명")).strip(), "hj": plain(au.find("한자성명")).strip(),
                  "ja": "|".join(plain(x).strip() for x in au.findall("자호[@type='자']")),
                  "ho": "|".join(plain(x).strip() for x in au.findall("자호[@type='호']")),
                  "si": "|".join(plain(x).strip() for x in au.findall("자호[@type='시호']")),
                  # 서기년="0" and "9999" are the ITKC's placeholders for an unknown year → blank
                  "birth": ((au.find("생년").get("서기년") if au.find("생년") is not None else "") or "").replace("0", "", 1) if (au.find("생년") is not None and au.find("생년").get("서기년") == "0") else ((au.find("생년").get("서기년") if au.find("생년") is not None else "") or ""),
                  "death": "" if (au.find("몰년") is not None and au.find("몰년").get("서기년") in ("0", "9999")) else ((au.find("몰년").get("서기년") if au.find("몰년") is not None else "") or ""),
                  "birth_text": plain(au.find("생년")).strip(), "death_text": plain(au.find("몰년")).strip()}
    jip = meta.find("간행정보/집수")
    pub = meta.find("간행정보/원문간행년")
    per = meta.find("간행정보/간행기간")
    sabu = {c.get("type"): plain(c).strip() for c in meta.findall("분류정보/분류항목[@type='사부분류']/분류내용")}
    vols = [plain(v).strip() for v in meta.findall("목차정보/목차/목차제목[@type='VOLUMETITLE']")]
    n_gwon = sum(1 for v in vols if re.match(r"^卷[一二三四五六七八九十百零〇\d]+$", v))
    haeje_el = lv1.find("해설정보/해설[@type='간략해제']/본문정보/내용")
    haeje = re.sub(r"\s+", " ", plain(haeje_el)).strip() if haeje_el is not None else ""
    gw = re.search(r"(\d+)권\s*(\d+)책", haeje)
    return {
        "collection_id": lv1.get("id"), "created": lv1.get("자료생성일") or "",
        "title_hj": titles.get("한자서명", ""), "title_ko": titles.get("한글서명", ""),
        "title_gwonsu": titles.get("권수제", ""), "title_pansim": titles.get("판심제", ""),
        "author_hj": author.get("hj", ""), "author_ko": author.get("ko", ""), "author_ja": author.get("ja", ""),
        "author_ho": author.get("ho", ""), "author_si": author.get("si", ""),
        "birth": author.get("birth", ""), "death": author.get("death", ""),
        "birth_text": author.get("birth_text", ""), "death_text": author.get("death_text", ""),
        "jip_start": jip.get("시작번호") if jip is not None else "", "jip_end": jip.get("끝번호") if jip is not None else "",
        "jip_count": plain(jip).strip() if jip is not None else "",
        "series": ({"a": "정편", "b": "속편"}.get((jip.get("시작번호") or " ")[0], "") if jip is not None else ""),
        "pub_year": (pub.get("서기년") if pub is not None else "") or "",
        "chonggan_years": f"{per.get('시작년')}-{per.get('종료년')}" if per is not None else "",
        "sabu_major": sabu.get("대분류", ""), "sabu_minor": sabu.get("중분류", ""),
        "n_volume_titles": len(vols), "n_gwon_titles": n_gwon,
        "haeje_chars": len(haeje), "haeje_gwon": gw.group(1) if gw else "", "haeje_chaek": gw.group(2) if gw else "",
        "_haeje": haeje,
    }


def parse_items(root, coll):
    """Yield one dict per 최종정보 element in a 권차 file."""
    lv1 = root.find("레벨1")
    for lv2 in lv1.findall("레벨2"):
        vol_id = lv2.get("id"); vol_title = ""
        t = lv2.find("메타정보/제목정보/제목")
        if t is not None:
            vol_title = re.sub(r"\s+", " ", plain(t)).strip()
        stack = [lv2]
        while stack:
            e = stack.pop(0)
            for c in e:
                if not c.tag.startswith("레벨"):
                    continue
                if c.get("type") == "최종정보":
                    yield item_row(c, coll, vol_id, vol_title)
                else:
                    stack.append(c)


def item_row(e, coll, vol_id, vol_title):
    meta = e.find("메타정보")
    title_el = meta.find("제목정보/제목") if meta is not None else None
    title = re.sub(r"\s+", " ", plain(title_el)).strip() if title_el is not None else ""
    w = meta.find("저자정보[@type='필자']/저자") if meta is not None else None
    writer_hj = plain(w.find("한자성명")).strip() if w is not None and w.find("한자성명") is not None else ""
    writer_ko = plain(w.find("한글성명")).strip() if w is not None and w.find("한글성명") is not None else ""
    # labels only: a few files write 類·車·狀 etc. as CJK compatibility ideographs → NFKC so that 公車類 is one class
    cls = {c.get("type"): unicodedata.normalize("NFKC", plain(c).strip()) for c in meta.findall("분류정보/분류항목[@type='문체분류']/분류내용")} if meta is not None else {}
    links = {l.get("type") for l in e.iter("연계항목")}   # 연계정보 sits beside 메타정보 under the level element
    body = e.find("본문정보/내용")
    main_t, note_t = itertext_split(body) if body is not None else ("", "")
    page = None
    for p in e.iter("페이지"):
        page = p.get("number"); break
    names_in_title = [plain(x).strip() for x in title_el.iter("고유명사")] if title_el is not None else []
    is_author = int(bool(writer_hj) and writer_hj == coll["author_hj"]) if coll["author_hj"] else ""
    return {
        "work_id": e.get("id"), "collection_id": coll["collection_id"], "volume_id": vol_id, "volume_title": vol_title,
        "level": e.tag, "genre1": cls.get("대분류", ""), "genre2": cls.get("중분류", ""),
        "title": title, "writer_hj": writer_hj, "writer_ko": writer_ko, "is_author_work": is_author,
        "chars_main": han_count(main_t), "chars_note": han_count(note_t),
        "n_paragraphs": len(body.findall(".//단락")) if body is not None else 0,
        "has_translation": int("번역문" in links), "has_punct": int("교감표점" in links), "has_image": int("이미지" in links),
        "page_first": page or "", "n_title_names": len(names_in_title),
        "created": e.get("자료생성일") or "",
    }


def parse_letter(title):
    t = re.sub(r"[。．\s]+$", "", title)
    t = re.sub(r"\s+[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥].*$", "", t)  # trailing 干支 date
    m = LETTER_VERB.match(t)
    if not m:
        return "", 0
    rest = t[m.end():]
    rest = re.split(r"(書|簡|問目|別紙|狀|札|啓|帖|疏|牘|函|序|詩)", rest, maxsplit=1)[0]
    rest = re.sub(r"[。，、\s].*$", "", rest).strip()
    # a verb after the addressee opens the topic (與金晦叔論景賢堂祭儀書 → 金晦叔); cut there if at least two characters precede it
    rest = re.sub(r"^(.{2,}?)(論|問|議|辨|請|乞|求|賀|慰|弔|索|討|告|示|約|勸|陳|辭)[^\s]*$", r"\1", rest)
    return rest, 1


def parse_epitaph(title):
    t = re.sub(r"[。．\s]+$", "", title)
    m = EPITAPH_KIND.search(t)
    if not m:
        return "", "", 0
    subj = t[: m.start()]
    subj = re.sub(r"^(有明朝鮮國?|有明|朝鮮國?|故|贈|先考|先妣|先祖考|先祖妣|亡室|亡兒|亡弟|亡妹|亡子|幼子|顯考|顯妣|先府君|先大夫)+", "", subj)
    return subj.strip(), m.group(1), 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", action="append", required=True); ap.add_argument("--out", default="data/derived")
    x = ap.parse_args()
    out = Path(x.out); out.mkdir(parents=True, exist_ok=True)
    zips = sorted(set(z for d in x.src for z in glob.glob(str(Path(d) / "*.zip"))))
    colls, works, letters, epis, haeje = [], [], [], [], []
    problems = []
    for zi, z in enumerate(zips, 1):
        zf = zipfile.ZipFile(z)
        names = sorted(n for n in zf.namelist() if n.lower().endswith(".xml"))
        coll = None; items = []
        for n in names:
            raw = read_xml(zf, n)
            try:
                root = ET.fromstring(raw)
            except ET.ParseError as err:
                problems.append((Path(z).name, n, f"parse: {err}")); continue
            lv1 = root.find("레벨1")
            if lv1 is None:
                problems.append((Path(z).name, n, "레벨1 없음")); continue
            if lv1.find("메타정보/저자정보[@type='저자']") is not None and lv1.find("레벨2") is None:
                coll = parse_level1(root); coll["zip"] = Path(z).name; coll["n_xml"] = len(names)
            else:
                items.append(root)
        if coll is None:
            problems.append((Path(z).name, "", "서지 파일 없음")); continue
        for root in items:
            for r in parse_items(root, coll):
                works.append(r)
                if r["genre1"] == "書簡類":
                    rec, ok = parse_letter(r["title"]); letters.append({"work_id": r["work_id"], "collection_id": r["collection_id"], "title": r["title"], "recipient_raw": rec, "pattern_ok": ok, "is_author_work": r["is_author_work"]})
                if r["genre2"] in ("碑誌類", "行狀類"):
                    subj, kind, ok = parse_epitaph(r["title"]); epis.append({"work_id": r["work_id"], "collection_id": r["collection_id"], "genre2": r["genre2"], "title": r["title"], "subject_raw": subj, "kind": kind, "pattern_ok": ok, "is_author_work": r["is_author_work"]})
        coll["n_works"] = sum(1 for w in works if w["collection_id"] == coll["collection_id"])
        haeje.append({"collection_id": coll["collection_id"], "haeje": coll.pop("_haeje")})
        colls.append(coll)
        if zi % 100 == 0:
            print(f"  {zi}/{len(zips)} zips, {len(works):,} works", flush=True)

    def write(name, rows):
        if not rows:
            return
        keys = list(rows[0].keys())
        with open(out / name, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
    write("collections.csv", colls); write("works.csv", works); write("letters.csv", letters); write("epitaphs.csv", epis)
    with open(out / "haeje_private.jsonl", "w", encoding="utf-8") as f:
        for h in haeje:
            f.write(json.dumps(h, ensure_ascii=False) + "\n")
    with open(out / "build_problems.tsv", "w", encoding="utf-8") as f:
        for p in problems:
            f.write("\t".join(p) + "\n")
    ids = [w["work_id"] for w in works]
    print(f"collections {len(colls):,} | works {len(works):,} (unique ids {len(set(ids)):,}) | letters {len(letters):,} | epitaphs {len(epis):,} | problems {len(problems)}")
    print(f"chars main {sum(w['chars_main'] for w in works):,} note {sum(w['chars_note'] for w in works):,}")


if __name__ == "__main__":
    main()
