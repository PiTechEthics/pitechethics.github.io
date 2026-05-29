#!/usr/bin/env python3
"""Verify each snippet body against its cited source URL.

For every snippet across all per-fellow JSONs in context/snippets/:
  1. Fetch the cited URL with a browser User-Agent (cached to /tmp).
  2. Strip HTML; if it's a PDF, run `strings` to extract printable text.
  3. Score the snippet by 5-gram overlap with the source text.
  4. Annotate the snippet with verify_score, verify_status, verify_method.

Statuses:
  - "verified"          score >= 0.85 against source page (or PDF via strings)
  - "partial"           0.40 <= score < 0.85   (likely paraphrased / composed)
  - "fail"              score < 0.40           (text not found at all)
  - "unverifiable_js"   source is a JS-rendered SPA — HTML body has no content
  - "unverifiable_pdf"  PDF text is compressed and `strings` finds nothing
  - "fetch_failed"      HTTP 4xx/5xx or network error

Writes per-fellow JSONs back in place and produces a report to stdout.
"""

from __future__ import annotations
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
SNIP_DIR = ROOT / "context" / "snippets"
CACHE_DIR = Path("/tmp/verify-cache")
CACHE_DIR.mkdir(exist_ok=True)

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

JS_APP_MARKERS = (
    b"__NEXT_DATA__",
    b'id="__next"',
    b'window.__INITIAL_STATE__',
    b'window.__INITIAL_DATA__',
    b'<div id="root"></div>',
    b'<div id="app"></div>',
    b'data-reactroot',
)


def url_from_attribution(attribution: str) -> Optional[str]:
    """Pull the URL out of '...Org · Title — https://...' style attribution."""
    m = re.search(r"https?://\S+", attribution)
    if not m:
        return None
    return m.group(0).rstrip(").,;")


def cache_path(url: str, suffix: str) -> Path:
    h = hashlib.sha1(url.encode()).hexdigest()[:16]
    return CACHE_DIR / f"{h}{suffix}"


def fetch(url: str) -> tuple[bytes, dict]:
    """Fetch URL with browser UA, caching to /tmp/verify-cache/. Returns (body, meta)."""
    meta_p = cache_path(url, ".meta")
    body_p = cache_path(url, ".body")
    if meta_p.exists() and body_p.exists():
        raw = meta_p.read_text()
        if raw.startswith("{"):
            return body_p.read_bytes(), json.loads(raw)
        code, _, ctype = raw.partition("|")
        return body_p.read_bytes(), {"http_code": int(code or 0), "content_type": ctype.strip()}

    cmd = [
        "curl", "-sS", "-L", "-A", UA,
        "--max-time", "30",
        "-o", str(body_p),
        "-w", "%{http_code}\t%{content_type}",
        url,
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if r.returncode != 0:
            meta = {"http_code": 0, "content_type": "", "error": r.stderr.strip()[:200]}
        else:
            code, _, ctype = r.stdout.partition("\t")
            meta = {"http_code": int(code or 0), "content_type": ctype.strip()}
    except Exception as e:
        meta = {"http_code": 0, "content_type": "", "error": str(e)[:200]}
        body_p.write_bytes(b"")

    meta_p.write_text(json.dumps(meta))
    return body_p.read_bytes(), meta


def extract_text(body: bytes, content_type: str, url: str) -> tuple[str, str]:
    """Return (text, method). method is 'html', 'pdf_strings', or 'empty'."""
    is_pdf = b"%PDF-" in body[:1024] or "pdf" in content_type.lower() or url.lower().endswith(".pdf")
    if is_pdf:
        try:
            r = subprocess.run(
                ["strings", "-n", "8", "-"],
                input=body, capture_output=True, check=False, timeout=30,
            )
            text = r.stdout.decode("utf-8", errors="replace")
        except Exception:
            text = ""
        return (text, "pdf_strings" if text.strip() else "empty")

    # HTML path
    try:
        raw = body.decode("utf-8", errors="replace")
    except Exception:
        raw = ""
    # Strip script/style first, then tags, then unescape entities, then collapse whitespace
    raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.IGNORECASE | re.DOTALL)
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = html.unescape(raw)
    raw = re.sub(r"\s+", " ", raw)
    return (raw, "html")


