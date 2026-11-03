# -*- coding: utf-8 -*-
"""Key-point sentences per metric (ko/en), the five home-page points and the person-page points.
Numbers are read from data/derived (1.0, 2026-11-03) and checked against it before each release.
Counts and shares only — no interpretation of causes.
"""

TAKE = {
    "a1_works": {"ko": "1,249종에 637,203편. 문집 하나의 중앙값은 339편이고, 『송자대전』(9,434편)·『여유당전서』(8,100편)·『면우집』(5,688편)이 가장 크다. 편의 95.7%가 저자 자신의 글이다.",
                 "en": "637,203 works in 1,249 collections; the median collection has 339. The largest are the Songja daejeon (9,434), the Yeoyudang jeonseo (8,100) and the Myeonu jip (5,688). 95.7% of all works are by the collection's own author."},
    "a2_chars": {"ko": "본문 1억 7,737만 자, 주(원주·교감주·난외주) 550만 자(3.0%). 문집 하나의 중앙값은 약 8만 자다. 『여유당전서』가 411만 자로 가장 길고 『송자대전』(368만)·『면우집』(288만)이 뒤를 잇는다.",
                 "en": "177.4 million characters of text and 5.5 million in notes (3.0%); the median collection has about 80,000. The Yeoyudang jeonseo is the longest at 4.1 million, followed by the Songja daejeon (3.7 million) and the Myeonu jip (2.9 million)."},
    "a3_centuries": {"ko": "저자 생년으로 보면 16세기(382종)·17세기(353종)·18세기(272종)에 문집이 몰려 있고, 14세기까지의 출생 저자는 48종, 19세기는 82종이다. 속편 586종 가운데 48종이 19세기 출생 저자의 문집이다. 생년이 없는 저자 8명의 문집은 세기 표에서 「생년 미상」 행에 있다.",
                     "en": "By the author's birth century the collections cluster in the 16th (382), 17th (353) and 18th (272); authors born up to the 14th century account for 48 collections and the 19th century for 82. Of the 586 supplement collections, 48 are by authors born in the 19th century. The 8 authors without a birth year sit in a separate row of the century tables."},
    "a4_chars_per_work": {"ko": "편당 글자 수의 중앙값은 13~16세기 56자(칠언율시 한 수), 17세기 75자, 18세기 118자, 19세기 157자다. 9세기(최치원) 168자와 12세기 80자는 예외다. 시 비중이 줄고 산문이 느는 것과 같은 방향이다.",
                          "en": "The median work has 56 characters (one seven-syllable regulated verse) in the 13th–16th centuries, then 75 in the 17th, 118 in the 18th and 157 in the 19th; the 9th century (Choe Chi-won, 168) and the 12th (80) are exceptions. The direction is the same as the falling share of poetry and the rising share of prose."},
    "a5_note_share": {"ko": "주(원주·교감주·난외주)는 전체 글자의 3.0%다. 세기별로는 19세기 1.9%에서 16세기 4.1% 사이이고, 9세기(최치원)만 11.6%다.",
                      "en": "Notes make up 3.0% of all characters, between 1.9% (19th century) and 4.1% (16th) in every century except the 9th (Choe Chi-won, 11.6%)."},
    "a6_own_share": {"ko": "편의 95.7%는 저자 자신의 글이다. 타인의 글은 서문·발문·행장·만사·부록이다. 여덟 문집(『망헌유고』·『추파집』·『창주유고』·『능허관만고』·『용이와집』·『내헌집』·『어당집』·『소송유고』)은 필자 태그가 저자와 한 편도 일치하지 않는다 — 필자 표기 관행 차이일 수 있다(가설, 표본 점검 대상).",
                     "en": "95.7% of works are by the author; the rest are prefaces, postscripts, biographies, elegies and appendices by others. In eight collections (the Manghyeon yugo 忘軒遺稿, Chupa jip 秋坡集, Changju yugo 滄洲遺稿, Neungheogwan mango 凌虛關漫稿, Yongiwa jip 龍耳窩集, Naeheon jip 耐軒集, Eodang jip 峿堂集 and Sosong yugo 小松遺稿) no writer tag matches the author at all — possibly a tagging convention (a hypothesis, flagged for sample checking)."},
    "a7_gwon": {"ko": "간략해제가 「n권 n책」을 밝힌 851종 중 691종(81%)에서 목차의 卷n 수가 그 n과 같다. 어긋난 160종의 원인은 코딩하지 않았다.",
                "en": "Of the 851 collections whose introduction states 'n fascicles, n volumes', 691 (81%) have exactly n '卷n' headings in the table of contents. The causes of the 160 mismatches were not coded."},
    "b1_poetry_share": {"ko": "저자 글 609,494편의 62.0%가 시다. 세기별로는 14~15세기 88%에서 16세기 75%, 17세기 62%, 18세기 51%, 19세기 42%로 내려온다. 글자 기준으로는 18.8%다 — 시는 편 수로는 많고 글자로는 적다. 곽지은(2026)이 보고한 방향(詩 최다, 점진 하락)과 같다.",
                        "en": "62.0% of the authors' own 609,494 works are poems. By century the share falls from 88% (14th–15th) to 75% (16th), 62% (17th), 51% (18th) and 42% (19th). By characters poetry is 18.8%: many works, few characters. The direction matches Kwak (2026): poetry largest, declining."},
    "b2_genre_mix": {"ko": "저자 글 기준 시 62.0%, 서간 13.4%, 잡저 9.1%, 공거 5.6%, 전기 3.7%, 애제 3.2%, 서발 3.0%. 글자로 보면 잡저 25.2%·시 18.8%·서간 17.8%·전기 16.9%로 순서가 바뀐다. 중분류에서는 詩類 374,153편, 書簡類 81,442편, 잡저의 其他類 26,505편, 疏箚類 26,386편 순이다.",
                     "en": "Of own works: poetry 62.0%, letters 13.4%, miscellany 9.1%, court documents 5.6%, biographies 3.7%, elegies 3.2%, prefaces 3.0%. By characters the order changes: miscellany 25.2%, poetry 18.8%, letters 17.8%, biographies 16.9%. Among minor classes poems (374,153), letters (81,442), 'other' within miscellany (26,505) and memorials (26,386) lead."},
    "b3_letters_share": {"ko": "서간은 저자 글의 13.4%다. 12~15세기에는 0.3~2.5%였고 16세기 5.7%, 17세기 15.0%, 18세기 15.1%, 19세기 30.2%로 늘었다. 9세기(최치원)는 32.9%다. 곽지은(2026)의 「서간 지속 증가」와 같은 방향이다.",
                         "en": "Letters are 13.4% of own works: 0.3–2.5% in the 12th–15th centuries, then 5.7% (16th), 15.0% (17th), 15.1% (18th) and 30.2% (19th); the 9th century (Choe Chi-won) stands at 32.9%. The direction matches the rising trend Kwak (2026) reports."},
    "b4_memorials_share": {"ko": "공거류(소·차·계·대책·교서)는 저자 글의 5.6%다. 9세기 최치원이 42%, 12·13세기가 9.1%·8.7%, 16·17세기가 5.8%·7.7%, 19세기가 2.4%다.",
                           "en": "Court documents (memorials, examination answers, edicts) are 5.6% of own works: 42% in the 9th century (Choe Chi-won), 9.1% and 8.7% in the 12th and 13th, 5.8% and 7.7% in the 16th and 17th, 2.4% in the 19th."},
    "b5_relational_share": {"ko": "남을 기리는 글(애제·비지·행장)은 저자 글의 6.4%다. 14~15세기 2% 안팎에서 17세기 6.3%, 18세기 8.3%, 19세기 9.8%로 늘었다.",
                            "en": "Works commemorating others (elegies, epitaphs, biographies) are 6.4% of own works, rising from about 2% in the 14th–15th centuries to 6.3% (17th), 8.3% (18th) and 9.8% (19th)."},
    "b6_prefaces_share": {"ko": "서발은 저자 글의 3.0%다. 13세기 3.3%를 빼면 16세기까지 2% 아래이고, 18세기 4.6%, 19세기 5.6%다.",
                          "en": "Prefaces and postscripts are 3.0% of own works: under 2% through the 16th century except the 13th (3.3%), then 4.6% in the 18th and 5.6% in the 19th."},
    "b7_other_share": {"ko": "중분류가 「其他類」인 편은 저자 글 전체의 6.4%다. 세기별로 2.8%(15세기)에서 12.1%(12세기) 사이이고 9세기는 30%다. 잡저의 其他類(26,505편)가 가장 큰 덩어리다.",
                       "en": "6.4% of own works sit in an 'other' minor class, between 2.8% (15th century) and 12.1% (12th), with the 9th century at 30%. The largest block is 'other' within miscellany (26,505 works)."},
    "b8_poem_length": {"ko": "시 한 편의 본문 글자 수 중앙값은 9세기(40자)를 빼면 모든 세기에서 56자 — 칠언율시 한 수의 길이다. 사분위는 28자 또는 40자(오언절구 20자·칠언절구 28자·오언율시 40자)와 56~109자 사이에 있고, 평균은 49~93자(9세기 48.7, 12세기 93.0)로 중앙값보다 크다 — 분포가 오른쪽으로 길다.",
                       "en": "The median poem has 56 characters in every century but the 9th (40) — the length of one seven-syllable regulated verse. Quartiles lie at 28 or 40 (quatrains have 20 or 28 characters, a five-syllable regulated verse 40) and 56–109; the mean (49–93; 48.7 in the 9th century, 93.0 in the 12th) exceeds the median — the distribution has a long right tail."},
    "c1_recipients": {"ko": "서간이 있는 895종의 저자의 서간 81,842편 중 93.4%에서 제목이 수신자 문자열을 담았다. 문집별 고유 수신자 수의 합은 34,890(전체에서 서로 다른 문자열은 25,303)이고, 한 문집의 고유 수신자 중앙값은 14, 수신자가 있는 서간 가운데 상위 3 수신자 점유율 중앙값은 41%다. 『간재집』(1,287)·『면우집』(1,033)·『송자대전』(798)이 수신자가 가장 많다.",
                      "en": "In the 895 collections with letters, 93.4% of the 81,842 letters carry an addressee string in the title. Summed over collections there are 34,890 distinct addressees (25,303 distinct strings corpus-wide); a collection's median is 14, and among letters with an addressee the top three take a median of 41%. The Ganjae jip (1,287), Myeonu jip (1,033) and Songja daejeon (798) have the most."},
    "c2_epitaph_subjects": {"ko": "880종에 저자가 쓴 비지·행장 19,789편이 있고 93.6%에서 피장자 문자열을 뽑았다(문집별 고유 합 17,972, 전체 고유 15,440). 『송사집』(968)·『송자대전』(576)·『면암집』(428)이 가장 많다.",
                            "en": "880 collections contain 19,789 epitaphs and biographies by the author; a subject string was parsed from 93.6% (17,972 distinct summed over collections, 15,440 corpus-wide). The Songsa jip (968), Songja daejeon (576) and Myeonam jip (428) have the most."},
    "c3_other_writers": {"ko": "1,120종에 저자 아닌 필자의 글 27,709편이 실려 있고 문집별 타인 필자 수의 합은 17,675, 중앙값은 8명이다. 『성재집』(173명)·『한주집』(143명)·『척암집』(138명)이 가장 많다.",
                         "en": "1,120 collections carry 27,709 works by writers other than the author; summed over collections that is 17,675 writers, a median of 8 per collection. The Seongjae jip (173), Hanju jip (143) and Cheogam jip (138) have the most."},
    "d1_dates": {"ko": "저자 1,248명 중 생년은 1,240명, 몰년은 1,231명, 둘 다 있는 사람은 1,228명(98.4%)이다. 수명 중앙값은 65.5세이고 세기별로 57.5세(15세기)에서 70세(18세기) 사이다. 한국역대인명정보에 성명+생년(P1) 또는 성명+호(P2)로 연결되어 몰년을 비교할 수 있는 1,077명 중 1,035명(96.1%)이 같다.",
                 "en": "Of 1,248 authors, 1,240 have a birth year, 1,231 a death year and 1,228 (98.4%) both. Median lifespan is 65.5 years, from 57.5 (15th century) to 70 (18th). Of the 1,077 authors matched to the AKS person database (by name and birth year, or name and pen name) with a comparable death year, 1,035 (96.1%) agree."},
    "d2_munkwa": {"ko": "저자 1,248명 중 49.1%(613명)가 문과방목의 급제자와 연결된다(성명+생년 546, 같은 사람의 첫 급제 65, 자·호 2). 15세기 출생 저자 83%, 16세기 62%, 17세기 52%, 18세기 30%, 19세기 22%다. 연결되지 않은 저자가 곧 급제하지 않은 저자는 아니다 — 이체자·동명 후보는 따로 검토한다. 급제 연령 중앙값은 30세(15세기 27세, 18세기 35세)다.",
                  "en": "49.1% of the 1,248 authors (613) link to a passer in the civil-examination roster (name and birth year 546, first pass of a re-examined person 65, courtesy or pen name 2): 83% of those born in the 15th century, 62% (16th), 52% (17th), 30% (18th), 22% (19th). An unlinked author is not necessarily a non-passer; variant-character and namesake candidates are reviewed separately. Median age at passing is 30 (27 in the 15th century, 35 in the 18th)."},
    "d3_pub_lag": {"ko": "간행년이 있는 문집은 1,038종, 몰년도 있어 시차를 잴 수 있는 문집은 1,026종이다. 몰년부터 간행까지 중앙값 66년(사분위 24~177년). 15세기 출생 저자는 175년, 16세기 128년, 17세기 59년, 18세기 39년, 19세기 15년이다.",
                   "en": "1,038 collections have a printing year and 1,026 also a death year to measure the lag. The median lag from death to printing is 66 years (quartiles 24–177): 175 years for authors born in the 15th century, 128 (16th), 59 (17th), 39 (18th), 15 (19th)."},
    "d4_translation": {"ko": "편의 16.6%에 번역문이 연계되어 있고, 1,105종에는 연계된 편이 없다(속편은 586종 중 585종). 정편에서 연계가 있는 문집은 143종으로, 최채기(2020)가 번역된 것으로 센 372종보다 적다 — 연계는 번역 현황이 아니라 DB 작업의 범위다.",
                       "en": "16.6% of works have a linked translation; 1,105 collections have none (585 of the 586 supplement collections). Only 143 first-series collections carry a link, fewer than the 372 Choi (2020) counted as translated — linkage measures database work, not translation."},
    "d5_punct": {"ko": "교감표점본이 연계된 편은 6.5%이고 58종에 몰려 있다. 세기별 비율은 0%(12세기)에서 26%(13세기) 사이다.",
                 "en": "6.5% of works have a linked collated and punctuated edition, concentrated in 58 collections. The share by century ranges from 0% (12th) to 26% (13th)."},
}

