# src/iqc/app.py

from pathlib import Path
import sys

# --- Make sure `src` is on sys.path so `import iqc` works ---
ROOT = Path(__file__).resolve().parents[2]  # go up: app.py → iqc → src → repo
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import streamlit as st

from iqc.ui import setup_page
from iqc.config_ui import (
    providers_config_section,
    questions_config_section,
)
from iqc.matrix import ( 
    matrix_selection_section,
    export_directory_section,
    run_matrix_section,
)


def system_prompt_section() -> None:
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = (
            "You are a transparent, careful assistant. "
            "If uncertain, say so explicitly; avoid speculation; "
            "use cautious, calibrated language."
        )
    if "experiment_tag" not in st.session_state:
        st.session_state["experiment_tag"] = None
    if "q_bank" not in st.session_state:
        st.session_state["q_bank"] = []
    if "yaml_entries" not in st.session_state:
        st.session_state["yaml_entries"] = []

    with st.expander("System Prompt (shared across all calls)", expanded=False):
        st.session_state.system_prompt = st.text_area(
            "System prompt",  # ✅ non-empty label
            value=st.session_state.system_prompt,
            height=60,
            label_visibility="collapsed",  # hides it visually
        )



def main() -> None:
    setup_page()
    system_prompt_section()

    providers_config_section()
    questions_config_section()

    selected_q_idxs, selected_model_idxs = matrix_selection_section()
    export_directory_section()
    run_matrix_section(selected_q_idxs, selected_model_idxs)


if __name__ == "__main__":
    main()
