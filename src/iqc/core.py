# src/iqc/core.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
import os
import json
import re
import time
import hashlib

import requests
import yaml
import streamlit as st


# ---------- Provider registry ----------

@dataclass
class Provider:
    name: str
    kind: str                  # "openai_compatible" or "custom"
    base_url: Optional[str] = None
    auth_header: str = "Authorization"
    bearer_prefix: str = "Bearer "
    notes: str = ""


PROVIDERS: List[Provider] = [
    Provider(
        "OpenRouter",
        "openai_compatible",
        "https://openrouter.ai/api",
        notes="Use 'openrouter/auto' or a specific route.",
    ),
    Provider(
        "Groq",
        "openai_compatible",
        "https://api.groq.com/openai",
        notes="Common: 'llama-3.3-70b-versatile', etc.",
    ),
    Provider(
        "Mistral (La Plateforme)",
        "openai_compatible",
        "https://api.mistral.ai",
        notes="E.g., 'mistral-small-latest'.",
    ),
    Provider(
        "Cerebras",
        "openai_compatible",
        "https://api.cerebras.ai",
        notes="OpenAI-compatible chat completions.",
    ),
    Provider(
        "NVIDIA NIM",
        "openai_compatible",
        "https://integrate.api.nvidia.com",
        notes="Model names vary by NIM.",
    ),
    Provider(
        "GitHub Models",
        "openai_compatible",
        "https://models.api.github.com",
        notes="Use GitHub token.",
    ),
    Provider(
        "Vercel AI Gateway (Custom)",
        "openai_compatible",
        "",
        notes="If used, set base_url in YAML.",
    ),
    Provider(
        "Cloudflare Workers AI (Shim)",
        "openai_compatible",
        "https://api.cloudflare.com/client/v4",
        notes="Account ID required; uses /ai/v1 shim.",
    ),
    Provider(
        "Cohere (Chat)",
        "custom",
        "https://api.cohere.com",
        notes="E.g., 'command-a-03-2025'.",
    ),
    Provider(
        "Google AI Studio (Gemini)",
        "custom",
        "https://generativelanguage.googleapis.com",
        notes="E.g., 'gemini-1.5-flash'.",
    ),
    Provider(
        "Ollama (local)",
        "openai_compatible",
        "http://localhost:11434",
        notes="Local model via Ollama; e.g., 'llama3.2', 'mistral', etc.",
    ),
]

PROVIDER_BY_NAME: Dict[str, Provider] = {p.name: p for p in PROVIDERS}


# ---------- YAML helpers ----------

def _sanitize_yaml(raw: str) -> str:
    lines = raw.strip().splitlines()
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
    if lines and lines[0].strip() == '"""':
        lines = lines[1:]
    if lines and lines[-1].strip() == '"""':
        lines = lines[:-1]
    return "\n".join(lines)


def sanitize_providers_yaml(raw: str) -> str:
    return _sanitize_yaml(raw)


def sanitize_questions_yaml(raw: str) -> str:
    return _sanitize_yaml(raw)


def extract_questions(yaml_obj: Any) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    if isinstance(yaml_obj, dict):
        if "questions" in yaml_obj and isinstance(yaml_obj["questions"], list):
            for q in yaml_obj["questions"]:
                if isinstance(q, dict) and "text" in q:
                    out.append(
                        {
                            "id": (str(q.get("id", "")).strip() or None),
                            "text": str(q["text"]),
                        }
                    )
        if "sets" in yaml_obj and isinstance(yaml_obj["sets"], list):
            for s in yaml_obj["sets"]:
                qs = s.get("questions", [])
                if isinstance(qs, list):
                    for q in qs:
                        if isinstance(q, dict) and "text" in q:
                            out.append(
                                {
                                    "id": (str(q.get("id", "")).strip() or None),
                                    "text": str(q["text"]),
                                }
                            )

    seen = set()
    uniq: list[dict[str, str]] = []
    for q in out:
        key = (q.get("id"), q.get("text"))
        if key not in seen:
            seen.add(key)
            uniq.append(q)
    return uniq


# ---------- API key + preflight ----------

def resolve_api_key(entry_key: Optional[str]) -> Optional[str]:
    """
    For simplicity, require keys in YAML.
    If entry_key is ${{ENV}}, expand from environment.
    """
    if not entry_key:
        return None
    ek = entry_key.strip()
    if ek.startswith("${") and ek.endswith("}"):
        env_name = ek[2:-1]
        return os.environ.get(env_name)
    return ek


def minimal_test_call(entry_name: str, entry_model: str, api_key: Optional[str]) -> None:
    if entry_name not in PROVIDER_BY_NAME:
        raise RuntimeError(f"Unknown provider name: {entry_name}")
    p = PROVIDER_BY_NAME[entry_name]

    if not api_key and p.kind != "custom" and p.name != "Ollama (local)":
        raise RuntimeError("Missing API key.")

    messages = [
        {"role": "system", "content": "ping"},
        {"role": "user", "content": "ping"},
    ]

    if p.kind == "openai_compatible":
        if not p.base_url:
            raise RuntimeError("Missing base_url for provider.")
        url = p.base_url.rstrip("/") + "/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            p.auth_header: f"{p.bearer_prefix}{api_key}",
        }
        payload = {
            "model": entry_model,
            "messages": messages,
            "max_tokens": 1,
            "temperature": 0.0,
            "stream": False,
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=25)
        if resp.status_code >= 400:
            raise RuntimeError(f"{p.name} {resp.status_code}: {resp.text[:200]}")
        _ = resp.json()
    elif p.name.startswith("Cohere"):
        url = "https://api.cohere.com/v1/chat"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        payload = {
            "model": entry_model,
            "message": "ping",
            "max_tokens": 1,
            "temperature": 0.0,
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=25)
        if resp.status_code >= 400:
            raise RuntimeError(f"Cohere {resp.status_code}: {resp.text[:200]}")
        _ = resp.json()
    elif p.name.startswith("Google AI Studio"):
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{entry_model}:generateContent?key={api_key}"
        )
        payload = {
            "contents": [{"role": "user", "parts": [{"text": "ping"}]}],
            "generationConfig": {"maxOutputTokens": 1},
        }
        headers = {"Content-Type": "application/json"}
        resp = requests.post(url, headers=headers, json=payload, timeout=25)
        if resp.status_code >= 400:
            raise RuntimeError(f"Gemini {resp.status_code}: {resp.text[:200]}")
        _ = resp.json()
    else:
        raise RuntimeError("Unsupported provider configuration for preflight test.")


