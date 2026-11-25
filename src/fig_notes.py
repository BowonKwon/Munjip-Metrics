# -*- coding: utf-8 -*-
"""Chart notes (1.0.9): a line above each chart saying what it draws, and labelled paragraphs under it — in short, how the
chart works, reading one value, the numbers, easy to misread, terms. Every number in these sentences is computed here from
the same tables the chart is drawn from; nothing is typed in by hand. The notes explain; they do not change a value, a rule
or a claim of the metric pages.

build_site.py calls setup() once with the loaded data, then the functions below one per chart.
"""
from __future__ import annotations

import math
import re

import pandas as pd

from site_common import esc, fmt

LAB = {"ko": {"short": "한눈에", "how": "그림 보는 법", "one": "숫자 하나 읽어 보기", "nums": "수로 보면", "mis": "잘못 읽기 쉬운 것", "terms": "낱말 풀이"},
       "en": {"short": "In short", "how": "How the chart works", "one": "Reading one value", "nums": "The numbers", "mis": "Easy to misread", "terms": "Terms"}}
NOTE_CSS = (" .fi{font-size:.92rem;color:var(--fg2);margin:0 0 .5rem;line-height:1.55;word-break:keep-all;overflow-wrap:anywhere}"
            " figcaption{word-break:keep-all;overflow-wrap:anywhere} figcaption .cp{margin:.45rem 0 0} figcaption .cp b{color:var(--fg);margin-right:.35rem}"
            " .spec dd.words{font-size:.9rem;color:var(--fg2)}")

C = {}   # filled by setup(): D, century_label, GENRES, GENRE_KO, GENRE_EN, few, ok, rc


def setup(D, century_label, genres, genre_ko, genre_en, genre_gloss):
    tot = D.tot[D.tot.index.notna()]
    few = {int(c) for c, n in tot.n_collections.items() if n <= 10}
    ok = sorted(int(c) for c in tot.index if int(c) not in few)
    C.update(gloss=genre_gloss, D=D, cl=century_label, GENRES=genres, GKO=genre_ko, GEN=genre_en, few=few, ok=ok, kmin=11,
             rc=int(tot.n_collections.idxmax()), unknown=int(D.tot.loc[D.tot.index.isna()].n_collections.sum()) if D.tot.index.isna().any() else 0)
    # 1.0.9 v1 (Codex 3.14, 3.10): works that are not the author's own are works by others *and* works with an empty writer
    # tag; and how far the very long works lift the mean. Both read from works.csv (not public; the same rows as works.csv.gz).
    wp = D.d / "works.csv"
    if wp.exists():
        w = pd.read_csv(wp, usecols=["collection_id", "writer_hj", "is_author_work", "chars_main", "chars_note"])
        w = w.merge(D.col[["collection_id", "birth_century"]], on="collection_id", how="left")
        blank = w[(w.is_author_work != 1) & (w.writer_hj.isna() | (w.writer_hj.astype(str).str.strip() == ""))]
        C["blank_col"] = blank.groupby("collection_id").size().to_dict()
        C["blank_cen"] = blank.groupby("birth_century").size().to_dict()
        w["len"] = w.chars_main + w.chars_note
        C["long"] = {int(c): (int((g.len > 1000).sum()), float(g[g.len <= 1000].len.mean())) for c, g in w[w.birth_century.notna()].groupby("birth_century")}


def figx(svg: str, intro: str, parts, lang: str) -> str:
    """A chart with its line above and its labelled paragraphs below. parts: [(key, text)]; empty texts are left out.
    1.0.9 v1 (Codex 4.3): the chart's accessible name is the line above it, in the page's language (it was 'bar chart')."""
    if not svg:
        return ""
    if intro:
        svg = re.sub(r'aria-label="[^"]*"', f'aria-label="{esc(intro)}"', svg, count=1)
    cps = "".join(f'<p class="cp"><b>{LAB[lang][k]}</b> {esc(t.strip())}</p>' for k, t in parts if t and t.strip())
    return f'<figure><p class="fi">{esc(intro)}</p>{svg}<figcaption>{cps}</figcaption></figure>'


# ----------------------------------------------------------------- small helpers
def cl(c, lang):
    return C["cl"](c, lang)


def cls(cs, lang):
    """A list of centuries in words: 14·15·16세기 / the 14th, 15th and 16th centuries."""
    cs = sorted(int(c) for c in cs)
    if lang == "ko":
        return "·".join(str(c) for c in cs) + "세기"
    o = [cl(c, "en").replace(" century", "") for c in cs]
    if len(o) == 1:
        return f"{o[0]} century"
    return ", ".join(o[:-1]) + f" and {o[-1]} centuries"


def ok_range(lang):
    ok = C["ok"]
    if ok == list(range(ok[0], ok[-1] + 1)):
        return f"{ok[0]}~{ok[-1]}세기" if lang == "ko" else f"{cl(ok[0], 'en').replace(' century', '')} to {cl(ok[-1], 'en')}"
    return cls(ok, lang)


def few_text(lang, pts=None, counts=None, unit=("종", "collections")):
    """The centuries with ten collections or fewer. 1.0.9 v1 (Codex 3.2): only those that have a point on the chart (pts),
    and, where a chart rests on fewer items than the collections (counts: century -> number that enter the value), that number."""
    tot = C["D"].tot
    f = sorted(C["few"])
    if pts is not None:
        have = {int(x) for x, y in pts if y == y}
        f = [c for c in f if c in have]
    if not f:
        return ""
    ns = [int(counts[c]) if counts is not None else int(tot.loc[c].n_collections) for c in f]
    rng_ko = f"{min(ns)}~{max(ns)}" if min(ns) != max(ns) else f"{min(ns)}"
    rng_en = f"{min(ns)} to {max(ns)}" if min(ns) != max(ns) else f"{min(ns)}"
    if counts is None:
        if lang == "ko":
            return f"{cls(f, 'ko')}의 점은 문집이 {rng_ko}종뿐인 세기의 값이어서, 한두 문집이 점을 크게 움직인다."
        return f"The points for the {cls(f, 'en')} rest on {rng_en} collections each, so one or two collections move them a lot."
    if lang == "ko":
        each = ", ".join(f"{c}세기 {int(counts[c]):,}{unit[0]}" for c in f)
        return f"{cls(f, 'ko')}의 점은 문집이 10종 이하인 세기의 값이고, 값에 실제로 들어간 수는 {each}뿐이어서 한두 {unit[0] if unit[0] != '종' else '문집'}이 점을 크게 움직인다."
    each = ", ".join(f"{int(counts[c]):,} ({cl(c, 'en')})" for c in f)
    return f"The points for the {cls(f, 'en')} come from centuries with ten collections or fewer and rest on only these numbers of {unit[1]}: {each}; one or two move them a lot."


def extremes(pts):
    """Largest and smallest value over the centuries with more than ten collections, ties kept together."""
    P = [(int(x), y) for x, y in pts if int(x) not in C["few"] and y == y]
    if not P:
        return None
    hv = max(y for _, y in P); lv = min(y for _, y in P)
    return [x for x, y in P if y == hv], hv, [x for x, y in P if y == lv], lv


def line_short(series, spec, idx, lang, far_ok=True):
    """「한눈에」 for a by-century line chart: for each chosen series, the centuries with the largest and smallest values."""
    out = []
    head = (f"문집이 {C['kmin']}종 이상인 세기({ok_range('ko')}) 가운데 " if lang == "ko"
            else f"Among the centuries with at least {C['kmin']} collections ({ok_range('en')}), ")
    for k, i in enumerate(idx):
        name, pts, _ = series[i]
        e = extremes(pts)
        if not e:
            continue
        hs, hv, ls, lv = e
        if hv == lv:   # the same value in every such century (the median poem length)
            out.append(tr(lang, f"{'「' + name + '」 선은 ' if len(idx) > 1 else '값은 '}모든 세기에서 같다({fmt(hv, spec)}).",
                          f"{'for ' + repr(name) + ' ' if len(idx) > 1 else ''}the value is {fmt(hv, spec)} in every one of them."))
            continue
        # 1.0.9 v1 (Codex 2.4): other centuries that show the same rounded value as the largest or smallest
        P = [(int(x), y) for x, y in pts if int(x) not in C["few"] and y == y]
        sh = [x for x, y in P if x not in hs and fmt(y, spec) == fmt(hv, spec)]
        sl = [x for x, y in P if x not in ls and fmt(y, spec) == fmt(lv, spec)]
        def _ko_same(xs, v, top):
            sv = fmt(v, spec)
            return f" {cls(xs, 'ko')}도 {sv}{_ro_num(sv)} 표시되지만, 반올림하기 전 값은 {cls(hs if top else ls, 'ko')}가 가장 {'크' if top else '작'}다."
        def _en_same(xs, v, top):
            verb = "shows" if len(xs) == 1 else "show"
            return f" (the {cls(xs, 'en')} also {verb} {fmt(v, spec)}; before rounding the {cls(hs if top else ls, 'en')} is the {'largest' if top else 'smallest'})"
        if lang == "ko":
            who = f"「{name}」 선에서 " if len(idx) > 1 else ""
            out.append(f"{who}값이 가장 큰 세기는 {cls(hs, 'ko')}({fmt(hv, spec)}), 가장 작은 세기는 {cls(ls, 'ko')}({fmt(lv, spec)})다."
                       + (_ko_same(sh, hv, True) if sh else "") + (_ko_same(sl, lv, False) if sl else ""))
        else:
            who = f"for '{name}' " if len(idx) > 1 else ""
            out.append(f"{who}the largest value is in the {cls(hs, 'en')} ({fmt(hv, spec)})" + (_en_same(sh, hv, True) if sh else "")
                       + f" and the smallest in the {cls(ls, 'en')} ({fmt(lv, spec)})" + (_en_same(sl, lv, False) if sl else "") + ".")
    if not out:
        return ""
    # 1.0.9 v1 (Codex 4.4): a point of a century with ten collections or fewer that lies beyond these extremes is named too
    named = len(idx) > 1 or (idx and series[idx[0]][0] in ("중앙값", "median"))   # 1.0.9 v2 (Codex 2.6): b8 · d3 say 'median'
    tail = far_tail([(series[i][0] if named else None, series[i][1]) for i in (idx if far_ok else [])], spec, lang)   # not for counts
    if lang == "ko":
        return head + " ".join(out) + tail
    s = head + "; ".join(o.rstrip(".") for o in out) + "."   # 1.0.9 v1: no '.;' between series
    return s + tail


def far_tail(items, spec, lang):
    """1.0.9 v1 (Codex 4.4), v2 (Codex 2.7, 3.7): the points of centuries with ten collections or fewer that lie beyond the
    largest and smallest value of the larger centuries, for each (name, pts) in items; name None leaves the series unnamed.
    Used by the line charts and, with the panel name, by the three small charts."""
    far = []
    for name, pts in items:
        e = extremes(pts)
        if not e:
            continue
        _, hv, _, lv = e
        for x, y in pts:
            if int(x) in C["few"] and y == y and (y > hv or y < lv):
                far.append((name, int(x), y))
    if not far:
        return ""
    groups = []   # one group per named series, in order
    for n, x, y in far:
        if groups and groups[-1][0] == [n]:
            groups[-1][1].append((x, y))
        else:
            groups.append(([n], [(x, y)]))
    merged = []   # 1.0.9 v3 (Codex 2.6): series with the very same far points are named together
    for ns, g in groups:
        if merged and merged[-1][1] == g and None not in ns:
            merged[-1][0].extend(ns)
        else:
            merged.append((ns, g))
    if lang == "ko":
        def _kn(ns):
            if ns == [None]:
                return ""
            q = "·".join(f"「{n}」" for n in ns)
            return f"{q} 선의 " if len(ns) == 1 else f"{q} {'두' if len(ns) == 2 else len(ns)} 선 모두 "
        return (" 문집이 10종 이하인 세기까지 보면 " + ", ".join(_kn(ns) + "·".join(f"{cl(x, 'ko')}({fmt(y, spec)})" for x, y in g) for ns, g in merged)
                + "가 이 범위 밖에 있다 — 문집이 적은 세기의 값이다.")
    def _en(ns, g):
        cs = [cl(x, "en").replace(" century", "") for x, _ in g]
        vs = [fmt(y, spec) for _, y in g]
        if ns == [None]:
            pre = ""
        elif len(ns) == 1:
            pre = f"in the '{ns[0]}' line, "
        else:
            pre = ("in both lines, " if len(ns) == 2 else f"in all {len(ns)} lines, ")
        if len(g) == 1:
            return f"{pre}the {cs[0]}-century value ({vs[0]}) falls outside this range"
        cj = ", ".join(cs[:-1]) + (", and " if len(cs) > 2 else " and ") + cs[-1]
        vj = f"all {vs[0]}" if len(set(vs)) == 1 else ", ".join(vs[:-1]) + (", and " if len(vs) > 2 else " and ") + vs[-1]
        return f"{pre}the values in the {cj} centuries ({vj}) fall outside this range"
    parts = "; ".join(_en(ns, g) for ns, g in merged)
    one = len(far) == 1
    return (f" Among the centuries with ten collections or fewer, {parts}. "
            f"{'That value rests' if one else 'These values rest'} on few collections.")


