# -*- coding: utf-8 -*-
"""Metric registry — one entry per published metric, Korean and English.
The site builder reads this; nothing about a metric is defined anywhere else.

Fields
  id          metric id (also the page name)
  series      A size · B genres · C relationships · D authors
  table       derived CSV the metric lives in
  unit, fmt   display unit and python format spec
  ko / en     name, definition, formula, reading (how to read it), caveat
  external    (optional) prior figure the number is set against
  reliability "exact"             counted from the XML; the card gives denominator and checks
              "external-match"    compared with a published figure; the card gives the agreement
              "sampled-precision" a parsing or linkage step measured on a coded stratified sample; precision + CI
  takeaway    one-paragraph key point per language (filled from the full-corpus numbers)
"""

SITE = {
    "ko": {"title": "문집 메트릭스", "subtitle": "한국문집총간 1,249종을 편 단위로 센 수치와, 수치마다 붙인 신뢰도"},
    "en": {"title": "Munjip Metrics", "subtitle": "Korean literary collections (Hanguk munjip chonggan) counted work by work, with a reliability card on every number"},
    "version": "1.0.2",
}

SERIES = {
    "A": {"ko": "규모", "en": "Size"},
    "B": {"ko": "문체 구성", "en": "Genre composition"},
    "C": {"ko": "관계 문체", "en": "Relationship genres"},
    "D": {"ko": "저자와 간행", "en": "Authors and publication"},
}

SERIES_INTRO = {
    "A": {"ko": "문집·편·글자를 센다. 글자는 본문과 주(원주·교감주·난외주)를 나눠 센다.",
          "en": "Collections, works and characters. Characters are counted separately for the main text and for notes (original notes, collation and marginal notes)."},
    "B": {"ko": "고전번역원이 편마다 붙인 문체분류(대분류 7·중분류 28)를 그대로 센다. 머리 수치는 저자 글(필자 태그가 문집의 저자와 같은 편)만으로 낸다 — 같은 문집에 실린 남의 서문·발문·행장·만사(타인 글)는 뺀다.",
          "en": "Counts the genre classification the ITKC attached to every work (7 major, 28 minor classes). Headline shares use the author's own works only — works whose writer tag is the collection's author, as opposed to prefaces, postscripts, biographies and elegies by others that are printed in the same collection."},
    "C": {"ko": "서간의 수신자와 비지·행장의 피장자를 제목에서 문자열로 뽑아 센다. 1.0 은 인물을 동일화하지 않는다 — 같은 사람이 자·호·관직으로 달리 불리면 다른 문자열이다.",
          "en": "Addressees of letters and subjects of epitaphs and biographies, parsed from titles as strings. Version 1.0 does not identify persons: the same person called by courtesy name, pen name or office counts as different strings."},
    "D": {"ko": "저자의 생몰, 문과방목 연결, 문집 간행 시차, 번역·교감표점 진도.",
          "en": "Author dates, linkage to the civil-examination roster, the lag between death and publication, and translation and punctuation progress."},
}

SOURCES = {
    "itkc_munjip": {
        "ko": "한국고전번역원, 「한국고전번역원_한국문집총간_20240830」(공공데이터포털 3074298, 이용허락범위 제한 없음). 파일 이력 1,251항목 중 채택한 1,249건의 XML zip(첨부 없는 1건·구 스키마 판본 1건 제외) — 문집마다 서지 1파일(저자·집수·간행년·목차·간략해제)과 권차 파일들(편 단위 제목·필자·문체분류·본문). 편(type=\"최종정보\") 단위로 셌다.",
        "en": "Institute for the Translation of Korean Classics, 'Hanguk munjip chonggan' (data.go.kr dataset 3074298, no license restriction): 1,249 XML archives adopted from the 1,251 portal entries (one without an attachment and one old-schema edition excluded), one per collection — a bibliographic file (author, series volume, publication year, table of contents, short introduction) plus one file per fascicle with every work's title, writer, genre class and text. Counted at the work level (type=\"최종정보\").",
        "license": "No restriction (data.go.kr)", "url": "https://www.data.go.kr/data/3074298/fileData.do",
    },
    "aks_munkwa": {
        "ko": "한국학중앙연구원, 「조선조문과급제자」(15052752): 문과 급제자 15,151명의 성명·자·호·본관·생년·시험년·등급.",
        "en": "Academy of Korean Studies, 'Successful candidates of the civil service examination' (15052752): 15,151 passers with name, courtesy and pen names, clan seat, birth year, examination year and grade.",
        "license": "No restriction (data.go.kr)", "url": "https://www.data.go.kr/data/15052752/fileData.do",
    },
    "aks_persons": {
        "ko": "한국학중앙연구원, 「한국역대인명정보」: 27,035명의 성명·자·호·생몰년·본관. 저자 생몰의 교차 확인에 썼다.",
        "en": "Academy of Korean Studies, 'Korean historical persons': 27,035 persons with names, courtesy and pen names, dates and clan seat; used to cross-check author dates.",
        "license": "No restriction (data.go.kr)", "url": "https://www.data.go.kr/",
    },
}