def run_preflight(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for row in entries:
        name = row.get("name")
        model = row.get("model")
        entry_key = row.get("api_key")
        t = row.get("temperature")
        mt = row.get("max_tokens")

        if not name or not model:
            results.append(
                {
                    "provider": name or "<missing>",
                    "model": model or "<missing>",
                    "status": "❌",
                    "temperature": t,
                    "max_tokens": mt,
                    "detail": "name/model required",
                }
            )
            continue

        try:
            resolved_key = resolve_api_key(entry_key)
            minimal_test_call(name, model, resolved_key)
            results.append(
                {
                    "provider": name,
                    "model": model,
                    "status": "✅ OK",
                    "temperature": t,
                    "max_tokens": mt,
                    "detail": "",
                }
            )
        except Exception as e:  # noqa: BLE001
            results.append(
                {
                    "provider": name,
                    "model": model,
                    "status": "❌ Fail",
                    "temperature": t,
                    "max_tokens": mt,
                    "detail": str(e),
                }
            )
    return results


# ---------- Networking helpers for benchmark loop ----------

def post_openai_compatible(
    provider: Provider,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
    extra_headers: Optional[dict[str, str]] = None,
    path_override: Optional[str] = None,
) -> str:
    if not provider.base_url:
        raise ValueError("Base URL is required for this provider.")
    url = provider.base_url.rstrip("/") + (
        "/v1/chat/completions" if not path_override else path_override
    )

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers[provider.auth_header] = f"{provider.bearer_prefix}{api_key}"
    if extra_headers:
        headers.update(extra_headers)

    payload = {
        "model": model,
        "messages": messages,
        "temperature": float(temperature),
        "max_tokens": int(max_tokens),
        "stream": False,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code >= 400:
        raise RuntimeError(f"{provider.name} error {resp.status_code}: {resp.text}")
    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except Exception:  # noqa: BLE001
        return json.dumps(data, indent=2)


def post_cohere_chat(
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
) -> str:
    url = "https://api.cohere.com/v1/chat"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    user_turns = [m["content"] for m in messages if m["role"] == "user"]
    prompt = "\n\n".join(user_turns) if user_turns else messages[-1]["content"]
    payload = {
        "model": model,
        "message": prompt,
        "temperature": float(temperature),
        "max_tokens": int(max_tokens),
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code >= 400:
        raise RuntimeError(f"Cohere error {resp.status_code}: {resp.text}")
    data = resp.json()
    return data.get("text") or data.get("message", {}).get(
        "content", json.dumps(data, indent=2)
    )


def post_gemini_responses(
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
) -> str:
    contents = []
    for m in messages:
        role = "user" if m["role"] != "assistant" else "model"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": float(temperature),
            "maxOutputTokens": int(max_tokens),
        },
    }
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code >= 400:
        raise RuntimeError(f"Google AI Studio error {resp.status_code}: {resp.text}")
    data = resp.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:  # noqa: BLE001
        return json.dumps(data, indent=2)


# ---------- JSONL export helpers ----------

def _slug(s: str, maxlen: int = 40) -> str:
    s = re.sub(r"[^\w\-]+", "-", s.strip())
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return (s[:maxlen] or "model").lower()


def _hash_text(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()[:12]


def get_export_dir() -> Path:
    default = "atl_data/exports"
    export_dir = Path(st.session_state.get("export_dir", default)).expanduser()
    export_dir.mkdir(parents=True, exist_ok=True)
    st.session_state["export_dir"] = str(export_dir)
    return export_dir


def export_interaction_jsonl_row(
    *,
    provider: str,
    model: str,
    temperature: float,
    max_tokens: int,
    system_prompt: str,
    question_id: Optional[str],
    question_text: str,
    response_text: str,
    status: str,
    error_message: Optional[str],
    latency_ms: Optional[float],
    token_input: Optional[int] = None,
    token_output: Optional[int] = None,
    experiment_tag: Optional[str] = None,
) -> Path:
    export_dir = get_export_dir()

    ts = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
    model_tag = _slug(model)
    qtag = question_id or "Q"
    fname = f"{ts}-{model_tag}-{qtag}.jsonl"
    fpath = export_dir / fname

    if "current_run_id" not in st.session_state:
        st.session_state["current_run_id"] = os.getenv("RUN_ID", "") or str(
            os.urandom(8).hex()
        )

    row = {
        "run_id": st.session_state["current_run_id"],
        "timestamp_utc": ts,
        "provider": provider,
        "model": model,
        "temperature": float(temperature),
        "max_tokens": int(max_tokens),
        "system_prompt_sha256": _hash_text(system_prompt),
        "system_prompt": system_prompt,
        "question_id": question_id,
        "question_text": question_text,
        "response_text": response_text,
        "status": status,
        "error_message": error_message,
        "latency_ms": None if latency_ms is None else float(latency_ms),
        "token_input": token_input,
        "token_output": token_output,
        "experiment_tag": experiment_tag,
    }

    with fpath.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

    return fpath