def qv(v, u_ko, u_en, L):
    """1.0.9 v3 (Codex 2.13): a median or quartile as computed, with the rounded value the chart shows when they differ."""
    s = fmt(v, ",.0f")
    if abs(v - round(v)) < 1e-9:
        return s + (u_ko if L == "ko" else u_en)
    ex = f"{v:,.2f}".rstrip("0").rstrip(".")
    return f"{ex}{u_ko}(그림에서 {s}{u_ko})" if L == "ko" else f"{ex}{u_en} ({s} on the chart)"


def round_eg(df, pre, u_ko, u_en, L):
    """1.0.9 v3 (Codex 2.13): the rounding example of the quartile gloss, taken from this chart's own values."""
    names = [("p75", "위 사분위", "upper quartile"), ("p25", "아래 사분위", "lower quartile"), ("median", "중앙값", "median")]
    for _, r in df.sort_values("century").iterrows():
        for suf, nk, ne in names:
            v = r.get(f"{pre}_{suf}")
            if v is not None and v == v and abs(v - round(v)) > 1e-9:
                ex = f"{v:,.2f}".rstrip("0").rstrip("."); s = fmt(v, ",.0f"); c = int(r.century)
                return (f"(이 그림에서는 {cl(c, 'ko')} {nk} {ex}{u_ko}{jo(u_ko, '이', '가')} {s}{u_ko}{_ro(u_ko)} 보인다)" if L == "ko"
                        else f" (here the {cl(c, 'en').replace(' century', '-century')} {ne}, {ex}{u_en}, shows as {s})")
    return ""


def denoms(df, ccol, ncol, unit_ko, unit_en, lang, people=False):
    """The denominators of a by-century share differ from century to century: name the largest and the smallest."""
    d = df[df[ccol].notna()]
    d = d[d[ncol].notna()]
    if d.empty:
        return ""
    hi = d.loc[d[ncol].idxmax()]; lo = d.loc[d[ncol].idxmin()]
    if lang == "ko":
        return (f"{'점마다 바탕이 된 사람 수가 다르다' if people else '점마다 비율의 바탕이 되는 수가 다르다'} — 가장 큰 {cl(hi[ccol], 'ko')}는 {int(hi[ncol]):,}{unit_ko}, 가장 작은 {cl(lo[ccol], 'ko')}는 {int(lo[ncol]):,}{unit_ko}{_ida(unit_ko)}. "
                f"바탕이 작은 세기의 값은 {'몇 사람' if people else '몇 편'}에 따라 크게 움직인다.")
    return (f"{'Each point rests on a different number of people' if people else 'Each point is a share of a different total'}: {int(hi[ncol]):,} {unit_en} in the {cl(hi[ccol], 'en')}, {int(lo[ncol]):,} in the {cl(lo[ccol], 'en')}. "
            f"Where the total is small, a few {'people' if people else 'works'} move the value a lot.")


def _ida(w):
    w = re.sub(r"\([^()]*\)$", "", str(w).strip())   # the particle follows the word before a closing bracket
    ch = w.strip()[-1:]
    return "이다" if "가" <= ch <= "힣" and (ord(ch) - 0xAC00) % 28 else "다"


def birth_not_writing(lang):
    return ("세기는 저자가 태어난 세기다. 글을 쓴 때나 문집을 펴낸 때가 아니며, 간행은 대개 그보다 늦다(지표 「간행 시차」)." if lang == "ko"
            else "The century is that of the author's birth, not of writing or printing; printing usually came later (see the publication-lag metric).")


def line_how(ylab, lang, extra=""):
    if lang == "ko":
        return f"점 하나가 한 세기다. 가로는 저자가 태어난 세기, 세로는 {ylab}{_ida(ylab)}. 위에 있을수록 값이 크다. 문집이 없는 세기에서는 선이 끊기고, 앞뒤가 끊긴 값은 점 하나로만 그렸다. {extra}".strip()
    return f"Each point is one century. Left to right is the century of the author's birth; up the side is {ylab}. Higher means a larger value. The line breaks at centuries with no collection, and a value with no neighbor is drawn as a lone dot. {extra}".strip()


QUART = {"ko": "중앙값 = 값을 크기 순으로 늘어세웠을 때 한가운데 값(값의 수가 짝수면 가운데 두 값의 평균). 사분위 = 늘어세운 값의 아래에서 4분의 1(아래 사분위)과 4분의 3(위 사분위) 자리의 값(그 자리가 두 값 사이에 떨어지면 두 값 사이를 비례로 나눈 값) (자리는 첫 값부터 마지막 값까지의 순위 간격으로 잰다) — 두 선이 순서상 가운데 절반의 경계다. 같은 값이 많으면 경계 위에 걸린 값이 많아, 경계값까지 넣어 세면 두 선 사이에 절반보다 많이 들 수 있다. 그림의 값은 정수로 반올림해 보인다{eg}.",
         "en": "Median: the middle value when the values are put in order (with an even count, the average of the two middle values). Quartiles: the values a quarter (lower quartile) and three quarters (upper quartile) of the way up that order (where that place falls between two values, a value in proportion between them; places are measured along the ranks from the first value to the last); the two lines mark off the middle half of the order. When many values are equal, many sit on the lines, and counting the values on the lines too, more than half may lie between them. Values on the chart are rounded to whole numbers{eg}."}
QUART_HOW = {"ko": "가운데 선이 중앙값이고, 위아래 두 선(사분위)이 순서상 가운데 절반의 경계다. 위아래 두 선은 같은 색이다 — 위의 것이 위 사분위, 아래 것이 아래 사분위다. 세 값이 같은 세기(대개 문집이나 사람이 아주 적은 세기)에서는 세 선이 한 점에서 만난다.",
             "en": "The middle line is the median; the two outer lines (the quartiles) mark off the middle half of the values in order. The two outer lines share a color: the upper one is the upper quartile, the lower one the lower quartile. Where the three values are equal (usually a century with very few collections or people), the three lines meet in one point."}


def _ro(w):
    """로 after a vowel or ㄹ, 으로 after another final consonant."""
    ch = str(w).strip()[-1:]
    if not ("가" <= ch <= "힣"):
        return "로"
    j = (ord(ch) - 0xAC00) % 28
    return "로" if j in (0, 8) else "으로"


def _ro_num(text):
    """로/으로 after a number as read aloud (% is 퍼센트; a final 0 is 십·백·천·만; 3 삼, 6 육 are closed; 1 일, 7 칠, 8 팔 end in ㄹ)."""
    t = str(text).strip()
    if t.endswith("%"):
        return "로"
    return "으로" if t[-1:] in "036" else "로"


def jo(text, with_final, without_final):
    """Particle after a number or word as read aloud: 은/는, 이다/다 … Digits read 영 일 이 삼 사 오 육 칠 팔 구; a final 0
    is read 십 · 백 · 천 · 만 (all closed); % is read 퍼센트 (open)."""
    t = str(text).strip()
    if t.endswith("%"):
        return without_final
    ch = t[-1:]
    if ch.isdigit():
        return with_final if ch in "013678" else without_final
    if "가" <= ch <= "힣":
        return with_final if (ord(ch) - 0xAC00) % 28 else without_final
    return without_final


def tr(lang, ko, en):
    return ko if lang == "ko" else en


