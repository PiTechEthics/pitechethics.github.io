#!/usr/bin/env python3
"""Verify ONE snippet body against ONE source URL.

For use by re-scrape agents BEFORE writing the snippet to JSON.

Usage:
    python3 scripts/verify_one.py <URL> <<<"snippet body here"
    python3 scripts/verify_one.py <URL> --body "snippet body here"
    python3 scripts/verify_one.py <URL> --file /path/to/snippet.txt

Prints a single line:
    score=<0.0–1.0> status=<verified|partial|fail|fetch_failed|js_empty|pdf_empty>

Exit code 0 if score >= 0.95 ("verified"), else 1. Agents should KEEP only
snippets where exit code is 0. Do NOT "fix" a failing snippet by rewording it —
pick a different verbatim span from the page.
"""

from __future__ import annotations
import argparse
import hashlib
import html
import re
import subprocess
import sys
from pathlib import Path

CACHE = Path("/tmp/verify-cache")
CACHE.mkdir(exist_ok=True)
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
JS_MARKERS = (b"__NEXT_DATA__", b'id="__next"', b"window.__INITIAL_STATE__")


def _read_meta(meta_p: Path) -> tuple[int, str]:
    raw = meta_p.read_text()
    # Two cache formats coexist: JSON (from verify_snippets.py) and pipe (here).
    if raw.startswith("{"):
        import json as _json
        m = _json.loads(raw)
        return int(m.get("http_code", 0) or 0), m.get("content_type", "")
    code, _, ctype = raw.partition("|")
    return int(code or 0), ctype


def fetch(url: str) -> tuple[bytes, int, str]:
    body_p = CACHE / f"{hashlib.sha1(url.encode()).hexdigest()[:16]}.body"
    meta_p = body_p.with_suffix(".meta")
    if body_p.exists() and meta_p.exists():
        code, ctype = _read_meta(meta_p)
        return body_p.read_bytes(), code, ctype
    r = subprocess.run(
        ["curl", "-sS", "-L", "-A", UA, "--max-time", "30",
         "-o", str(body_p), "-w", "%{http_code}|%{content_type}", url],
        capture_output=True, text=True, check=False,
    )
    code_ctype = r.stdout if r.returncode == 0 else "0|"
    meta_p.write_text(code_ctype)
    code, _, ctype = code_ctype.partition("|")
    return body_p.read_bytes() if body_p.exists() else b"", int(code or 0), ctype


def extract(body: bytes, ctype: str, url: str) -> tuple[str, str]:
    if b"%PDF-" in body[:1024] or "pdf" in ctype.lower() or url.lower().endswith(".pdf"):
        r = subprocess.run(["strings", "-n", "8", "-"], input=body,
                           capture_output=True, check=False, timeout=30)
        text = r.stdout.decode("utf-8", errors="replace")
        return text, ("pdf" if text.strip() else "pdf_empty")
    raw = body.decode("utf-8", errors="replace")
    raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.I | re.S)
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = html.unescape(raw)
    raw = re.sub(r"\s+", " ", raw)
    if not raw.strip() and any(m in body for m in JS_MARKERS):
        return raw, "js_empty"
    return raw, "html"


def normalize(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[‘’‚‛′‵]", "'", s)
    s = re.sub(r"[“”„‟″‶]", '"', s)
    s = re.sub(r"[–—−]", "-", s)
    s = re.sub(r"[^a-z0-9\s'\-]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def score(body_snippet: str, source_text: str, n: int = 5) -> float:
    s = normalize(body_snippet)
    t = normalize(source_text)
    words = s.split()
    if not words:
        return 0.0
    if len(words) < n:
        return 1.0 if s in t else 0.0
    ngrams = [" ".join(words[i:i + n]) for i in range(len(words) - n + 1)]
    if not ngrams:
        return 0.0
    return sum(1 for ng in ngrams if ng in t) / len(ngrams)


def classify(sc: float, http_code: int, method: str) -> str:
    if http_code != 200:
        return "fetch_failed"
    if method in ("js_empty", "pdf_empty"):
        return method
    if sc >= 0.95:
        return "verified"
    if sc >= 0.50:
        return "partial"
    return "fail"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("url")
    src = p.add_mutually_exclusive_group()
    src.add_argument("--body", help="snippet body as a string")
    src.add_argument("--file", help="read snippet body from file")
    args = p.parse_args()

    if args.body is not None:
        body = args.body
    elif args.file:
        body = Path(args.file).read_text(encoding="utf-8")
    else:
        body = sys.stdin.read()
    body = body.strip()

    raw, code, ctype = fetch(args.url)
    text, method = extract(raw, ctype, args.url)
    sc = score(body, text) if method in ("html", "pdf") else 0.0
    status = classify(sc, code, method)
    print(f"score={sc:.3f} status={status} method={method} http={code} chars_body={len(body)} chars_source={len(text)}")
    sys.exit(0 if status == "verified" else 1)


if __name__ == "__main__":
    main()
