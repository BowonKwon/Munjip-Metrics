# -*- coding: utf-8 -*-
"""Write data/derived/raw_manifest.json: one entry per source zip (name, bytes, sha256, uddi, fetch date, ITKC collection id).

  python src/raw_manifest.py [--raw data/raw/itkc] [--derived data/derived]

The digests are recomputed from the files on disk (not copied from _fetch-log.tsv), so the manifest states what was
actually parsed. The zips themselves are never exported.
"""
import argparse, csv, hashlib, json, sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--raw", default="data/raw/itkc"); ap.add_argument("--derived", default="data/derived"); x = ap.parse_args()
    R = Path(x.raw); D = Path(x.derived)
    zip2id = {}
    if (D / "collections.csv").exists():
        for r in csv.DictReader(open(D / "collections.csv", encoding="utf-8")):
            zip2id[r["zip"]] = r["collection_id"]
    entries = []
    for z in sorted(R.glob("*.zip")):
        meta = {}
        sj = z.with_name(z.stem + ".source.json")
        if sj.exists():
            meta = json.loads(sj.read_text(encoding="utf-8"))
        b = z.read_bytes()
        entries.append({"file": z.name, "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest(), "uddi": meta.get("uddi", ""), "fetched": meta.get("fetched", ""),
                        "collection_id": zip2id.get(z.name, "")})
    man = {"dataset": "data.go.kr 3074298 (한국고전번역원_한국문집총간_20240830)", "license": "이용허락범위 제한 없음 / no restriction", "n_files": len(entries),
           "total_bytes": sum(e["bytes"] for e in entries), "files": entries}
    (D / "raw_manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"manifest: {len(entries)} zips, {man['total_bytes']:,} bytes")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
