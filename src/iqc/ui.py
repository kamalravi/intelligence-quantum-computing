# src/iqc/ui.py

import streamlit as st

APP_TITLE = "Quantum Computing Benchmark"


def inject_css(high_contrast: bool = False) -> None:
    primary = "#2563eb"
    primary_hover = "#1d4ed8"
    accent = "#ec4899"
    border = "#94a3b8"
    surface = "rgba(255,255,255,0.92)"
    text = "#0f172a"
    shadow = "0 14px 40px rgba(15, 23, 42, 0.18)"
    border_thick = "2px" if high_contrast else "1.5px"

    st.markdown(
        f"""
    <style>
    :root {{
        --primary:{primary};
        --primary-hover:{primary_hover};
        --accent:{accent};
        --border:{border};
        --surface:{surface};
        --text:{text};
        --radius:16px;
        --shadow:{shadow};
        --border-thick:{border_thick};
    }}

    html, body, .stApp, .main, .stMarkdown {{
        font-size: 0.9rem !important;
        line-height: 1.1 !important;
    }}

    html, body, [data-testid="stAppViewContainer"] {{
        width: 6.5in;
        max-width: 6.5in;
        height: 8.5in;
        max-height: 8.5in;
        margin: 0 auto;
        box-sizing: border-box;
        overflow: hidden;
        background: radial-gradient(circle at top left, #fdf2ff 0, #eff6ff 45%, #ecfeff 100%);
    }}

    .main .block-container {{
        padding: 0.01rem 0.18rem 0.01rem 0.18rem;
        box-sizing: border-box;
        max-height: 8.5in;
        overflow-y: auto;
    }}

    div[data-testid="stVerticalBlock"] {{
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }}

    div[data-testid="stMarkdown"] h3 {{
        margin-top: 0.05rem !important;
        margin-bottom: 0.05rem !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }}

    div[data-testid="stCaptionContainer"] {{
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }}

    div[data-testid="stMarkdown"] h3 {{
        margin-top: 0.02rem !important;
    }}

    div[data-testid="stMarkdown"] {{
        margin-top: 0.02rem !important;
        margin-bottom: 0.02rem !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }}

    div[data-testid="column"] > div {{
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }}

    div[data-testid="stMarkdown"] {{
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }}

    .atl-hero {{
        background: linear-gradient(135deg, rgba(59,130,246,0.96), rgba(236,72,153,0.96));
        color: #f9fafb;
        border-radius: 14px;
        padding: 0 6px;
        box-shadow: {shadow};
        border: {border_thick} solid rgba(15,23,42,0.10);
        margin-top: 0;
        margin-bottom: 0.02rem;
        display: inline-block;
    }}

    .atl-hero h2 {{
        margin: 0;
        font-weight: 700;
        letter-spacing: -0.02em;
        font-size: 0.9rem !important;
        line-height: 1.05;
    }}

    .stMarkdown h3,
    .stMarkdown h4 {{
        margin-top: 0.01rem !important;
        margin-bottom: 0.005rem !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        line-height: 1.1;
    }}

    div[data-testid="stExpander"] {{
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }}

    div[data-testid="stExpander"] > details > summary {{
        padding-top: 0.01rem !important;
        padding-bottom: 0.01rem !important;
        margin: 0 !important;
        font-size: 0.9rem !important;
        line-height: 1.1 !important;
    }}

    div[data-testid="stExpander"] details > div {{
        padding-top: 0.01rem !important;
        padding-bottom: 0.01rem !important;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }}

    [data-testid="stFileUploaderLabel"],
    div[data-testid="stFileUploader"] > label {{
        margin-top: 0 !important;
        margin-bottom: 0.01rem !important;
        font-size: 0.9rem !important;
        line-height: 1.1 !important;
    }}

    div[data-testid="stFileUploader"] {{
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }}

    [data-testid="stFileUploaderDropzone"] {{
        border-radius: 8px !important;
        border: 1.1px dashed rgba(148,163,184,0.9) !important;
        background: rgba(255,255,255,0.94) !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }}

    [data-testid="stFileUploaderDropzone"] > div {{
        padding-top: 0.08rem !important;
        padding-bottom: 0.08rem !important;
    }}

    [data-testid="stFileUploaderDropzone"] * {{
        font-size: 0.9rem !important;
        line-height: 1.1 !important;
    }}

    [data-testid="stFileUploaderDropzone"] p,
    [data-testid="stFileUploaderDropzone"] small,
    [data-testid="stFileUploaderDropzone"] span {{
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }}

    div[data-testid="stCaptionContainer"] {{
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        font-size: 0.9rem !important;
    }}

    div.stButton {{
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }}

    .stButton > button {{
        background: var(--primary) !important;
        color: #f9fafb !important;
        border: 0 !important;
        border-radius: 999px !important;
        padding: 0.08rem 0.38rem !important;
        box-shadow: 0 2px 5px rgba(37,99,235,0.24) !important;
        font-weight: 600 !important;
        letter-spacing: 0.01em;
        font-size: 0.9rem !important;
        line-height: 1.1 !important;
    }}

    .stButton > button:hover {{
        background: var(--primary-hover) !important;
        transform: translateY(-1px);
    }}

    [data-testid="stDownloadButton"] > button {{
        background: var(--primary) !important;
        color: #f9fafb !important;
        border: 0 !important;
        border-radius: 999px !important;
        padding: 0.08rem 0.38rem !important;
        box-shadow: 0 2px 5px rgba(37,99,235,0.24) !important;
        font-weight: 600 !important;
        letter-spacing: 0.01em;
        font-size: 0.9rem !important;
        line-height: 1.1 !important;
    }}

    [data-testid="stDownloadButton"] > button:hover {{
        background: var(--primary-hover) !important;
        transform: translateY(-1px);
    }}

    textarea, input[type="text"], input[type="password"], 
    .stSelectbox div[data-baseweb="select"] > div,
    .stMultiSelect div[data-baseweb="select"] > div {{
        border-radius: 8px !important;
        border: {border_thick} solid rgba(148,163,184,0.9) !important;
        background: rgba(248,250,252,0.9) !important;
        color: {text} !important;
        box-shadow: 0 0 0 1px rgba(255,255,255,0.8);
        font-size: 0.9rem !important;
        min-height: 1.35rem;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0.02rem !important;
        padding-bottom: 0.02rem !important;
    }}

    div[data-testid="stDataFrame"] {{
        border-radius: 8px;
        border: {border_thick} solid rgba(148,163,184,0.9);
        overflow: hidden;
        box-shadow: 0 6px 18px rgba(15,23,42,0.12);
        background: #f8fafc;
        margin-top: 0.01rem !important;
        margin-bottom: 0.01rem !important;
        font-size: 0.9rem !important;
    }}

    hr {{
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(148,163,184,0.9), transparent);
        margin: 0.04rem 0 0.04rem 0;
    }}

    div[data-testid="stMultiSelect"] > label,
    div[data-testid="stSelectbox"] > label {{
        margin-top: 0 !important;
        margin-bottom: 0.01rem !important;
        font-size: 0.9rem !important;
        line-height: 1.1 !important;
    }}

    div[data-baseweb="select"] > div {{
        min-height: 1.15rem !important;
        padding-top: 0.02rem !important;
        padding-bottom: 0.02rem !important;
        padding-left: 0.25rem !important;
        padding-right: 0.25rem !important;
    }}

    div[data-baseweb="tag"],
    div[data-baseweb="tag"] * {{
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        font-size: 0.9rem !important;
        line-height: 1.1 !important;
    }}

    div[data-baseweb="tag"] > div {{
        margin: 0 !important;
        padding: 0 0.18rem !important;
    }}

    div[data-baseweb="select"] [class*="placeholder"],
    div[data-baseweb="select"] span {{
        font-size: 0.9rem !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        line-height: 1.1 !important;
    }}

    div.stButton {{
        margin-top: 0 !important;
        padding-top: 0 !important;
    }}

    div.stButton > button {{
        margin-top: 0 !important;
        padding-top: 0.0rem !important;
    }}

    div[data-testid="stVerticalBlock"]:has(div.stButton) {{
        margin-top: 0 !important;
        padding-top: 0 !important;
    }}

    div[data-testid="stCaptionContainer"] + div[data-testid="stVerticalBlock"] {{
        margin-top: 0 !important;
        padding-top: 0 !important;
    }}

    div[data-testid="stVerticalBlock"]:has(div.stButton) {{
        margin-top: -0.28rem !important;
        padding-top: 0 !important;
    }}

    div.stButton {{
        margin-top: -0.20rem !important;
        padding-top: 0 !important;
    }}

    div.stButton > button {{
        margin-top: -0.35rem !important;
    }}

    div[data-testid="stCaptionContainer"] + div[data-testid="stVerticalBlock"] {{
        margin-top: -0.158rem !important;
    }}

    .atl-hero {{
        margin-left: auto !important;
        margin-right: auto !important;
        text-align: center !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }}

    .atl-hero h2 {{
        text-align: center !important;
        width: 100% !important;
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )


def setup_page() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="⚛️", layout="centered")

    with st.sidebar:
        hc = st.toggle(
            "High-contrast mode",
            value=False,
            help="Thicker borders / higher contrast inputs.",
        )
    inject_css(high_contrast=hc)

    st.markdown(
        """
        <div class="atl-hero">
          <h2>⚛️ Quantum Computing Benchmark</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
