# 문집 메트릭스 · Munjip Metrics

한국문집총간 1,249종을 편 단위로 센 수치와, 수치마다 붙인 신뢰도.
Korean literary collections (Hanguk munjip chonggan) counted work by work, with a reliability card on every number.

**사이트 · Site:** https://bowonkwon.github.io/Munjip-Metrics/ ([한국어](https://bowonkwon.github.io/Munjip-Metrics/ko/) · [English](https://bowonkwon.github.io/Munjip-Metrics/en/))
**공개 자료 전체 · All public materials:** https://bowonkwon.github.io/

## 무엇인가 · What this is

한국고전번역원이 공공데이터포털에 개방한 「한국문집총간」 XML(목록 1,251항목 중 첨부 있는 1,250건을 받고 구 스키마 중복 1건을 뺀 1,249종, 이용허락범위 제한 없음)을 편(詩 한 수·편지 한 통·묘지명 한 편) 단위 표로 만들고, 규모·문체 구성·관계 문체·저자와 간행의 네 계열 23개 지표를 센다. 원문 전문은 싣지 않고 편마다 고전종합DB 로 연결한다. 번역문·웹 콘텐츠는 쓰지 않았다.

All 1,251 XML archives of the Hanguk munjip chonggan released by the Institute for the Translation of Korean Classics on data.go.kr (no license restriction) were listed; 1,250 attachments were downloaded (one entry has none), 1,249 archives adopted (one old-schema duplicate excluded) and turned into a work-level table (one poem, one letter, one epitaph = one row). Twenty-three metrics in four series — size, genre composition, relationship genres, authors and publication — are counted from it. No full text is reproduced; every work links to the ITKC database.

| | |
|---|---|
| 문집 · collections | 1,249 (정편 663 · 속편 586) |
| 편 · works | 637,203 (저자 글 609,494) |
| 글자 · characters | 182,868,728 (본문 177,365,899 · 주 5,502,829) |
| 저자 · authors | 1,248 (문과방목 연결 613) |
| 지표 · metrics | 23 (A 7 · B 8 · C 3 · D 5) |

포털 목록 1,251항목 중 1건(운암집, 2021 등록)은 내려받기 요청에 첨부 ID 가 돌아오지 않았고(포털 응답 `atachFileYn: N`, 원응답은 작업 기록에 보존), 1건(망헌유고 1571년, 2017 등록)은 2003년 구 스키마(UTF-16)로 된 같은 문집의 다른 판본이라(신 스키마 판과 85편 중 84편 본문 일치) 제외했다. Of the 1,251 portal entries, one (Unam jip, 2021) returned no attachment id (portal response `atachFileYn: N`, kept in the working records) and one (Manghyeon yugo 1571, 2017) is an old-schema (UTF-16) edition of a collection also present in the new schema (84 of 85 works identical); both are excluded.

## 신뢰도 카드 · Reliability cards

- **집계값 · exact** — 원본 XML에서 그대로 센 수. 글자 수는 모든 문집에서 원본 `<내용>` 재계산과 일치하고 문자 참조 잔존 0 이다. Counted straight from the XML; character counts equal an independent recount for every collection.
- **외부 대조 · external** — 곽지은(2026)의 문체 비중 추이, 최채기(2020)의 미번역 291종, 한국학종합DB 시대별 건수와 나란히 둔다. Set against published figures.
- **표본 정밀도 · sampled** — 서간 수신자·비지 피장자 파싱과 문과방목 연결은 층화 표본을 코딩해 정밀도와 윌슨 95% 구간을 적는다(`data/coding/`). Parsing and linkage steps are measured on coded stratified samples.

## 데이터 · Data

`data/` 의 CSV 와 `datapackage.json`. 뼈대는 `works.csv.gz`(편마다 ID·문집·권·문체분류·제목·필자·글자 수(본문/주)·연계 유무, 본문 없음)이며 모든 지표는 이 표와 `authors.csv` 에서 다시 만들 수 있다. `raw_manifest.json` 에 원본 zip 1,249건의 SHA-256 이 있다.

CSV tables and `datapackage.json` in `data/`. The backbone is `works.csv.gz` (per work: id, collection, fascicle, genre class, title, writer, characters text/notes, link flags; no text); every metric can be rebuilt from it and `authors.csv`. `raw_manifest.json` lists SHA-256 digests of the 1,249 source archives.

## 재현 · Reproduce

```
pip install -r requirements.txt
python src/fetch_itkc.py --out data/raw/itkc          # data.go.kr 3074298, 1 s between requests
python src/build_works.py --src data/raw/itkc           # works / collections / letters / epitaphs
python src/check_works.py --src data/raw/itkc           # recount vs raw XML, ids, residue
python src/link_authors.py --derived data/derived --munkwa <AKS 문과급제자 XML> --persons <AKS 인명 XML>
python src/metrics_a.py; python src/metrics_b.py; python src/metrics_c.py; python src/metrics_d.py
python src/reliability.py                                # from data/coding/*_coded.csv
python src/build_site.py                                 # -> site/ (ko, en); 공개 사이트는 그 사본인 docs/ · the published copy is docs/
```

위 1~4단계와 `reliability.py` 는 이 저장소에 없는 원자료(고전번역원 zip, 한국학중앙연구원 XML)가 있어야 돈다. 지표 스크립트는 `data/derived/works.csv` 를 읽지만 이 저장소에는 `data/works.csv.gz` 로 들어 있으므로, 이 저장소만으로 지표와 사이트를 다시 만들 때는 다음처럼 한다. `reliability.json` 은 그대로 쓰고, 글자 수 검산 문장(검산 보고서가 필요)은 「?」로 나온다.
Steps 1–4 and `reliability.py` need source files not included here (ITKC archives, AKS XML). The metric scripts read `data/derived/works.csv`, while this repository ships `data/works.csv.gz`; to rebuild the metrics and the site from this repository alone (the shipped `reliability.json` is reused; the character-recount sentence shows "?" because it needs the check report):

```
mkdir -p data/derived && cp data/*.csv data/*.json data/derived/
python -c "import gzip,shutil;[shutil.copyfileobj(gzip.open(f'data/{n}.csv.gz'),open(f'data/derived/{n}.csv','wb')) for n in ('works','letters')]"
python src/metrics_a.py; python src/metrics_b.py; python src/metrics_c.py; python src/metrics_d.py
python src/build_site.py                                 # -> site/
```

## 라이선스 · License

코드 MIT, 파생 표·사이트 텍스트 CC BY 4.0. 원문·분류·제목·서지는 한국고전번역원, 방목·인명은 한국학중앙연구원의 것이다. Code MIT; derived tables and site text CC BY 4.0; source data belongs to the ITKC and the Academy of Korean Studies. See `LICENSE.md`.

## 인용 · Citation

Kwon, Bowon (2026). Munjip Metrics 1.0.2. https://bowonkwon.github.io/Munjip-Metrics/
