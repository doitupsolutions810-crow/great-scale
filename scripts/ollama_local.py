#!/usr/bin/env python3
"""Run a local Ollama model; sends no requests to a cloud LLM provider."""
from __future__ import annotations
import json, os, sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

def main() -> int:
    prompt = " ".join(sys.argv[1:]).strip()
    if not prompt:
        print('Usage: python scripts/ollama_local.py "Summarize this Great Scale result..."', file=sys.stderr)
        return 2
    base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    model = os.environ.get("OLLAMA_MODEL", "llama3.2")
    data = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    request = Request(base + "/api/generate", data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=180) as response:
            result = json.loads(response.read().decode())
        print(result.get("response", ""))
        return 0
    except HTTPError as exc:
        print(f"Ollama returned HTTP {exc.code}; verify the local model and server.", file=sys.stderr)
    except (URLError, TimeoutError):
        print("Cannot reach local Ollama. Start it and pull the configured model first.", file=sys.stderr)
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
