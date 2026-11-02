# -*- coding: utf-8 -*-
"""Key-point sentences per metric (ko/en), the five home-page points and the person-page points.
Numbers are read from data/derived at the time of writing (1.0, 2026-11-03); the generator prints the live values
beside them and they are re-checked in the claim table before each release. No interpretation beyond the counts.
"""

TAKE = {
    "a1_works": {"ko": "1,249종에 637,203편. 문집 하나의 중앙값은 339편이고, 『송자대전』(9,434편)·『여유당전서』(8,100편)·『면우집』(5,688편)이 가장 크다. 편의 95.7%가 저자 본인의 글이다.",
                 "en": "637,203 works in 1,249 collections; the median collection has 339. The largest are the Songja daejeon (9,434), the Yeoyudang jeonseo (8,100) and the Myeonu jip (5,688). 95.7% of all works are by the collection's own author."},
    "a2_chars": {"ko": "본문 1억 8,030만 자, 주 257만 자(1.4%). 문집 하나의 중앙값은 약 8만 자다. 『여유당전서』가 410만 자로 가장 길고 『송자대전』(368만)·『면우집』(288만)이 뒤를 잇는다.",
                 "en": "180.3 million characters of text and 2.6 million in notes (1.4%); the median collection has about 80,000. The Yeoyudang jeonseo is the longest at 4.1 million, followed by the Songja daejeon (3.7 million) and the Myeonu jip (2.9 million)."},
    "a3_centuries": {"ko": "저자 생년으로 보면 16세기(382종)·17세기(353종)·18세기(272종)에 문집이 몰려 있고, 14세기 이전은 48종이다. 속편 586종은 19세기 출생 저자 48종을 포함해 정편이 비운 자리를 채운다.",
                     "en": "By the author's birth century the collections cluster in the 16th (382), 17th (353) and 18th (272); only 48 belong to authors born before 1400. The 586 supplement volumes fill gaps left by the first series, including 48 authors born in the 19th century."},
    "a4_chars_per_work": {"ko": "편당 글자 수의 중앙값은 16세기까지 56자(칠언율시 한 수)이고 17세기 75자, 18세기 118자, 19세기 157자로 커진다. 시 비중이 줄고 산문이 늘어난 것과 같은 방향이다.",
                          "en": "The median work is 56 characters (one seven-syllable regulated verse) up to the 16th century, then 75 in the 17th, 118 in the 18th and 157 in the 19th — the same direction as the falling share of poetry."},
    "a5_note_share": {"ko": "주(원주·교감주·난외주)는 전체 글자의 1.4%다. 세기별로 1.0~1.8% 사이에 머물고, 9세기(최치원)만 5.7%다.",
                      "en": "Notes make up 1.4% of all characters, staying between 1.0% and 1.8% in every century except the 9th (Choe Chi-won, 5.7%)."},
    "a6_own_share": {"ko": "편의 95.7%는 저자 본인의 글이다. 타인의 글은 서문·발문·행장·만사·부록이며, 세 문집(『내헌집』·『용이와집』·『창주유고』)은 필자 태그가 저자와 한 편도 일치하지 않는다 — 필자 표기 방식의 문제일 수 있어 표본 점검 대상이다.",
                     "en": "95.7% of works are by the author; the rest are prefaces, postscripts, biographies, elegies and appendices by others. In three collections no writer tag matches the author at all — possibly a tagging convention, flagged for sample checking."},
    "a7_gwon": {"ko": "간략해제가 「n권 n책」을 밝힌 851종 중 691종(81%)에서 목차의 卷n 수가 그 n과 같다. 어긋난 160종은 대개 속집·별집·부록에 따로 권차를 매긴 경우다.",
                "en": "Of the 851 collections whose introduction states 'n fascicles, n volumes', 691 (81%) have exactly n '卷n' headings in the table of contents; most of the other 160 number continuations, separate collections or appendices on their own."},
    "b1_poetry_share": {"ko": "본인 편의 62.0%가 시다. 세기별로는 14~15세기 88%에서 16세기 75%, 17세기 62%, 18세기 51%, 19세기 42%로 내려온다. 글자 기준으로는 18.8%에 그친다 — 시는 편 수로는 많고 글자로는 적다. 곽지은(2026)이 보고한 방향(詩 최다, 점진 하락)과 같다.",
                        "en": "62.0% of own works are poems. By century the share falls from 88% (14th–15th) to 75% (16th), 62% (17th), 51% (18th) and 42% (19th). By characters poetry is only 18.8%: many works, few characters. The direction matches Kwak (2026): poetry largest, declining."},
    "b2_genre_mix": {"ko": "시 62.0%, 서간 13.4%, 잡저 9.1%, 공거 5.6%, 전기 3.7%, 애제 3.2%, 서발 3.0%. 글자로 보면 잡저 25.2%·시 18.8%·서간 17.8%·전기 16.9%로 순서가 바뀐다. 중분류에서는 詩類 373,534편, 書簡類 81,423편, 疏箚類 26,369편 순이다.",
                     "en": "Poetry 62.0%, letters 13.4%, miscellany 9.1%, court documents 5.6%, biographies 3.7%, elegies 3.2%, prefaces 3.0%. By characters the order changes: miscellany 25.2%, poetry 18.8%, letters 17.8%, biographies 16.9%. Among minor classes poems (373,534), letters (81,423) and memorials (26,369) lead."},
    "b3_letters_share": {"ko": "서간은 본인 편의 13.4%다. 15세기 이전에는 1% 안팎이었고 16세기 5.7%, 17세기 15.0%, 18세기 15.1%, 19세기 30.2%로 늘었다. 곽지은(2026)의 「서간 지속 증가」와 같은 방향이다.",
                         "en": "Letters are 13.4% of own works: around 1% before the 16th century, then 5.7% (16th), 15.0% (17th), 15.1% (18th) and 30.2% (19th) — the rising trend Kwak (2026) reports."},
    "b4_memorials_share": {"ko": "공거류(소·차·계·대책·교서)는 본인 편의 5.6%다. 9세기 최치원(42%)을 빼면 16세기 5.8%·17세기 7.7%가 가장 높고 19세기에는 2.4%로 내려온다.",
                           "en": "Court documents (memorials, examination answers, edicts) are 5.6% of own works. Apart from the 9th century (Choe Chi-won, 42%), the share peaks in the 16th (5.8%) and 17th (7.7%) centuries and falls to 2.4% in the 19th."},
    "b5_relational_share": {"ko": "남을 기리는 글(애제·비지·행장)은 본인 편의 6.4%다. 14~15세기 2% 안팎에서 17세기 6.3%, 18세기 8.3%, 19세기 9.8%로 늘었다.",
                            "en": "Works commemorating others (elegies, epitaphs, biographies) are 6.4% of own works, rising from about 2% in the 14th–15th centuries to 6.3% (17th), 8.3% (18th) and 9.8% (19th)."},
    "b6_prefaces_share": {"ko": "서발은 본인 편의 3.0%다. 16세기까지 2% 아래, 18세기 4.6%, 19세기 5.6%다.",
                          "en": "Prefaces and postscripts are 3.0% of own works: under 2% through the 16th century, 4.6% in the 18th and 5.6% in the 19th."},
    "b7_other_share": {"ko": "중분류가 「其他類」인 편은 전체의 6.4%다. 세기별로 2.8%(15세기)에서 9.4%(18세기) 사이이고 9세기만 30%다. 잡저의 其他類(26,493편)가 가장 큰 덩어리다.",
                       "en": "6.4% of own works sit in an 'other' minor class, between 2.8% (15th century) and 9.4% (18th), except the 9th century at 30%. The largest block is 'other' within miscellany (26,493 works)."},
    "b8_poem_length": {"ko": "시 한 편의 본문 글자 수 중앙값은 모든 세기에서 56자 — 칠언율시 한 수의 길이다. 사분위는 28자(오언절구·칠언절구)와 60~110자 사이에 있고, 평균은 연작·장편 때문에 64~96자로 중앙값보다 크다.",
                       "en": "The median poem has 56 characters in every century — the length of one seven-syllable regulated verse. Quartiles lie at 28 (quatrains) and 60–110; the mean (64–96) exceeds the median because of cycles and long poems."},
    "c1_recipients": {"ko": "서간이 있는 895종의 본인 서간 81,842편 중 93.7%에서 제목이 수신자를 담았고, 수신자 문자열은 34,980개다. 한 문집의 고유 수신자 중앙값은 14, 상위 3 수신자 점유율 중앙값은 41%다. 『간재집』(1,290)·『면우집』(1,033)·『송자대전』(801)이 수신자가 가장 많다.",
                      "en": "In the 895 collections with letters, 93.7% of the 81,842 letters name an addressee in the title, giving 34,980 addressee strings. A collection's median is 14 distinct addressees, with the top three taking 41% of its letters. The Ganjae jip (1,290), Myeonu jip (1,033) and Songja daejeon (801) have the most."},
    "c2_epitaph_subjects": {"ko": "880종에 본인이 쓴 비지·행장 19,789편이 있고 94.8%에서 피장자 문자열을 뽑았다(고유 17,972). 『송사집』(968)·『송자대전』(576)·『면암집』(428)이 가장 많다.",
                            "en": "880 collections contain 19,789 epitaphs and biographies by the author; a subject string was parsed from 94.8% (17,972 distinct). The Songsa jip (968), Songja daejeon (576) and Myeonam jip (428) have the most."},
    "c3_other_writers": {"ko": "1,120종에 저자 아닌 필자의 글 27,709편이 실려 있고 문집별 타인 필자 수의 합은 17,675, 중앙값은 8명이다. 『성재집』(173명)·『한주집』(143명)·『척암집』(138명)이 가장 많다.",
                         "en": "1,120 collections carry 27,709 works by writers other than the author; summed over collections that is 17,675 writers, a median of 8 per collection. The Seongjae jip (173), Hanju jip (143) and Cheogam jip (138) have the most."},
    "d1_dates": {"ko": "저자 1,248명 중 생년은 1,240명, 몰년은 1,231명에 있다. 수명 중앙값은 65.5세이고 세기별로 57.5세(15세기)에서 70세(18세기) 사이다. 한국역대인명정보와 성명+생년으로 맞춘 1,072명 중 몰년이 같은 사람은 1,030명(96.1%)이다.",
                 "en": "Of 1,248 authors, 1,240 have a birth year and 1,231 a death year. Median lifespan is 65.5 years, ranging from 57.5 (15th century) to 70 (18th). Of 1,072 authors matched to the AKS person database by name and birth year, 1,030 (96.1%) agree on the death year."},
    "d2_munkwa": {"ko": "저자 1,248명 중 48.9%(610명)가 문과방목의 급제자와 연결된다. 15세기 82%, 16세기 62%, 17세기 52%, 18세기 29%, 19세기 22%로 내려온다 — 급제자 아닌 저자(산림·승려·여성 등)의 문집이 늘어난 결과이며 급제율이 아니다. 급제 연령 중앙값은 30세(15세기 27세 → 18세기 35세)다.",
                  "en": "48.9% of the 1,248 authors (610) link to a passer in the civil-examination roster: 82% of those born in the 15th century, 62% (16th), 52% (17th), 29% (18th), 22% (19th). The decline reflects more collections by non-passers (rural scholars, monks, women); it is not a pass rate. Median age at passing is 30 (27 in the 15th century, 35 in the 18th)."},
    "d3_pub_lag": {"ko": "간행년이 있는 1,026종에서 몰년부터 간행까지 중앙값 66년(사분위 24~177년)이다. 15세기 출생 저자는 175년, 16세기 128년, 17세기 59년, 18세기 39년, 19세기 15년으로 짧아진다.",
                   "en": "For the 1,026 collections with a printing year, the median lag from the author's death is 66 years (quartiles 24–177). It shortens by birth century: 175 years (15th), 128 (16th), 59 (17th), 39 (18th), 15 (19th)."},
    "d4_translation": {"ko": "편의 16.6%에 번역문이 연계되어 있고, 1,105종에는 연계된 편이 없다(속편은 586종 중 585종). 정편에서 연계가 있는 문집은 143종으로, 최채기(2020)가 번역된 것으로 센 372종보다 적다 — 연계는 번역 현황이 아니라 DB 작업의 범위다.",
                       "en": "16.6% of works have a linked translation; 1,105 collections have none (585 of the 586 supplement volumes). Only 143 first-series collections carry a link, fewer than the 372 Choi (2020) counted as translated — linkage measures database work, not translation."},
    "d5_punct": {"ko": "교감표점본이 연계된 편은 6.5%이고 58종에 몰려 있다. 세기별 2~26%로 들쭉날쭉한 것은 사업 대상 문집이 고르게 분포하지 않아서다.",
                 "en": "6.5% of works have a linked collated and punctuated edition, concentrated in 58 collections. The share by century ranges from 2% to 26% because the program's target collections are unevenly spread."},
}