PRIOR = {
    "kwak_2026": {"ko": "곽지은(2026)은 한국문집총간과 한국역대문집총서의 문집을 7개 문체 단위로 나눠 시대별 비중을 구했다. 詩가 일관되게 최다이나 점차 줄다가 20세기에 반등, 서간은 지속 증가, 공거류는 19세기 후반 급락, 애제·서발·전기는 일정하다고 보고했고, 저자 활동기와 간행기 사이 약 1세기 시차를 밝혔다(초록 기준 — 수치는 원문 확인 뒤 싣는다).",
                  "en": "Kwak Ji-eun (2026) split the collections of the Hanguk munjip chonggan and the Hanguk yeokdae munjip chongseo into seven genre units and measured their shares over time: poetry always largest but declining until a 20th-century rebound, letters rising steadily, court documents falling sharply in the late 19th century, elegies, prefaces and biographies steady; the paper also reports a lag of about a century between an author's active years and the printing of the collection (from the abstract; figures to be added after reading the full text).",
                  "cite": "곽지은, 「한국 문집 내 문체 구성 변화에 대한 계량적 분석」, 『한문학논집』 73, 2026.", "cite_en": "Kwak Ji-eun, 'A quantitative analysis of changes in genre composition within Korean literary collections' (in Korean), Hanmunhak nonjip 73, 2026."},
    "choi_2020": {"ko": "최채기(2020): 한국문집총간 정편 663종 가운데 번역되지 않은 문집 291종(2020년 기준).",
                  "en": "Choi Chae-gi (2020): of the 663 collections in the first series, 291 had not been translated as of 2020.",
                  "cite": "최채기, 「한국문집총간 우선번역서목 선정원칙과 서목의 선정」, 『민족문화』 55, 2020.", "cite_en": "Choi Chae-gi, 'Principles and selection of priority titles for translation from the Hanguk munjip chonggan' (in Korean), Minjok munhwa 55, 2020."},
    "choi_h_2021": {"ko": "최혜미(2021): 한국문집총간 소재 인물 1,258명의 문집·연보 데이터셋. 연보 대부분은 1700년대 이후에 만들어졌다.",
                    "en": "Choi Hye-mi (2021): a dataset of the 1,258 persons in the Hanguk munjip chonggan with their collections and chronologies; most chronologies date from the 1700s onward.",
                    "cite": "최혜미, 「한국 연보의 존재 양상 일고찰 — 『한국문집총간』 소재의 인물을 대상으로」, 『Journal of Korean Culture』 55, 2021.", "cite_en": "Choi Hye-mi, 'On the existence of Korean chronologies: the persons of the Hanguk munjip chonggan' (in Korean), Journal of Korean Culture 55, 2021."},
    "choi_j_2021": {"ko": "최지연·조성덕·최동빈(2021): 한국문집총간 XML 의 데이터 정제 장애 네 가지 — 페이지 번호 불일치, 데이터 추가, 데이터 누락, 원문 이미지와 XML 한자의 불일치. DB 구축은 1999~2021년, 1,259종 500책.",
                    "en": "Choi Ji-yeon, Cho Seong-deok and Choi Dong-bin (2021): four obstacles to cleaning the Hanguk munjip chonggan XML — page-number mismatches, added data, missing data, and characters that differ between the XML and the page images. The database was built 1999–2021 for 1,259 collections in 500 volumes.",
                    "cite": "최지연·조성덕·최동빈, 「데이터 정제의 관점에서 본 한국문집총간 XML 문서 검토」, 『한문학논집』 60, 2021.", "cite_en": "Choi Ji-yeon, Cho Seong-deok and Choi Dong-bin, 'A review of the Hanguk munjip chonggan XML documents from the viewpoint of data cleaning' (in Korean), Hanmunhak nonjip 60, 2021."},
    "mkstudy": {"ko": "한국학종합DB(미디어한국학) 한국문집총간DB 시대 분류: 전체 1,259 — 고려 26, 조선 전기 77, 조선 중기 434, 조선 후기 668, 대한제국 36 (2026-11-03 열람; 분류 합 1,241 과 전체의 차 18 은 그 면이 설명하지 않는다).",
                "en": "Korean Studies DB (Media Korean Studies), Hanguk munjip chonggan DB period filter: 1,259 in all — Goryeo 26, early Joseon 77, mid Joseon 434, late Joseon 668, Korean Empire 36 (read 2026-11-03; the filter counts sum to 1,241 and the page does not explain the 18 missing).",
                "cite": "https://db.mkstudy.com/opendatabase/itkc/chonggan/", "cite_en": "https://db.mkstudy.com/opendatabase/itkc/chonggan/"},
}

