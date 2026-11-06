# -*- coding: utf-8 -*-
"""Static site builder: derived CSVs + registry -> site/ (ko + en).

  python src/build_site.py [--derived data/derived] [--out site]

Every number on the site comes from a CSV in data/derived (copied to site/data) and every metric text
from registry.py / takeaways.py. Charts are inline SVG (helpers in site_common.py, shared with Sillok Metrics).
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import shutil
from pathlib import Path

import pandas as pd

import site_common as sc
from site_common import esc, fmt, fig, svg_bars, svg_lines, legend, table_html, cap, take_block, blurb
from registry import METRICS, PRIOR, SERIES, SERIES_INTRO, SITE, SOURCES, PERSON_PAGES
try:
    from takeaways import TAKE, HOME_FIVE, PAGE_TAKE
except ImportError:  # before the takeaways are written
    TAKE, HOME_FIVE, PAGE_TAKE = {}, {"ko": [], "en": []}, {}

VERSION = SITE["version"]
BUILD_DATE = "2026-11-07"
REPO = "https://github.com/BowonKwon/Munjip-Metrics"
ITKC = "https://db.itkc.or.kr/dir/node?dataId="
GENRES = ["詩類", "書簡類", "序跋類", "傳記類", "公車類", "哀祭類", "雜著類"]
GENRE_EN = {"詩類": "poetry", "書簡類": "letters", "序跋類": "prefaces and postscripts", "傳記類": "biographies", "公車類": "court documents", "哀祭類": "elegies", "雜著類": "miscellany"}
GENRE_KO = {"詩類": "시", "書簡類": "서간", "序跋類": "서발", "傳記類": "전기", "公車類": "공거", "哀祭類": "애제", "雜著類": "잡저"}

T = {
    "ko": dict(site=SITE["ko"]["title"], tagline=SITE["ko"]["subtitle"],
               nav_home="홈", nav_centuries="세기", nav_collections="문집", nav_persons="인물", nav_metrics="지표", nav_prior="선행 결과", nav_reading="읽기용 판", nav_data="데이터", nav_method="방법·한계", lang_other="English",
               series="계열", definition="정의", formula="공식", reading="읽는 법", caveat="한계", source="자료원", unit="단위", external="외부 대조",
               reliability="신뢰도 카드", rel_exact="집계값 — 원본 XML에서 그대로 센 수", rel_ext="외부 대조값 — 선행 수치와 맞춰 본 값", rel_samp="표본 정밀도 — 제목 파싱·인물 연결의 정확도를 코딩한 표본에서 잰 값",
               table="표", download="CSV 내려받기", search="필터", metric_list="지표 목록", century_list="세기 목록", collection_list="문집 목록", person_list="인물 면",
               license="라이선스", cite="인용", built="생성일", version="판", hub="공개 자료 전체", itkc_link="고전종합DB 원문",
               works="편", own="저자 글", chars="글자(한자)", notes="주 글자", collections="문집", authors="저자", century="세기", series_col="구분", share="비율", n="건수", prior="선행 결과", ours="이 사이트",
               author="저자", birth="생년", death="몰년", pub="간행년", title="서명", genre="문체", recipients="수신자", letters="서간", epitaphs="비지·행장"),
    "en": dict(site=SITE["en"]["title"], tagline=SITE["en"]["subtitle"],
               nav_home="Home", nav_centuries="Centuries", nav_collections="Collections", nav_persons="Persons", nav_metrics="Metrics", nav_prior="Prior results", nav_reading="Reading edition", nav_data="Data", nav_method="Method and limits", lang_other="한국어",
               series="Series", definition="Definition", formula="Formula", reading="How to read it", caveat="Caveats", source="Sources", unit="Unit", external="External check",
               reliability="Reliability card", rel_exact="Exact count — read straight from the source XML", rel_ext="External match — set against a published figure", rel_samp="Sampled precision — accuracy of title parsing or person linkage measured on a coded sample",
               table="Table", download="Download CSV", search="Filter", metric_list="All metrics", century_list="Centuries", collection_list="All collections", person_list="Person pages",
               license="License", cite="Citation", built="Built", version="Version", hub="All public materials", itkc_link="ITKC source",
               works="works", own="own works", chars="characters", notes="note characters", collections="collections", authors="authors", century="century", series_col="series", share="share", n="count", prior="prior result", ours="this site",
               author="author", birth="born", death="died", pub="printed", title="title", genre="genre", recipients="addressees", letters="letters", epitaphs="epitaphs and biographies"),
}
sc.T = T

# 1.0.3: navigation on leaf pages (metric pages, person pages) — same helper as Physical Constants / Sillok Metrics
sc.CSS += ' main.wide{max-width:1300px} .crumbs{font-size:.84rem;color:var(--fg3);margin:-.4rem 0 .9rem} .crumbs .sep{margin:0 .25rem} .crumbs [aria-current]{color:var(--fg2)} .leaf{display:grid;grid-template-columns:220px minmax(0,1fr);gap:2rem;align-items:start} .sibs{position:sticky;top:4.2rem;max-height:calc(100vh - 5rem);overflow:auto;font-size:.84rem;border-right:1px solid var(--line);padding-right:.8rem} .sibs ol,.sibs-m ol{list-style:none;margin:.2rem 0 .8rem;padding:0} .sibs li a,.sibs-m li a{display:block;padding:.18rem .4rem;border-radius:6px;color:var(--fg2)} .sibs li a:hover,.sibs-m li a:hover{background:var(--bg2);text-decoration:none} .sibs a[aria-current],.sibs-m a[aria-current]{background:var(--bg2);color:var(--fg);font-weight:600} .sibs summary,.sibs-m summary{cursor:pointer;font-weight:600;color:var(--fg);margin:.3rem 0} .sibs .sg{font-weight:600;margin:.2rem 0} .sibs-m{display:none;border:1px solid var(--line);border-radius:10px;padding:.4rem .8rem;margin:0 0 1rem;font-size:.9rem} .pn{display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap;border-top:1px solid var(--line);margin-top:2.4rem;padding-top:1rem;font-size:.92rem} .pn a[rel=next]{margin-left:auto;text-align:right} .pn small{display:block;color:var(--fg3)} @media(max-width:860px){.leaf{display:block}.sibs{display:none}.sibs-m{display:block}} @media print{.crumbs,.sibs,.sibs-m,.pn{display:none}.leaf{display:block}}'
sc.JS += ';document.addEventListener("keydown",function(e){if(e.altKey||e.ctrlKey||e.metaKey||e.shiftKey)return;var t=e.target;if(t&&t.closest&&t.closest("input,textarea,select,[contenteditable]"))return;var a=null;if(e.key==="ArrowLeft")a=document.querySelector("a[rel=prev]");else if(e.key==="ArrowRight")a=document.querySelector("a[rel=next]");if(a){location.href=a.href}});var sb=document.querySelector(".sibs"),cu=sb&&sb.querySelector("a[aria-current]");if(cu){sb.scrollTop=cu.offsetTop-sb.clientHeight/2}'

LEAF_T = {"ko": dict(crumbs="위치", sibs="같은 계열", others="이 계열의 다른 면", pn="이전·다음", prev="이전", next="다음", next_group="다음 계열"),
          "en": dict(crumbs="Breadcrumb", sibs="In this series", others="Other pages in this series", pn="Previous and next", prev="Previous", next="Next", next_group="Next series")}


def leaf_html(lang, leaf, body):
    """Breadcrumb, same-series list (sidebar on wide screens, collapsed box on narrow ones) and previous/next links.
    leaf = dict(crumbs=[(label, href)...], groups=[(group label, [(label, href), ...]), ...], cur=href of this page)."""
    L = LEAF_T[lang]
    flat = [(lab, href, gi, glab) for gi, (glab, items) in enumerate(leaf["groups"]) for lab, href in items]
    idx = next(i for i, x in enumerate(flat) if x[1] == leaf["cur"])
    cur_g = flat[idx][2]
    crumbs = " <span class='sep' aria-hidden='true'>›</span> ".join(f'<a href="{h}">{esc(l)}</a>' for l, h in leaf["crumbs"])
    crumbs += f" <span class='sep' aria-hidden='true'>›</span> <span aria-current='page'>{esc(flat[idx][0])}</span>"

    def lists():
        out = []
        many = len(leaf["groups"]) > 1
        for gi, (glab, items) in enumerate(leaf["groups"]):
            lis = "".join(f'<li><a href="{h}"' + (' aria-current="page"' if h == leaf["cur"] else "") + f'>{esc(l)}</a></li>' for l, h in items)
            if many:
                out.append(f'<details{" open" if gi == cur_g else ""}><summary>{esc(glab)} <small>({len(items)})</small></summary><ol>{lis}</ol></details>')
            else:
                out.append(f'<p class="sg">{esc(glab)} <small>({len(items)})</small></p><ol>{lis}</ol>')
        return "".join(out)

    side = f'<aside class="sibs"><nav aria-label="{L["sibs"]}">{lists()}</nav></aside>'
    mobile = f'<details class="sibs-m"><summary>{L["others"]} ({sum(len(i) for _, i in leaf["groups"])})</summary><nav aria-label="{L["sibs"]}">{lists()}</nav></details>'
    pn = []
    if idx > 0:
        p = flat[idx - 1]
        pn.append(f'<a rel="prev" href="{p[1]}">← {esc(p[0])}</a>')
    if idx + 1 < len(flat):
        n = flat[idx + 1]
        note = f'<small>{L["next_group"]}: {esc(n[3])}</small> ' if n[2] != cur_g else ""
        pn.append(f'<a rel="next" href="{n[1]}">{note}{esc(n[0])} →</a>')
    pnav = f'<nav class="pn" aria-label="{L["pn"]}">{"".join(pn)}</nav>'
    return (f'<nav class="crumbs" aria-label="{L["crumbs"]}">{crumbs}</nav><div class="leaf">{side}<div class="leafbody">{mobile}'
            f'{body}{pnav}</div></div>')


def metric_leaf(lang, mid):
    """Siblings of a metric page: every metric, grouped by series in the order of the metric index."""
    t = T[lang]
    groups = [(sl[lang], [(m[lang]["name"], f'{m["id"]}.html') for m in METRICS if m["series"] == s]) for s, sl in SERIES.items()]
    return dict(crumbs=[(t["nav_home"], "../index.html"), (t["nav_metrics"], "index.html")], cur=f"{mid}.html", groups=[g for g in groups if g[1]])


def person_leaf(D, lang, cid):
    """Siblings of a person page: the ten person pages in order of the author's birth year."""
    t = T[lang]; ko = lang == "ko"
    rows = []
    for hj, nko, nen in PERSON_PAGES:
        rr = D.col[D.col.title_hj == hj]
        if len(rr):
            r = rr.iloc[0]
            rows.append((r.birth if not pd.isna(r.birth) else 9999, f"{nko if ko else nen} ({fmt(r.birth, '.0f')})", f"{r.collection_id}.html"))
    items = [(lab, href) for _, lab, href in sorted(rows, key=lambda x: x[0])]
    return dict(crumbs=[(t["nav_home"], "../index.html"), (t["person_list"], "../persons.html")], cur=f"{cid}.html", groups=[(t["person_list"], items)])


def century_label(c, lang):
    if c is None or (isinstance(c, float) and math.isnan(c)):
        return "생년 미상" if lang == "ko" else "birth year unknown"
    c = int(c)
    if lang == "ko":
        return f"{c}세기"
    return f"{c}th century" if c not in (21, 22, 23) else f"{c}st century"



UNIT_KO = {"works": "편", "characters": "자", "collections": "종", "share": "비율", "fascicles": "권", "volumes": "권", "strings": "문자열", "persons": "명", "years": "년"}


def series_label(v, lang):
    if lang == "ko":
        return v
    return {"정편": "first series", "속편": "supplement", "전체": "all"}.get(v, v)


def _n_match(D) -> str:
    v = D.check.split("chars match ")[1].split("\n")[0].strip() if "chars match" in D.check else "?"
    return f"{int(v):,}" if v.isdigit() else v


