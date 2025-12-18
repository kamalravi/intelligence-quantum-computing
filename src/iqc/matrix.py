# src/iqc/matrix.py

from pathlib import Path
from typing import List

import streamlit as st

from iqc.core import (
    PROVIDER_BY_NAME,
    resolve_api_key,
    post_openai_compatible,
    post_cohere_chat,
    post_gemini_responses,
    export_interaction_jsonl_row,
    get_export_dir,
)



def matrix_selection_section() -> tuple[list[int], list[int]]:
    st.markdown("### 🔢 Select questions and models")

    selected_q_idxs: list[int] = []
    selected_model_idxs: list[int] = []

    # ----- Questions -----
    q_bank = st.session_state.get("q_bank", [])
    if q_bank:
        q_labels = [
            f"{(q['id'] or str(i+1))}: "
            f"{q['text'][:60]}{'…' if len(q['text']) > 60 else ''}"
            for i, q in enumerate(q_bank)
        ]

        q_preset = st.radio(
            "Question selection",
            options=["Custom", "All", "None"],
            index=0,
            horizontal=True,
            key="q_preset",
        )

        current_q_selection = st.session_state.get("matrix_q_selection", [])

        if q_preset == "All":
            current_q_selection = q_labels
        elif q_preset == "None":
            current_q_selection = []

        st.session_state["matrix_q_selection"] = current_q_selection

        selected_q_labels = st.multiselect(
            "Select questions",
            options=q_labels,
            default=current_q_selection,
            help="Choose one or more questions (or use the preset above).",
            key="matrix_q_selection",
        )

        label_to_idx = {lbl: i for i, lbl in enumerate(q_labels)}
        selected_q_idxs = [label_to_idx[lbl] for lbl in selected_q_labels]
    else:
        st.info("Upload questions.yaml to enable question selection.")

    # ----- Models -----
    yaml_entries = st.session_state.get("yaml_entries", [])
    if yaml_entries:
        m_labels = [
            f"{i+1}. {row.get('name','?')} — {row.get('model','?')}"
            for i, row in enumerate(yaml_entries)
        ]

        m_preset = st.radio(
            "Model selection",
            options=["Custom", "All", "None"],
            index=0,
            horizontal=True,
            key="m_preset",
        )

        current_m_selection = st.session_state.get("matrix_m_selection", [])

        if m_preset == "All":
            current_m_selection = m_labels
        elif m_preset == "None":
            current_m_selection = []

        st.session_state["matrix_m_selection"] = current_m_selection

        selected_m_labels = st.multiselect(
            "Select models (from providers.yaml)",
            options=m_labels,
            default=current_m_selection,
            help="Choose one or more provider/model configs.",
            key="matrix_m_selection",
        )

        m_label_to_idx = {lbl: i for i, lbl in enumerate(m_labels)}
        selected_model_idxs = [m_label_to_idx[lbl] for lbl in selected_m_labels]
    else:
        st.info("Upload providers.yaml to enable model selection.")

    st.caption(
        f"Matrix selection: {len(selected_q_idxs)} question(s) × "
        f"{len(selected_model_idxs)} model(s) = "
        f"{len(selected_q_idxs) * len(selected_model_idxs) if selected_q_idxs and selected_model_idxs else 0} runs."
    )

    return selected_q_idxs, selected_model_idxs


def export_directory_section() -> Path:
    st.markdown("### 📁 Export Directory")

    default_export_path = st.session_state.get("export_dir", "atl_data/exports")

    export_dir_input = st.text_input(
        "Choose or type an export directory:",
        value=default_export_path,
        help="All JSONL outputs will be saved here.",
    )

    export_path = Path(export_dir_input).expanduser()
    try:
        export_path.mkdir(parents=True, exist_ok=True)
        st.session_state["export_dir"] = str(export_path)
        st.success(f"Export directory: {export_path}")
    except Exception as e:  # noqa: BLE001
        st.error(f"Failed to create directory: {e}")

    return export_path


