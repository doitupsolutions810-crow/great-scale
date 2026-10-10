# Great Scale setup

## Daily Tavily research

1. In GitHub, open **Settings → Secrets and variables → Actions**.
2. Add repository secret `TAVILY_API_KEY`. The value is only consumed by the scheduled workflow and is never written to a source file.
3. Open **Actions → Daily Tavily Research → Run workflow** to launch a manual run. Scheduled runs occur daily at 12:17 UTC.
4. Download the `great-scale-research-*` artifact from the successful run. The artifact is an evidence snapshot; validate sources and claims independently.

If the research job fails, inspect its step logs. The script deliberately avoids printing credentials and reports only a generic HTTP status for API errors.

## Local Ollama

Install Ollama on the machine that should run inference, start its local service, and pull a model, for example `ollama pull llama3.2`. Copy `.env.example` to `.env` and adjust `OLLAMA_MODEL` if needed. Export the desired variables into the shell, then run:

```sh
python scripts/ollama_local.py "Summarize the Great Scale phase-aware invariant hypothesis and list falsifiable tests."
```

The adapter calls the local Ollama HTTP endpoint. A GitHub-hosted Actions runner cannot reach your local Mac by default; use the local script manually or configure a secured self-hosted runner if cloud automation is required.

## Tests

```sh
python -m unittest discover -s tests -v
```