def _title_hj(D, cid) -> str:
    r = D.col[D.col.collection_id == cid]
    return r.title_hj.iloc[0] if len(r) else cid

def page(lang: str, title: str, body: str, depth: int = 1, desc: str = "", active: str = "", rel: str = "index.html", leaf=None) -> str:
    if leaf:   # 1.0.3: breadcrumb, same-series list and previous/next on metric and person pages
        body = leaf_html(lang, leaf, body)
    t = T[lang]
    root = "../" * depth
    other = "en" if lang == "ko" else "ko"
    hub_path = "" if lang == "ko" else "en/"
    nav = [("home", f"{root}{lang}/index.html", t["nav_home"]), ("metrics", f"{root}{lang}/metrics/index.html", t["nav_metrics"]),
           ("centuries", f"{root}{lang}/centuries/index.html", t["nav_centuries"]), ("collections", f"{root}{lang}/collections/index.html", t["nav_collections"]),
           ("persons", f"{root}{lang}/persons.html", t["nav_persons"]), ("prior", f"{root}{lang}/prior.html", t["nav_prior"]),
           ("reading", f"{root}{lang}/reading.html", t["nav_reading"]), ("data", f"{root}{lang}/data.html", t["nav_data"]), ("method", f"{root}{lang}/method.html", t["nav_method"])]
    navh = "".join(f'<a href="{h}"{" class=\"on\"" if k == active else ""}>{n}</a>' for k, h, n in nav)
    attribution = ("본 사이트의 집계는 한국고전번역원이 공공데이터포털에 개방한 「한국문집총간」(이용허락범위 제한 없음)과 한국학중앙연구원의 「조선조문과급제자」·「한국역대인명정보」를 이용하였습니다. 원문 전문은 싣지 않습니다."
                   if lang == "ko" else
                   "Counts on this site use the 'Hanguk munjip chonggan' XML released by the Institute for the Translation of Korean Classics on data.go.kr (no license restriction) and the examination roster and person database of the Academy of Korean Studies. No full text is reproduced.")
    return f"""<!DOCTYPE html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title) if title == t['site'] else esc(title) + ' — ' + t['site']}</title><meta name="description" content="{esc(desc or t['tagline'])}">
<script>(function(){{var q=new URLSearchParams(location.search).get("theme");if(q==="light"||q==="dark"){{localStorage.setItem("mjm-theme",q)}}else if(q==="auto"){{localStorage.removeItem("mjm-theme")}}var v=localStorage.getItem("mjm-theme");if(v)document.documentElement.setAttribute("data-theme",v)}})();</script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@600&display=swap" rel="stylesheet">
<style>{sc.CSS}</style></head><body>
<header><a class="brand" href="{root}{lang}/index.html">{t['site']}</a>
<nav>{navh}</nav>
<div class="right"><button id="theme" class="theme" type="button" aria-label="theme">◑</button><a class="lang" href="{root}{other}/{rel}">{t['lang_other']}</a></div></header>
<main{' class="wide"' if leaf else ''}>{body}</main>
<footer>{t['site']} · {t['version']} {VERSION} · {t['built']} {BUILD_DATE} · <a href="{REPO}">GitHub</a> · {t['hub']} <a href="https://bowonkwon.github.io/{hub_path}">bowonkwon.github.io</a><br>{attribution}</footer>
<script>{sc.JS}</script></body></html>"""


# ----------------------------------------------------------------- data
class Data:
    def __init__(self, d: Path):
        self.d = d
        self.col = pd.read_csv(d / "a_collections.csv")
        self.cen = pd.read_csv(d / "a_centuries.csv")
        self.gwon = pd.read_csv(d / "a_gwon_check.csv")
        self.b = pd.read_csv(d / "b_centuries.csv")
        self.b_all = pd.read_csv(d / "b_centuries_all.csv")
        self.b_col = pd.read_csv(d / "b_collections.csv")
        self.b2 = pd.read_csv(d / "b_genre2.csv")
        self.poems = pd.read_csv(d / "b_poems.csv")
        self.other = pd.read_csv(d / "b_other_share.csv")
        self.letters = pd.read_csv(d / "c_letters.csv")
        self.recip = pd.read_csv(d / "c_recipients.csv")
        self.epi = pd.read_csv(d / "c_epitaphs.csv")
        self.writers = pd.read_csv(d / "c_writers.csv")
        self.c_cen = pd.read_csv(d / "c_centuries.csv")
        self.dcen = pd.read_csv(d / "d_centuries.csv")
        self.authors = pd.read_csv(d / "d_authors.csv")
        self.dcol = pd.read_csv(d / "d_collections.csv")
        self.precision = json.load(open(d / "reliability.json", encoding="utf-8")) if (d / "reliability.json").exists() else {}
        self.check = (d / "check_report.txt").read_text(encoding="utf-8") if (d / "check_report.txt").exists() else ""
        self.col["label_ko"] = self.col.title_ko + "(" + self.col.title_hj + ")"
        self.col["label_en"] = self.col.title_hj + " (" + self.col.author_hj.fillna("") + ")"
        self.tot = self.cen[self.cen.series == "전체"].set_index("birth_century")
        self.ser = self.cen[self.cen.series != "전체"]

    def label(self, r, lang):
        return r.label_ko if lang == "ko" else r.label_en


def cen_series(df, col, lang, name=None, ci=0):
    ccol = "birth_century" if "birth_century" in df.columns else "century"
    pts = [(int(r[ccol]), float(r[col])) for _, r in df.iterrows() if not pd.isna(r[col]) and not pd.isna(r[ccol])]
    return (name or col, pts, ci)


# ----------------------------------------------------------------- headline, reliability, figures
def headline(m, D: Data, lang):
    ko = lang == "ko"; mid = m["id"]; tot = D.tot
    if mid == "a1_works":
        return f"{int(D.col.n_works.sum()):,}", (f"편 · 문집 {len(D.col):,}종" if ko else f"works · {len(D.col):,} collections")
    if mid == "a2_chars":
        return f"{D.col.chars.sum()/1e6:.1f}M", (f"한자 · 주 {D.col.chars_note.sum()/1e6:.1f}M 포함" if ko else f"characters incl. {D.col.chars_note.sum()/1e6:.1f}M in notes")
    if mid == "a3_centuries":
        r = tot.n_collections.idxmax()
        return f"{int(tot.n_collections.max()):,}", (f"{century_label(r, lang)} 출생 저자의 문집 — 최다" if ko else f"collections by authors born in the {century_label(r, lang)} — the most")
    if mid == "a4_chars_per_work":
        t9 = D.tot[D.tot.index.notna()]
        return f"{t9.chars_per_work_median.median():,.0f}", (f"세기별 중앙값 {len(t9)}개의 중앙값, 자/편" if ko else f"median of the {len(t9)} century medians, characters per work")
    if mid == "a5_note_share":
        return f"{D.col.chars_note.sum()/D.col.chars.sum():.1%}", ("전체 글자 중 주" if ko else "of all characters are in notes")
    if mid == "a6_own_share":
        return f"{D.col.n_own_works.sum()/D.col.n_works.sum():.1%}", ("전체 편 중 저자 자신의 글" if ko else "of all works are by the collection's author")
    if mid == "a7_gwon":
        return f"{int(D.gwon.match.sum())}/{len(D.gwon)}", ("권 수가 해제와 일치하는 문집" if ko else "collections whose fascicle count matches the introduction")
    b = D.b
    if mid == "b1_poetry_share":
        p = b[b.genre1 == "詩類"]
        v = p.n_works.sum() / p.total_works.sum()
        return f"{v:.1%}", ("저자 글 중 시(편 기준, 전체)" if ko else "of own works are poetry (by works, all centuries)")
    if mid == "b2_genre_mix":
        g = b.groupby("genre1").n_works.sum().sort_values(ascending=False)
        return f"{g.iloc[1]/g.sum():.1%}", (f"둘째로 큰 분류 {GENRE_KO[g.index[1]]}의 비중" if ko else f"share of the second-largest class, {GENRE_EN[g.index[1]]}")
    for mid_, gname in (("b3_letters_share", "書簡類"), ("b4_memorials_share", "公車類"), ("b6_prefaces_share", "序跋類")):
        if mid == mid_:
            p = b[b.genre1 == gname]; v = p.n_works.sum() / b.groupby("century").total_works.first().sum()
            return f"{v:.1%}", (f"저자 글 중 {GENRE_KO[gname]}" if ko else f"of own works are {GENRE_EN[gname]}")
    if mid == "b5_relational_share":
        g2 = D.b2; v = g2[(g2.genre1 == "哀祭類") | (g2.genre2.isin(["碑誌類", "行狀類"]))].n_works.sum() / g2.n_works.sum()
        return f"{v:.1%}", ("저자 글 중 애제·비지·행장" if ko else "of own works commemorate others")
    if mid == "b7_other_share":
        return f"{(D.other.n * D.other.other_share).sum() / D.other.n.sum():.1%}", ("저자 글 전체 중 기타류" if ko else "of own works are in an 'other' class")
    if mid == "b8_poem_length":
        return f"{D.poems.poem_chars_median.median():,.0f}", ("시 한 편 글자 수, 세기 중앙값들의 중앙값" if ko else "characters per poem, median of century medians")
    if mid == "c1_recipients":
        return f"{int(D.letters.n_unique.sum()):,}", (f"수신자 문자열(문집 {len(D.letters):,}종 합)" if ko else f"addressee strings across {len(D.letters):,} collections")
    if mid == "c2_epitaph_subjects":
        return f"{int(D.epi.n_epitaphs.sum()):,}", ("저자가 쓴 비지·행장 편" if ko else "epitaphs and biographies by the authors")
    if mid == "c3_other_writers":
        return f"{int(D.writers.n_other_writers.sum()):,}", ("문집에 글을 보탠 타인 필자(문집별 합)" if ko else "other writers contributing (summed over collections)")
    dc = D.dcen
    if mid == "d1_dates":
        return f"{(D.authors.birth.notna() & D.authors.death.notna()).mean():.1%}", ("저자 중 생년·몰년 모두 있음" if ko else "of authors have both birth and death years")
    if mid == "d2_munkwa":
        return f"{D.authors.linked.mean():.1%}", ("저자 중 문과방목에 연결" if ko else "of authors linked to the examination roster")
    if mid == "d3_pub_lag":
        return f"{D.dcol.pub_lag.median():,.0f}", ("몰년에서 간행까지 햇수(중앙값)" if ko else "years from death to printing (median)")
    if mid == "d4_translation":
        return f"{D.dcol.n_translated.sum()/D.dcol.n_works.sum():.1%}", (f"편 중 번역문 연계 · 연계 0건 문집 {int((D.dcol.n_translated == 0).sum()):,}종" if ko else f"of works have a linked translation · {int((D.dcol.n_translated == 0).sum()):,} collections with none")
    if mid == "d5_punct":
        return f"{D.dcol.n_punct.sum()/D.dcol.n_works.sum():.1%}", ("편 중 교감표점 연계" if ko else "of works have a collated and punctuated edition")
    return "", ""


