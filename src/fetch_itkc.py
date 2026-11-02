# -*- coding: utf-8 -*-
"""Download every 한국문집총간 file from data.go.kr dataset 3074298 (file-history list, 1,251 entries).

  python src/fetch_itkc.py --out data/raw/itkc [--dataset 3074298] [--limit N]

- Lists the file history (uddi per file), writes _list-{date}.tsv, then downloads each zip with a 1 s gap,
  skipping files already present with the same byte length. Writes {name}.source.json next to each zip
  and _fetch-log.tsv (name, bytes, sha256, seconds). License text is read from the dataset page every run
  and the run stops if it is not '이용허락범위 제한 없음'.
- No personal data in headers, URLs or parameters.
"""
import argparse, hashlib, http.cookiejar, json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BASE = "https://www.data.go.kr"
CJ = http.cookiejar.CookieJar()
OP = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CJ))
OP.addheaders = [("User-Agent", "Mozilla/5.0 (MunjipMetrics/1.0; research)")]


def get(url, data=None, tries=4):
    body = urllib.parse.urlencode(data).encode() if data else None
    for i in range(tries):
        time.sleep(1)
        try:
            with OP.open(BASE + url, body, timeout=180) as r:
                return r.read(), r.headers
        except Exception as e:  # noqa
            print(f"  재시도 {i+1}: {e}", flush=True); time.sleep(5 * (i + 1))
    raise RuntimeError("요청 실패: " + url)


def text(b):
    import html
    t = b.decode("utf-8", "replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", "\n", t))
    return re.sub(r"\s*\n\s*", "\n", t)


def dataset(pk):
    b, _ = get(f"/data/{pk}/fileData.do")
    t = text(b)
    title = (re.search(r"파일데이터명\n([^\n]+)", t) or [0, "?"])[1]
    lic = (re.search(r"이용허락범위\n([^\n]+)", t) or [0, "?"])[1]
    s = b.decode("utf-8", "replace")
    dls = re.findall(r"fn_fileDataDown\('(\d+)',\s*'([^']+)',\s*'([^']*)',\s*'(\d+)'", s)
    return {"pk": pk, "title": title, "license": lic, "downloads": dls}


def file_list(pk):
    info = dataset(pk)
    detail = info["downloads"][0][1]
    b, _ = get("/tcs/dss/selectHistAndCsvData.do", {"publicDataPk": pk, "publicDataDetailPk": detail})
    s = b.decode("utf-8", "replace")
    rows = re.findall(r'data-public-pk="(uddi:[^"]+)"\s+data-public-detail-sn="(\d+)">\s*([^<]+?)\s*</a>', s)
    return info, [(name, uddi, sn) for uddi, sn, name in rows]


def safe(name):
    return re.sub(r'[\/:*?"<>|]', "_", name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True); ap.add_argument("--dataset", default="3074298"); ap.add_argument("--limit", type=int, default=0)
    x = ap.parse_args()
    out = Path(x.out); out.mkdir(parents=True, exist_ok=True)
    info, rows = file_list(x.dataset)
    if "제한 없음" not in info["license"]:
        sys.exit(f"이용허락범위가 바뀌었다: {info['license']}")
    today = time.strftime("%Y-%m-%d")
    (out / f"_list-{today}.tsv").write_text("\n".join(f"{n}\t{u}\t{s}" for n, u, s in rows) + "\n", encoding="utf-8")
    print(f"{info['title']} | {info['license']} | 파일 {len(rows)}건", flush=True)
    log = out / "_fetch-log.tsv"
    done = {l.split("\t")[0] for l in log.read_text(encoding="utf-8").splitlines()} if log.exists() else set()
    n_ok = n_skip = n_fail = 0
    counts = {}
    for name, _, _ in rows:
        counts[safe(name)] = counts.get(safe(name), 0) + 1
    for i, (name, uddi, sn) in enumerate(rows[: x.limit or None], 1):
        stem = safe(name) + (f"_{uddi[-8:]}" if counts[safe(name)] > 1 else "")   # some list entries share a display name (and even the sn); the uddi is unique
        f = out / (stem + ".zip")
        if f.exists() and (name in done or stem in done):
            n_skip += 1; continue
        t0 = time.time()
        try:
            b, _ = get("/tcs/dss/selectFileDataDownload.do", {"publicDataDetailPk": uddi, "publicDataPk": x.dataset,
                                                            "atchFileId": "", "fileDetailSn": sn, "publicDataTyCode": "PR0051"})
            j = json.loads(b.decode("utf-8"))
            if not j.get("status"):
                raise RuntimeError(str(j.get("error")))
            b, h = get(f"/cmm/cmm/fileDownload.do?atchFileId={j['atchFileId']}&fileDetailSn={j['fileDetailSn']}")
            if b[:2] != b"PK":
                raise RuntimeError(f"zip 아님 ({len(b)} B, {b[:20]!r})")
            f.write_bytes(b)
            sha = hashlib.sha256(b).hexdigest()
            rec = {"dataset": x.dataset, "file": name, "uddi": uddi, "sn": sn, "license": info["license"],
                   "url": f"{BASE}/data/{x.dataset}/fileData.do", "fetched": today, "bytes": len(b), "sha256": sha}
            (out / (stem + ".source.json")).write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
            with log.open("a", encoding="utf-8") as w:
                w.write(f"{stem}\t{len(b)}\t{sha}\t{time.time()-t0:.1f}\n")
            n_ok += 1
            if n_ok % 25 == 0:
                print(f"  {i}/{len(rows)} 저장 {n_ok} 건너뜀 {n_skip} 실패 {n_fail}", flush=True)
        except Exception as e:  # noqa
            n_fail += 1
            with (out / "_fetch-errors.tsv").open("a", encoding="utf-8") as w:
                w.write(f"{name}\t{uddi}\t{sn}\t{e}\n")
            print(f"  실패: {name} — {e}", flush=True)
    print(f"끝: 저장 {n_ok} 건너뜀 {n_skip} 실패 {n_fail}", flush=True)


if __name__ == "__main__":
    main()