# ----------------------------------------------------------------- by-century line charts on the metric pages
def line_notes(mid, k, series, spec, lang):
    """Notes for the k-th by-century line chart of metric `mid`. Returns (intro, parts)."""
    D = C["D"]; rc = C["rc"]; L = lang; ko = lang == "ko"
    tot = D.tot; t = tot.loc[rc]; rcl = cl(rc, L)
    dc = D.dcen.set_index("century"); d = dc.loc[rc] if rc in dc.index else None
    allpts = [p_ for _, pts_, _ in series for p_ in pts_]
    one = mis = terms = nums = ""; extra_mis = few_text(L, pts=allpts); bn = birth_not_writing(L)   # 1.0.9 v1: only centuries drawn
    idx = [0]
    if mid == "a1_works":
        intro = tr(L, "저자가 태어난 세기마다 문집에 실린 글이 몇 편인지 센 그림이다. 두 선은 전체 편 수와, 그 가운데 저자 자신이 쓴 글(저자 글)의 편 수다.",
                   "Works per century of the author's birth: one line for all works, one for the works by the collection's own author.")
        how = line_how(tr(L, "편 수", "the number of works"), L)
        idx = [0, 1]
        one = tr(L, f"{rcl}의 「편」 {int(t.n_works):,}{jo(int(t.n_works), '은', '는')} {rcl}에 태어난 저자 {int(t.n_authors):,}명의 문집 {int(t.n_collections):,}종에 실린 글을 모두 더한 수이고, 「저자 글」 {int(t.n_own_works):,}{jo(int(t.n_own_works), '은', '는')} 그 가운데 저자 자신이 쓴 글이다. 차이 {int(t.n_works - t.n_own_works):,}편은 남이 쓴 서문·발문·행장 같은 글과 필자 표지가 비어 있는 글({C.get('blank_cen', {}).get(rc, 0):,}편)이다.",
                 f"In the {rcl}, 'works' {int(t.n_works):,} adds up every work in the {int(t.n_collections):,} collections of the {int(t.n_authors):,} authors born then; 'own works' {int(t.n_own_works):,} are those written by the authors themselves. The other {int(t.n_works - t.n_own_works):,} are prefaces, postscripts, biographies and the like by others, and works with an empty writer tag ({C.get('blank_cen', {}).get(rc, 0):,}).")
        mis = tr(L, "총간에 실린 문집만 센 수다. 값이 큰 세기는 그 세기에 태어난 저자들의 총간 수록 문집에 실린 편을 더한 수가 크다는 뜻이지, 문집이 더 많다거나 그 세기에 글이 더 많이 쓰였다는 뜻은 아니다. 「편」은 고전번역원 편집진이 끊은 단위여서 연작시가 한 편으로 묶이기도 하고 수마다 나뉘기도 한다. ",
                 "Only the collections in the compendium are counted: a large value means the works in the compendium's collections by authors born in that century add up to a large number, not that there are more collections or that more was written then. A 'work' is a unit cut by the ITKC editors; a poem series may be one work or one per poem. ") + bn + " " + extra_mis
        terms = tr(L, "편 = 고전번역원 자료에서 글 하나의 단위(시 한 수, 편지 한 통, 묘지명 한 편). 저자 글 = 필자 표지가 문집의 저자와 같은 편.",
                   "Work: one piece in the ITKC data (a poem, a letter, an epitaph). Own works: works whose writer tag is the collection's author.")
    elif mid == "a2_chars":
        intro = tr(L, "저자가 태어난 세기마다 문집의 한자 수를 센 그림이다. 본문 글자와 주(註) 안의 글자를 두 선으로 나눴다.",
                   "Characters per century of the author's birth, with the main text and the notes as two lines.")
        how = line_how(tr(L, "한자 수", "the number of Chinese characters"), L)
        idx = [0, 1]
        one = tr(L, f"{rcl}의 「본문」 {int(t.chars_main):,}{jo(int(t.chars_main), '과', '와')} 「주」 {int(t.chars_note):,}{jo(int(t.chars_note), '은', '는')} {rcl}에 태어난 저자의 문집 {int(t.n_collections):,}종의 글자를 모두 더한 수다. 둘을 합치면 {int(t.chars):,}자다.",
                 f"In the {rcl}, 'text' {int(t.chars_main):,} and 'notes' {int(t.chars_note):,} add up the characters of the {int(t.n_collections):,} collections of authors born then; together {int(t.chars):,}.")
        mis = tr(L, "주 선은 본문 선보다 훨씬 아래에 붙어 있어 작게 보이지만, 같은 눈금이다 — 주의 몫은 지표 「주석 비율」에서 따로 본다. 구두점·공백·한글은 세지 않는다. ",
                 "The notes line hugs the bottom because notes are a small part of the text on the same scale; their share is on the note-share metric. Punctuation, spaces and Hangul are not counted. ") + bn + " " + extra_mis
        terms = tr(L, "주 = 본문에 작은 글씨로 단 설명과 판면 가장자리에 붙인 주. 저자·편찬자가 붙인 원주와 고전번역원이 붙인 교감주·난외주를 합쳤다.",
                   "Notes: explanations set in small type in the text or added at the edge of the printed page — the original notes of the author or compiler, plus the ITKC's collation and marginal notes.")
    elif mid == "a3_centuries":
        s = D.ser; a = s[(s.birth_century == rc) & (s.series == "정편")]; b = s[(s.birth_century == rc) & (s.series == "속편")]
        na = int(a.n_collections.sum()); nb = int(b.n_collections.sum())
        intro = tr(L, "저자가 태어난 세기마다 문집이 몇 종인지, 총간의 두 묶음(정편·속편)으로 나눠 센 그림이다.",
                   "Collections per century of the author's birth, counted separately for the two parts of the compendium (first series and supplement).")
        how = line_how(tr(L, "문집 수(종)", "the number of collections"), L)
        idx = [0, 1]
        one = tr(L, f"{rcl}에 태어난 저자의 문집은 정편에 {na:,}종, 속편에 {nb:,}종 실려 있다 — 합쳐 {na + nb:,}종이다.",
                 f"Collections by authors born in the {rcl}: {na:,} in the first series and {nb:,} in the supplement, {na + nb:,} in all.")
        mis = tr(L, "총간에 실린 문집의 수다. 그 세기 문집이 모두 몇 종 있었는지가 아니다. 속편 문집이 없는 세기에는 속편 점이 없다. ", "These are collections in the compendium, not all the collections that existed. Centuries without a supplement collection have no supplement point. ") + bn + " " + extra_mis
        terms = tr(L, "정편·속편 = 한국문집총간의 두 묶음. 고전번역원이 먼저 펴낸 정편에 이어 속편을 더 펴냈다.",
                   "First series and supplement: the two parts of the Hanguk munjip chonggan; the supplement was published after the first series.")
    elif mid == "a4_chars_per_work":
        intro = tr(L, "글 한 편이 보통 몇 자인지를 세기마다 두 가지 방식(중앙값·평균)으로 낸 그림이다.",
                   "How long a work usually is, per century, in two ways: the median and the mean.")
        how = line_how(tr(L, "편 하나의 글자 수(본문 + 주)", "characters per work (text + notes)"), L)
        idx = [0, 1]
        one = tr(L, f"{rcl}의 중앙값 {fmt(t.chars_per_work_median, ',.0f')}자는 그 세기 저자의 편 {int(t.n_works):,}편을 글자 수 순으로 늘어세웠을 때 한가운데 편의 글자 수다. 평균 {fmt(t.chars_per_work_mean, ',.0f')}자는 글자 {int(t.chars):,}자를 편 수로 나눈 값이다.",
                 f"In the {rcl}, the median {fmt(t.chars_per_work_median, ',.0f')} is the length of the middle work when the {int(t.n_works):,} works are put in order of length; the mean {fmt(t.chars_per_work_mean, ',.0f')} is {int(t.chars):,} characters divided by the number of works.")
        lg = C.get("long", {}).get(rc)
        pb = D.b[(D.b.genre1 == "詩類") & D.b.century.isin(C["ok"])].set_index("century").share_works
        ph, pl = int(pb.idxmax()), int(pb.idxmin())
        mis = tr(L, (f"평균은 중앙값보다 위에 있다. 아주 긴 글이 평균을 크게 올린다 — {rcl}에서 1,000자가 넘는 {lg[0]:,}편을 빼고 내면 평균은 {fmt(t.chars_per_work_mean, ',.0f')}자에서 {fmt(lg[1], ',.0f')}자로 내려간다(중앙값 {fmt(t.chars_per_work_median, ',.0f')}자). " if lg else "")
                 + f"문집이 {C['kmin']}종 이상인 세기에서 저자 글 가운데 시의 몫(편 기준)이 가장 큰 {cl(ph, 'ko')}({fmt(pb[ph], '.1%')})의 중앙값은 {fmt(tot.loc[ph].chars_per_work_median, ',.0f')}자, 가장 작은 {cl(pl, 'ko')}({fmt(pb[pl], '.1%')})는 {fmt(tot.loc[pl].chars_per_work_median, ',.0f')}자다(칠언율시 한 수가 56자, 오언율시가 40자). ",
                 (f"The mean sits above the median. Very long works lift the mean a lot: in the {rcl}, leaving out the {lg[0]:,} works over 1,000 characters brings the mean from {fmt(t.chars_per_work_mean, ',.0f')} down to {fmt(lg[1], ',.0f')} (median {fmt(t.chars_per_work_median, ',.0f')}). " if lg else "")
                 + f"Among the centuries with at least {C['kmin']} collections, the one where poetry's share of own works (by works) is largest, the {cl(ph, 'en')} ({fmt(pb[ph], '.1%')}), has a median of {fmt(tot.loc[ph].chars_per_work_median, ',.0f')} characters, and the one where it is smallest, the {cl(pl, 'en')} ({fmt(pb[pl], '.1%')}), {fmt(tot.loc[pl].chars_per_work_median, ',.0f')} (a seven-character regulated verse has 56 characters, a five-character one 40). ") + bn + " " + extra_mis
        terms = QUART[L].split(" 사분위")[0].split(" Quartiles")[0] + tr(L, " 평균 = 모든 편의 글자 수를 더해 편 수로 나눈 값.", " Mean: all characters divided by the number of works.")
    elif mid == "a5_note_share":
        intro = tr(L, "세기마다 전체 글자 가운데 주(註) 안의 글자가 차지하는 비율을 그린 그림이다.", "The share of characters that sit in notes, per century.")
        how = line_how(tr(L, "주 글자 ÷ 전체 글자", "note characters ÷ all characters"), L)
        one = tr(L, f"{rcl}의 {fmt(t.note_share, '.1%')}는 글자 {int(t.chars):,}자 가운데 {int(t.chars_note):,}자가 주 안에 있다는 뜻이다.",
                 f"The {rcl}'s {fmt(t.note_share, '.1%')} means {int(t.chars_note):,} of {int(t.chars):,} characters are in notes.")
        mis = tr(L, "원주(저자·편찬자의 주)와 고전번역원이 붙인 교감주·난외주를 합친 비율이라, 값이 크다고 저자가 주를 많이 달았다는 뜻은 아니다. ",
                 "Original notes and the ITKC's collation and marginal notes are added together, so a high share does not by itself mean the author wrote many notes. ") + denoms(tot.reset_index(), "birth_century", "chars", "자", "characters", L) + " " + bn
        terms = tr(L, "원주 = 저자나 편찬자가 붙인 주. 교감주 = 판본 사이의 글자 차이를 적은 주. 난외주 = 판면 바깥 여백의 주.",
                   "Original notes: by the author or compiler. Collation notes: differences between editions. Marginal notes: notes outside the printed block.")
    elif mid == "a6_own_share":
        intro = tr(L, "세기마다 문집에 실린 글 가운데 저자 자신이 쓴 글의 비율을 그린 그림이다.", "The share of works written by the collection's own author, per century.")
        how = line_how(tr(L, "저자 글 ÷ 전체 편", "own works ÷ all works"), L)
        one = tr(L, f"{rcl}의 {fmt(t.own_share, '.1%')}는 글 {int(t.n_works):,}편 가운데 {int(t.n_own_works):,}편이 저자 자신의 글이라는 뜻이다. 나머지는 남이 쓴 서문·발문·행장·만사 같은 글과 필자 표지가 비어 있는 글({C.get('blank_cen', {}).get(rc, 0):,}편)이다.",
                 f"The {rcl}'s {fmt(t.own_share, '.1%')} means {int(t.n_own_works):,} of {int(t.n_works):,} works are the author's own; the rest are prefaces, postscripts, biographies and elegies by others, and works with an empty writer tag ({C.get('blank_cen', {}).get(rc, 0):,}).")
        mis = tr(L, "필자 표지가 비어 있는 편은 저자 글로 세지 않았다. 세로 눈금이 0에서 시작하므로 세기 사이 차이가 작아 보일 수 있다 — 값은 표와 커서를 둔 자리의 숫자로 읽는다. ",
                 "Works with an empty writer tag are not counted as own works. The vertical scale starts at 0, so differences between centuries look small; read the values from the tooltips. ") + denoms(tot.reset_index(), "birth_century", "n_works", "편", "works", L) + " " + bn
        terms = tr(L, "저자 글 = 필자 표지가 문집의 저자와 같은 편. 타인 글 = 같은 문집에 실린 남의 글.", "Own works: works whose writer tag is the collection's author. Works by others: the rest of the collection.")
    elif mid == "b2_genre_mix":
        G = C["GENRES"]; nm = (lambda g: C["GKO"][g]) if ko else (lambda g: C["GEN"][g])
        b = D.b[D.b.century.isin(C["ok"])]
        lead = b.loc[b.groupby("century").share_works.idxmax()]
        leaders = sorted(set(lead.genre1))
        rng = b.groupby("genre1").share_works.agg(lambda s: s.max() - s.min()).sort_values(ascending=False)
        gw = rng.index[0]; sw = b[b.genre1 == gw].set_index("century").share_works
        intro = tr(L, "세기마다 저자 글이 일곱 갈래(문체 대분류)에 어떻게 나뉘는지, 갈래 하나를 선 하나로 그린 그림이다.",
                   "How the own works of each century split among the seven genre classes, one line per class.")
        pairs = [(G[i], G[j]) for i in range(len(G)) for j in range(i + 1, len(G)) if i % 4 == j % 4]
        how = line_how(tr(L, "저자 글 가운데 그 갈래의 몫(편 수 기준)", "the class's share of own works (by number of works)"), L,
                       tr(L, "색은 네 가지를 돌려 써서 " + ", ".join(f"{nm(a)}와 {nm(b_)}" if not (ord(nm(a)[-1]) - 0xAC00) % 28 else f"{nm(a)}과 {nm(b_)}" for a, b_ in pairs) + "가 같은 색이다. 갈래는 선 끝의 이름과 커서를 둔 자리의 이름으로 가린다. 한 세기의 일곱 값을 반올림하기 전 값으로 더하면 100%다(표시된 값을 더하면 반올림 때문에 조금 어긋날 수 있다).",
                          "Four colors are reused, so " + ", ".join(f"{nm(a)} with {nm(b_)}" for a, b_ in pairs) + " share a color; tell the classes apart by the names at the line ends and in the tooltips. Before rounding, the seven values of a century add up to 100% (the rounded values shown may be slightly off)."))
        idx = []
        lead_txt = tr(L, f"문집이 {C['kmin']}종 이상인 세기({ok_range('ko')})마다 가장 큰 갈래는 " + "·".join(nm(g) for g in leaders) + ("다." if len(leaders) == 1 else "이다(세기마다 다르다)."),
                      f"In every century with at least {C['kmin']} collections ({ok_range('en')}) the largest class is " + " or ".join(nm(g) for g in leaders) + ".")
        short2 = tr(L, f" 세기 사이 차이가 가장 큰 갈래는 {nm(gw)}{_ro(nm(gw))}, {cl(int(sw.idxmin()), 'ko')} {fmt(sw.min(), '.1%')}에서 {cl(int(sw.idxmax()), 'ko')} {fmt(sw.max(), '.1%')}까지 걸쳐 있다.",
                    f" The class that differs most between centuries is {nm(gw)}, from {fmt(sw.min(), '.1%')} in the {cl(int(sw.idxmin()), 'en')} to {fmt(sw.max(), '.1%')} in the {cl(int(sw.idxmax()), 'en')}.")
        gwp = [(int(c), v) for c, v in D.b[D.b.genre1 == gw].set_index("century").share_works.items() if c == c]
        short2 += far_tail([(nm(gw), gwp)], ".1%", L)   # 1.0.9 v2 (Codex 2.7)
        r = D.b[(D.b.century == rc) & (D.b.genre1 == "詩類")].iloc[0]
        one = tr(L, f"{rcl}의 시 {fmt(r.share_works, '.1%')}는 그 세기 저자 글 {int(r.total_works):,}편 가운데 {int(r.n_works):,}편이 시라는 뜻이다.",
                 f"The {rcl}'s poetry value {fmt(r.share_works, '.1%')} means {int(r.n_works):,} of the {int(r.total_works):,} own works are poems.")
        z = D.b2[(D.b2.century == rc) & (D.b2.genre1 == "雜著類")]; zo = int(z[z.genre2 == "其他類"].n_works.sum()); zt = int(z.n_works.sum())
        mis = tr(L, f"편 수로 센 몫이라 짧은 시 한 수와 긴 상소 한 편이 똑같이 한 편이다(글자 기준은 표에 있다). 잡저는 논설·기·잠명·상량문 등 그 밖의 글을 모은 갈래이고, {rcl} 잡저 {zt:,}편 가운데 {zo:,}편({fmt(zo / zt, '.1%')})은 중분류가 「기타류」다. ",
                 f"Shares count works, so a short poem and a long memorial each count once (the table also has character-based shares). Miscellany gathers the remaining writings (discourses, records, admonitions, beam-raising texts and so on); of the {rcl}'s {zt:,} miscellany works, {zo:,} ({fmt(zo / zt, '.1%')}) have the minor class 'other'. ") + bn + " " + extra_mis
        terms = tr(L, "갈래(대분류) = 고전번역원이 편마다 붙인 문체 분류 일곱 가지. 갈래마다 무엇이 드는지는 그림 위 단락에 있다.",
                   "Class (major genre class): the ITKC's seven-way classification of each work; what each holds is in the paragraph above the chart.")
        return intro, [("short", lead_txt + short2), ("how", how), ("one", one), ("mis", mis), ("terms", terms)]
    elif mid == "b5_relational_share":
        g2 = D.b2; sel = g2[(g2.genre1 == "哀祭類") | (g2.genre2.isin(["碑誌類", "行狀類"]))].groupby("century").n_works.sum(); tw = g2.groupby("century").n_works.sum()
        intro = tr(L, "세기마다 저자 글 가운데 애제 갈래 전체(제문·애사 등 — 제문에는 신에게 올린 것도 있다)와 전기 갈래의 비지·행장을 합친 글의 비율을 그린 그림이다.",
                   "The share of own works in the whole elegy class (rites and laments; some rite texts were addressed to spirits) plus the epitaphs and accounts of conduct of the biography class, per century.")
        how = line_how(tr(L, "애제·비지·행장 편 ÷ 저자 글", "elegy, epitaph and conduct-account works ÷ own works"), L)
        one = tr(L, f"{rcl}의 {fmt(sel.get(rc, 0) / tw[rc], '.1%')}는 저자 글 {int(tw[rc]):,}편 가운데 {int(sel.get(rc, 0)):,}편이 이런 글이라는 뜻이다.",
                 f"The {rcl}'s {fmt(sel.get(rc, 0) / tw[rc], '.1%')} means {int(sel.get(rc, 0)):,} of {int(tw[rc]):,} own works are of this kind.")
        mis = tr(L, "전기 갈래 가운데 비지·행장만 넣고 계보·기타는 넣지 않았다. ", "Of the biography class only epitaphs and accounts of conduct are included; genealogies and the rest are not. ") + \
            denoms(pd.DataFrame({"c": tw.index, "n": tw.values}), "c", "n", "편", "own works", L) + " " + bn
        terms = tr(L, "애제 = 제사 때 읽는 글(제문)과 죽음을 슬퍼하는 글(애사). 비지 = 묘비·묘지에 새긴 글. 행장 = 죽은 이의 행적을 적은 글.",
                   "Elegies: texts read at rites and laments. Epitaphs: texts for tombstones and tomb records. Accounts of conduct: records of a dead person's life.")
    elif mid == "b7_other_share":
        o = D.other.set_index("century"); r = o.loc[rc]
        intro = tr(L, "세기마다 저자 글 가운데 고전번역원 분류에서 중분류가 「기타류」인 글의 비율을 그린 그림이다. 분류가 얼마나 거친지를 보는 지표다.",
                   "The share of own works whose minor class is 'other' in the ITKC classification, per century — a measure of how coarse the classification is.")
        how = line_how(tr(L, "중분류 其他類 편 ÷ 저자 글", "works in an 'other' minor class ÷ own works"), L)
        one = tr(L, f"{rcl}의 {fmt(r.other_share, '.1%')}는 저자 글 {int(r.n):,}편 가운데 {int(round(r.n * r.other_share)):,}편이 중분류 없이 「기타」로 묶였다는 뜻이다.",
                 f"The {rcl}'s {fmt(r.other_share, '.1%')} means {int(round(r.n * r.other_share)):,} of {int(r.n):,} own works were filed under 'other' with no finer class.")
        mis = tr(L, "값이 크다고 그 세기 글이 특이하다는 뜻이 아니다 — 분류가 세분되지 않았다는 뜻이고, 그만큼 그 세기의 문체 구성 수치가 거칠다. ",
                 "A high value does not mean unusual writing; it means the classification is coarse there, so that century's genre figures are rougher. ") + \
            denoms(D.other, "century", "n", "편", "own works", L) + " " + bn
        pr = D.b2[["genre1", "genre2"]].drop_duplicates(); n28 = int((pr.genre1 != pr.genre2).sum())
        terms = tr(L, f"중분류 = 일곱 갈래(대분류) 아래의 더 잘게 나눈 분류(대분류마다 그 아래 중분류를 세어 더하되, 대분류와 이름이 같은 詩類·書簡類 같은 것을 빼면 {n28}가지). 其他類 = 그 갈래 안에서 따로 이름을 붙이지 않은 나머지.",
                   f"Minor class: the finer classes under the seven major ones ({n28}, counting the minor classes under each major class and leaving out those named the same as their major class, such as 詩類 and 書簡類). 'Other' (其他類): the rest of a class, given no name of its own.")
    elif mid == "b8_poem_length":
        p = D.poems.set_index("century"); r = p.loc[rc]
        intro = tr(L, "저자가 쓴 시 갈래의 글(부·사 포함) 한 편이 몇 자인지를 세기마다 그린 그림이다. 가운데 선은 중앙값, 위아래 선은 사분위다.",
                   "Length in main-text characters of the authors' poetry-class works (including fu and ci), by century: the median, with the quartiles above and below.")
        how = line_how(tr(L, "시 한 편의 본문 글자 수", "main-text characters per poem"), L, QUART_HOW[L])
        one = tr(L, f"{rcl}에 태어난 저자의 시 갈래 글 {int(r.n_poems):,}편을 글자 수 순으로 늘어세우면 한가운데가 {qv(r.poem_chars_median, '자', '', 'ko')}이고, 순서상 가운데 절반의 경계는 {qv(r.poem_chars_p25, '자', '', 'ko')}와 {qv(r.poem_chars_p75, '자', '', 'ko')}다.",
                 f"Put the {int(r.n_poems):,} poetry-class works of authors born in the {rcl} in order of length: the middle one has {qv(r.poem_chars_median, '', '', 'en')} characters, and the middle half of the order is bounded by {qv(r.poem_chars_p25, '', '', 'en')} and {qv(r.poem_chars_p75, '', '', 'en')}.")
        mis = tr(L, "정형시는 길이가 정해져 있다 — 오언절구 20자, 칠언절구 28자, 오언율시 40자, 칠언율시 56자. 이 길이에 값이 많이 모여 중앙값과 아래 사분위가 이런 수에 놓인다. 다만 길이만으로 한 편의 형식을 정할 수는 없다. 연작시가 한 편으로 묶이면 그 편은 길어진다. ",
                 "Fixed forms have fixed lengths: a five-character quatrain 20 characters, a seven-character quatrain 28, a five-character regulated verse 40, a seven-character regulated verse 56. Many values gather at these lengths, so the medians and lower quartiles sit on these numbers; length alone does not tell a poem's form. A poem series filed as one work is long. ") + bn + " " + extra_mis
        terms = QUART[L].replace("{eg}", round_eg(D.poems, "poem_chars", "자", " characters", L))
        idx = [0]
    elif mid == "d1_dates" and k == 0:
        intro = tr(L, "세기마다 저자 가운데 몰년(죽은 해)이 기록된 사람의 비율을 그린 그림이다.", "The share of authors whose death year is recorded, per century.")
        how = line_how(tr(L, "몰년이 있는 저자 ÷ 저자", "authors with a death year ÷ authors"), L)
        one = tr(L, f"{rcl}의 {fmt(d.death_known / d.n_authors, '.0%')}는 저자 {int(d.n_authors):,}명 가운데 {int(d.death_known):,}명의 몰년이 서지에 있다는 뜻이다.",
                 f"The {rcl}'s {fmt(d.death_known / d.n_authors, '.0%')} means {int(d.death_known):,} of {int(d.n_authors):,} authors have a death year in the bibliography.")
        mis = tr(L, "생년이 없는 저자는 어느 세기에도 들지 않아 이 그림에 없다. 세로 눈금이 0에서 시작하므로 100%에 가까운 세기들의 차이는 작게 보인다. ",
                 "Authors with no birth year belong to no century and are not on the chart. The scale starts at 0, so centuries near 100% look alike. ") + denoms(D.dcen, "century", "n_authors", "명", "authors", L, people=True)
        terms = tr(L, "몰년 = 죽은 해. 고전번역원 서지에 적힌 서기 연도를 그대로 썼다.", "Death year: as given in the ITKC bibliography (Western calendar).")
    elif mid == "d1_dates":
        intro = tr(L, "세기마다 저자가 몇 해를 살았는지(몰년 − 생년)의 중앙값을 그린 그림이다.", "Median lifespan (death year − birth year) of the authors, per century.")
        how = line_how(tr(L, "수명(년)", "lifespan in years"), L)
        one = tr(L, f"{rcl}의 {fmt(d.lifespan_median, ',.0f')}년은 몰년이 있는 저자 {int(d.death_known):,}명의 수명을 늘어세웠을 때 한가운데 값이다.",
                 f"The {rcl}'s {fmt(d.lifespan_median, ',.0f')} years is the middle lifespan of the {int(d.death_known):,} authors with a death year.")
        dk = {int(c): int(v) for c, v in dc.death_known.items()}
        mis = tr(L, "문집을 남긴 사람들의 수명이라 같은 시대 사람 전체의 수명이 아니다. 수명은 서지의 두 연도를 뺀 값이고, 몰년이 없는 저자는 빠졌다. ",
                 "These are the lifespans of people who left collections, not of everyone of their time. Lifespan is the difference of the two years in the bibliography; authors without a death year are left out. ") + few_text(L, pts=allpts, counts=dk, unit=("명", "authors"))
        terms = QUART[L].split(" 사분위")[0].split(" Quartiles")[0]
    elif mid == "d2_munkwa" and k == 0:
        intro = tr(L, "세기마다 저자 가운데 문과 급제자 명단(문과방목)의 사람과 같은 사람으로 이어진 비율을 그린 그림이다. 두 선은 연결 규칙을 모두 쓴 값과, 성명과 생년이 모두 맞는 경우만 센 값이다.",
                   "The share of authors linked to a person in the civil examination roster, per century: one line with every linking rule, one with name and birth year matching only.")
        how = line_how(tr(L, "연결된 저자 ÷ 저자", "linked authors ÷ authors"), L)
        idx = [0, 1]
        one = tr(L, f"{rcl}의 「연결률」 {fmt(d.link_rate, '.0%')}는 저자 {int(d.n_authors):,}명 가운데 {int(d.n_linked):,}명이 방목의 급제자와 이어졌다는 뜻이다. 「성명+생년만」은 {int(d.n_linked_strict):,}명({fmt(d.link_rate_strict, '.0%')})이다.",
                 f"The {rcl}'s linkage of {fmt(d.link_rate, '.0%')} means {int(d.n_linked):,} of {int(d.n_authors):,} authors were matched to someone who passed; with name and birth year only, {int(d.n_linked_strict):,} ({fmt(d.link_rate_strict, '.0%')}).")
        mis = tr(L, "연결률은 급제율이 아니다. 급제하지 않은 저자는 연결되지 않는 것이 정상이고, 동명이인이 여럿 남아 정하지 못한 경우(미확정)도 연결로 세지 않았다. ",
                 "Linkage is not a pass rate: authors who never passed are rightly left unlinked, and cases left ambiguous by namesakes are not counted as linked. ") + denoms(D.dcen, "century", "n_authors", "명", "authors", L, people=True)
        # 1.0.9 v2 (Codex 3.3): say why the two lines coincide when they do
        au = D.authors; extra = au[au.munkwa_rule.isin(["M2", "M3"])]; nob = int(extra.birth.isna().sum())
        if (D.dcen.n_linked == D.dcen.n_linked_strict).all():
            mis += tr(L, f" 이 그림에서 두 선은 모든 세기에서 겹친다. (2)·(3)으로 이어진 저자는 {len(extra):,}명이고" + (f" 모두 생년이 없어 어느 세기에도 들지 않기 때문이다." if nob == len(extra) else "다."),
                      f" The two lines coincide in every century: {len(extra):,} authors were linked by (2) or (3)" + (", all without a birth year, so they belong to no century." if nob == len(extra) else "."))
        terms = tr(L, "문과방목 = 조선 시대 문과 급제자 명단(한국학중앙연구원 자료). 연결 = 한자 성명이 같은 방목의 사람(이체자를 맞춘 뒤)을 후보로 놓고 다음 순서로 본다. 앞 단계에서 정해지면 뒤 단계는 보지 않는다. (1) 생년도 같은 후보가 한 사람이면 같은 사람으로 본다. 생년이 같은 후보가 여럿이면, 본관이 모두 같을 때는 한 사람이 여러 시험(중시·발영시 등)에 오른 것으로 보고 가장 이른 급제를 쓰고, 본관이 서로 다를 때는 미확정으로 두고 (2)·(3)으로 넘어가지 않는다. (2) 생년이 같은 후보가 없으면, 방목에 생년이 없고 자 또는 호가 같은 후보를 본다. 한 사람이면 같은 사람으로 보고, 둘 이상이면 미확정이다. (3) 그것도 없으면(저자의 생년이 있을 때), 후보가 한 사람뿐이고 방목에 생년이 없으며 시험년이 저자 생년 + 15년부터 몰년(몰년이 없으면 생년 + 70년) 사이일 때 같은 사람으로 본다(성명이 같은 후보가 여럿이고 그 가운데 시험년이 이 범위에 드는 후보가 둘 이상이면 미확정). 미확정은 연결로 세지 않는다. 「성명+생년만」 선은 (1)로 이어진 저자(가장 이른 급제를 쓴 경우 포함)만 센 값이다. 규칙은 지표의 공식란에 있다.",
                   "Examination roster: the list of those who passed the Joseon civil examination (Academy of Korean Studies data). Linked: roster entries with the same name in Chinese characters (after variant forms are unified) are the candidates, and the steps below are tried in order; once a step decides, the later ones are not tried. (1) If one candidate also has the same birth year, it is the same person. If several do, then where all share one clan seat they are taken as one person who passed several examinations (re-examinations and the like) and the earliest pass is used; where their clan seats differ, the case is left unresolved and (2) and (3) are not tried. (2) If no candidate has the same birth year: candidates whose roster entry has no birth year and whose courtesy or pen name matches. One such candidate is the same person; more than one leaves the case unresolved. (3) Failing that (when the author's birth year is known): the only candidate, with no birth year in the roster and an exam year between the author's birth year + 15 and the death year (birth year + 70 if no death year), is the same person (if there are several same-name candidates and more than one falls in that window, the case is unresolved). Unresolved cases are not counted as linked. The 'name + birth only' line counts the authors linked by (1), the earliest-pass cases included. The rules are in the formula above.")
    elif mid == "d2_munkwa":
        intro = tr(L, "문과방목과 이어진 저자가 몇 살에 급제했는지를 세기마다 그린 그림이다. 가운데 선은 중앙값, 위아래 선은 사분위다.",
                   "Age at passing the examination for the linked authors, per century: the median, with the quartiles above and below.")
        how = line_how(tr(L, "급제 연령(세는나이)", "age at passing (East Asian reckoning)"), L, QUART_HOW[L])
        one = tr(L, f"{rcl}에 태어나 연결된 저자 {int(d.n_linked):,}명의 급제 연령을 늘어세우면 한가운데가 {qv(d.exam_age_median, '세', '', 'ko')}이고, 순서상 가운데 절반의 경계는 {qv(d.exam_age_p25, '세', '', 'ko')}와 {qv(d.exam_age_p75, '세', '', 'ko')}다.",
                 f"For the {int(d.n_linked):,} linked authors born in the {rcl}, the middle age at passing is {qv(d.exam_age_median, '', '', 'en')}, and the middle half of the order is bounded by {qv(d.exam_age_p25, '', '', 'en')} and {qv(d.exam_age_p75, '', '', 'en')}.")
        mis = tr(L, "연결된 저자만의 값이다 — 연결되지 않은 급제자는 빠져 있다. 연결된 저자가 적은 세기의 선은 몇 사람의 값이다. ",
                 "Only linked authors are included; passers who were not linked are missing. Where few authors are linked, the line rests on a few people. ") + denoms(D.dcen[D.dcen.n_linked > 0], "century", "n_linked", "명", "linked authors", L, people=True)
        terms = tr(L, "세는나이 = 태어난 해를 한 살로 치는 나이(시험년 − 생년 + 1). ", "East Asian reckoning: a person is one in the year of birth (exam year − birth year + 1). ") + QUART[L].replace("{eg}", round_eg(D.dcen, "exam_age", "세", "", L))
    elif mid == "d3_pub_lag":
        intro = tr(L, "저자가 죽은 해부터 문집(총간에 실린 판)이 간행된 해까지 몇 해가 걸렸는지를 세기마다 그린 그림이다. 가운데 선은 중앙값, 위아래 선은 사분위다.",
                   "Years from the author's death to the printing of the edition in the compendium, per century: the median, with the quartiles above and below.")
        how = line_how(tr(L, "몰년에서 간행년까지 햇수", "years from death to printing"), L, QUART_HOW[L])
        dcl = D.dcol; lagn = {int(c): int(g.pub_lag.notna().sum()) for c, g in dcl[dcl.century.notna()].groupby("century")}
        nl = lagn.get(rc, 0); neg = int((dcl.pub_lag < 0).sum())
        one = tr(L, f"{rcl}에 태어난 저자의 문집 가운데 간행년이 있는 {int(d.pub_year_known):,}종에서 몰년도 있는 {nl:,}종의 몰년부터 간행년까지 햇수를 늘어세우면 한가운데가 {qv(d.pub_lag_median, '년', '', 'ko')}이고, 순서상 가운데 절반의 경계는 {qv(d.pub_lag_p25, '년', '', 'ko')}과 {qv(d.pub_lag_p75, '년', '', 'ko')}이다.",
                 f"Of the collections of authors born in the {rcl}, {int(d.pub_year_known):,} have a printing year and {nl:,} of these also a death year; put their lags from death to printing in order and the middle one is {qv(d.pub_lag_median, '', '', 'en')} years, and the middle half of the order is bounded by {qv(d.pub_lag_p25, '', '', 'en')} and {qv(d.pub_lag_p75, '', '', 'en')}.")
        mis = tr(L, f"간행년은 총간이 저본으로 삼은 판의 간행년이어서 첫 간행이 아닐 수 있다. 저본이 초간보다 나중에 간행된 문집에서는 이 햇수가 첫 간행까지의 햇수보다 길다. 이 값은 두 해의 차이일 뿐이어서, 저자가 죽기 전에 간행된 판이면 음수가 된다(모든 세기를 합쳐 {neg:,}종). 간행년이나 몰년이 없는 문집은 빠졌다. ",
                 f"The printing year is that of the edition the compendium reproduces, which may not be the first; where that edition came after the first printing, the lag is longer than the lag to the first printing. The value is simply the difference of the two years, so an edition printed before the author's death gives a negative lag ({neg:,} collections over all centuries). Collections without a printing year or a death year are left out. ") + few_text(L, pts=allpts, counts=lagn)
        terms = QUART[L].replace("{eg}", round_eg(D.dcen, "pub_lag", "년", " years", L))
    elif mid in ("d4_translation", "d5_punct"):
        tr_ = mid == "d4_translation"
        num = int(d.n_translated if tr_ else d.n_punct); share = d.translation_share if tr_ else d.punct_share
        intro = tr(L, ("세기마다 편 가운데 고전종합DB 안에서 번역문이 이어져 있는 편의 비율을 그린 그림이다." if tr_ else "세기마다 편 가운데 고전종합DB 안에서 교감표점본이 이어져 있는 편의 비율을 그린 그림이다."),
                   ("The share of works linked to a translation inside the ITKC database, per century." if tr_ else "The share of works linked to a collated and punctuated edition inside the ITKC database, per century."))
        how = line_how(tr(L, "연계된 편 ÷ 편", "linked works ÷ works"), L)
        one = tr(L, f"{rcl}의 {fmt(share, '.0%')}는 편 {int(d.n_works):,}편 가운데 {num:,}편에 {'번역문' if tr_ else '교감표점본'} 연계가 있다는 뜻이다.",
                 f"The {rcl}'s {fmt(share, '.0%')} means {num:,} of {int(d.n_works):,} works carry a link to {'a translation' if tr_ else 'a collated and punctuated edition'}.")
        mis = tr(L, ("데이터베이스 안의 연계를 센 값이다 — 번역 사업의 현황이 아니며, 번역서가 있어도 연계되지 않은 문집이 있다. 「미번역」으로 읽지 않는다. " if tr_ else
                     "데이터베이스 안의 연계를 센 값이다 — 교감표점 사업은 정편의 일부에서 진행됐다. "),
                 ("These are links inside the database, not the state of translation: some translated collections are not linked. Do not read the gaps as 'untranslated'. " if tr_ else
                  "These are links inside the database; the collation and punctuation project covered part of the first series. ")) + extra_mis
        terms = tr(L, "연계 = 고전종합DB에서 원문 편과 " + ("번역문" if tr_ else "교감표점본") + "이 서로 이어져 있음(2024년 8월 자료 기준). 교감표점 = 여러 판본을 견줘 글자를 바로잡고(교감) 문장부호를 찍은(표점) 본.",
                   "Linked: the source work and its " + ("translation" if tr_ else "collated and punctuated edition") + " are joined in the ITKC database (data of August 2024). Collated and punctuated edition: a text checked against other editions and given modern punctuation.")
    else:
        return "", []
    return intro, [("short", line_short(series, spec, idx, lang, far_ok=mid not in ("a1_works", "a2_chars", "a3_centuries"))), ("how", how), ("one", one), ("nums", nums), ("mis", mis), ("terms", terms)]