def reliability_card(m, D: Data, lang) -> str:
    t = T[lang]; kind = m["reliability"]; mid = m["id"]; ko = lang == "ko"
    head = {"exact": t["rel_exact"], "external-match": t["rel_ext"], "sampled-precision": t["rel_samp"]}[kind]
    body = []
    if "external" in m:
        body.append(f"<p>{esc(m['external'][lang])}</p>")
    if mid in ("a1_works", "a2_chars"):
        n_match = _n_match(D)
        body.append("<p>" + (f"검산: 문집 {n_match}종 전부에서 원본 XML 의 <내용> 문자 수 재계산과 일치, 문자 참조 잔존 0, 편 ID 중복 0." if ko else
                             f"Check: for all {n_match} collections the count equals an independent recount of every <내용> in the raw XML; zero residual character references; no duplicate work ids.") + "</p>")
    if mid == "a7_gwon":
        body.append("<p>" + (f"간략해제에 「n권 n책」이 있는 {len(D.gwon):,}종 중 목차의 卷n 수와 일치 {int(D.gwon.match.sum()):,}종({D.gwon.match.mean():.1%}). 불일치 160종의 원인은 코딩하지 않았다(표 참조)." if ko else
                             f"Of the {len(D.gwon):,} collections whose introduction states 'n fascicles, n volumes', {int(D.gwon.match.sum()):,} ({D.gwon.match.mean():.1%}) agree with the 卷n count of the table of contents; the causes of the 160 mismatches were not coded (see the table).") + "</p>")
    if mid == "d1_dates":
        a = D.authors; agree = a.death_agrees.dropna()
        body.append("<p>" + (f"한국역대인명정보에 성명+생년(P1 {int((a.persons_rule == 'P1').sum()):,}명) 또는 성명+호(P2 {int((a.persons_rule == 'P2').sum()):,}명)로 연결되어 몰년을 비교할 수 있는 {len(agree):,}명 중 일치 {int(agree.sum()):,}명({agree.mean():.1%})." if ko else
                             f"Of the {len(agree):,} authors matched to the AKS person database (P1 by name and birth year, {int((a.persons_rule == 'P1').sum()):,}; P2 by name and pen name, {int((a.persons_rule == 'P2').sum()):,}) whose death year can be compared, {int(agree.sum()):,} ({agree.mean():.1%}) agree.") + "</p>")
    g = D.precision.get("genre"); blk = D.precision.get("genre_block_note")
    if m["series"] == "B" and g:
        body.append("<p>" + (f"분류 품질: 저자 글 층화 표본 {g['n']}편(대분류 × 세기)을 제목으로 블라인드 코딩한 결과 고전번역원 대분류와 일치 {g['precision']:.1%} (윌슨 95% {g['ci_lo']:.1%}–{g['ci_hi']:.1%}; 판단 유보 {g['undecided']}건은 불일치로 셈" + (f"; 그중 {D.precision['genre_recode']['n']}편을 다른 코더가 블라인드로 다시 코딩해 일치 {D.precision['genre_recode']['agreement']:.0%}" if D.precision.get('genre_recode') else "") + ")." if ko else
                             f"Classification quality: a stratified sample of {g['n']} own works (major class × century) was blind-coded from titles; {g['precision']:.1%} agree with the ITKC major class (Wilson 95% {g['ci_lo']:.1%}–{g['ci_hi']:.1%}; {g['undecided']} undecided counted as disagreement" + (f"; a second coder re-coded {D.precision['genre_recode']['n']} of them blind with {D.precision['genre_recode']['agreement']:.0%} agreement" if D.precision.get('genre_recode') else "") + ").") +
                    ((f" 알려진 덩어리 오류: 『{blk['title_ko']}』({blk['collection_id']})의 冊文類 {blk['n_works']:,}편은 제목이 시다 — 고전번역원 분류대로 두고 여기 적는다." if ko else f" Known block error: {blk['n_works']:,} works of {_title_hj(D, blk['collection_id'])} ({blk['collection_id']}) filed as 冊文類 carry poem titles; they are left as classified and noted here.") if blk else "") + "</p>")
    key = {"c1_recipients": "recipients", "c2_epitaph_subjects": "epitaphs"}.get(mid)
    p = D.precision.get(key) if key else None
    if kind == "sampled-precision":
        if mid == "d2_munkwa":
            j = D.precision.get("munkwa_jaho"); h = D.precision.get("munkwa")
            body.append("<p>" + ((f"연결 정밀도의 1차 계획(간략해제의 급제 서술과 대조)은 신호가 없었다 — 해제 표본 {h['n']+h.get('unclear',0)+h.get('recall_n',0)}건 중 급제를 적은 것이 1건뿐이다. 대신 서지의 자·호와 방목의 자·호가 양쪽에 있는 연결 저자 {j['n']}명(연결 613명 중 비교 가능한 부분집합; M2 2명은 연결에 쓴 자·호를 다시 비교)에서 하나라도 같은 비율 {j['rate']:.1%} ({j['agree']}명; 불일치 {j['n']-j['agree']}명은 이체자·별호 차이를 포함). 전체 연결의 독립 정밀도는 아니다." if h else "") if ko else
                                 (f"The first plan for linkage precision (checking the examination statement in the short introductions) gave no signal: only 1 of {h['n']+h.get('unclear',0)+h.get('recall_n',0)} sampled introductions mentions a pass. Instead, among the {j['n']} linked authors whose courtesy or pen name is given on both sides (a comparable subset of the 613; for the 2 M2 links the same names were used for linking), {j['rate']:.1%} ({j['agree']}) agree on at least one; the {j['n']-j['agree']} disagreements include variant characters and alternative pen names. This is not an independent precision for all links." if h else "")) + "</p>")
        elif p:
            design = {"recipients": ("파싱된 서간 300편 + 파싱 안 된 60편(두 층, 가중 없음)" if ko else "300 parsed and 60 unparsed letters (two strata, unweighted)"),
                      "epitaphs": ("단순무작위 200편(그중 패턴 일치 194편이 정밀도 분모)" if ko else "a simple random sample of 200 (194 with a pattern match form the precision denominator)")}[key]
            body.append("<p>" + (f"표본 {design}을 코딩해 잰 정밀도 {p['precision']:.1%} ({p['yes']}/{p['n']}, 윌슨 95% {p['ci_lo']:.1%}–{p['ci_hi']:.1%})" + (f"; 비가중 표본 재현율 {p['recall']:.1%}(코더가 이름을 찾은 {p['recall_n']}건 중)" if p.get('recall') is not None else "") + ". 코드북과 판정 전체는 데이터 면에." if ko else
                                 f"Precision {p['precision']:.1%} ({p['yes']}/{p['n']}, Wilson 95% {p['ci_lo']:.1%}–{p['ci_hi']:.1%}) on {design}" + (f"; unweighted sample recall {p['recall']:.1%} (of {p['recall_n']} with a coder-found name)" if p.get('recall') is not None else "") + ". Codebook and all judgments on the Data page.") + "</p>")
        else:
            body.append("<p>" + ("표본 코딩 진행 중 — 이 판에서는 파싱 결과의 건수만 싣는다." if ko else "Sample coding in progress; this version shows parsed counts only.") + "</p>")
    badge = {"exact": ("집계" if ko else "exact"), "external-match": ("외부 대조" if ko else "external"), "sampled-precision": ("표본 정밀도" if ko else "sampled")}[kind]
    return f'<div class="spec rel"><dl><dt>{t["reliability"]}</dt><dd><span class="badge">{esc(badge)}</span><b>{esc(head)}</b>{"".join(body)}</dd></dl></div>'


def top_bars(D, df, col, spec, lang, n=30, label_col=None, xlabel=""):
    df = df.copy()
    if "label_ko" not in df.columns:
        df = df.join(D.col[["label_ko", "label_en"]], how="left") if df.index.name == "collection_id" else df.merge(D.col[["collection_id", "label_ko", "label_en"]], on="collection_id", how="left")
    top = df.sort_values(col, ascending=False).head(n)
    return svg_bars([(D.label(r, lang), float(r[col]), 0) for _, r in top.iterrows()], spec, row_h=20, label_w=220, xlabel=xlabel)