HOME_FIVE = {
    "ko": ["1,249종 637,203편 1억 8,300만 자. 저자 글의 62%가 시지만 글자로는 19%다.",
           "저자 글 중 시 비중은 15세기 88%에서 19세기 42%로, 서간은 1%에서 30%로 — 전체 편당 글자 수 중앙값은 56자에서 157자로.",
           "서간 81,842편의 93%가 제목에 수신자를 적었다. 문집별 고유 수신자 합 34,890, 수신자가 있는 서간 가운데 상위 3 수신자 점유율의 문집별 중앙값은 41%다.",
           "저자의 49%가 문과방목과 연결된다 — 15세기 출생 83%, 19세기 22%. 급제 연령 중앙값 30세.",
           "몰년에서 간행까지 중앙값 66년. 15세기 출생 저자는 175년, 19세기는 15년."],
    "en": ["1,249 collections, 637,203 works, 183 million characters. 62% of the authors' own works are poems, but only 19% of characters.",
           "Among own works, poetry falls from 88% (15th century) to 42% (19th) while letters rise from 1% to 30%; the median work grows from 56 to 157 characters.",
           "93% of 81,842 letters name an addressee in the title: 34,890 distinct addressees summed over collections, and the per-collection median share taken by the top three addressees among addressed letters is 41%.",
           "49% of authors link to the civil-examination roster — 83% of those born in the 15th century, 22% in the 19th. Median age at passing: 30.",
           "Median lag from death to printing: 66 years — 175 for authors born in the 15th century, 15 for the 19th."],
}

PAGE_TAKE = {}