# ---------------------------------------------------------------------------------------------------------------
METRICS = [
    # ---------------- A size
    dict(id="a1_works", series="A", table="a_collections", unit="works", fmt=",.0f", reliability="exact",
         ko=dict(name="문집별 편 수", definition="문집 하나에 들어 있는 편(고전번역원 XML 의 최종정보 단위 — 시 한 수, 편지 한 통, 묘지명 한 편)의 수. 저자 자신의 글과 타인의 글(서문·발문·행장·부록)을 나눠 보인다.",
                 formula="type=\"최종정보\" 요소 수. 저자 글 = 편의 필자 한자성명이 서지의 저자와 같은 편.",
                 reading="", caveat="「편」은 고전번역원 편집진이 끊은 단위다. 연작시 「○○ 十首」가 한 편으로 묶이기도 하고 수마다 나뉘기도 한다. 글자 수 지표와 함께 본다."),
         en=dict(name="Works per collection", definition="Number of works in a collection — the ITKC's final unit (one poem, one letter, one epitaph), split into the author's own works and works by others (prefaces, postscripts, biographies, appendices).",
                 formula="Count of type=\"최종정보\" elements; own work = the work's writer equals the collection's author.",
                 reading="", caveat="A 'work' is a unit cut by the ITKC editors: a poem cycle '… 十首' may be one work or ten. Read together with the character counts.")),
    dict(id="a2_chars", series="A", table="a_collections", unit="characters", fmt=",.0f", reliability="exact",
         ko=dict(name="문집별 글자 수", definition="편 본문의 한자 수. 본문과 주(원주·교감주·난외주)를 나눠 센다.",
                 formula="<내용> 안 CJK 문자 수. chars_main = 원주·주석 밖, chars_note = 원주·주석 안. 검산: 원본 XML 의 <내용> 전체 문자 수와 100% 일치, 문자 참조 잔존 0.",
                 reading="", caveat="구두점·공백·한글은 세지 않는다. 고전번역원 입력본 기준이므로 영인본 면과 어긋난 글자(최지연 외 2021)는 반영되지 않는다."),
         en=dict(name="Characters per collection", definition="Chinese characters in the text of the works, counted separately for the main text and for notes (original notes, collation and marginal notes).",
                 formula="CJK code points inside <내용>; chars_main outside, chars_note inside 원주/주석 elements. Check: equals a direct recount of every <내용> in the raw XML, zero residual character references.",
                 reading="", caveat="Punctuation, spaces and Hangul are not counted. The ITKC transcription is the reference; characters that differ from the facsimile pages (Choi et al. 2021) are not corrected.")),
    dict(id="a3_centuries", series="A", table="a_centuries", unit="collections", fmt=",.0f", reliability="exact",
         ko=dict(name="세기별 문집 수", definition="저자 생년의 세기별 문집 수와 저자 수, 정편·속편 구분.",
                 formula="세기 = (생년 − 1) ÷ 100 + 1. 정편 = 집수 번호 a, 속편 = b.",
                 reading="", caveat="편 단위 연대가 XML 에 없어 저자 생년으로 묶는다. 저자 활동기와 간행기 사이에는 약 1세기 시차가 있다(곽지은 2026)."),
         en=dict(name="Collections by century", definition="Collections and authors by the author's birth century, first series and supplement apart.",
                 formula="Century = (birth year − 1) ÷ 100 + 1; first series = volume numbers a, supplement = b.",
                 reading="", caveat="The XML carries no date per work, so works are grouped by the author's birth year. Printing lags the author's active years by about a century (Kwak 2026)."),
         external=dict(ko="한국학종합DB 의 시대 분류(고려 26·전기 77·중기 434·후기 668·대한제국 36)와 세기 분포를 나란히 둔다 — 시대 경계가 세기와 다르므로 합계(1,259 대 이 사이트의 문집 수)만 맞춰 본다.",
                       en="Set against the period filter of the Korean Studies DB (Goryeo 26, early 77, mid 434, late 668, Korean Empire 36); periods do not coincide with centuries, so only the totals (1,259 vs this site's collection count) are compared.")),
    dict(id="a4_chars_per_work", series="A", table="a_centuries", unit="characters", fmt=",.0f", reliability="exact",
         ko=dict(name="편당 글자 수", definition="편 하나의 글자 수(본문 + 주)의 중앙값과 평균, 세기별.",
                 formula="median(chars_main + chars_note) over works", reading="", caveat="시가 많은 문집일수록 작다. 문체별 길이는 B 계열의 시 길이 지표에."),
         en=dict(name="Characters per work", definition="Median and mean characters (text + notes) of a work, by century.",
                 formula="median(chars_main + chars_note) over works", reading="", caveat="Smaller where poems dominate; genre-specific length is in the poem-length metric of series B.")),
    dict(id="a5_note_share", series="A", table="a_centuries", unit="share", fmt=".1%", reliability="exact",
         ko=dict(name="주석 비율", definition="전체 글자 중 주(원주·교감주·난외주) 안의 글자 비율.",
                 formula="chars_note / (chars_main + chars_note)", reading="", caveat="원주는 저자·편찬자의 것이고 교감주·난외주는 고전번역원의 것이다. XML 은 둘을 다른 태그로 구분하므로 나눠 세었으나 이 지표는 합이다."),
         en=dict(name="Share of characters in notes", definition="Share of all characters that lie inside notes (original notes, collation and marginal notes).",
                 formula="chars_note / (chars_main + chars_note)", reading="", caveat="Original notes belong to the author or compiler, collation and marginal notes to the ITKC; the XML tags them differently, but this metric sums both.")),
    dict(id="a6_own_share", series="A", table="a_collections", unit="share", fmt=".1%", reliability="exact",
         ko=dict(name="저자 글 비율", definition="문집의 편 가운데 필자가 저자 자신이 쓴 편의 비율. 나머지는 서문·발문·행장·만사·부록 등 타인의 글이다.",
                 formula="필자 한자성명 = 저자 한자성명인 편 / 전체 편", reading="", caveat="필자 태그가 비어 있으면 저자 글로 세지 않는다. 같은 이름의 다른 사람은 구별하지 못한다(저자와 동명인 필자는 드물다)."),
         en=dict(name="Share of own works", definition="Share of a collection's works written by the author; the rest are prefaces, postscripts, biographies, elegies and appendices by others.",
                 formula="Works whose writer equals the author / all works", reading="", caveat="A work with an empty writer tag is not counted as the author's. Namesakes cannot be told apart (rare for a collection's own author).")),
    dict(id="a7_gwon", series="A", table="a_gwon_check", unit="fascicles", fmt=",.0f", reliability="exact",
         ko=dict(name="권 수와 권당 편 수", definition="목차의 「卷n」 제목 수로 센 권 수, 그리고 편 수를 권 수로 나눈 값.",
                 formula="목차제목 type=\"VOLUMETITLE\" 중 「卷」+숫자 형태의 수. 권당 편 수 = 편 수 / 권 수.", reading="", caveat="외집·별집·부록·연보는 「卷n」 꼴이 아니면 세지 않는다. 간략해제의 「n권 n책」과 자동 대조해 불일치율을 신뢰도 카드에 적는다. 불일치의 원인은 코딩하지 않았다."),
         en=dict(name="Fascicles and works per fascicle", definition="Fascicles counted from '卷n' headings in the table of contents, and works divided by fascicles.",
                 formula="VOLUMETITLE headings of the form 卷 + number; works per fascicle = works / fascicles.", reading="", caveat="Outer collections, separate collections, appendices and chronologies are not counted unless titled '卷n'. The count is checked against the 'n卷 n冊' statement of the short introduction; the mismatch rate is on the reliability card. The causes of mismatches were not coded."),
         external=dict(ko="간략해제의 첫 「n권 n책」 서술과 대조.", en="Checked against the first 'n fascicles, n volumes' statement in the short introduction.")),
    # ---------------- B genres
    dict(id="b1_poetry_share", series="B", table="b_centuries", unit="share", fmt=".1%", reliability="exact",
         ko=dict(name="시 비중", definition="저자 글(저자 자신이 쓴 편) 가운데 詩類의 비율. 편 기준과 글자 기준을 함께 보인다. 이 사이트의 대표 지표다.",
                 formula="詩類 편 / 저자 글 (세기별); 詩類 글자 / 저자 글자", reading="", caveat="고전번역원 분류를 그대로 쓴다(부·사는 詩類 안의 중분류). 편 단위가 「十首」 묶음인 경우 편 기준 비중은 낮아지고 글자 기준은 그렇지 않다."),
         en=dict(name="Share of poetry", definition="Share of the author's own works classified as poetry (詩類), by works and by characters. The site's headline metric.",
                 formula="Poetry works / own works (per century); poetry characters / own characters", reading="", caveat="Uses the ITKC classification as given (rhapsodies and lyrics are subclasses of 詩類). Where a cycle of ten poems is one work, the work-based share falls and the character-based share does not."),
         external=dict(ko="곽지은(2026)의 문체 비중 추이와 방향을 대조한다 — 詩 최다·점진 하락·20세기 반등.", en="Direction compared with Kwak (2026): poetry largest, gradual decline, 20th-century rebound.")),
    dict(id="b2_genre_mix", series="B", table="b_centuries", unit="share", fmt=".1%", reliability="exact",
         ko=dict(name="7대분류 구성", definition="세기별로 저자 글이 7개 대분류(詩·書簡·序跋·傳記·公車·哀祭·雜著)에 어떻게 나뉘는가.",
                 formula="대분류별 편 / 저자 글; 글자 기준도 함께", reading="", caveat="雜著類가 크다 — 論說·記·箴銘·其他가 모두 들어간다. 중분류 표를 따로 둔다."),
         en=dict(name="Seven-class genre mix", definition="How the author's own works divide among the seven major classes (poetry, letters, prefaces and postscripts, biographies, memorials, elegies, miscellany), by century.",
                 formula="Works per major class / own works; characters likewise", reading="", caveat="Miscellany (雜著類) is large: essays, records, inscriptions and 'other' all fall there. A separate table gives the minor classes.")),
    dict(id="b3_letters_share", series="B", table="b_centuries", unit="share", fmt=".1%", reliability="exact",
         ko=dict(name="서간 비중", definition="저자 글 중 書簡類의 비율, 세기별.", formula="書簡類 편 / 저자 글", reading="", caveat="문집에 실린 편지만이다 — 문집 편찬 때 고른 결과이지 쓴 편지 전부가 아니다."),
         en=dict(name="Share of letters", definition="Share of own works that are letters (書簡類), by century.", formula="Letter works / own works", reading="", caveat="Only letters selected for the printed collection, not all letters written.")),
    dict(id="b4_memorials_share", series="B", table="b_centuries", unit="share", fmt=".1%", reliability="exact",
         ko=dict(name="공거류(소·차·계) 비중", definition="저자 글 중 公車類(疏箚·對策·敎書 등 조정에 올리거나 조정에서 내린 글)의 비율, 세기별.", formula="公車類 편 / 저자 글", reading="", caveat="조정에 올리거나 조정에서 내린 글과 과거 답안(對策)이므로 관직·과거와 관련된 문체다. 저자의 관력은 이 사이트가 검증하지 않았다."),
         en=dict(name="Share of court documents", definition="Share of own works in the court-document class (公車類: memorials, examination answers, royal edicts), by century.", formula="Court-document works / own works", reading="", caveat="Documents submitted to or issued by the court, plus examination answers (對策), so the genre is tied to office and examinations; the authors' careers were not verified on this site.")),
    dict(id="b5_relational_share", series="B", table="b_centuries", unit="share", fmt=".1%", reliability="exact",
         ko=dict(name="애제·비지·행장 비중", definition="저자 글 중 哀祭類(제문·애사·뇌)와 傳記類 중 碑誌·行狀의 비율 — 남을 기리는 글.", formula="(哀祭類 + 碑誌類 + 行狀類) 편 / 저자 글", reading="", caveat="傳記類의 系譜·其他는 넣지 않는다."),
         en=dict(name="Share of elegies, epitaphs and biographies", definition="Share of own works that commemorate others: elegies (哀祭類) plus epitaphs and biographies within the biography class.", formula="(哀祭類 + 碑誌類 + 行狀類) works / own works", reading="", caveat="Genealogies and 'other' within the biography class are excluded.")),
    dict(id="b6_prefaces_share", series="B", table="b_centuries", unit="share", fmt=".1%", reliability="exact",
         ko=dict(name="서발 비중", definition="저자 글 중 序跋類(서·발·증서)의 비율, 세기별.", formula="序跋類 편 / 저자 글", reading="", caveat="다른 사람의 책에 붙인 서문이 많다 — 저자의 교유 범위와 관련된다(해석은 하지 않는다)."),
         en=dict(name="Share of prefaces and postscripts", definition="Share of own works that are prefaces, postscripts or farewell prefaces (序跋類), by century.", formula="Preface works / own works", reading="", caveat="Many are prefaces to other people's books, which relates to the range of the author's acquaintances (not interpreted here).")),
    dict(id="b7_other_share", series="B", table="b_other_share", unit="share", fmt=".1%", reliability="exact",
         ko=dict(name="기타류 잔여율", definition="저자 글 중 중분류가 「其他類」인 편의 비율 — 고전번역원 분류가 세분하지 않은 나머지.", formula="중분류 其他類 편 / 저자 글", reading="", caveat="분류 품질의 지표다. 값이 크면 그 세기의 문체 구성 수치는 거칠다."),
         en=dict(name="Residual 'other' share", definition="Share of own works whose minor class is 'other' (其他類) — what the ITKC classification did not subdivide.", formula="Works in 其他類 / own works", reading="", caveat="A measure of classification quality: where it is high, the genre shares for that century are coarse.")),
    dict(id="b8_poem_length", series="B", table="b_poems", unit="characters", fmt=",.0f", reliability="exact",
         ko=dict(name="시 한 편의 글자 수", definition="詩類 편의 본문 글자 수 중앙값과 사분위, 세기별.", formula="median(chars_main) over 詩類 works", reading="", caveat="오언절구 20자, 칠언율시 56자가 기준점이다. 연작이 한 편으로 묶이면 커진다."),
         en=dict(name="Characters per poem", definition="Median and quartiles of the main-text characters of poetry works, by century.", formula="median(chars_main) over poetry works", reading="", caveat="Reference points: 20 characters for a five-syllable quatrain, 56 for a seven-syllable regulated verse. Cycles bundled as one work push the value up.")),
    # ---------------- C relationships
    dict(id="c1_recipients", series="C", table="c_letters", unit="strings", fmt=",.0f", reliability="sampled-precision",
         ko=dict(name="서간 수신자 수와 집중도", definition="저자의 서간의 제목에서 뽑은 수신자 문자열의 고유 수, 상위 1·3 수신자 점유율, 허핀달 지수.",
                 formula="제목이 (又·再·三…)答·與·上·寄·復·報·奉·呈·贈·簡·謝·代 로 시작하면 그 다음부터 書·簡·問目·別紙·狀·札·啓·帖·疏·牘 등 앞까지(수신자 뒤의 論·問·議 등 화제어 앞까지)를 수신자로 본다. 擬作(擬…)은 빈칸. 고유 수 = 문집 안에서 서로 다른 문자열 수(사이트 합계는 문집별 고유 수의 합).",
                 reading="", caveat="문자열 단위다. 「退溪先生」·「李景浩」·「李滉」은 셋으로 센다. 추출 정밀도는 표본으로 쟀다(신뢰도 카드)."),
         en=dict(name="Letter addressees and concentration", definition="Distinct addressee strings parsed from the titles of the author's letters, the share of the top one and top three, and a Herfindahl index.",
                 formula="If the title begins with (又·再·三…)答·與·上·寄·復·報·奉·呈·贈·簡·謝·代, the addressee is the text up to 書·簡·問目·別紙·狀·札·啓·帖·疏·牘 etc. (and before a topic verb such as 論·問·議); imagined letters (擬…) are blank. Distinct = distinct strings within a collection (the site total sums per-collection counts).",
                 reading="", caveat="String level: '退溪先生', '李景浩' and '李滉' are three addressees. Parsing precision was measured on a sample (reliability card).")),
    dict(id="c2_epitaph_subjects", series="C", table="c_epitaphs", unit="strings", fmt=",.0f", reliability="sampled-precision",
         ko=dict(name="비지·행장 피장자 수", definition="저자가 쓴 묘지명·묘갈명·신도비·행장 등의 제목에서 뽑은 피장자 문자열의 수와 고유 수.",
                 formula="제목에서 墓誌銘·墓碣銘·神道碑·墓表·行狀·諡狀 등 앞부분을 피장자로 본다(贈·故·先考 등 머리말 제거).", reading="", caveat="관직·시호가 붙은 긴 문자열이라 고유 수는 거의 편 수와 같다. 1.0 은 동일인 묶기를 하지 않는다."),
         en=dict(name="Subjects of epitaphs and biographies", definition="Subject strings parsed from the titles of the author's epitaphs, tomb inscriptions and biographies, with the number of distinct strings.",
                 formula="Text before 墓誌銘·墓碣銘·神道碑·墓表·行狀·諡狀 etc. is the subject (honorific prefixes 贈·故·先考 removed).", reading="", caveat="Strings carry offices and posthumous names, so distinct counts are close to work counts. Version 1.0 does not merge persons.")),
    dict(id="c3_other_writers", series="C", table="c_writers", unit="persons", fmt=",.0f", reliability="exact",
         ko=dict(name="타인 필자 수", definition="문집에 글을 보탠 저자 이외의 필자 수(서문·발문·행장·만사·부록)와 그 편 수.", formula="필자 ≠ 저자인 편의 고유 필자 한자성명 수", reading="", caveat="필자 태그 기준이다. 「門人」처럼 이름 아닌 표기는 한 사람으로 센다."),
         en=dict(name="Other writers", definition="Writers other than the author who contributed to the collection (prefaces, postscripts, biographies, elegies, appendices) and their works.", formula="Distinct writer names among works whose writer ≠ author", reading="", caveat="Follows the writer tag; a label such as '門人' (disciples) counts as one.")),
    # ---------------- D authors
    dict(id="d1_dates", series="D", table="d_centuries", unit="share", fmt=".1%", reliability="exact",
         ko=dict(name="생몰 완비율과 수명", definition="저자 가운데 생년·몰년이 모두 있는 비율과, 있는 저자의 수명 중앙값, 세기별.", formula="생년·몰년 있는 저자 / 저자; median(몰년 − 생년)", reading="", caveat="고전번역원 서지의 서기년을 그대로 쓴다. 한국역대인명정보와 맞춰 본 일치율을 신뢰도 카드에 적는다."),
         en=dict(name="Date completeness and lifespan", definition="Share of authors with both birth and death years, and the median lifespan of those who have them, by century.", formula="Authors with both years / authors; median(death − birth)", reading="", caveat="Uses the ITKC bibliographic years as given; agreement with the AKS person database is on the reliability card."),
         external=dict(ko="한국역대인명정보의 생몰년과 대조.", en="Compared with the dates in the AKS person database.")),
    dict(id="d2_munkwa", series="D", table="d_centuries", unit="share", fmt=".1%", reliability="sampled-precision",
         ko=dict(name="문과 급제 연결률과 급제 연령", definition="저자 가운데 문과방목의 급제자와 연결된 비율, 연결된 저자의 급제 연령(세는나이) 분포.",
                 formula="성명은 NFKC 정규화(煕=熙 포함). M1 성명+생년 일치(같은 본관의 여러 행은 첫 급제 = M1-first) / M2 성명 일치·방목 생년 없음·자 또는 호 일치 / M3 성명 일치·후보 1·방목 생년 없음·시험년이 [생년+15, 몰년(없으면 생년+70)] 안. 둘 이상 남으면 미확정. 연결률 = (M1+M1-first+M2+M3) / 저자.",
                 reading="", caveat="연결률은 급제율이 아니다 — 급제하지 않은 저자(산림·승려·여성·고려인)는 정상적으로 연결되지 않는다. 간략해제는 급제를 거의 적지 않아 정밀도를 해제로 잴 수 없었고, 자·호 교차 일치율로 대신한다(신뢰도 카드)."),
         en=dict(name="Examination linkage and age at passing", definition="Share of authors linked to a passer in the civil-examination roster, and the distribution of the age at passing (East Asian reckoning) for linked authors.",
                 formula="Names NFKC-normalized (煕=熙 included). M1 same name and birth year (several rows of one clan seat: first pass = M1-first) / M2 same name, roster birth absent, courtesy or pen name identical / M3 same name, single candidate, roster birth absent, exam year within [birth+15, death (or birth+70)]. More than one survivor: unresolved. Linkage = (M1+M1-first+M2+M3) / authors.",
                 reading="", caveat="Linkage is not a pass rate: authors who never passed the examination (rural scholars, monks, women, Goryeo authors) rightly stay unlinked. The short introductions rarely mention examinations, so precision could not be measured against them; a courtesy- and pen-name cross-check stands in (reliability card).")),
    dict(id="d3_pub_lag", series="D", table="d_centuries", unit="years", fmt=",.0f", reliability="exact",
         ko=dict(name="간행 시차", definition="원문 간행년에서 저자 몰년을 뺀 햇수의 중앙값과 사분위, 세기별.", formula="median(원문간행년 − 몰년), 간행년이 있는 문집만", reading="", caveat="서지의 원문간행년은 총간 저본의 간행년이다(초간이 아닐 수 있다). 간행년 없는 문집은 뺀다."),
         en=dict(name="Publication lag", definition="Median and quartiles of years from the author's death to the printing of the source edition, by century.", formula="median(publication year − death year), collections with a publication year only", reading="", caveat="The bibliographic year is that of the edition reproduced in the series, not necessarily the first printing; collections without a year are excluded."),
         external=dict(ko="곽지은(2026)의 「약 1세기 시차」와 나란히.", en="Set against Kwak (2026): 'about a century'.")),
    dict(id="d4_translation", series="D", table="d_centuries", unit="share", fmt=".1%", reliability="exact",
         ko=dict(name="번역문 연계 진도", definition="편 가운데 고전종합DB 안에서 번역문이 연계된 편의 비율, 그리고 연계된 편이 하나도 없는 문집의 수. 번역 사업의 현황이 아니라 DB 연계의 현황이다.", formula="연계항목 type=\"번역문\" 있는 편 / 편; 문집 단위 0건 수", reading="", caveat="2024-08 자 XML 의 태그 기준이다. 연계가 하나도 없는 정편 문집 520종은 최채기(2020)가 센 미번역 291종보다 훨씬 많다 — 번역서가 있어도 DB 에 연계되지 않은 문집이 있다는 뜻이므로, 이 수치를 「미번역」으로 읽지 않는다."),
         en=dict(name="Linked-translation progress", definition="Share of works with a translation linked inside the ITKC database, and the number of collections with no linked work at all. This measures database linkage, not the translation program.", formula="Works with a 번역문 link / works; collections with zero", reading="", caveat="Tags of the 2024-08 XML. The 520 first-series collections without any link far exceed the 291 that Choi (2020) counted as untranslated, so some translated collections are simply not linked; do not read this metric as 'untranslated'."),
         external=dict(ko="최채기(2020): 정편 663종 가운데 미번역 291종(번역됐거나 진행 중 372종). 이 사이트에서 정편 가운데 번역문 연계가 1편 이상인 문집은 143종이다. 두 수는 서로 다른 것을 센다(번역 여부와 DB 안의 연계). 372종 가운데 적어도 229종은 2024-08 XML 에 연계가 없다. 그 이유가 연계 지연인지 연계 대상이 아니어서인지는 이 자료로 알 수 없다.", en="Choi (2020): 291 of the 663 first-series collections untranslated (372 translated or in progress). On this site 143 first-series collections have at least one linked translation. The two figures count different things (whether a translation exists vs. a link inside the database): at least 229 of the 372 have no link in the 2024-08 XML. Whether that reflects linking still to be done or collections outside the linking scope cannot be told from these data.")),
    dict(id="d5_punct", series="D", table="d_centuries", unit="share", fmt=".1%", reliability="exact",
         ko=dict(name="교감표점 진도", definition="편 가운데 교감표점본이 연계된 편의 비율, 세기별.", formula="연계항목 type=\"교감표점\" 있는 편 / 편", reading="", caveat="교감표점 사업은 정편의 일부에서 진행됐다. 2024-08 자 XML 기준."),
         en=dict(name="Collation and punctuation progress", definition="Share of works with a linked collated and punctuated edition, by century.", formula="Works with a 교감표점 link / works", reading="", caveat="The collation program covers part of the first series. As of the 2024-08 XML.")),
]

PERSON_PAGES = [  # collection ids filled after the full build (title_hj -> id)
    ("弘齋全書", "정조", "Jeongjo"), ("與猶堂全書", "정약용", "Jeong Yak-yong"), ("東國李相國集", "이규보", "Yi Gyu-bo"), ("四佳集", "서거정", "Seo Geo-jeong"),
    ("星湖全集", "이익", "Yi Ik"), ("退溪集", "이황", "Yi Hwang"), ("栗谷全書", "이이", "Yi I"), ("宋子大全", "송시열", "Song Si-yeol"),
    ("燕巖集", "박지원", "Bak Ji-won"), ("阮堂全集", "김정희", "Kim Jeong-hui"),
]