def metric_figure(m, D: Data, lang) -> str:
    t = T[lang]; ko = lang == "ko"; mid = m["id"]; out = []
    cl = lambda c: century_label(c, lang)
    col = D.col.set_index("collection_id")
    if mid == "a1_works":
        out.append(fig(top_bars(D, col, "n_works", ",.0f", lang, xlabel=t["works"]), ("편 수 상위 30 문집." if ko else "The 30 collections with the most works.")))
        out.append(fig(svg_lines([cen_series(D.tot.reset_index(), "n_works", lang, ("편" if ko else "works"), 0), cen_series(D.tot.reset_index(), "n_own_works", lang, ("저자 글" if ko else "own works"), 1)], ",.0f", xstep=1), ("저자 생년 세기별 편 수." if ko else "Works by the author's birth century.")))
        out.append(table_html(col.reset_index().assign(series_l=lambda f: f.series.map(lambda v: series_label(v, lang))), [("label_" + lang, t["title"], None), ("author_" + ("ko" if ko else "hj"), t["author"], None), ("birth", t["birth"], None), ("series_l", t["series_col"], None), ("n_works", t["works"], ",.0f"), ("n_own_works", t["own"], ",.0f"), ("own_share", t["share"], ".1%")], "t_a1", lang))
    elif mid == "a2_chars":
        out.append(fig(top_bars(D, col, "chars", ",.0f", lang, xlabel=t["chars"]), ("글자 수 상위 30 문집(본문 + 주)." if ko else "The 30 collections with the most characters (text + notes).")))
        out.append(fig(svg_lines([cen_series(D.tot.reset_index(), "chars_main", lang, ("본문" if ko else "text"), 0), cen_series(D.tot.reset_index(), "chars_note", lang, ("주" if ko else "notes"), 1)], ",.0f", xstep=1), ("세기별 글자 수." if ko else "Characters by century.")))
        out.append(table_html(col.reset_index(), [("label_" + lang, t["title"], None), ("author_" + ("ko" if ko else "hj"), t["author"], None), ("chars_main", ("본문 글자" if ko else "text characters"), ",.0f"), ("chars_note", t["notes"], ",.0f"), ("note_share", ("주 비율" if ko else "note share"), ".1%"), ("chars_per_work_median", ("편당 글자 중앙값" if ko else "median per work"), ",.0f")], "t_a2", lang))
    elif mid == "a3_centuries":
        s = D.ser
        out.append(fig(svg_lines([cen_series(s[s.series == "정편"], "n_collections", lang, ("정편" if ko else "first series"), 0), cen_series(s[s.series == "속편"], "n_collections", lang, ("속편" if ko else "supplement"), 1)], ",.0f", xstep=1), ("저자 생년 세기별 문집 수, 정편·속편." if ko else "Collections by the author's birth century, first series and supplement.")))
        tbl = D.cen.copy(); tbl["century"] = tbl.birth_century.map(cl); tbl["series_l"] = tbl.series.map(lambda v: series_label(v, lang))
        out.append(table_html(tbl, [("century", t["century"], None), ("series_l", t["series_col"], None), ("n_collections", t["collections"], ",.0f"), ("n_authors", t["authors"], ",.0f"), ("n_works", t["works"], ",.0f"), ("chars", t["chars"], ",.0f")], "t_a3", lang, filt=False))
    elif mid == "a4_chars_per_work":
        out.append(fig(svg_lines([cen_series(D.tot.reset_index(), "chars_per_work_median", lang, ("중앙값" if ko else "median"), 0), cen_series(D.tot.reset_index(), "chars_per_work_mean", lang, ("평균" if ko else "mean"), 1)], ",.0f", xstep=1), ("편당 글자 수, 세기별." if ko else "Characters per work by century.")))
    elif mid == "a5_note_share":
        out.append(fig(svg_lines([cen_series(D.tot.reset_index(), "note_share", lang, ("주 비율" if ko else "note share"), 0)], ".1%", xstep=1), ("전체 글자 중 주의 비율, 세기별." if ko else "Share of characters in notes by century.")))
        out.append(fig(top_bars(D, col, "note_share", ".1%", lang, xlabel=t["share"]), ("주 비율 상위 30 문집." if ko else "The 30 collections with the highest note share.")))
    elif mid == "a6_own_share":
        out.append(fig(svg_lines([cen_series(D.tot.reset_index(), "own_share", lang, ("저자 글 비율" if ko else "own-work share"), 0)], ".1%", xstep=1), ("저자 글 비율, 세기별." if ko else "Own-work share by century.")))
        low = col.sort_values("own_share").head(30)
        out.append(fig(svg_bars([(D.label(r, lang), float(r.own_share), 2) for _, r in low.iterrows()], ".1%", row_h=20, label_w=220), ("저자 글 비율이 낮은 30 문집 — 부록·타인 글이 많은 문집." if ko else "The 30 collections with the lowest own-work share — collections heavy with appendices and others' writing.")))
    elif mid == "a7_gwon":
        g = D.gwon.merge(D.col[["collection_id", "title_hj"]], on="collection_id", how="left")
        out.append(table_html(g, [(("title_ko" if ko else "title_hj"), t["title"], None), ("n_gwon_titles", ("목차 卷n 수" if ko else "卷n headings"), ",.0f"), ("haeje_gwon", ("해제 권수" if ko else "fascicles per introduction"), ",.0f"), ("haeje_chaek", ("해제 책수" if ko else "volumes per introduction"), ",.0f"), ("match", ("일치" if ko else "match"), ",.0f")], "t_a7", lang))
    elif mid in ("b1_poetry_share", "b3_letters_share", "b4_memorials_share", "b6_prefaces_share"):
        g = {"b1_poetry_share": "詩類", "b3_letters_share": "書簡類", "b4_memorials_share": "公車類", "b6_prefaces_share": "序跋類"}[mid]
        b = D.b[D.b.genre1 == g]; ba = D.b_all[D.b_all.genre1 == g]
        out.append(fig(svg_lines([cen_series(b, "share_works", lang, ("편 기준" if ko else "by works"), 0), cen_series(b, "share_chars", lang, ("글자 기준" if ko else "by characters"), 1), cen_series(ba, "share_works", lang, ("편 기준, 타인 글 포함" if ko else "by works, incl. others"), 2)], ".1%", xstep=1), (f"{GENRE_KO[g]} 비중, 저자 생년 세기별." if ko else f"Share of {GENRE_EN[g]} by the author's birth century.")))
        bc = D.b_col.copy(); colname = f"share_works_{g}"
        bc = bc.merge(D.col[["collection_id", "label_ko", "label_en"]], on="collection_id", how="left")
        top = bc.sort_values(colname, ascending=False).head(30)
        out.append(fig(svg_bars([(D.label(r, lang), float(r[colname]), 0) for _, r in top.iterrows()], ".1%", row_h=20, label_w=220), (f"{GENRE_KO[g]} 비중 상위 30 문집(편 기준, 저자 글)." if ko else f"The 30 collections with the highest {GENRE_EN[g]} share (by works, own works).")))
        tbl = b.copy(); tbl["century_l"] = tbl.century.map(cl)
        out.append(table_html(tbl, [("century_l", t["century"], None), ("n_works", t["works"], ",.0f"), ("total_works", ("저자 글 전체" if ko else "own works"), ",.0f"), ("share_works", ("편 기준" if ko else "by works"), ".1%"), ("share_chars", ("글자 기준" if ko else "by characters"), ".1%")], "t_b", lang, filt=False))
    elif mid == "b2_genre_mix":
        series = [cen_series(D.b[D.b.genre1 == g], "share_works", lang, (GENRE_KO[g] if ko else GENRE_EN[g]), i % 4) for i, g in enumerate(GENRES)]
        out.append(fig(svg_lines(series, ".0%", xstep=1, height=380), ("7대분류의 편 기준 비중, 세기별(저자 글)." if ko else "Work-based share of the seven classes by century (own works).")))
        piv = D.b.pivot(index="century", columns="genre1", values="share_works").reindex(columns=GENRES).reset_index(); piv["century_l"] = piv.century.map(cl)
        out.append(table_html(piv, [("century_l", t["century"], None)] + [(g, (GENRE_KO[g] if ko else GENRE_EN[g]), ".1%") for g in GENRES], "t_b2", lang, filt=False))
        g2 = D.b2.groupby(["genre1", "genre2"]).n_works.sum().reset_index().sort_values("n_works", ascending=False)
        out.append("<h2>" + ("중분류" if ko else "Minor classes") + "</h2>" + table_html(g2, [("genre1", ("대분류" if ko else "major"), None), ("genre2", ("중분류" if ko else "minor"), None), ("n_works", t["works"], ",.0f")], "t_b2b", lang, filt=False))
    elif mid == "b5_relational_share":
        g2 = D.b2; sel = g2[(g2.genre1 == "哀祭類") | (g2.genre2.isin(["碑誌類", "行狀類"]))].groupby("century").n_works.sum()
        tot = g2.groupby("century").n_works.sum(); df = pd.DataFrame({"century": tot.index, "n": sel.reindex(tot.index).fillna(0).values, "total": tot.values}); df["share"] = df.n / df.total
        out.append(fig(svg_lines([cen_series(df, "share", lang, ("비중" if ko else "share"), 0)], ".1%", xstep=1), ("애제·비지·행장 비중, 세기별." if ko else "Share of elegies, epitaphs and biographies by century.")))
        df["century_l"] = df.century.map(cl)
        out.append(table_html(df, [("century_l", t["century"], None), ("n", t["works"], ",.0f"), ("total", ("저자 글 전체" if ko else "own works"), ",.0f"), ("share", t["share"], ".1%")], "t_b5", lang, filt=False))
    elif mid == "b7_other_share":
        out.append(fig(svg_lines([cen_series(D.other, "other_share", lang, ("기타류" if ko else "other"), 0)], ".1%", xstep=1), ("중분류 其他類의 비율, 세기별." if ko else "Share of works in 'other' minor classes by century.")))
    elif mid == "b8_poem_length":
        out.append(fig(svg_lines([cen_series(D.poems, "poem_chars_median", lang, ("중앙값" if ko else "median"), 0), cen_series(D.poems, "poem_chars_p25", lang, "p25", 2), cen_series(D.poems, "poem_chars_p75", lang, "p75", 2)], ",.0f", xstep=1), ("시 한 편의 본문 글자 수, 세기별 중앙값과 사분위." if ko else "Main-text characters per poem: median and quartiles by century.")))
        tbl = D.poems.copy(); tbl["century_l"] = tbl.century.map(cl)
        out.append(table_html(tbl, [("century_l", t["century"], None), ("n_poems", ("시 편 수" if ko else "poems"), ",.0f"), ("poem_chars_median", ("중앙값" if ko else "median"), ",.0f"), ("poem_chars_mean", ("평균" if ko else "mean"), ",.1f")], "t_b8", lang, filt=False))
    elif mid == "c1_recipients":
        L = D.letters.merge(D.col[["collection_id", "label_ko", "label_en"]], on="collection_id", how="left")
        top = L.sort_values("n_unique", ascending=False).head(30)
        out.append(fig(svg_bars([(D.label(r, lang), float(r.n_unique), 0) for _, r in top.iterrows()], ",.0f", row_h=20, label_w=220, xlabel=("수신자 문자열 고유 수" if ko else "distinct addressee strings")), ("수신자 고유 수 상위 30 문집." if ko else "The 30 collections with the most distinct addressees.")))
        out.append(table_html(L, [("label_" + lang, t["title"], None), ("n_letters", t["letters"], ",.0f"), ("parse_rate", ("파싱 성공" if ko else "parsed"), ".0%"), ("n_unique", ("고유 수신자" if ko else "distinct addressees"), ",.0f"), ("top1_share", ("1위 점유" if ko else "top-1 share"), ".1%"), ("top3_share", ("상위 3 점유" if ko else "top-3 share"), ".1%"), ("hhi", "HHI", ".3f")], "t_c1", lang))
        cc = D.c_cen.copy(); cc["century_l"] = cc.century.map(cl)
        out.append("<h2>" + ("세기별" if ko else "By century") + "</h2>" + table_html(cc, [("century_l", t["century"], None), ("n_letters", t["letters"], ",.0f"), ("n_unique", ("고유 수신자" if ko else "distinct addressees"), ",.0f"), ("top3_share", ("상위 3 점유" if ko else "top-3 share"), ".1%")], "t_c1c", lang, filt=False))
    elif mid == "c2_epitaph_subjects":
        E = D.epi.merge(D.col[["collection_id", "label_ko", "label_en"]], on="collection_id", how="left")
        top = E.sort_values("n_epitaphs", ascending=False).head(30)
        out.append(fig(svg_bars([(D.label(r, lang), float(r.n_epitaphs), 0) for _, r in top.iterrows()], ",.0f", row_h=20, label_w=220, xlabel=t["epitaphs"]), ("비지·행장 편 수 상위 30 문집." if ko else "The 30 collections with the most epitaphs and biographies.")))
        cols = [("label_" + lang, t["title"], None), ("n_epitaphs", t["epitaphs"], ",.0f"), ("n_parsed", ("파싱" if ko else "parsed"), ",.0f"), ("subj_n_unique", ("고유 피장자" if ko else "distinct subjects"), ",.0f")] + [(k, k, ",.0f") for k in ("碑誌類", "行狀類") if k in E.columns]
        out.append(table_html(E, cols, "t_c2", lang))
    elif mid == "c3_other_writers":
        Wr = D.writers.merge(D.col[["collection_id", "label_ko", "label_en"]], on="collection_id", how="left")
        top = Wr.sort_values("n_other_writers", ascending=False).head(30)
        out.append(fig(svg_bars([(D.label(r, lang), float(r.n_other_writers), 0) for _, r in top.iterrows()], ",.0f", row_h=20, label_w=220), ("타인 필자 수 상위 30 문집." if ko else "The 30 collections with the most other writers.")))
        out.append(table_html(Wr, [("label_" + lang, t["title"], None), ("n_other_works", ("타인 편" if ko else "works by others"), ",.0f"), ("n_other_writers", ("타인 필자" if ko else "other writers"), ",.0f"), ("top_writers", ("최다 필자(편)" if ko else "most frequent (works)"), None)], "t_c3", lang))
    elif mid in ("d1_dates", "d2_munkwa", "d3_pub_lag", "d4_translation", "d5_punct"):
        dc = D.dcen.copy(); dc["century_l"] = dc.century.map(cl)
        if mid == "d1_dates":
            dc["death_share"] = dc.death_known / dc.n_authors
            out.append(fig(svg_lines([cen_series(dc, "death_share", lang, ("몰년 있음" if ko else "death year known"), 0)], ".0%", xstep=1), ("몰년이 있는 저자 비율, 세기별." if ko else "Share of authors with a death year by century.")))
            out.append(fig(svg_lines([cen_series(dc, "lifespan_median", lang, ("수명 중앙값" if ko else "median lifespan"), 1)], ",.0f", xstep=1), ("수명 중앙값(몰년 − 생년), 세기별." if ko else "Median lifespan (death − birth) by century.")))
            out.append(table_html(dc, [("century_l", t["century"], None), ("n_authors", t["authors"], ",.0f"), ("birth_known", ("생년 있음" if ko else "birth known"), ",.0f"), ("death_known", ("몰년 있음" if ko else "death known"), ",.0f"), ("lifespan_median", ("수명 중앙값" if ko else "median lifespan"), ",.0f")], "t_d1", lang, filt=False))
        elif mid == "d2_munkwa":
            out.append(fig(svg_lines([cen_series(dc, "link_rate", lang, ("연결률" if ko else "linkage"), 0), cen_series(dc, "link_rate_strict", lang, ("성명+생년만" if ko else "name + birth only"), 2)], ".0%", xstep=1), ("문과방목 연결률, 세기별." if ko else "Examination-roster linkage by century.")))
            out.append(fig(svg_lines([cen_series(dc, "exam_age_median", lang, ("급제 연령 중앙값" if ko else "median age at passing"), 1), cen_series(dc, "exam_age_p25", lang, "p25", 2), cen_series(dc, "exam_age_p75", lang, "p75", 2)], ",.0f", xstep=1), ("연결된 저자의 급제 연령(세는나이), 세기별." if ko else "Age at passing (East Asian reckoning) of linked authors by century.")))
            out.append(table_html(dc, [("century_l", t["century"], None), ("n_authors", t["authors"], ",.0f"), ("n_linked", ("연결" if ko else "linked"), ",.0f"), ("link_rate", ("연결률" if ko else "linkage"), ".1%"), ("n_ambiguous", ("동명 미확정" if ko else "ambiguous"), ",.0f"), ("exam_age_median", ("급제 연령 중앙값" if ko else "median age at passing"), ",.0f")], "t_d2", lang, filt=False))
            A = D.authors[D.authors.linked == 1].sort_values("exam_year")
            out.append("<h2>" + ("연결된 저자" if ko else "Linked authors") + "</h2>" + table_html(A, [("author_" + ("ko" if ko else "hj"), t["author"], None), ("birth", t["birth"], ".0f"), ("exam_year", ("시험년" if ko else "exam year"), ".0f"), ("exam_age", ("급제 연령" if ko else "age"), ".0f"), ("munkwa_bon", ("본관" if ko else "clan seat"), None), ("munkwa_rule", ("규칙" if ko else "rule"), None)], "t_d2a", lang))
        elif mid == "d3_pub_lag":
            out.append(fig(svg_lines([cen_series(dc, "pub_lag_median", lang, ("중앙값" if ko else "median"), 0), cen_series(dc, "pub_lag_p25", lang, "p25", 2), cen_series(dc, "pub_lag_p75", lang, "p75", 2)], ",.0f", xstep=1), ("몰년에서 간행까지 햇수, 세기별." if ko else "Years from death to printing by century.")))
            out.append(table_html(dc, [("century_l", t["century"], None), ("n_collections", t["collections"], ",.0f"), ("pub_year_known", ("간행년 있음" if ko else "year known"), ",.0f"), ("pub_lag_median", ("중앙값" if ko else "median"), ",.0f"), ("pub_lag_p25", "p25", ",.0f"), ("pub_lag_p75", "p75", ",.0f")], "t_d3", lang, filt=False))
            dl = D.dcol.merge(D.col[["collection_id", "label_ko", "label_en"]], on="collection_id", how="left")
            out.append("<h2>" + ("문집별" if ko else "By collection") + "</h2>" + table_html(dl, [("label_" + lang, t["title"], None), ("death", t["death"], ".0f"), ("pub_year", t["pub"], ".0f"), ("pub_lag", ("시차(년)" if ko else "lag (years)"), ",.0f")], "t_d3c", lang))
        elif mid in ("d4_translation", "d5_punct"):
            c = "translation_share" if mid == "d4_translation" else "punct_share"
            out.append(fig(svg_lines([cen_series(dc, c, lang, ("비율" if ko else "share"), 0)], ".0%", xstep=1), (("번역문 연계 편 비율, 세기별." if mid == "d4_translation" else "교감표점 연계 편 비율, 세기별.") if ko else ("Share of works linked to a translation, by century." if mid == "d4_translation" else "Share of works linked to a collated and punctuated edition, by century."))))
            cols = [("century_l", t["century"], None), ("n_collections", t["collections"], ",.0f"), ("n_works", t["works"], ",.0f"), (c, t["share"], ".1%")] + ([("collections_no_translation", ("번역 0건 문집" if ko else "no translation"), ",.0f"), ("collections_full_translation", ("전편 번역 문집" if ko else "fully translated"), ",.0f")] if mid == "d4_translation" else [])
            out.append(table_html(dc, cols, "t_d4", lang, filt=False))
    return "".join(out)