def run_matrix_section(
    selected_q_idxs: List[int],
    selected_model_idxs: List[int],
) -> None:
    run_matrix_btn = st.button(
        "Benchmark Matrix (Questions × Models)",
        type="primary",
        key="run_matrix_btn",
    )

    if not run_matrix_btn:
        return

    if not selected_q_idxs:
        st.error("Please select at least one question.")
        return
    if not selected_model_idxs:
        st.error("Please select at least one model.")
        return

    entries = st.session_state.get("yaml_entries", [])
    q_bank = st.session_state.get("q_bank", [])
    if not entries:
        st.error("No provider entries loaded.")
        return

    import time as _time

    total_runs = len(selected_q_idxs) * len(selected_model_idxs)
    st.info(
        f"Running matrix: {len(selected_q_idxs)} question(s) × "
        f"{len(selected_model_idxs)} model(s) = {total_runs} calls."
    )

    progress = st.progress(0.0)
    progress_text = st.empty()
    run_count = 0
    progress_text.markdown(f"**Progress:** 0.0% (0 / {total_runs})")

    if "current_run_id" not in st.session_state:
        st.session_state["current_run_id"] = __import__("uuid").uuid4().hex

    system_prompt = st.session_state.get("system_prompt", "")
    for qi in selected_q_idxs:
        q_obj = q_bank[qi]
        question_id = q_obj.get("id")
        question_text = q_obj.get("text", "").strip()

        for mi in selected_model_idxs:
            row = entries[mi]
            name = row.get("name")
            entry_model = row.get("model")
            entry_key = row.get("api_key")
            temp = row.get("temperature", 0.7)
            mtoks = row.get("max_tokens", 512)

            if not name or not entry_model:
                continue
            if name not in PROVIDER_BY_NAME:
                st.warning(f"Unknown provider in YAML: {name}. Skipping.")
                continue
            p = PROVIDER_BY_NAME[name]
            resolved_key = resolve_api_key(entry_key)

            if not resolved_key and p.kind != "custom" and p.name != "Ollama (local)":
                st.warning(f"Missing API key for {name}. Skipping.")
                continue

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question_text},
            ]

            t0 = _time.perf_counter()
            content = ""
            status = "ok"
            error_message = None

            try:
                if p.kind == "openai_compatible":
                    path_override = None
                    extra_headers = {}
                    if p.name == "GitHub Models":
                        extra_headers["Accept"] = "application/json"
                    content = post_openai_compatible(
                        provider=p,
                        api_key=resolved_key or "",
                        model=entry_model,
                        messages=messages,
                        temperature=temp,
                        max_tokens=mtoks,
                        extra_headers=extra_headers,
                        path_override=path_override,
                    )
                elif p.name.startswith("Cohere"):
                    content = post_cohere_chat(
                        resolved_key or "",
                        entry_model,
                        messages,
                        temp,
                        mtoks,
                    )
                elif p.name.startswith("Google AI Studio"):
                    content = post_gemini_responses(
                        resolved_key or "",
                        entry_model,
                        messages,
                        temp,
                        mtoks,
                    )
                else:
                    raise RuntimeError("Unsupported provider configuration.")
            except Exception as e:  # noqa: BLE001
                status = "error"
                error_message = str(e)
                content = ""

            latency_ms = (_time.perf_counter() - t0) * 1000.0

            export_interaction_jsonl_row(
                provider=name,
                model=entry_model,
                temperature=temp,
                max_tokens=mtoks,
                system_prompt=system_prompt,
                question_id=question_id,
                question_text=question_text,
                response_text=content,
                status=status,
                error_message=error_message,
                latency_ms=latency_ms,
                token_input=None,
                token_output=None,
                experiment_tag=st.session_state.get("experiment_tag"),
            )

            run_count += 1
            frac = run_count / total_runs
            pct = frac * 100.0
            progress.progress(frac)
            progress_text.markdown(
                f"**Progress:** {pct:.1f}% ({run_count} / {total_runs})"
            )

    st.success(
        f"Finished matrix run: {run_count} calls.\n\n"
        f"JSONL files saved in:\n{get_export_dir().resolve()}"
    )