def is_js_app(body: bytes) -> bool:
    return any(m in body for m in JS_APP_MARKERS)


def normalize(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[‘’‚‛′‵]", "'", s)  # smart single quotes
    s = re.sub(r"[“”„‟″‶]", '"', s)  # smart double quotes
    s = re.sub(r"[–—−]", "-", s)                    # dashes
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^a-z0-9\s'-]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def score_overlap(snippet_body: str, source_text: str, n: int = 5) -> float:
    """Fraction of N-grams from snippet_body that appear in source_text."""
    s = normalize(snippet_body)
    t = normalize(source_text)
    words = s.split()
    if not words:
        return 0.0
    if len(words) < n:
        # short snippet: substring check
        return 1.0 if s in t else 0.0
    ngrams = [" ".join(words[i : i + n]) for i in range(len(words) - n + 1)]
    if not ngrams:
        return 0.0
    hits = sum(1 for ng in ngrams if ng in t)
    return hits / len(ngrams)


def classify(score: float, fetch_meta: dict, method: str, body: bytes) -> str:
    code = fetch_meta.get("http_code", 0)
    if code != 200:
        return "fetch_failed"
    if method == "empty":
        if is_js_app(body):
            return "unverifiable_js"
        return "unverifiable_pdf"
    if method == "html" and is_js_app(body) and score < 0.2:
        return "unverifiable_js"
    if score >= 0.85:
        return "verified"
    if score >= 0.40:
        return "partial"
    return "fail"


def main() -> None:
    files = sorted(p for p in SNIP_DIR.glob("*.json") if not p.name.startswith("_"))
    print(f"Verifying {len(files)} fellow files...\n")

    totals = {"verified": 0, "partial": 0, "fail": 0,
              "unverifiable_js": 0, "unverifiable_pdf": 0, "fetch_failed": 0,
              "no_url": 0}
    flagged: list[tuple[str, str, int, dict]] = []  # (fellow, status, idx, snippet)

    for path in files:
        with open(path) as f:
            data = json.load(f)
        fellow_label = data.get("fellow", path.stem)
        per_fellow_counts: dict[str, int] = {}
        for i, s in enumerate(data["snippets"]):
            url = url_from_attribution(s.get("attribution", ""))
            if not url:
                status = "no_url"
                s["verify_score"] = 0.0
                s["verify_status"] = status
                s["verify_method"] = "no_url"
            else:
                body, meta = fetch(url)
                text, method = extract_text(body, meta.get("content_type", ""), url)
                score = score_overlap(s["body"], text) if method != "empty" else 0.0
                status = classify(score, meta, method, body)
                s["verify_score"] = round(score, 3)
                s["verify_status"] = status
                s["verify_method"] = method

            per_fellow_counts[status] = per_fellow_counts.get(status, 0) + 1
            totals[status] += 1
            if status in ("partial", "fail"):
                flagged.append((fellow_label, status, i, s))

        with open(path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        bits = " / ".join(f"{k}:{v}" for k, v in sorted(per_fellow_counts.items()))
        print(f"  {fellow_label:<22} {bits}")

    print("\n" + "=" * 80)
    print("TOTALS:")
    for k, v in sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])):
        if v: print(f"  {k:<20} {v}")

    if flagged:
        print("\n" + "=" * 80)
        print(f"FLAGGED ({len(flagged)} — partial or fail):")
        for fellow, status, idx, s in flagged:
            print(f"\n  [{fellow}] #{idx}  {status}  (score={s['verify_score']})")
            print(f"    cat:    {s['category']}")
            print(f"    body:   {s['body'][:160].replace(chr(10),' ')}{'...' if len(s['body'])>160 else ''}")
            print(f"    attrib: {s['attribution'][:160]}")

    # Update combined _all.json
    combined = {}
    for path in files:
        combined[path.stem] = json.loads(path.read_text())
    (SNIP_DIR / "_all.json").write_text(json.dumps(combined, indent=2, ensure_ascii=False))
    print(f"\nRebuilt {SNIP_DIR}/_all.json")


if __name__ == "__main__":
    main()