# ----------------------------------------------------------------- pages
def metric_page(m, D, lang):
    t = T[lang]; L = m[lang]
    hv, hl = headline(m, D, lang)
    body = [f'<div class="eyebrow"><span class="tag layer">{esc(SERIES[m["series"]][lang])}</span><span class="tag">{esc(UNIT_KO.get(m["unit"], m["unit"]) if lang == "ko" else m["unit"])}</span></div>',
            f'<div class="mhero"><div><h1>{esc(L["name"])}</h1><p class="lead">{esc(L["definition"])}</p></div><div class="big">{esc(hv)}<small>{esc(hl)}</small></div></div>']
    if m["id"] in TAKE:
        body.append(take_block(TAKE[m["id"]][lang], lang))
    body += ['<div class="spec"><dl>', f'<dt>{t["formula"]}</dt><dd class="formula">{esc(L["formula"])}</dd>']
    if L.get("reading"):
        body.append(f'<dt>{t["reading"]}</dt><dd>{esc(L["reading"])}</dd>')
    body.append(f'<dt>{t["caveat"]}</dt><dd>{esc(L["caveat"])}</dd>')
    if "external" in m:
        body.append(f'<dt>{t["external"]}</dt><dd>{esc(m["external"][lang])}</dd>')
    body.append("</dl></div>")
    body.append(reliability_card(m, D, lang))
    body.append(metric_figure(m, D, lang))
    body.append(f'<p class="files"><a href="../../data/{m["table"]}.csv">{t["download"]}: {m["table"]}.csv</a></p>')
    return page(lang, L["name"], "".join(body), depth=2, desc=L["definition"], active="metrics", rel=f"metrics/{m['id']}.html", leaf=metric_leaf(lang, m["id"]))


def metrics_index(D, lang):
    t = T[lang]; ko = lang == "ko"
    body = [f"<h1>{t['metric_list']}</h1>", '<p class="src" style="max-width:80ch">' + (("「저자 글」은 필자 태그가 문집의 저자와 같은 편(609,494편), 「타인 글」은 같은 문집에 실린 남의 서문·발문·행장·만사다. 세기는 저자 생년 기준. 지표마다 정의·공식·한계와 신뢰도 카드가 있다." if ko else
            "'Own works' are works whose writer tag is the collection's author (609,494); 'works by others' are prefaces, postscripts, biographies and elegies printed in the same collection. Centuries follow the author's birth year. Every metric page gives a definition, a formula, caveats and a reliability card.")) + "</p>"]
    for s, sl in SERIES.items():
        body.append(f"<h2>{esc(sl[lang])}</h2><p class='src' style='max-width:80ch'>{esc(SERIES_INTRO[s][lang])}</p><div class='cards'>")
        for m in METRICS:
            if m["series"] == s:
                hv, hl = headline(m, D, lang)
                body.append(f'<a class="card s-{s}" href="{m["id"]}.html"><b>{esc(m[lang]["name"])}</b><span class="kv">{esc(hv)}<small>{esc(hl)}</small></span><small>{esc(m[lang]["definition"])}</small></a>')
        body.append("</div>")
    return page(lang, t["metric_list"], "".join(body), depth=2, active="metrics", rel="metrics/index.html")


def collection_page(r, D, lang, is_person=False):
    t = T[lang]; ko = lang == "ko"; cid = r.collection_id
    bc = D.b_col[D.b_col.collection_id == cid]; bc = bc.iloc[0] if len(bc) else None
    L = D.letters[D.letters.collection_id == cid]; L = L.iloc[0] if len(L) else None
    E = D.epi[D.epi.collection_id == cid]; E = E.iloc[0] if len(E) else None
    dl = D.dcol[D.dcol.collection_id == cid].iloc[0]
    a = D.authors[D.authors.author_id == f"{r.author_hj}_{int(r.birth) if not pd.isna(r.birth) else 'x'}"]; a = a.iloc[0] if len(a) else None
    title = f"{r.title_ko}({r.title_hj})" if ko else f"{r.title_hj} ({r.title_ko})"
    sub = (f"{r.author_ko}({r.author_hj}) · {fmt(r.birth, '.0f')}~{fmt(r.death, '.0f')} · {r.series} 제{r.jip_start[1:].lstrip('0')}~{r.jip_end[1:].lstrip('0')}집" if ko else
           f"{r.author_hj} ({r.author_ko}) · {fmt(r.birth, '.0f')}–{fmt(r.death, '.0f')} · {'first series' if r.series == '정편' else 'supplement'} vols. {r.jip_start[1:].lstrip('0')}–{r.jip_end[1:].lstrip('0')}")
    body = [f'<div class="eyebrow"><span class="tag">{esc(cid)}</span><span class="tag">{esc(century_label(r.birth_century, lang))}</span>' + ('<span class="tag layer">' + ("인물 면" if ko else "person page") + '</span>' if is_person else "") + '</div>',
            f'<h1>{esc(title)}</h1><p class="lead">{esc(sub)}</p>']
    if is_person and cid in PAGE_TAKE:
        body.append(take_block(PAGE_TAKE[cid][lang], lang))
    stats = [(t["works"], f"{int(r.n_works):,}"), (t["own"], f"{int(r.n_own_works):,}"), (t["chars"], f"{int(r.chars):,}"), (("주 비율" if ko else "note share"), f"{r.note_share:.1%}"),
             (("권(卷n)" if ko else "fascicles"), f"{int(r.n_gwon_titles)}"), (t["pub"], fmt(r.pub_year, ".0f") or "—")]
    body.append('<div class="stats">' + "".join(f'<div class="stat"><div class="n">{v}</div><small>{k}</small></div>' for k, v in stats) + "</div>")
    # genre mix bars
    if bc is not None:
        items = [((GENRE_KO[g] if ko else GENRE_EN[g]), float(bc[f"share_works_{g}"]), i % 4) for i, g in enumerate(GENRES)]
        body.append("<h2>" + ("문체 구성(저자 글, 편 기준)" if ko else "Genre mix (own works, by works)") + "</h2>" + fig(svg_bars(items, ".1%", row_h=22, label_w=200), ("7대분류 비중. 전체 분포 안의 위치는 지표 면 참조." if ko else "Share of the seven classes; see the metric pages for the position within the whole distribution.")))
    rows = []
    def pct(col_df, col, v):
        s = col_df[col].dropna()
        return float((s < v).mean()) if len(s) else float("nan")
    for name, v, col_df, col, spec in [(("시 비중" if ko else "poetry share"), bc[f"share_works_詩類"] if bc is not None else float("nan"), D.b_col, "share_works_詩類", ".1%"),
                                        (("서간 비중" if ko else "letter share"), bc[f"share_works_書簡類"] if bc is not None else float("nan"), D.b_col, "share_works_書簡類", ".1%"),
                                        (("편당 글자 중앙값" if ko else "median characters per work"), r.chars_per_work_median, D.col, "chars_per_work_median", ",.0f"),
                                        (("저자 글 비율" if ko else "own-work share"), r.own_share, D.col, "own_share", ".1%"),
                                        (("번역문 연계 비율" if ko else "linked-translation share"), dl.translation_share, D.dcol, "translation_share", ".1%")]:
        rows.append((name, v, pct(col_df, col, v), spec))
    body.append("<h2>" + ("이 문집의 지표" if ko else "Metrics for this collection") + "</h2><div class='wrap'><table><thead><tr><th>" + ("지표" if ko else "Metric") + f"</th><th class='num'>{cap(t['ours'], lang)}</th><th class='num'>" + ("백분위(전체 문집 중)" if ko else "Percentile among all collections") + "</th></tr></thead><tbody>" +
                "".join(f"<tr><td>{esc(n)}</td><td class='num'>{fmt(v, sp)}</td><td class='num'>{fmt(p, '.0%')}</td></tr>" for n, v, p, sp in rows) + "</tbody></table></div>")
    if L is not None and L.n_letters > 0:
        rc = D.recip[D.recip.collection_id == cid]
        body.append("<h2>" + ("서간" if ko else "Letters") + "</h2><p>" + (f"저자의 서간 {int(L.n_letters):,}편, 제목 파싱 {L.parse_rate:.0%}, 수신자 문자열 고유 {int(L.n_unique):,}, 상위 3 점유 {fmt(L.top3_share, '.1%')}." if ko else
                                                                       f"{int(L.n_letters):,} letters by the author; {L.parse_rate:.0%} of titles parsed; {int(L.n_unique):,} distinct addressee strings; top-3 share {fmt(L.top3_share, '.1%')}.") + "</p>")
        if len(rc):
            body.append(table_html(rc, [("recipient_raw", t["recipients"], None), ("n", t["letters"], ",.0f")], "t_rc", lang, filt=False))
    if E is not None and E.n_epitaphs > 0:
        body.append("<h2>" + ("비지·행장" if ko else "Epitaphs and biographies") + "</h2><p>" + (f"저자가 쓴 비지·행장 {int(E.n_epitaphs):,}편, 제목 파싱 {int(E.n_parsed):,}편, 피장자 문자열 고유 {int(E.subj_n_unique):,}." if ko else
                                                                                   f"{int(E.n_epitaphs):,} epitaphs and biographies by the author; {int(E.n_parsed):,} titles parsed; {int(E.subj_n_unique):,} distinct subject strings.") + "</p>")
    if a is not None:
        has_age = not pd.isna(a.exam_age)
        link = (f"문과방목 연결: {a.munkwa_rule} — {fmt(a.exam_year, '.0f')}년 {a.exam_name} ({a.munkwa_bon})" + (f", 급제 연령 {fmt(a.exam_age, '.0f')}세" if has_age else "") + "." if a.linked == 1 else "문과방목에 연결되지 않음(급제 기록 없음 또는 미확정).") if ko else \
               (f"Examination roster: rule {a.munkwa_rule} — passed {fmt(a.exam_year, '.0f')} ({a.exam_name}, clan seat {a.munkwa_bon})" + (f", age {fmt(a.exam_age, '.0f')}" if has_age else "") + "." if a.linked == 1 else "Not linked to the examination roster (no record found, or ambiguous).")
        body.append("<h2>" + cap(t["author"], lang) + f"</h2><p>{esc(link)} " + (f"한국역대인명정보: {a.persons_rule}" + (f", 몰년 일치" if a.death_agrees == 1 else (", 몰년 불일치" if a.death_agrees == 0 else "")) + "." if ko else f"AKS persons: {a.persons_rule}" + (", death year agrees" if a.death_agrees == 1 else (", death year differs" if a.death_agrees == 0 else "")) + ".") + "</p>")
    body.append(f'<p class="links"><a href="{ITKC}{esc(cid)}">{t["itkc_link"]}</a></p>')
    return page(lang, title, "".join(body), depth=2, active="persons" if is_person else "collections", rel=f"collections/{cid}.html", leaf=person_leaf(D, lang, cid) if is_person else None)


