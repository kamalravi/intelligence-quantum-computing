# IQC — Intelligence Quantum Computing (Benchmark UI)

A compact Streamlit UI to **benchmark multiple AI assistants / LLM providers** across a shared question set, export per-call JSONL logs, and run quick preflight checks on provider/model configs.

> Current UI title targets “Benchmarking AI for quantum computing”, but the tool is designed to be **general-purpose**.

## What it does

- Load `providers.yaml` (provider + model + key + sampling params)
- Load `questions.yaml` (question bank)
- Select **Questions × Models** (with All/None presets)
- Run the matrix and export **one JSONL file per call**
- Preflight “Check APIs/Models” + download CSV report

## Repo layout

```
.
├─ configs/
│  ├─ providers.example.yaml
│  └─ questions.example.yaml
├─ src/
│  └─ iqc/
│     ├─ __init__.py
│     ├─ app.py              # Streamlit entrypoint
│     ├─ core.py             # providers + HTTP logic + export helpers
│     └─ ui.py               # CSS/theme + UI helpers
├─ atl_data/                 # (optional default) local output folder (gitignored)
├─ .streamlit/
│  └─ config.toml
├─ pyproject.toml
├─ requirements.txt
└─ README.md
```

## Quickstart

### 1) Create & activate an env
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Run the UI
From the repo root:
```bash
streamlit run src/iqc/app.py
```

### 3) Provide YAML configs
Use the examples in `configs/`:
- `configs/providers.example.yaml`
- `configs/questions.example.yaml`

## Outputs

By default, outputs go to `atl_data/exports/` (or the directory you set in the UI).
Each call writes a JSONL row with:
- run_id, timestamp_utc
- provider, model, temperature, max_tokens
- system prompt (and sha256)
- question_id, question_text
- response_text, status, error_message
- latency_ms

## Notes

- API keys can be literal in YAML or `${ENV_VAR}` to read from environment.
- Local `Ollama (local)` can run without an API key.

## License

See `LICENSE`.