# ----------------------------------------------------------------- the three share panels (b1, b3, b4, b6)
def panel_notes(g, lang):
    D = C["D"]; rc = C["rc"]; L = lang; rcl = cl(rc, L)
    gn = C["GKO"][g] if L == "ko" else C["GEN"][g]
    b = D.b[D.b.genre1 == g].set_index("century"); ba = D.b_all[D.b_all.genre1 == g].set_index("century")
    r = b.loc[rc]; ra = ba.loc[rc]
    pts = [(int(c), v) for c, v in b.share_works.items() if c == c]
    hs, hv, ls, lv = extremes(pts)
    intro = tr(L, f"{gn}의 비중을 저자가 태어난 세기마다 세 가지 방식으로 센 작은 그림 셋이다.", f"The {gn} share by the century of the author's birth, counted three ways in three small charts.")
    how = tr(L, f"점 하나가 한 세기다. 가로는 저자가 태어난 세기, 세로는 그 갈래의 몫이다. 위에 있을수록 몫이 크다. 왼쪽 「편 기준」은 저자 글의 편 수로, 가운데 「글자 기준」은 저자 글의 글자 수로 센 비율이고, 오른쪽 「편 기준, 타인 글 포함」은 문집에 함께 실린 다른 사람의 글까지 넣어 편 수로 센 비율이다. 세 그림의 세로 눈금이 같아서 높이를 그대로 견줄 수 있다. 문집이 없는 세기에서는 선이 끊긴다.",
             f"Each point is one century. Left to right is the century of the author's birth; up the side is the class's share. Higher means a larger share. Left, 'by works' counts the author's own works; middle, 'by characters' counts their characters; right, 'by works, incl. others' also counts the works by other writers printed in the collection. The three charts share one vertical scale, so heights compare directly. The lines break at centuries with no collection.")
    short = tr(L, f"「편 기준」으로 보면 문집이 {C['kmin']}종 이상인 세기({ok_range('ko')}) 가운데 몫이 가장 큰 세기는 {cls(hs, 'ko')}({fmt(hv, '.1%')}), 가장 작은 세기는 {cls(ls, 'ko')}({fmt(lv, '.1%')})다.",
               f"By works, among the centuries with at least {C['kmin']} collections ({ok_range('en')}), the share is largest in the {cls(hs, 'en')} ({fmt(hv, '.1%')}) and smallest in the {cls(ls, 'en')} ({fmt(lv, '.1%')}).")
    short += far_tail([(tr(L, "편 기준", "by works"), pts)], ".1%", L)   # 1.0.9 v2 (Codex 2.7): the small centuries of the panel compared
    one = tr(L, f"{rcl}의 「편 기준」 {fmt(r.share_works, '.1%')}는 저자 글 {int(r.total_works):,}편 가운데 {int(r.n_works):,}편이 {gn}{jo(gn, '이라는', '라는')} 뜻이다. 같은 세기 「글자 기준」은 {fmt(r.share_chars, '.1%')}(글자 {int(r.total_chars):,}자 가운데 {int(r.chars):,}자), 「타인 글 포함」은 {fmt(ra.share_works, '.1%')}(편 {int(ra.total_works):,}편 가운데 {int(ra.n_works):,}편)다.",
             f"The {rcl}'s 'by works' {fmt(r.share_works, '.1%')} means {int(r.n_works):,} of {int(r.total_works):,} own works are {gn}. In the same century 'by characters' is {fmt(r.share_chars, '.1%')} ({int(r.chars):,} of {int(r.total_chars):,} characters) and 'incl. others' {fmt(ra.share_works, '.1%')} ({int(ra.n_works):,} of {int(ra.total_works):,} works).")
    longer = r.share_chars > r.share_works
    mis = tr(L, f"세 값은 세는 단위(편이냐 글자냐)와 넣은 글(저자 글만이냐 남의 글까지냐)이 달라서 다르다. {rcl}에서 「글자 기준」이 「편 기준」보다 {'크다' if longer else '작다'} — {gn} 한 편의 평균 글자 수가 저자 글 전체의 평균보다 {'많다' if longer else '적다'}는 뜻이다. ",
             f"The three values differ because the unit differs (works or characters) and so do the works included (own works only, or others' too). In the {rcl} 'by characters' is {'above' if longer else 'below'} 'by works': a work in this class is on average {'longer' if longer else 'shorter'} than the author's works overall. ")
    if g == "詩類":
        mis += tr(L, "연작시 「十首」가 한 편으로 묶이면, 다른 갈래와 함께 실린 경우 편 기준 몫은 낮아지고 글자 기준은 그대로다(모두 시인 경우는 100% 그대로). ",
                  "A series such as 十首 ('ten poems') filed as one work lowers the share by works where other classes are present, but not the share by characters (an all-poetry collection stays at 100%). ")
    mis += few_text(L) + " " + birth_not_writing(L)
    terms = tr(L, "편 기준 = 편 수로 센 몫. 글자 기준 = 글자 수로 센 몫. 저자 글 = 필자 표지가 문집의 저자와 같은 편. 타인 글 = 같은 문집에 실린 저자 글이 아닌 편(남의 서문·발문·행장·만사와 필자 표지가 빈 편).",
               "By works: the share counted in works. By characters: the share counted in characters. Own works: works whose writer tag is the collection's author. Others: the other works in the same collection (prefaces, postscripts, biographies and elegies by others, and works with an empty writer tag).")
    return intro, [("short", short), ("how", how), ("one", one), ("mis", mis), ("terms", terms)]