def collections_index(D, lang):
    t = T[lang]; ko = lang == "ko"
    df = D.col.sort_values(["birth", "collection_id"]).copy()
    df["link"] = df.collection_id
    body = [f"<h1>{t['collection_list']}</h1>", '<p class="src">' + (f"{len(df):,}종. 서명을 누르면 문집 면으로 간다. 열 머리글을 누르면 정렬된다." if ko else f"{len(df):,} collections. Click a title for its page, a column header to sort.") + "</p>"]
    # custom table with links
    cols = [("title", t["title"]), ("author", t["author"]), ("birth", t["birth"]), ("death", t["death"]), ("series", t["series_col"]), ("n_works", t["works"]), ("chars", t["chars"]), ("poetry", ("시 비중" if ko else "poetry"))]
    bc = D.b_col.set_index("collection_id")["share_works_詩類"]
    out = [f'<div class="filter"><input placeholder="{t["search"]}…" data-target="t_all"></div><div class="wrap"><table class="sort fixed" id="t_all"><thead><tr>' + "".join(f'<th{" class=\"num\"" if c in ("n_works", "chars", "poetry") else ""}>{esc(cap(h, lang))}</th>' for c, h in cols) + "</tr></thead><tbody>"]
    for _, r in df.iterrows():
        p = bc.get(r.collection_id, float("nan"))
        out.append(f'<tr><td><a href="{r.collection_id}.html">{esc(r.title_ko if ko else r.title_hj)}</a></td><td>{esc(r.author_ko if ko else r.author_hj)}</td><td>{fmt(r.birth, ".0f")}</td><td>{fmt(r.death, ".0f")}</td><td>{esc(r.series if ko else ("first" if r.series == "정편" else "suppl."))}</td>'
                   f'<td class="num" data-v="{r.n_works}">{fmt(float(r.n_works), ",.0f")}</td><td class="num" data-v="{r.chars}">{fmt(float(r.chars), ",.0f")}</td><td class="num" data-v="{p}">{fmt(p, ".0%")}</td></tr>')
    out.append("</tbody></table></div>")
    body.append("".join(out))
    return page(lang, t["collection_list"], "".join(body), depth=2, active="collections", rel="collections/index.html")


def century_page(c, D, lang):
    t = T[lang]; ko = lang == "ko"; cl = century_label(c, lang)
    tot = D.tot.loc[c]; cols = D.col[D.col.birth_century == c].sort_values("n_works", ascending=False)
    b = D.b[D.b.century == c].set_index("genre1").reindex(GENRES)
    dc = D.dcen[D.dcen.century == c].iloc[0] if (D.dcen.century == c).any() else None
    body = [f'<div class="eyebrow"><span class="tag">{esc(cl)}</span></div><h1>{esc(cl)}</h1>']
    stats = [(t["collections"], f"{int(tot.n_collections):,}"), (t["authors"], f"{int(tot.n_authors):,}"), (t["works"], f"{int(tot.n_works):,}"), (t["chars"], f"{int(tot.chars):,}"),
             (("시 비중" if ko else "poetry share"), fmt(float(b.loc["詩類", "share_works"]) if not pd.isna(b.loc["詩類", "share_works"]) else float("nan"), ".1%")),
             (("문과 연결률" if ko else "exam linkage"), fmt(float(dc.link_rate), ".0%") if dc is not None else "—")]
    body.append('<div class="stats">' + "".join(f'<div class="stat"><div class="n">{v}</div><small>{k}</small></div>' for k, v in stats) + "</div>")
    items = [((GENRE_KO[g] if ko else GENRE_EN[g]), float(b.loc[g, "share_works"]) if not pd.isna(b.loc[g, "share_works"]) else float("nan"), i % 4) for i, g in enumerate(GENRES)]
    body.append("<h2>" + ("문체 구성(저자 글, 편 기준)" if ko else "Genre mix (own works, by works)") + "</h2>" + fig(svg_bars(items, ".1%", row_h=22, label_w=200), ""))
    body.append("<h2>" + ("이 세기 출생 저자의 문집" if ko else "Collections by authors born in this century") + "</h2>")
    out = ['<div class="wrap"><table class="sort fixed"><thead><tr><th>' + cap(t["title"], lang) + "</th><th>" + cap(t["author"], lang) + "</th><th>" + cap(t["birth"], lang) + f'</th><th class="num">{cap(t["works"], lang)}</th><th class="num">{cap(t["chars"], lang)}</th></tr></thead><tbody>']
    for _, r in cols.iterrows():
        out.append(f'<tr><td><a href="../collections/{r.collection_id}.html">{esc(r.title_ko if ko else r.title_hj)}</a></td><td>{esc(r.author_ko if ko else r.author_hj)}</td><td>{fmt(r.birth, ".0f")}</td><td class="num" data-v="{r.n_works}">{fmt(float(r.n_works), ",.0f")}</td><td class="num" data-v="{r.chars}">{fmt(float(r.chars), ",.0f")}</td></tr>')
    out.append("</tbody></table></div>")
    body.append("".join(out))
    return page(lang, cl, "".join(body), depth=2, active="centuries", rel=f"centuries/{int(c)}.html")


def centuries_index(D, lang):
    t = T[lang]; ko = lang == "ko"
    tot = D.tot.reset_index(); tot = tot[tot.birth_century.notna()]
    body = [f"<h1>{t['century_list']}</h1>", '<p class="src">' + ("세기는 저자 생년 기준이다. 간행은 대개 그보다 늦다." if ko else "Centuries follow the author's birth year; printing usually came later.") + "</p>",
            fig(svg_bars([(century_label(r.birth_century, lang), float(r.n_collections), 0) for _, r in tot.iterrows()], ",.0f", row_h=22, label_w=160, xlabel=t["collections"]), ("세기별 문집 수." if ko else "Collections per century.")), "<div class='cards'>"]
    for _, r in tot.iterrows():
        c = int(r.birth_century)
        body.append(f'<a class="card s-A" href="{c}.html"><b>{esc(century_label(c, lang))}</b><small>{int(r.n_collections):,} {t["collections"]} · {int(r.n_authors):,} {t["authors"]} · {int(r.n_works):,} {t["works"]}</small></a>')
    body.append("</div>")
    return page(lang, t["century_list"], "".join(body), depth=2, active="centuries", rel="centuries/index.html")


def persons_page(D, lang):
    t = T[lang]; ko = lang == "ko"
    body = [f"<h1>{t['person_list']}</h1>", '<p class="src">' + ("대표 저작가 열 사람의 문집 면. 수치는 문집 면과 같고 전체 분포 안의 백분위를 붙였다. 평가는 하지 않는다." if ko else "Collection pages of ten major authors, with each number's percentile among all collections. No evaluation is offered.") + "</p>", "<div class='cards'>"]
    for hj, nko, nen in PERSON_PAGES:
        rr = D.col[D.col.title_hj == hj]
        if not len(rr):
            continue
        r = rr.iloc[0]
        body.append(f'<a class="card s-D" href="collections/{r.collection_id}.html"><b>{esc(nko if ko else nen)} — {esc(r.title_ko + "(" + hj + ")" if ko else hj)}</b><small>{fmt(r.birth, ".0f")}{"~" if ko else "–"}{fmt(r.death, ".0f")} · {int(r.n_works):,}{"" if ko else " "}{t["works"]} · {int(r.chars):,} {t["chars"]}</small></a>')
    body.append("</div>")
    return page(lang, t["person_list"], "".join(body), depth=1, active="persons", rel="persons.html")