HOME_FIVE = {
    "ko": ["1,249종 637,203편 1억 8,300만 자. 편의 62%가 시지만 글자로는 19%다.",
           "시 비중은 15세기 88%에서 19세기 42%로, 서간은 1%에서 30%로 — 편당 글자 수는 56자에서 157자로.",
           "서간 81,842편의 94%가 제목에 수신자를 적었다. 수신자 문자열 34,980개, 한 문집의 상위 3 수신자가 서간의 41%를 받는다.",
           "저자의 49%가 문과방목과 연결된다 — 15세기 82%, 19세기 22%. 급제 연령 중앙값 30세.",
           "몰년에서 간행까지 중앙값 66년. 15세기 출생 저자는 175년, 19세기는 15년."],
    "en": ["1,249 collections, 637,203 works, 183 million characters. 62% of works are poems, but only 19% of characters.",
           "Poetry falls from 88% of works (15th century) to 42% (19th) while letters rise from 1% to 30%; the median work grows from 56 to 157 characters.",
           "94% of 81,842 letters name an addressee in the title: 34,980 addressee strings, and a collection's top three addressees receive 41% of its letters.",
           "49% of authors link to the civil-examination roster — 82% of those born in the 15th century, 22% in the 19th. Median age at passing: 30.",
           "Median lag from death to printing: 66 years — 175 for authors born in the 15th century, 15 for the 19th."],
}

PAGE_TAKE = {}