# ----------------------------------------------------------------- top-30 bars on the metric pages
def _title(r, lang):
    cid = r["collection_id"] if "collection_id" in r.index else r.name
    row = C["D"].col.set_index("collection_id").loc[cid]
    return f"『{row.title_ko}』" if lang == "ko" else str(row.title_hj)


def bar_short(items, spec, lang, low=False, allv=None):
    """1.0.9 v1 (Codex 2.9): ties at the first or the last bar are named, counted over all collections (allv)."""
    (n0, v0, _), (nl, vl, _) = items[0], items[-1]
    k = len(items)
    if v0 == vl:   # every bar the same length (top 30 of a share at 100%): the order is explained under Easy to misread
        return tr(lang, f"막대 {k}개가 모두 같은 값이어서({fmt(v0, spec)}) 길이로는 순서를 가릴 수 없다. 늘어놓은 순서는 「잘못 읽기 쉬운 것」에 적었다.",
                  f"All {k} bars have the same value ({fmt(v0, spec)}), so their length does not order them; the order is explained under Easy to misread.")
    vals = [float(x) for x in allv if x == x] if allv is not None else [v for _, v, _ in items]
    t0 = sum(1 for x in vals if x == v0); tl = sum(1 for x in vals if x == vl)
    pos = [i + 1 for i, (_, v, _) in enumerate(items) if v == vl]
    s0, sl = fmt(v0, spec), fmt(vl, spec)
    if lang == "ko":
        a = f"{'가장 짧은' if low else '가장 긴'} 막대는 {n0}의 {s0}" + (f"(이 값인 문집 {t0}종 가운데 맨 위)" if t0 > 1 else "")
        if tl > 1 and tl == len(pos):
            b = f"{k}번째는 {nl}의 {sl}{jo(sl, '이다', '다')}({'·'.join(map(str, pos))}번째가 같은 값)."
        elif tl > 1:
            b = f"{k}번째는 {nl}의 {sl}{jo(sl, '이다', '다')}(이 값인 문집 {tl}종 가운데 {len(pos)}종만 그렸다)."
        else:
            b = f"{k}번째는 {nl}의 {sl}{jo(sl, '이다', '다')}."
        return a + ", " + b
    a = f"The {'shortest' if low else 'longest'} bar is {n0} at {s0}" + (f" (the first of {t0} collections with this value)" if t0 > 1 else "")
    if tl > 1 and tl == len(pos):
        b = f"number {k} is {nl} at {sl} (numbers {', '.join(map(str, pos[:-1]))} and {pos[-1]} share this value)."
    elif tl > 1:
        b = f"number {k} is {nl} at {sl} ({len(pos)} of the {tl} collections with this value are drawn)."
    else:
        b = f"number {k} is {nl} at {sl}."
    return a + "; " + b