def home(D, lang):
    t = T[lang]; ko = lang == "ko"
    p = D.b[D.b.genre1 == "詩類"]; poetry = p.n_works.sum() / p.total_works.sum()
    stats = [(f"{len(D.col):,}", ("문집" if ko else "collections"), "collections/index.html"),
             (f"{int(D.col.n_works.sum()):,}", ("편" if ko else "works"), "metrics/a1_works.html"),
             (f"{D.col.chars.sum()/1e6:.0f}M", ("한자" if ko else "characters"), "metrics/a2_chars.html"),
             (f"{poetry:.0%}", ("저자 글 중 시" if ko else "of authors' own works are poetry"), "metrics/b1_poetry_share.html"),
             (f"{D.authors.linked.mean():.0%}", ("저자 중 문과방목에 연결" if ko else "of authors linked to the exam roster"), "metrics/d2_munkwa.html")]
    scope = ("범위는 공공데이터포털 한국문집총간 목록 1,251항목 중 채택한 1,249종(정편 663·속편 586)이다. 번역문·한국고전종합DB 웹 콘텐츠는 쓰지 않았고, 원문 전문은 싣지 않는다 — 편마다 고전종합DB 로 연결한다. 세기는 저자 생년 기준이다."
             if ko else
             "Scope: 1,249 collections (first series 663, supplement 586) adopted from the 1,251 Hanguk munjip chonggan entries on data.go.kr. Translations and the ITKC website content are not used, and no full text is reproduced; each work links to the ITKC database. Centuries follow the author's birth year.")
    intro = (("<b>무엇을 셌나.</b> 한국고전번역원이 영인·입력한 『한국문집총간』 1,249종의 원문 XML 전문을 편(시 한 수·편지 한 통·묘지명 한 편 — 고전번역원이 끊은 최종 단위) 단위로 나누어 637,203편을 만들고, 편마다 제목·필자·문체분류(고전번역원 부여)·글자 수(본문/주)·번역문 연계 유무를 세었다. "
              "문집에는 저자 자신의 글 외에 남이 쓴 서문·발문·행장·만사가 함께 실리므로, 필자 태그가 문집의 저자와 같은 편을 <b>저자 글</b>(609,494편, 95.7%), 나머지를 <b>타인 글</b>로 나눈다. 문체 비중 같은 지표는 저자 글만으로 낸다. "
              "본문의 어휘·주제는 분석하지 않았고 원문도 싣지 않는다 — 편마다 고전종합DB 로 연결한다. 세기는 저자 생년 기준이다. "
              "<b>쓸 수 있는 것:</b> 세기별 추이(지표 23면), 문집 1,249종 각각의 면과 순위표, 저자 10명의 인물 면, 모든 표의 CSV.")
             if ko else
             ("<b>What was counted.</b> The full XML text of the 1,249 collections of the Hanguk munjip chonggan (facsimile edition transcribed by the ITKC) was split into works — one poem, one letter, one epitaph, the ITKC's final unit — giving 637,203 works, each with its title, writer, genre class (assigned by the ITKC), character counts (text/notes) and translation links. "
              "A collection prints the author's writing together with prefaces, postscripts, biographies and elegies by others, so works whose writer tag is the collection's author are called <b>own works</b> (609,494, 95.7%) and the rest <b>works by others</b>; genre shares use own works only. "
              "Vocabulary and themes of the text were not analyzed and no text is reproduced; every work links to the ITKC database. Centuries follow the author's birth year. "
              "<b>What you can do here:</b> follow trends by century (23 metric pages), open a page for each of the 1,249 collections and a sortable list, read ten person pages, and download every table as CSV."))
    body = [f'<div class="hero"><div class="glyph" aria-hidden="true">文集</div><h1>{t["site"]}</h1><p class="lead">{esc(t["tagline"])}</p><p class="src" style="max-width:70ch">{esc(scope)}</p></div>',
            f'<div class="note" style="max-width:90ch">{intro}</div>']
    if HOME_FIVE.get(lang):
        body.append('<div class="take"><div class="l">' + ("핵심" if ko else "Key points") + '</div><p>' + "<br>".join(f"{i+1}. {esc(x)}" for i, x in enumerate(HOME_FIVE[lang])) + "</p></div>")
    body.append('<div class="stats">' + "".join(f'<a class="stat" href="{h}"><div class="n">{n}</div><small>{l}</small></a>' for n, l, h in stats) + "</div>")
    body.append('<div class="note">' + ("숫자마다 <b>신뢰도 카드</b>가 붙어 있다. 원본 XML에서 그대로 센 값인지, 선행 수치와 맞춰 본 값인지, 코딩한 표본에서 잰 정밀도인지를 지표 면마다 적었다." if ko else
                                       "Every number carries a <b>reliability card</b>: whether it was counted straight from the source XML, set against a published figure, or measured on a coded sample.") + "</div>")
    NUM = {"A": "1", "B": "2", "C": "3", "D": "4"}
    for s, sl in SERIES.items():
        body.append(f"<h2 class='num' data-n='{NUM[s]}'>{esc(sl[lang])}</h2><p class='src' style='max-width:80ch'>{esc(SERIES_INTRO[s][lang])}</p><div class='cards'>")
        for m in METRICS:
            if m["series"] == s:
                hv, hl = headline(m, D, lang)
                tk = blurb(TAKE[m["id"]][lang]) if m["id"] in TAKE else m[lang]["definition"]
                body.append(f'<a class="card s-{s}" href="metrics/{m["id"]}.html"><b>{esc(m[lang]["name"])}</b><span class="kv">{esc(hv)}<small>{esc(hl)}</small></span><small>{esc(tk)}</small></a>')
        body.append("</div>")
    tot = D.tot.reset_index(); tot = tot[tot.birth_century.notna()]
    body.append("<h2>" + t["century_list"] + "</h2>" + fig(svg_bars([(century_label(r.birth_century, lang), float(r.n_works), 0) for _, r in tot.iterrows()], ",.0f", row_h=20, label_w=160), ("세기별 편 수. 각 세기 면은 「세기」 메뉴." if ko else "Works per century; see the Centuries menu.")))
    return page(lang, t["site"], "".join(body), depth=1, active="home")


def prior_page(D, lang):
    t = T[lang]; ko = lang == "ko"
    body = [f"<h1>{t['nav_prior']}</h1>", '<p class="lead">' + ("새로 보탠 것과 모아 정리한 것을 가른다. 문체 구성의 통시 추이(곽지은 2026), 인물 1,258명 데이터셋(최혜미 2021), 미번역 291종(최채기 2020), XML 결함(최지연 외 2021)은 이미 있던 결과라 이 사이트의 재계산과 나란히 둔다. 수치는 원문에서 읽은 것만 싣는다." if ko else
                                                       "Separates what is new here from what was already measured: the genre-composition trend (Kwak 2026), the 1,258-person dataset (Choi 2021), the 291 untranslated collections (Choi 2020) and the XML defects (Choi et al. 2021) existed before and sit next to this site's recount. Only figures read from the original publications are included.") + "</p>"]
    for k, p in PRIOR.items():
        body.append(f'<div class="spec"><p>{esc(p[lang])}</p><p class="src">{esc(p.get("cite_en", p["cite"]) if lang == "en" else p["cite"])}</p></div>')
    return page(lang, t["nav_prior"], "".join(body), depth=1, active="prior", rel="prior.html")


DATA_FILES = ["works.csv.gz", "collections.csv", "authors.csv", "letters.csv.gz", "epitaphs.csv", "a_collections.csv", "a_centuries.csv", "a_gwon_check.csv",
              "b_centuries.csv", "b_centuries_all.csv", "b_centuries_series.csv", "b_collections.csv", "b_genre2.csv", "b_poems.csv", "b_other_share.csv",
              "c_letters.csv", "c_recipients.csv", "c_epitaphs.csv", "c_writers.csv", "c_centuries.csv", "d_centuries.csv", "d_authors.csv", "d_collections.csv", "reliability.json", "raw_manifest.json"]
GZIP = {"works.csv", "letters.csv"}


def data_page(D, lang, files):
    t = T[lang]; ko = lang == "ko"
    body = [f"<h1>{t['nav_data']}</h1>", '<p class="lead">' + (f"작품 테이블 한 장(works.csv.gz, {len(D.col):,}종 {int(D.col.n_works.sum()):,}행)이 뼈대다. 편마다 ID·문집·권·문체분류·제목·필자·글자 수(본문/주)·연계 유무가 있고 본문은 없다. 모든 지표는 이 표와 저자 표에서 다시 만들 수 있다. datapackage.json 에 파일마다 라이선스와 원자료를 적었다." if ko else
                                                       f"One work table (works.csv.gz, {int(D.col.n_works.sum()):,} rows from {len(D.col):,} collections) is the backbone: id, collection, fascicle, genre class, title, writer, characters (text/notes) and link flags per work, no text. Every metric can be rebuilt from it and the author table. datapackage.json lists the license and sources of each file.") + "</p>",
            '<div class="files">' + "".join(f'<a href="../data/{f}">{f}</a>' for f in files) + "</div>", '<p class="files"><a href="../data/datapackage.json">datapackage.json</a> · <a href="https://github.com/BowonKwon/Munjip-Metrics/tree/main/data/coding">data/coding/</a> (' + ("코드북·표본·판정" if ko else "codebook, samples, judgments") + ")</p>",
            "<h2>" + t["license"] + "</h2><p>" + ("파생 표: 이용허락범위 제한 없는 공공데이터의 2차 저작물이며, 이 사이트의 자체 저작 부분은 CC BY 4.0. 코드: MIT. 원문·분류·제목은 한국고전번역원, 방목·인명은 한국학중앙연구원의 것이다." if ko else
                                                   "Derived tables are derivative works of public data released without license restriction; this site's own contributions are CC BY 4.0, code MIT. Text, classification and titles belong to the ITKC; the roster and person data to the Academy of Korean Studies.") + "</p>"]
    return page(lang, t["nav_data"], "".join(body), depth=1, active="data", rel="data.html")


