# src/iqc/config_ui.py

from io import StringIO
from typing import Any

import streamlit as st
import yaml

from iqc.core import (
    sanitize_providers_yaml,
    sanitize_questions_yaml,
    extract_questions,
    run_preflight,
)


def providers_config_section() -> None:
    st.markdown("### 🧩 Provider Configuration (`providers.yaml`)")

    prov_file = st.file_uploader(
        "Upload providers.yaml",
        type=["yaml", "yml"],
        key="providers_yaml_uploader",
    )

    yaml_entries: list[dict[str, Any]] = []

    if prov_file:
        try:
            raw = prov_file.read().decode("utf-8", errors="ignore")
            sanitized = sanitize_providers_yaml(raw)
            cfg = yaml.safe_load(sanitized)
            entries = cfg.get("providers", [])
            if not isinstance(entries, list):
                st.error("`providers` must be a list in the YAML.")
            else:
                yaml_entries = entries
                st.session_state["yaml_entries"] = yaml_entries
                st.success(f"Loaded {len(yaml_entries)} provider entries.")
        except Exception as e:  # noqa: BLE001
            st.error(f"Failed to parse providers YAML: {e}")

    col_check, col_dl = st.columns([1, 1])
    with col_check:
        check_btn = st.button("Check APIs/Models", key="check_btn")

    if check_btn:
        entries = st.session_state.get("yaml_entries", [])
        if not entries:
            st.error("Upload providers.yaml first.")
            return

        with st.spinner("Checking providers/models..."):
            results = run_preflight(entries)

        st.markdown("#### Preflight Results")
        st.dataframe(results, width="stretch")


        csv_io = StringIO()
        headers = [
            "provider",
            "model",
            "temperature",
            "max_tokens",
            "status",
            "detail",
        ]
        csv_io.write(",".join(headers) + "\n")
        for r in results:
            row = [
                str(r.get(h, "")).replace("\n", " ").replace(",", ";")
                for h in headers
            ]
            csv_io.write(",".join(row) + "\n")
        csv_bytes = csv_io.getvalue().encode("utf-8")

        with col_dl:
            st.download_button(
                label="Download CSV",
                data=csv_bytes,
                file_name="preflight_results.csv",
                mime="text/csv",
                key="preflight_csv_dl",
            )


def questions_config_section() -> None:
    st.markdown("### 🧩 Question Configuration (`questions.yaml`)")

    q_file = st.file_uploader(
        "Upload questions.yaml",
        type=["yaml", "yml"],
        key="questions_yaml_uploader",
    )

    if q_file:
        try:
            raw_q = q_file.read().decode("utf-8", errors="ignore")
            cfg_q = yaml.safe_load(sanitize_questions_yaml(raw_q))
            st.session_state["q_bank"] = extract_questions(cfg_q)
            st.success(f"Loaded {len(st.session_state['q_bank'])} questions.")
        except Exception as e:  # noqa: BLE001
            st.error(f"Failed to parse questions YAML: {e}")

    st.caption(f"{len(st.session_state.get('q_bank', []))} questions loaded.")