def bar_how(what_ko, what_en, lang, low=False):
    return tr(lang, f"막대 하나가 문집 하나다. 막대 길이는 {what_ko}이고, 아래 눈금으로 읽는다. 위에서부터 {'값이 작은' if low else '값이 큰'} 순이다. 막대에 커서를 두면 값이 보인다.",
              f"Each bar is one collection. Its length is {what_en}, read on the scale below. Bars run from the {'smallest' if low else 'largest'} value down. Hover over a bar for its value.")


def top_notes(mid, items, spec, lang, extra_mis="", top_row=None, idx=0, allv=None):
    """Notes for the top-30 (or bottom-30) bar chart of a metric page. items are the drawn bars; top_row the data row of the first bar."""
    D = C["D"]; L = lang; r = top_row; nums = ""
    low = mid == "a6_own_share"
    if mid == "a1_works":
        intro = tr(L, "글이 가장 많이 실린 문집 30종을 많은 순으로 늘어놓은 그림이다.", "The 30 collections holding the most works, largest first.")
        how = bar_how("문집에 실린 편 수(저자 글과 남의 글을 합친 수)", "the number of works in the collection (own works and works by others together)", L)
        one = tr(L, f"맨 위 막대는 {_title(r, 'ko')}{jo(_title(r, 'ko').strip('『』'), '이다', '다')}. 글 {int(r.n_works):,}편이 실려 있고, 그 가운데 {int(r.n_own_works):,}편({fmt(r.own_share, '.1%')})이 저자 자신의 글이다.",
                 f"The top bar is {_title(r, 'en')}: {int(r.n_works):,} works, of which {int(r.n_own_works):,} ({fmt(r.own_share, '.1%')}) are the author's own.")
        mis = tr(L, "편 수는 편집진이 글을 끊은 방식에 따라 달라진다 — 시가 많은 문집은 편 수가 많고 글자 수는 적을 수 있다. 글자 수 순위는 지표 「글자 수」에 있다.",
                 "The number of works depends on how the editors cut the text; a collection of many poems can have many works and few characters. The ranking by characters is on the character-count metric.")
        terms = tr(L, "편 = 고전번역원 자료에서 글 하나의 단위(시 한 수, 편지 한 통, 묘지명 한 편).", "Work: one piece in the ITKC data (a poem, a letter, an epitaph).")
    elif mid == "a2_chars":
        intro = tr(L, "한자가 가장 많은 문집 30종을 많은 순으로 늘어놓은 그림이다. 본문과 주를 합친 글자 수다.", "The 30 collections with the most characters (text and notes together), largest first.")
        how = bar_how("문집의 한자 수(본문 + 주)", "the number of Chinese characters (text + notes)", L)
        one = tr(L, f"맨 위 막대는 {_title(r, 'ko')}{jo(_title(r, 'ko').strip('『』'), '이다', '다')}. 본문 {int(r.chars_main):,}자와 주 {int(r.chars_note):,}자를 더해 {int(r.chars):,}자다.",
                 f"The top bar is {_title(r, 'en')}: {int(r.chars_main):,} characters of text and {int(r.chars_note):,} in notes, {int(r.chars):,} in all.")
        mis = tr(L, "고전번역원 입력본의 글자를 센 것이어서 영인본 면과 어긋난 글자는 반영되지 않는다. 구두점·공백·한글은 세지 않는다.",
                 "The ITKC's keyed text is counted, so characters that differ from the facsimile pages are not corrected. Punctuation, spaces and Hangul are not counted.")
        terms = tr(L, "주 = 본문에 작은 글씨로 단 설명과 판면 가장자리에 붙인 주(원주·교감주·난외주).", "Notes: explanations in small type in the text or at the edge of the printed page (original, collation and marginal notes).")
    elif mid == "a5_note_share":
        intro = tr(L, "전체 글자 가운데 주 안의 글자 비율이 가장 높은 문집 30종을 높은 순으로 늘어놓은 그림이다.", "The 30 collections with the highest share of characters in notes, highest first.")
        how = bar_how("주 글자 ÷ 전체 글자", "note characters ÷ all characters", L)
        one = tr(L, f"맨 위 막대 {_title(r, 'ko')}의 {fmt(r.note_share, '.1%')}는 글자 {int(r.chars):,}자 가운데 {int(r.chars_note):,}자가 주 안에 있다는 뜻이다.",
                 f"The top bar, {_title(r, 'en')}, at {fmt(r.note_share, '.1%')}: {int(r.chars_note):,} of its {int(r.chars):,} characters are in notes.")
        mis = tr(L, "원주와 고전번역원이 붙인 교감주·난외주를 합친 비율이다.", "Original notes and the ITKC's collation and marginal notes are added together.") + extra_mis
        terms = tr(L, "원주 = 저자나 편찬자가 붙인 주. 교감주 = 판본 사이의 글자 차이를 적은 주. 난외주 = 판면 바깥 여백의 주.",
                   "Original notes: by the author or compiler. Collation notes: differences between editions. Marginal notes: notes outside the printed block.")
    elif mid == "a6_own_share":
        intro = tr(L, "문집에 실린 글 가운데 저자 자신의 글 비율이 가장 낮은 문집 30종을 낮은 순으로 늘어놓은 그림이다. 부록이나 남의 글이 많은 문집이다.",
                   "The 30 collections with the lowest share of the author's own works, lowest first — collections heavy with appendices and others' writing.")
        how = bar_how("저자 글 ÷ 전체 편", "own works ÷ all works", L, low=True)
        one = tr(L, f"맨 위 막대 {_title(r, 'ko')}의 {fmt(r.own_share, '.1%')}는 글 {int(r.n_works):,}편 가운데 저자 글이 {int(r.n_own_works):,}편이라는 뜻이다.",
                 f"The top bar, {_title(r, 'en')}, at {fmt(r.own_share, '.1%')}: {int(r.n_own_works):,} of its {int(r.n_works):,} works are the author's own.")
        mis = tr(L, "필자 표지가 비어 있는 편은 저자 글로 세지 않았으므로, 표지가 빠진 문집은 이 그림에 올라오기 쉽다.", "Works with an empty writer tag are not counted as own works, so a collection with missing tags can land here.") + extra_mis
        terms = tr(L, "저자 글 = 필자 표지가 문집의 저자와 같은 편.", "Own works: works whose writer tag is the collection's author.")
    elif mid in ("b1_poetry_share", "b3_letters_share", "b4_memorials_share", "b6_prefaces_share"):
        g = {"b1_poetry_share": "詩類", "b3_letters_share": "書簡類", "b4_memorials_share": "公車類", "b6_prefaces_share": "序跋類"}[mid]
        gn = C["GKO"][g] if L == "ko" else C["GEN"][g]
        sh = float(r[f"share_works_{g}"]); n = int(r.n_own_works)
        intro = tr(L, f"저자 글 가운데 {gn}의 몫이 가장 큰 문집 30종을 큰 순으로 늘어놓은 그림이다(편 수 기준).", f"The 30 collections with the largest {gn} share of own works (by works), largest first.")
        how = bar_how(f"저자 글 가운데 {gn}의 편 수 비율", f"the {gn} share of own works, by number of works", L)
        one = tr(L, f"맨 위 막대 {_title(r, 'ko')}의 {fmt(sh, '.1%')}는 저자 글 {n:,}편 가운데 {int(round(sh * n)):,}편이 {gn}{jo(gn, '이라는', '라는')} 뜻이다.",
                 f"The top bar, {_title(r, 'en')}, at {fmt(sh, '.1%')}: {int(round(sh * n)):,} of its {n:,} own works are {gn}.")
        mis = tr(L, "비율만 보면 글이 몇 편 안 되는 문집도 맨 위에 올 수 있다 — 막대가 길다고 그 갈래의 글이 많은 문집은 아니다.", "A share puts small collections next to large ones; a long bar does not mean many works of the class.") + extra_mis
        terms = tr(L, "저자 글 = 필자 표지가 문집의 저자와 같은 편.", "Own works: works whose writer tag is the collection's author.")
    elif mid == "c1_recipients":
        intro = tr(L, "서간 제목에서 뽑은 수신자(받는 사람) 문자열의 가짓수가 가장 많은 문집 30종을 많은 순으로 늘어놓은 그림이다. 사람 수가 아니라 서로 다른 문자열의 수다.", "The 30 collections whose letter titles yield the most distinct addressee strings, largest first; strings, not people.")
        how = bar_how("그 문집의 서간 제목에서 나온, 서로 다른 수신자 문자열의 수", "the number of distinct addressee strings in the titles of the collection's letters", L)
        one = tr(L, f"맨 위 막대는 {_title(r, 'ko')}{jo(_title(r, 'ko').strip('『』'), '이다', '다')}. 저자의 서간 {int(r.n_letters):,}편의 제목에서 서로 다른 수신자 문자열 {int(r.n_unique):,}개가 나왔다.",
                 f"The top bar is {_title(r, 'en')}: the titles of the author's {int(r.n_letters):,} letters give {int(r.n_unique):,} distinct addressee strings.")
        lt = D.d / "letters.csv"
        if lt.exists():
            a = pd.read_csv(lt)
            a = a[(a.is_author_work == 1) & a.recipient_raw.notna() & (a.recipient_raw.astype(str).str.len() > 0)]
            per = int(a.groupby("collection_id").recipient_raw.nunique().sum()); allc = int(a.recipient_raw.nunique())
            spread = a.groupby("recipient_raw").collection_id.nunique()
            if per == int(D.letters.n_unique.sum()):
                nums = tr(L, f"면 머리의 {per:,}{jo(per, '은', '는')} 문집마다 따로 센 고유 수신자 수를 저자 자신의 서간이 있는 문집 {len(D.letters):,}종에 걸쳐 더한 값이다(그 가운데 수신자 문자열이 하나라도 나온 문집은 {a.collection_id.nunique():,}종). 같은 문자열이 여러 문집에 나오면 문집마다 한 번씩 들어간다. 모든 문집을 한데 모아 서로 다른 문자열만 세면 {allc:,}개다. 둘 이상의 문집에 나오는 문자열이 {int((spread > 1).sum()):,}개이고, 가장 여러 문집에 나오는 문자열은 「{spread.idxmax()}」이고, {int(spread.max()):,}종에 나온다.",
                          f"The {per:,} at the top of the page is found in two steps. First, for each of the {len(D.letters):,} collections with letters by their own author, the distinct addressee strings are counted ({a.collection_id.nunique():,} of these collections yield at least one string). Then these counts are added up, so a string found in several collections is counted once in each. Pooling all collections and counting each string once gives {allc:,}. {int((spread > 1).sum()):,} strings appear in more than one collection; the most widespread is '{spread.idxmax()}' ({int(spread.max()):,} collections).")
        mis = tr(L, "문자열 단위다 — 같은 사람이 이름·자·호·관직으로 달리 불리면 여러 개로 세고, 다른 사람이 같은 호칭으로 불리면 하나로 센다. 저자의 서간이 많은 문집에서 서로 다른 수신자 문자열도 대체로 많이 나왔다.",
                 "These are strings: one person called by name, courtesy name, pen name or office counts several times, and different people with the same appellation count once. Collections with many letters by their author also tended to yield many distinct addressee strings.")
        terms = tr(L, "수신자 문자열 = 편지 제목에서 받는 사람을 가리키는 부분의 글자를 공백 없이 그대로 뽑은 것(예: 「與宋淵齋」의 「宋淵齋」). 고유 수 = 서로 다른 문자열의 수.",
                   "Addressee string: the characters of a letter's title that name the recipient, taken as written without spaces (in 與宋淵齋, 宋淵齋). Distinct: counted once however often it occurs.")
    elif mid == "c2_epitaph_subjects":
        intro = tr(L, "저자가 쓴 묘비·묘지의 글과 행장이 가장 많은 문집 30종을 많은 순으로 늘어놓은 그림이다.", "The 30 collections with the most epitaphs and accounts of conduct written by the author, largest first.")
        how = bar_how("저자가 쓴 비지·행장 편 수", "the number of epitaphs and accounts of conduct by the author", L)
        bz = int(r["碑誌類"]) if "碑誌類" in r.index and r["碑誌類"] == r["碑誌類"] else None; hz = int(r["行狀類"]) if "行狀類" in r.index and r["行狀類"] == r["行狀類"] else None
        one = tr(L, f"맨 위 막대는 {_title(r, 'ko')}{jo(_title(r, 'ko').strip('『』'), '이다', '다')}. 비지·행장 {int(r.n_epitaphs):,}편" + (f"(비지 {bz:,}편, 행장 {hz:,}편)" if bz is not None and hz is not None else "") + f"이 실려 있고, 제목에서 피장자를 뽑은 것이 {int(r.n_parsed):,}편이다.",
                 f"The top bar is {_title(r, 'en')}: {int(r.n_epitaphs):,} epitaphs and accounts of conduct" + (f" ({bz:,} epitaphs, {hz:,} accounts)" if bz is not None and hz is not None else "") + f"; the subject was taken from the title in {int(r.n_parsed):,}.")
        mis = tr(L, "이 그림은 편 수만 센다. 피장자 이름은 관직·시호가 붙은 긴 문자열이라 같은 사람을 묶지 않았다.",
                 "The chart counts works only. Subject names carry offices and titles and are not merged into persons.")
        terms = tr(L, "비지 = 묘비·묘지에 새긴 글(묘지명·묘갈명·신도비 등). 행장 = 죽은 이의 행적을 적은 글. 피장자 = 그 글이 기리는 죽은 사람.",
                   "Epitaphs: texts for tombstones and tomb records. Accounts of conduct: records of a dead person's life. Subject: the person commemorated.")
    elif mid == "c3_other_writers":
        tw = str(r.top_writers).split("|")[0] if r.top_writers == r.top_writers else ""
        wn, _, wk = tw.partition(":")
        intro = tr(L, "문집에 글을 보탠 저자 아닌 필자(서문·발문·행장·만사를 쓴 사람)의 필자 표지 문자열 가짓수가 가장 많은 문집 30종을 많은 순으로 늘어놓은 그림이다. 사람 수가 아니라 서로 다른 문자열의 수다.",
                   "The 30 collections with the most distinct writer-tag strings of other writers (people who wrote prefaces, postscripts, biographies or elegies in them), largest first; strings, not people.")
        how = bar_how("서로 다른 타인 필자 표지의 수", "the number of distinct writer tags of other writers", L)
        # 1.0.9 v2 (Codex 2.19): the count is of distinct non-empty writer-tag strings, not of people
        one = tr(L, f"맨 위 막대는 {_title(r, 'ko')}{jo(_title(r, 'ko').strip('『』'), '이다', '다')}. 남이 쓴 글과 필자 표지가 빈 글 {int(r.n_other_works):,}편에 서로 다른 필자 표지 {int(r.n_other_writers):,}개가 나온다" + (f". 가장 많이 나온 표지는 {wn}({wk}편)다." if wn and wk else "."),
                 f"The top bar is {_title(r, 'en')}: {int(r.n_other_writers):,} distinct writer tags among {int(r.n_other_works):,} works by others or with an empty tag" + (f"; the most frequent tag is {wn} ({wk} works)." if wn and wk else "."))
        mis = tr(L, "사람 수가 아니라 필자 표지 문자열의 수다. 「門人」처럼 이름이 아닌 표기와 「未詳」(미상)도 문자열 하나로 세고, 한 사람이 다른 표기로 적혔으면 둘로 센다. 필자 표지가 빈 글은 편 수에는 들지만 표지 수에는 들지 않는다.",
                 "This counts writer-tag strings, not people. A non-name such as 'disciple' (門人) or 'unknown' (未詳) is one string, and one person written two ways counts twice. Works with an empty tag are in the number of works but add no tag.")
        terms = tr(L, "타인 필자 = 필자 표지가 문집의 저자가 아닌 사람. 만사 = 죽은 이를 애도해 지어 보낸 시.", "Other writer: a writer tag that is not the collection's author. Elegy poems: poems sent in mourning.")
    else:
        return figx_none()
    return intro, [("short", bar_short(items, spec, L, low, allv)), ("how", how), ("one", one), ("nums", nums), ("mis", mis), ("terms", terms)]