def method_page(D, lang):
    t = T[lang]; ko = lang == "ko"
    n_match = _n_match(D)
    secs = []
    if ko:
        secs.append(f"<h1>방법·한계</h1><h2>자료</h2><p>{esc(SOURCES['itkc_munjip']['ko'])}</p><p>{esc(SOURCES['aks_munkwa']['ko'])} {esc(SOURCES['aks_persons']['ko'])}</p>")
        secs.append(f"<h2>세는 단위</h2><p>모든 수는 <b>편</b> 단위다. 고전번역원 XML 에서 type=\"최종정보\" 인 레벨 요소 하나가 편 하나이고, 전체 {int(D.col.n_works.sum()):,}편 가운데 {int(D.col.n_own_works.sum()):,}편이 저자 자신의 글이다(필자 한자성명 = 서지 저자). 글자는 <내용> 안의 한자 수이며 원주·교감주·난외주 안의 글자를 주로 따로 센다. 검산: 문집 {n_match}종 전부에서 원본 XML 의 <내용> 재계산과 일치, 문자 참조 잔존 0.</p>")
        secs.append("<h2>문체</h2><p>고전번역원이 편마다 붙인 문체분류(대분류 7·중분류 28)를 그대로 쓴다. 사이트가 분류를 고치거나 보태지 않았다. 분류의 품질은 기타류 잔여율(B7)로 보이고, 표본 300편을 제목·본문으로 블라인드 코딩한 일치율을 신뢰도 카드에 적는다(1.0 에서 진행 중이면 그렇게 표시).</p>")
        secs.append("<h2>세기</h2><p>XML 에 편 단위 연대가 없어 모든 시계열은 저자 생년의 세기로 묶는다. 저자 활동기와 간행 사이에는 약 1세기의 시차가 있다(곽지은 2026; 간행 시차 D3). 생년이 없는 저자의 문집은 세기 표에서 「생년 미상」 행에 둔다.</p>")
        secs.append("<h2>저자 묶기</h2><p>저자 ID 는 한자성명 + 생년이다. 같은 저자의 여러 문집(본집·속집·유고)은 저자 표에서 합산하고 문집 수를 열로 보인다. 필자가 저자와 다른 편(서문·발문·행장·만사·부록)은 저자 저작량에서 뺀다. 같은 이름·같은 생년의 다른 사람은 구별하지 못한다 — 발견되면 overrides 로 고친다.</p>")
        secs.append("<h2>인물 연결</h2><p>문과방목 연결 규칙은 M1 성명+생년 일치(중시·발영시로 여러 행이면 첫 급제), M2 성명 일치·방목 생년 없음·자 또는 호 일치, M3 성명 일치·후보 하나·시험년이 생애 안. 둘 이상 남으면 미확정(AMB)으로 두고 연결하지 않는다. 연결률은 급제율이 아니다. 한국역대인명정보는 성명+생년(P1) 또는 성명+호(P2)로 연결해 몰년 일치율만 본다.</p>")
        secs.append("<h2>관계 문체</h2><p>서간 수신자는 제목이 答·與·上·寄·復·報·奉·呈·贈·簡·謝 로 시작할 때 그 뒤부터 書·簡·問目·別紙·狀 등 앞까지의 문자열이고, 비지·행장 피장자는 墓誌銘·墓碣銘·神道碑·行狀 등 앞의 문자열(贈·故·先考 등 머리말 제거)이다. 1.0 은 문자열을 사람으로 합치지 않는다 — 자·호·관직으로 달리 불린 같은 사람은 다른 수신자로 센다. 파싱 정밀도는 표본으로 잰다.</p>")
        secs.append("<h2>알려진 한계</h2><ul><li>XML 의 결함(페이지 번호 불일치·추가·누락·이미지와 한자 불일치, 최지연 외 2021)은 고치지 않았다. 면 번호는 지표로 쓰지 않는다.</li><li>「편」의 크기는 편집진의 결정이다. 연작시가 한 편으로 묶인 곳에서는 편 기준 비중이 글자 기준과 달라진다.</li><li>고유명사 태그는 문집마다 밀도가 달라(0~100%) 어떤 지표에도 쓰지 않았다.</li><li>생년 없는 저자 8명(841편, 저자 글 709)은 A·B 계열 세기 표에 「생년 미상」 행으로 따로 있고, C·D 계열 세기 표에는 없다(그 표의 합은 생년 있는 저자만). 지표 머리의 전체 값(저자 1,248·편 637,203·저자 글 609,494)에는 들어간다.</li><li>『호음잡고』(ITKC_MO_0126A)의 冊文類 284편은 제목이 시다(고전번역원 분류의 덩어리 오류). 분류를 고치지 않고 그대로 센 뒤 B 계열 신뢰도 카드에 적었다. 문체분류가 없는 편 88(속편 후반 5종)은 「미분류」로 분모에만 들어간다.</li><li>번역문·교감표점 연계는 2024-08 자 XML 의 태그이며 사업 현황과 다를 수 있다.</li><li>해석은 하지 않는다. 저자·학파를 평가하는 서술은 없다.</li></ul>")
        secs.append("<h2>재현</h2><p>GitHub 저장소의 src/ 에 수집(fetch_itkc.py)·작품 테이블(build_works.py)·검산(check_works.py)·저자 연결(link_authors.py)·지표(metrics_a~d.py)·신뢰도(reliability.py)·사이트(build_site.py) 코드가 있다. 포털 파일 이력은 1,251항목, 내려받은 첨부는 1,250건(운암집 1건은 첨부 없음), 채택한 문집 zip 은 1,249건(구 스키마 중복 1건 제외)이며 그 SHA-256 이 raw_manifest.json 에 있다.</p>")
        secs.append("<h2>로마자</h2><p>문집명과 인물 이름은 국어의 로마자 표기법(2000)을 따르되, 성 김·이는 관용 표기 Kim·Yi로 적는다.</p>")
        secs.append(f"<h2>판</h2><ul><li>{VERSION} ({BUILD_DATE}) — 탐색 개선: 지표 면과 인물 면에 위치 표시줄, 같은 계열 목록, 이전·다음 링크(←/→ 키)를 넣었다. 지표는 계열 순, 인물 면은 생년 순. 내용·수치 변화 없음.</li><li>1.0.2 (2026-11-04) — 번역문 연계 지표(D4)의 외부 대조 문구를 고치고 로마자 규칙을 적었다. 수치 변화 없음.</li><li>1.0.1 (2026-11-04) — 문집 면의 저자 절 복구, 언어 전환 링크가 같은 면으로 가도록 수정, 한국어·영어 문구와 표기 정리. 수치 변화 없음.</li><li>1.0 (2026-11-03) — 첫 공개.</li></ul>")
    else:
        secs.append(f"<h1>Method and limits</h1><h2>Sources</h2><p>{esc(SOURCES['itkc_munjip']['en'])}</p><p>{esc(SOURCES['aks_munkwa']['en'])} {esc(SOURCES['aks_persons']['en'])}</p>")
        secs.append(f"<h2>Unit of counting</h2><p>Every number is counted per <b>work</b>: one level element of type=\"최종정보\" in the ITKC XML. Of {int(D.col.n_works.sum()):,} works, {int(D.col.n_own_works.sum()):,} are by the collection's author (writer name equals the bibliographic author). Characters are CJK code points inside <내용>; those inside original, collation and marginal notes are counted separately as note characters. Check: for all {n_match} collections the count equals an independent recount of every <내용> in the raw XML; zero residual character references.</p>")
        secs.append("<h2>Genres</h2><p>The genre classification the ITKC attached to each work (7 major, 28 minor classes) is used as given; nothing was corrected or added. Classification quality is shown by the residual 'other' share (B7) and by a blind coding of a 300-work sample reported on the reliability card (marked as in progress where not yet done in 1.0).</p>")
        secs.append("<h2>Centuries</h2><p>The XML carries no date per work, so every time series is grouped by the author's birth century. Printing lags the author's active years by about a century (Kwak 2026; publication lag D3). Collections whose author has no birth year sit in a 'birth year unknown' row.</p>")
        secs.append("<h2>Merging authors</h2><p>The author id is the Chinese-character name plus the birth year. Several collections by one author (main collection, continuation, posthumous works) are summed in the author table with the number of collections shown. Works whose writer differs from the author (prefaces, postscripts, biographies, elegies, appendices) are excluded from the author's output. Two different people sharing a name and birth year cannot be told apart; such cases are corrected through overrides when found.</p>")
        secs.append("<h2>Person linkage</h2><p>Examination-roster rules: M1 same name and birth year (first pass when a person is listed for re-examinations), M2 same name, roster birth absent, courtesy or pen name identical, M3 same name, a single candidate, examination year within the lifetime. Where more than one candidate survives the author stays unlinked (AMB). Linkage is not a pass rate. The AKS person database is matched by name and birth year (P1) or name and pen name (P2) and used only to check death years.</p>")
        secs.append("<h2>Relationship genres</h2><p>A letter's addressee is the string after an opening 答·與·上·寄·復·報·奉·呈·贈·簡·謝 up to 書·簡·問目·別紙·狀 etc.; an epitaph's subject is the string before 墓誌銘·墓碣銘·神道碑·行狀 etc. with honorific prefixes removed. Version 1.0 does not merge strings into persons: the same person named by courtesy name, pen name or office counts as different addressees. Parsing precision is measured on a sample.</p>")
        secs.append("<h2>Known limits</h2><ul><li>Defects of the XML (page-number mismatches, additions, omissions, characters differing from the page images; Choi et al. 2021) were not corrected; page numbers are not used in any metric.</li><li>The size of a 'work' is an editorial decision; where poem cycles are bundled, work-based shares diverge from character-based ones.</li><li>Named-entity tags vary in density from 0 to 100% between collections and are not used in any metric.</li><li>The 8 authors without a birth year (841 works, 709 own) appear as a separate 'birth year unknown' row in the series A and B century tables and are absent from the series C and D century tables (whose sums cover dated authors only); the headline totals (1,248 authors, 637,203 works, 609,494 own works) include them.</li><li>284 works of the Hoeum japgo (ITKC_MO_0126A) filed under 冊文類 carry poem titles — a block error in the ITKC classification. They are counted as classified and noted on the series B reliability cards. 88 works without a genre class (five late supplement collections) enter denominators only.</li><li>Translation and collation links are tags of the 2024-08 XML and may differ from the current state of the programs.</li><li>No interpretation is offered; no author or school is evaluated.</li></ul>")
        secs.append("<h2>Reproduction</h2><p>The GitHub repository's src/ holds the fetcher (fetch_itkc.py), work table (build_works.py), checks (check_works.py), author linkage (link_authors.py), metrics (metrics_a–d.py), reliability (reliability.py) and site (build_site.py). The portal lists 1,251 entries; 1,250 attachments were downloaded (one entry has none) and 1,249 archives adopted (one old-schema duplicate excluded); their SHA-256 digests are in raw_manifest.json.</p>")
        secs.append("<h2>Romanization</h2><p>Collection titles and personal names follow the Revised Romanization of Korean (2000); the surnames 김 and 이 are given in their customary forms, Kim and Yi.</p>")
        secs.append(f"<h2>Versions</h2><ul><li>{VERSION} ({BUILD_DATE}) — Navigation: metric and person pages now have a breadcrumb, a list of pages in the same series and previous/next links (← and → keys); metrics follow series order, person pages birth order. No content or numbers changed.</li><li>1.0.2 (2026-11-04) — external-check wording of the linked-translation metric (D4) revised; romanization rule stated. No numbers changed.</li><li>1.0.1 (2026-11-04) — author section restored on collection pages, language switch now opens the same page, wording and notation fixes in both languages. No numbers changed.</li><li>1.0 (2026-11-03) — first release.</li></ul>")
    return page(lang, t["nav_method"], "".join(secs), depth=1, active="method", rel="method.html")


def reading_page(D, lang):
    t = T[lang]; ko = lang == "ko"
    body = [f"<h1>{t['nav_reading']}</h1>"]
    for s, sl in SERIES.items():
        body.append(f"<h2>{esc(sl[lang])}</h2><p>{esc(SERIES_INTRO[s][lang])}</p>")
        for m in METRICS:
            if m["series"] == s and m["id"] in TAKE:
                body.append(f'<h3><a href="metrics/{m["id"]}.html">{esc(m[lang]["name"])}</a></h3><p>{esc(TAKE[m["id"]][lang])}</p>')
    return page(lang, t["nav_reading"], "".join(body), depth=1, active="reading", rel="reading.html")


def write_datapackage(data_dir: Path, files, D) -> None:
    res = []
    for f in files:
        if not (data_dir / f).exists():
            continue
        src = "itkc_munjip" if not f.startswith("d_") and f not in ("authors.csv", "reliability.json") else "itkc_munjip; aks_munkwa; aks_persons"
        res.append({"name": f.replace(".csv.gz", "").replace(".csv", "").replace(".json", ""), "path": f, "format": "csv" if ".csv" in f else "json",
                    "licenses": [{"name": "CC-BY-4.0", "title": "Creative Commons Attribution 4.0 (this site's derived tables)"}], "sources": [{"title": SOURCES[k]["en"], "path": SOURCES[k]["url"], "license": SOURCES[k]["license"]} for k in src.split("; ")]})
    pkg = {"name": "munjip-metrics", "title": SITE["en"]["title"], "version": VERSION, "created": BUILD_DATE, "homepage": REPO,
           "description": f"Korean literary collections (Hanguk munjip chonggan, {len(D.col):,} collections) counted work by work: sizes, genre composition, relationship genres, authors. No text is included; works link to the ITKC database.",
           "licenses": [{"name": "CC-BY-4.0"}], "resources": res}
    (data_dir / "datapackage.json").write_text(json.dumps(pkg, ensure_ascii=False, indent=1), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--derived", default="data/derived"); ap.add_argument("--out", default="site"); x = ap.parse_args()
    root = Path(__file__).resolve().parent.parent
    d = (root / x.derived) if not Path(x.derived).is_absolute() else Path(x.derived)
    out = (root / x.out) if not Path(x.out).is_absolute() else Path(x.out)
    D = Data(d)
    if out.exists():
        shutil.rmtree(out)
    (out / "data").mkdir(parents=True)
    for f in DATA_FILES:
        base = f.replace(".gz", "")
        if not (d / base).exists():
            continue
        if base in GZIP:
            with open(d / base, "rb") as fi, gzip.open(out / "data" / f, "wb", compresslevel=9) as fo:
                shutil.copyfileobj(fi, fo)
        else:
            shutil.copy(d / base, out / "data" / f)
    write_datapackage(out / "data", DATA_FILES, D)
    files = [f for f in DATA_FILES if (out / "data" / f).exists()]
    n = 0
    for lang in ("ko", "en"):
        L = out / lang; (L / "metrics").mkdir(parents=True); (L / "centuries").mkdir(); (L / "collections").mkdir()
        (L / "index.html").write_text(home(D, lang), encoding="utf-8"); n += 1
        (L / "metrics" / "index.html").write_text(metrics_index(D, lang), encoding="utf-8"); n += 1
        for m in METRICS:
            (L / "metrics" / f"{m['id']}.html").write_text(metric_page(m, D, lang), encoding="utf-8"); n += 1
        (L / "centuries" / "index.html").write_text(centuries_index(D, lang), encoding="utf-8"); n += 1
        for c in D.tot.index:
            if not pd.isna(c):
                (L / "centuries" / f"{int(c)}.html").write_text(century_page(c, D, lang), encoding="utf-8"); n += 1
        (L / "collections" / "index.html").write_text(collections_index(D, lang), encoding="utf-8"); n += 1
        persons = {hj for hj, _, _ in PERSON_PAGES}
        for _, r in D.col.iterrows():
            (L / "collections" / f"{r.collection_id}.html").write_text(collection_page(r, D, lang, is_person=r.title_hj in persons), encoding="utf-8"); n += 1
        (L / "persons.html").write_text(persons_page(D, lang), encoding="utf-8"); n += 1
        (L / "prior.html").write_text(prior_page(D, lang), encoding="utf-8"); n += 1
        (L / "data.html").write_text(data_page(D, lang, files), encoding="utf-8"); n += 1
        (L / "method.html").write_text(method_page(D, lang), encoding="utf-8"); n += 1
        (L / "reading.html").write_text(reading_page(D, lang), encoding="utf-8"); n += 1
    (out / "index.html").write_text('<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0; url=ko/index.html"><title>Munjip Metrics</title></head><body><a href="ko/index.html">문집 메트릭스</a> · <a href="en/index.html">Munjip Metrics</a></body></html>', encoding="utf-8")
    print(f"site: {n} pages, data files {len(files)} -> {out}")


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    main()
