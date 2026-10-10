# Great Scale

Research and telemetry harness for the Great Scale mathematical descent. This repository will add reproducible model tests, scheduled Tavily research/crawl, secret-safe configuration, and an optional local Ollama adapter.

## Safety
- Never commit API keys or `.env` files.
- Scheduled cloud research uses `TAVILY_API_KEY` from GitHub Actions secrets.
- Ollama is local by default; GitHub-hosted runners cannot reach your Mac unless you deliberately configure a self-hosted runner.
- Research outputs are evidence records, not automatic validation of scientific claims.