def figx_none():
    return "", []


# ----------------------------------------------------------------- genre-mix bars (collection and century pages)
def mix_notes(shares: dict, n_own, lead: str, lang, where: str, few=False):
    """Genre-mix bars: one bar per class. where = 'collection' or 'century'."""
    L = lang; G = C["GENRES"]; nm = (lambda g: C["GKO"][g]) if L == "ko" else (lambda g: C["GEN"][g])
    v = sorted(((x, g) for g, x in shares.items() if x == x), reverse=True)
    intro = tr(L, ("이 문집에서 저자가 쓴 글이 일곱 갈래(문체 대분류)에 어떻게 나뉘는지 그린 그림이다." if where == "collection" else "이 세기에 태어난 저자들이 쓴 글이 일곱 갈래(문체 대분류)에 어떻게 나뉘는지 그린 그림이다."),
               ("How the author's own works in this collection split among the seven genre classes." if where == "collection" else "How the own works of the authors born in this century split among the seven genre classes."))
    zero = [g for g, x in shares.items() if x == x and x == 0]
    how = tr(L, "막대 하나가 갈래 하나다. 막대 길이는 저자 글 가운데 그 갈래의 편 수 비율이고, 일곱 막대를 반올림하기 전 값으로 더하면 100%다(표시된 값을 더하면 반올림 때문에 조금 어긋날 수 있다). 막대에 커서를 두면 값이 보인다."
             + (f" 0편인 갈래({'·'.join(nm(g) for g in zero)})도 자리를 보이려고 아주 가는 막대로 그렸다 — 값은 0.0%다." if zero else ""),
             "Each bar is one class. Its length is the class's share of own works, by number of works; before rounding the seven bars add up to 100% (the rounded values shown may be slightly off). Hover over a bar for its value."
             + (f" A class with no works ({', '.join(nm(g) for g in zero)}) is still drawn as a hairline bar to keep its place; its value is 0.0%." if zero else ""))
    one = ""
    if v and n_own == n_own and n_own > 0:
        x, g = v[0]; k = int(round(x * n_own))
        one = tr(L, f"{nm(g)} 막대 {fmt(x, '.1%')}는 저자 글 {int(n_own):,}편 가운데 {k:,}편이 {nm(g)}{jo(nm(g), '이라는', '라는')} 뜻이다.",
                 f"The {nm(g)} bar, {fmt(x, '.1%')}, means {k:,} of {int(n_own):,} own works are {nm(g)}.")
    mis = tr(L, "편 수로 센 비율이라 짧은 시 한 수와 긴 상소 한 편이 똑같이 한 편이다. ", "Shares count works, so a short poem and a long memorial each count once. ")
    if n_own == n_own and 0 < n_own < 100:
        mis += tr(L, f"저자 글이 {int(n_own):,}편뿐이어서 한 편이 {fmt(1 / n_own, '.1%')}에 해당한다. ", f"With only {int(n_own):,} own works, one work is {fmt(1 / n_own, '.1%')}. ")
    if where == "collection":
        mis += tr(L, "전체 문집 안에서의 자리는 아래 「이 문집의 지표」 표와 지표 면에 있다.", "Its place among all collections is in the metrics table below and on the metric pages.")
    else:
        mis += tr(L, "이 세기에 태어난 저자의 글을 모두 합쳐 낸 비율이다." + (" 문집이 적은 세기라 몇 문집의 값이다." if few else ""),
                  "Shares are computed over all works by authors born in this century." + (" With so few collections, these are the shares of a handful of collections." if few else ""))
    return intro, [("short", lead), ("how", how), ("one", one), ("mis", mis), ("terms", C["gloss"][L])]


