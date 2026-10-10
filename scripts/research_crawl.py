#!/usr/bin/env python3
"""Search with Tavily and optionally extract a small set of result URLs.

Requires TAVILY_API_KEY in the environment. Never logs the key. Output is a
JSON evidence snapshot; it is not scientific validation or a trusted verdict.
"""
from __future__ import annotations
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API = "https://api.tavily.com"

def post_json(url: str, payload: dict) -> dict:
    body = json.dumps(payload).encode()
    req = Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(req, timeout=45) as response:
            return json.loads(response.read().decode())
    except HTTPError as exc:
        # Do not dump request headers or credentials into logs.
        raise RuntimeError(f"Tavily API returned HTTP {exc.code}") from None
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(f"Tavily request failed: {type(exc).__name__}") from None

def main() -> int:
    key = os.environ.get("TAVILY_API_KEY", "").strip()
    if not key:
        print("TAVILY_API_KEY is not set; skipping research run.", file=sys.stderr)
        return 2
    query = os.environ.get("TAVILY_QUERY", "Great Scale mathematics symmetry predictive closure phase-aware invariants")
    max_results = max(1, min(10, int(os.environ.get("TAVILY_MAX_RESULTS", "5"))))
    search = post_json(f"{API}/search", {"api_key": key, "query": query, "search_depth": "advanced", "max_results": max_results, "include_answer": False, "include_raw_content": False})
    results = search.get("results", [])
    urls = [item.get("url") for item in results if isinstance(item.get("url"), str) and item["url"].startswith("https://")][:max_results]
    extracted = []
    if urls:
        try:
            crawl = post_json(f"{API}/extract", {"api_key": key, "urls": urls, "extract_depth": "basic", "format": "text"})
            extracted = crawl.get("results", [])
        except RuntimeError as exc:
            # Preserve search results when extraction is unavailable.
            print(f"Extraction warning: {exc}", file=sys.stderr)
    snapshot = {"generated_at": datetime.now(timezone.utc).isoformat(), "query": query, "source": "Tavily Search + Extract", "research_is_not_validation": True, "results": results, "extracted": extracted}
    out = Path("artifacts/research") / (datetime.now(timezone.utc).strftime("%Y-%m-%d") + ".json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Saved {len(results)} search results and {len(extracted)} extracted pages to {out}")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