# ----------------------------------------------------------------- bars by century (home, centuries list)
def century_bar_notes(kind, lang):
    """kind = 'works' (home) or 'collections' (centuries list)."""
    D = C["D"]; L = lang; tot = D.tot[D.tot.index.notna()]; col = "n_works" if kind == "works" else "n_collections"
    top = tot[col].idxmax(); rc = C["rc"]
    unk = D.tot.loc[D.tot.index.isna()]
    nunk = int(unk[col].sum()) if len(unk) else 0
    if kind == "works":
        intro = tr(L, "저자가 태어난 세기마다 문집에 실린 글이 몇 편인지 센 그림이다.", "Works per century of the author's birth.")
        how = tr(L, "막대 하나가 한 세기다. 막대 길이는 그 세기에 태어난 저자들의 문집에 실린 편 수를 모두 더한 값이다(남이 쓴 글 포함).",
                 "Each bar is one century. Its length adds up the works in the collections of the authors born in that century (works by others included).")
        one = tr(L, f"{cl(rc, 'ko')} 막대 {int(tot.loc[rc, col]):,}편은 그 세기에 태어난 저자 {int(tot.loc[rc, 'n_authors']):,}명의 문집 {int(tot.loc[rc, 'n_collections']):,}종을 합친 수다.",
                 f"The {cl(rc, 'en')} bar, {int(tot.loc[rc, col]):,} works, adds up the {int(tot.loc[rc, 'n_collections']):,} collections of the {int(tot.loc[rc, 'n_authors']):,} authors born then.")
        short = tr(L, f"가장 긴 막대는 {cl(top, 'ko')}({int(tot.loc[top, col]):,}편)다.", f"The longest bar is the {cl(top, 'en')} ({int(tot.loc[top, col]):,} works).")
        extra = tr(L, " 각 세기 면은 「세기」 메뉴에 있다.", " Each century has its own page under Centuries.")
    else:
        intro = tr(L, "저자가 태어난 세기마다 문집이 몇 종인지 센 그림이다.", "Collections per century of the author's birth.")
        how = tr(L, "막대 하나가 한 세기다. 막대 길이는 그 세기에 태어난 저자의 문집 수다.", "Each bar is one century. Its length is the number of collections by authors born in that century.")
        one = tr(L, f"{cl(rc, 'ko')} 막대 {int(tot.loc[rc, col]):,}종은 그 세기에 태어난 저자 {int(tot.loc[rc, 'n_authors']):,}명의 문집 수다.",
                 f"The {cl(rc, 'en')} bar, {int(tot.loc[rc, col]):,}, counts the collections of the {int(tot.loc[rc, 'n_authors']):,} authors born then.")
        short = tr(L, f"가장 긴 막대는 {cl(top, 'ko')}({int(tot.loc[top, col]):,}종)다.", f"The longest bar is the {cl(top, 'en')} ({int(tot.loc[top, col]):,} collections).")
        extra = ""
    gone = [c for c in range(int(tot.index.min()), int(tot.index.max()) + 1) if c not in {int(x) for x in tot.index}]
    mis = birth_not_writing(L) + tr(L, " 총간에 실린 문집만 센 수다.", " Only collections in the compendium are counted.")
    if gone:
        mis += tr(L, f" {cls(gone, 'ko')}에는 문집이 없어 막대가 없다.", f" The {cls(gone, 'en')} have no collection and no bar.")
    if nunk:
        mis += tr(L, f" 저자의 생년을 모르는 문집({int(unk.n_collections.sum()):,}종)은 어느 세기에도 넣지 않았다.", f" Collections whose author's birth year is unknown ({int(unk.n_collections.sum()):,}) are in no century.")
    return intro, [("short", short), ("how", how), ("one", one), ("mis", mis + extra)]


# ----------------------------------------------------------------- words in the metric texts (1.0.9, reader test 2026-11-17)
BODY_WORDS = [
    ("XML", r"XML", r"XML",
     "XML = 고전번역원이 원문을 배포한 파일 형식. 제목·필자·문체 같은 정보에 표지를 붙여 둔다.",
     "XML: the file format in which the ITKC releases the texts, with tags for title, writer, genre and so on."),
    ("id", r"ITKC_MO_", r"ITKC_MO_",
     "ITKC_MO_… = 고전번역원 데이터베이스가 문집마다 붙인 번호. 고전종합DB 주소에도 쓰인다.",
     "ITKC_MO_…: the ITKC database's number for a collection, also used in its web addresses."),
    ("chaek", r"冊文類", r"冊文類",
     "冊文類(책문류) = 책봉하거나 존호를 올릴 때 쓰는 글(책문)을 모은 중분류. 공거 갈래 안에 있다.",
     "冊文類: the minor class, under court documents, for texts written for investitures and for presenting honorific titles."),
    ("fusa", r"부·사|賦|辭類", r"\bfu\b|賦|辭類|rhapsodies",
     "부(賦)·사(辭) = 시 갈래 안의 중분류. 부는 운을 단 긴 글, 사는 『초사』에서 내려온 노래체 운문이다.",
     "Rhapsodies (fu 賦) and lyrics (ci 辭): minor classes within poetry — fu are long rhymed pieces, ci songlike verse in the line of the Chuci."),
    ("shou", r"首", r"首|ten poems",
     "首(수) = 시를 세는 단위. 「十首」는 열 수.", "首 (shou): the counter for poems; 十首 means 'ten poems'."),
    ("unw", r"비가중", r"\bunweighted\b",
     "비가중 = 표본의 층마다 뽑힌 비율이 달라도 그것을 바로잡지 않고 그대로 합친 값.",
     "Unweighted: the strata of a sample are pooled as drawn, without correcting for their different sampling rates."),
    ("letterwords", r"答·與", r"答·與",
     "서간 제목의 한자 — 수신자 앞에 오는 글자: 答(답하다)·與(주다, 보내다)·上(윗사람에게 올리다)·寄(부치다)·復·報(회답하다)·奉·呈(받들어 드리다)·贈(주다)·簡(편지하다)·謝(사례하다)·代(대신하다), 그 앞에 붙는 又·再(다시)·三(세 번째). 수신자 뒤에 오는 글자: 書·簡·札·牘(편지)·帖(짧은 편지)·疏(편지를 이르기도 하는 글자 — 상소의 疏와 같은 글자)·問目(물음 조목)·別紙(따로 붙인 종이)·狀·啓(아뢰는 글). 이 글자들은 제목에서 수신자가 어디서 시작하고 끝나는지 가리는 표지로 쓰였고, 그 사이의 글자를 공백 없이 수신자 문자열로 삼았다. 수신자 뒤에 論·問·議 같은 화제어가 오면 그 앞에서 끊고, 남의 이름을 빌려 지은 글(擬作)은 수신자를 비워 두었다.",
     "Letter-title characters. Before the addressee: 答 answer, 與 send to, 上 present to a superior, 寄 send, 復 and 報 reply, 奉 and 呈 offer respectfully, 贈 give, 簡 write to, 謝 thank, 代 on behalf of, sometimes preceded by 又 or 再 (again) or 三 (a third time). After the addressee: 書, 簡, 札, 牘, 帖 (letter, short letter), 疏 (also used for a letter; the same character as in memorials), 問目 (list of questions), 別紙 (separate sheet), 狀, 啓 (report). These characters mark where the addressee starts and ends in a title, and the characters between them, without spaces, are taken as the addressee string; a topic word such as 論, 問 or 議 after the addressee ends it, and imagined letters (擬作) have no addressee."),
]


def body_words(text: str, lang: str) -> str:
    """The plain-language notes for the words of BODY_WORDS that appear in a metric page's text (definition, formula,
    caveats, reliability card). Returns a <dt>/<dd> pair for the spec block, or ''."""
    import re
    i = 0 if lang == "ko" else 1
    got = [w[3 + i] for w in BODY_WORDS if re.search(w[1 + i], text)]
    if not got:
        return ""
    return f'<dt>{"이 면의 낱말" if lang == "ko" else "Words on this page"}</dt><dd class="words">{esc(" ".join(got))}</dd>'
