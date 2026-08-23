"""
Google Query Fan-Out Extractor
Extract hidden sub-queries that Google AI Overviews run internally.
Built with Streamlit + Google Gemini API + OpenAI ChatGPT + Anthropic Claude.
"""

import streamlit as st
import pandas as pd
import re
import time

# ─── Page Configuration ───
st.set_page_config(
    page_title="Query Fan-Out Extractor — SEO Tool",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Premium Dark Mode CSS ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Global Reset ── */
*, *::before, *::after { font-family: 'Inter', sans-serif !important; }

.stApp {
    background: linear-gradient(160deg, #07071a 0%, #0c0f1f 30%, #0f1629 60%, #111827 100%);
    color: #e2e8f0;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(12,18,38,0.99) 0%, rgba(8,8,26,0.99) 100%);
    border-right: 1px solid rgba(99,102,241,0.12);
    backdrop-filter: blur(24px);
}
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #a5b4fc;
    font-weight: 700;
    letter-spacing: -0.02em;
    font-size: 1.1rem;
}

/* ── Sidebar Provider Badge ── */
.provider-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    border-radius: 8px;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.5rem;
}
.provider-gemini { background: rgba(66,133,244,0.15); color: #93bbfc; border: 1px solid rgba(66,133,244,0.25); }
.provider-openai { background: rgba(16,163,127,0.12); color: #6ee7b7; border: 1px solid rgba(16,163,127,0.2); }
.provider-claude { background: rgba(217,119,87,0.12); color: #f0a882; border: 1px solid rgba(217,119,87,0.2); }

/* ── Hero Header ── */
.hero-container {
    background: linear-gradient(135deg, rgba(99,102,241,0.1) 0%, rgba(168,85,247,0.06) 50%, rgba(59,130,246,0.04) 100%);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 24px;
    padding: 2.8rem 2.2rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(20px);
}
.hero-container::before {
    content: '';
    position: absolute;
    top: -60%;
    left: -30%;
    width: 160%;
    height: 160%;
    background: radial-gradient(circle at 25% 40%, rgba(99,102,241,0.08) 0%, transparent 45%),
                radial-gradient(circle at 75% 70%, rgba(168,85,247,0.05) 0%, transparent 40%),
                radial-gradient(circle at 50% 10%, rgba(59,130,246,0.04) 0%, transparent 35%);
    animation: heroGlow 10s ease-in-out infinite alternate;
    pointer-events: none;
}
@keyframes heroGlow {
    0% { transform: translate(0, 0) rotate(0deg) scale(1); }
    50% { transform: translate(-3%, 3%) rotate(1.5deg) scale(1.02); }
    100% { transform: translate(-5%, 5%) rotate(3deg) scale(1); }
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: linear-gradient(135deg, rgba(99,102,241,0.2), rgba(168,85,247,0.15));
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 50px;
    padding: 7px 18px;
    font-size: 0.7rem;
    font-weight: 700;
    color: #a5b4fc;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 1.2rem;
    animation: badgePulse 4s ease-in-out infinite;
    position: relative;
    z-index: 1;
}
@keyframes badgePulse {
    0%, 100% { box-shadow: 0 0 12px rgba(99,102,241,0.15); }
    50% { box-shadow: 0 0 28px rgba(99,102,241,0.3); }
}
.hero-title {
    font-size: 2.4rem;
    font-weight: 900;
    background: linear-gradient(135deg, #f1f5f9 0%, #a5b4fc 40%, #c084fc 70%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.15;
    margin-bottom: 0.6rem;
    position: relative;
    z-index: 1;
    letter-spacing: -0.02em;
}
.hero-subtitle {
    font-size: 0.95rem;
    color: #94a3b8;
    font-weight: 400;
    line-height: 1.7;
    position: relative;
    z-index: 1;
    max-width: 620px;
}

/* ── Search Box ── */
.search-container {
    background: linear-gradient(135deg, rgba(30,30,60,0.3), rgba(20,20,50,0.4));
    border: 1px solid rgba(99,102,241,0.1);
    border-radius: 18px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 2rem;
    backdrop-filter: blur(12px);
}

/* ── Metric Cards ── */
.metric-card {
    background: linear-gradient(145deg, rgba(25,25,55,0.7), rgba(15,15,40,0.9));
    border: 1px solid rgba(99,102,241,0.12);
    border-radius: 18px;
    padding: 1.6rem 1.2rem;
    text-align: center;
    backdrop-filter: blur(16px);
    transition: all 0.35s cubic-bezier(0.4,0,0.2,1);
    position: relative;
    overflow: hidden;
}
.metric-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #6366f1, #8b5cf6, #c084fc);
    border-radius: 18px 18px 0 0;
    opacity: 0;
    transition: opacity 0.3s ease;
}
.metric-card:hover {
    border-color: rgba(99,102,241,0.35);
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(99,102,241,0.12);
}
.metric-card:hover::after { opacity: 1; }
.metric-icon {
    font-size: 1.4rem;
    margin-bottom: 0.4rem;
    display: block;
}
.metric-value {
    font-size: 2.5rem;
    font-weight: 900;
    background: linear-gradient(135deg, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
}
.metric-label {
    font-size: 0.72rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 0.4rem;
    font-weight: 700;
}

/* ── Section Title ── */
.section-title {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 1.2rem;
}
.section-title h3 {
    color: #e2e8f0;
    font-weight: 700;
    font-size: 1.15rem;
    margin: 0;
    letter-spacing: -0.01em;
}
.section-title .title-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(99,102,241,0.3), transparent);
}

/* ── Query Row ── */
.query-row {
    display: flex;
    align-items: center;
    gap: 14px;
    background: linear-gradient(135deg, rgba(25,25,55,0.45), rgba(18,18,45,0.6));
    border: 1px solid rgba(99,102,241,0.08);
    border-radius: 14px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 0.5rem;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    animation: fadeSlideIn 0.4s ease-out forwards;
    opacity: 0;
}
.query-row:hover {
    border-color: rgba(99,102,241,0.3);
    background: linear-gradient(135deg, rgba(35,35,75,0.5), rgba(25,25,60,0.7));
    transform: translateX(6px);
    box-shadow: 0 4px 20px rgba(99,102,241,0.08);
}
@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.query-number {
    min-width: 34px;
    height: 34px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 10px;
    font-weight: 700;
    font-size: 0.8rem;
    color: white;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(99,102,241,0.25);
}
.query-text {
    color: #cbd5e1;
    font-size: 0.9rem;
    font-weight: 500;
    line-height: 1.45;
}
.query-row:hover .query-text { color: #e2e8f0; }

/* ── Success/Method Banner ── */
.method-banner {
    border-radius: 14px;
    padding: 0.9rem 1.4rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 600;
    font-size: 0.85rem;
    animation: fadeSlideIn 0.5s ease-out;
}
.method-grounding {
    background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(52,211,153,0.06));
    border: 1px solid rgba(16,185,129,0.2);
    color: #6ee7b7;
}
.method-prompt {
    background: linear-gradient(135deg, rgba(251,191,36,0.1), rgba(245,158,11,0.06));
    border: 1px solid rgba(251,191,36,0.2);
    color: #fcd34d;
}
.method-chatgpt {
    background: linear-gradient(135deg, rgba(16,163,127,0.1), rgba(16,163,127,0.05));
    border: 1px solid rgba(16,163,127,0.2);
    color: #4ade80;
}
.method-claude {
    background: linear-gradient(135deg, rgba(217,119,87,0.1), rgba(217,119,87,0.05));
    border: 1px solid rgba(217,119,87,0.2);
    color: #f0a882;
}

/* ── Buttons ── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.7rem 1.5rem !important;
    transition: all 0.3s ease !important;
    letter-spacing: 0.01em !important;
}
.stDownloadButton > button:hover {
    box-shadow: 0 6px 24px rgba(99,102,241,0.35) !important;
    transform: translateY(-2px) !important;
}
button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #7c3aed) !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
}

/* ── Input Styling ── */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: rgba(25,25,55,0.5) !important;
    border: 1px solid rgba(99,102,241,0.15) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-size: 0.9rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(99,102,241,0.45) !important;
    box-shadow: 0 0 20px rgba(99,102,241,0.12) !important;
}

/* ── Slider ── */
.stSlider > div > div > div > div {
    background: linear-gradient(90deg, #6366f1, #8b5cf6) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader,
div[data-testid="stExpander"] summary {
    background: rgba(25,25,55,0.4) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(99,102,241,0.12) !important;
    color: #a5b4fc !important;
    font-weight: 600 !important;
    overflow: visible !important;
    white-space: normal !important;
    padding: 0.9rem 1.2rem !important;
    font-size: 0.9rem !important;
}
div[data-testid="stExpander"] summary span {
    color: #a5b4fc !important;
    overflow: visible !important;
    white-space: normal !important;
}
div[data-testid="stExpander"] summary svg {
    flex-shrink: 0;
    margin-right: 8px;
}
div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
    background: rgba(15,15,40,0.5) !important;
    border: 1px solid rgba(99,102,241,0.08) !important;
    border-top: none !important;
    border-radius: 0 0 14px 14px !important;
    padding: 1rem 1.2rem !important;
}

/* ── Download Button Fix ── */
.stDownloadButton {
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
}

/* ── General Text Visibility ── */
.stMarkdown, .stMarkdown p, .stMarkdown li { color: #e2e8f0 !important; }
label, .stTextInput label, .stSelectbox label { color: #94a3b8 !important; font-weight: 600 !important; font-size: 0.82rem !important; }

/* ── Error/Warning Styling ── */
div[data-testid="stAlert"] {
    border-radius: 14px !important;
    font-size: 0.88rem !important;
    backdrop-filter: blur(8px) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.25); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(99,102,241,0.45); }

/* ── Divider ── */
.custom-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.2), transparent);
    margin: 1.5rem 0;
    border: none;
}

/* ── Footer ── */
.app-footer {
    text-align: center;
    color: #334155;
    font-size: 0.72rem;
    padding: 2rem 0 1rem;
    letter-spacing: 0.02em;
}
.app-footer a { color: #6366f1; text-decoration: none; }

/* ── Hide Streamlit Defaults (keep sidebar toggle visible) ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] {
    background: rgba(7,7,26,0.85) !important;
    backdrop-filter: blur(12px) !important;
}

/* Sidebar toggle button — just recolor, don't restructure */
button[data-testid="stSidebarCollapseButton"],
button[data-testid="collapsedControl"] {
    color: #a5b4fc !important;
}
</style>
""", unsafe_allow_html=True)


# ─── Sidebar ───
with st.sidebar:
    st.markdown("### 🔐 Configuration")
    st.markdown("---")

    ai_provider = st.selectbox(
        "AI Provider",
        options=["Google Gemini", "ChatGPT (OpenAI)", "Claude (Anthropic)"],
        index=0,
        help="Choose which AI provider to use for extraction",
    )

    if ai_provider == "Google Gemini":
        st.markdown('<div class="provider-badge provider-gemini">🔷 Google Gemini — Free Tier</div>', unsafe_allow_html=True)
        api_key = st.text_input(
            "Google Gemini API Key",
            type="password",
            placeholder="Paste your Gemini API key…",
            help="Get your free key → https://aistudio.google.com/apikey",
        )

        model_options = [
            "gemini-3.6-flash",
            "gemini-3.5-flash-lite",
            "gemini-2.5-flash",
            "gemini-2.5-pro",
        ]
        selected_model = st.selectbox(
            "Select Model",
            options=model_options,
            index=0,
            help="gemini-3.6-flash is recommended for best results",
        )
    elif ai_provider == "ChatGPT (OpenAI)":
        st.markdown('<div class="provider-badge provider-openai">🟢 OpenAI — Paid API</div>', unsafe_allow_html=True)
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-…",
            help="Get your key → https://platform.openai.com/api-keys",
        )

        model_options = [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4.1",
            "gpt-4.1-mini",
        ]
        selected_model = st.selectbox(
            "Select Model",
            options=model_options,
            index=0,
            help="gpt-4o is recommended for best results",
        )
    else:
        st.markdown('<div class="provider-badge provider-claude">🟠 Anthropic — Paid API</div>', unsafe_allow_html=True)
        api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            placeholder="sk-ant-…",
            help="Get your key → https://console.anthropic.com/settings/keys",
        )

        model_options = [
            "claude-sonnet-4-20250514",
            "claude-haiku-4-20250514",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
        ]
        selected_model = st.selectbox(
            "Select Model",
            options=model_options,
            index=0,
            help="Claude Sonnet 4 is recommended for best results",
        )

    query_count = st.slider(
        "Number of Queries",
        min_value=5,
        max_value=30,
        value=15,
        step=1,
        help="How many fan-out queries to generate",
    )

    st.markdown("---")
    st.markdown(
        """
        <div style='padding:1rem; background:linear-gradient(135deg,rgba(99,102,241,0.06),rgba(168,85,247,0.04));
                    border-radius:14px; border:1px solid rgba(99,102,241,0.1); font-size:0.78rem;
                    color:#94a3b8; line-height:1.7;'>
            <strong style='color:#a5b4fc; font-size:0.82rem;'>💡 How It Works</strong><br><br>
            <strong style='color:#93bbfc;'>Gemini</strong> — Search Grounding extracts <em>real</em>
            sub-queries. Falls back to AI prediction if quota is exceeded.<br><br>
            <strong style='color:#6ee7b7;'>ChatGPT</strong> &
            <strong style='color:#f0a882;'>Claude</strong> — AI prediction mode generates
            realistic fan-out queries.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:#334155; font-size:0.68rem; line-height:1.6;'>"
        "Built with ❤️ by <strong>Amir</strong><br>"
        "Gemini • ChatGPT • Claude</div>",
        unsafe_allow_html=True,
    )


# ─── Hero Header ───
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">✨ AI-Powered SEO Intelligence</div>
    <div class="hero-title">Google Query Fan-Out Extractor</div>
    <div class="hero-subtitle">
        Discover the hidden sub-queries that Google AI Overviews secretly run
        behind the scenes. Target these queries to rank in Google AIO & AI Mode.
    </div>
</div>
""", unsafe_allow_html=True)


# ─── Search Input ───
st.markdown('<div class="search-container">', unsafe_allow_html=True)
col_input, col_btn = st.columns([5, 1])
with col_input:
    user_query = st.text_input(
        "Enter your search query",
        placeholder="e.g.  best laptops for programming 2026",
        label_visibility="collapsed",
    )
with col_btn:
    extract_btn = st.button("🔍 Extract", use_container_width=True, type="primary")
st.markdown('</div>', unsafe_allow_html=True)


# ─── Core Extraction Logic ───

def extract_via_grounding(client, model: str, query: str):
    """Mode 1 — Use Google Search Grounding to extract real fan-out queries."""
    from google.genai import types

    response = client.models.generate_content(
        model=model,
        contents=query,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        ),
    )

    fan_out_queries = []
    answer_text = ""

    # Extract answer text
    if response.text:
        answer_text = response.text

    # Extract grounding search queries
    if response.candidates:
        for candidate in response.candidates:
            gm = candidate.grounding_metadata
            if gm and gm.web_search_queries:
                fan_out_queries.extend(gm.web_search_queries)

    return fan_out_queries, answer_text


def extract_via_prompt(client, model: str, query: str, num_queries: int = 15):
    """Mode 2 — Prompt-based fan-out query prediction as fallback (Gemini)."""
    prompt = _build_fanout_prompt(query, num_queries)

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    answer_text = response.text if response.text else ""
    fan_out_queries = _parse_numbered_list(answer_text)
    return fan_out_queries, answer_text


def _build_fanout_prompt(query: str, num_queries: int) -> str:
    """Shared prompt for all providers."""
    return f"""You are an expert Google Search analyst specializing in how Google AI Overviews work internally.

For the search query: "{query}"

Generate exactly {num_queries} realistic Fan-Out Queries that Google AI Overview would internally execute as sub-searches to build its answer. These are the hidden decomposed queries Google runs behind the scenes.

Rules:
- Each query should target a specific aspect or sub-topic
- Include comparison queries, "best of" queries, technical queries, and informational queries
- Make them realistic — as if Google's internal system generated them
- Return ONLY a numbered list (1. query, 2. query, etc.)
- No explanations, no headers, no extra text"""


def _parse_numbered_list(text: str) -> list:
    """Parse numbered list from AI response."""
    fan_out_queries = []
    lines = text.strip().split("\n")
    for line in lines:
        line = line.strip()
        match = re.match(r'^\d+[\.\)\-]\s*(.+)$', line)
        if match:
            q = match.group(1).strip().strip('"').strip("'")
            if q:
                fan_out_queries.append(q)
    return fan_out_queries


def extract_via_chatgpt(api_key: str, model: str, query: str, num_queries: int = 15):
    """Extract fan-out queries using OpenAI ChatGPT."""
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    prompt = _build_fanout_prompt(query, num_queries)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert Google Search analyst. Return only numbered lists."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    answer_text = response.choices[0].message.content or ""
    fan_out_queries = _parse_numbered_list(answer_text)
    return fan_out_queries, answer_text


def extract_via_claude(api_key: str, model: str, query: str, num_queries: int = 15):
    """Extract fan-out queries using Anthropic Claude."""
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    prompt = _build_fanout_prompt(query, num_queries)

    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt},
        ],
    )

    answer_text = response.content[0].text if response.content else ""
    fan_out_queries = _parse_numbered_list(answer_text)
    return fan_out_queries, answer_text


def run_extraction(api_key: str, model: str, query: str, num_queries: int = 15, provider: str = "Google Gemini"):
    """Smart dual-mode extraction with automatic fallback."""

    # ── ChatGPT path (prompt-only) ──
    if provider == "ChatGPT (OpenAI)":
        fan_out_queries, answer_text = extract_via_chatgpt(api_key, model, query, num_queries)
        return fan_out_queries, answer_text, "chatgpt"

    # ── Claude path (prompt-only) ──
    if provider == "Claude (Anthropic)":
        fan_out_queries, answer_text = extract_via_claude(api_key, model, query, num_queries)
        return fan_out_queries, answer_text, "claude"

    # ── Gemini path (grounding → prompt fallback) ──
    from google import genai

    client = genai.Client(api_key=api_key)
    method_used = "grounding"

    try:
        fan_out_queries, answer_text = extract_via_grounding(client, model, query)

        # If grounding returned no queries, fall back to prompt mode
        if not fan_out_queries:
            method_used = "prompt"
            fan_out_queries, answer_text = extract_via_prompt(client, model, query, num_queries)

    except Exception as e:
        error_str = str(e).lower()
        # Check for quota / rate-limit / grounding-specific errors → fallback silently
        if any(kw in error_str for kw in ["quota", "rate", "limit", "429", "503", "resource_exhausted",
                                           "grounding", "unavailable", "overloaded", "capacity", "high demand"]):
            method_used = "prompt"
            try:
                fan_out_queries, answer_text = extract_via_prompt(client, model, query, num_queries)
            except Exception as inner_e:
                raise inner_e
        else:
            raise e

    return fan_out_queries, answer_text, method_used


# ─── Execution ───
if extract_btn:
    # Validation
    if not api_key:
        if ai_provider == "Google Gemini":
            st.error("⚠️ Please enter your **Gemini API Key** in the sidebar. "
                     "[Get a free key →](https://aistudio.google.com/apikey)")
        elif ai_provider == "ChatGPT (OpenAI)":
            st.error("⚠️ Please enter your **OpenAI API Key** in the sidebar. "
                     "[Get your key →](https://platform.openai.com/api-keys)")
        else:
            st.error("⚠️ Please enter your **Anthropic API Key** in the sidebar. "
                     "[Get your key →](https://console.anthropic.com/settings/keys)")
        st.stop()

    if not user_query.strip():
        st.warning("⚠️ Please enter a search query to extract fan-out queries.")
        st.stop()

    # Run extraction with spinner
    with st.spinner("🔍 Extracting fan-out queries…"):
        try:
            fan_out_queries, answer_text, method_used = run_extraction(
                api_key, selected_model, user_query.strip(), query_count, ai_provider
            )
        except Exception as e:
            error_msg = str(e)
            err_lower = error_msg.lower()

            if any(kw in err_lower for kw in ["api_key", "invalid", "incorrect", "authentication", "401"]):
                links = {
                    "Google Gemini": "[Google AI Studio](https://aistudio.google.com/apikey)",
                    "ChatGPT (OpenAI)": "[OpenAI Platform](https://platform.openai.com/api-keys)",
                    "Claude (Anthropic)": "[Anthropic Console](https://console.anthropic.com/settings/keys)",
                }
                st.error(f"🔑 **Invalid API Key.** Please check your key and try again. {links.get(ai_provider, '')}")
            elif any(kw in err_lower for kw in ["quota", "insufficient_quota", "billing", "exceeded"]):
                st.error(f"💳 **Quota exceeded.** Your {ai_provider} API plan limit has been reached. "
                         "Please check your billing or upgrade your plan.")
            elif any(kw in err_lower for kw in ["rate", "429", "too many"]):
                st.warning("⏳ **Rate limited.** Too many requests. Please wait a moment and try again.")
            else:
                st.error(f"❌ An error occurred: {error_msg}")
            st.stop()

    if not fan_out_queries:
        st.warning("No fan-out queries were extracted. Try a different search query.")
        st.stop()

    # ── Method Banner ──
    banners = {
        "grounding": ("method-grounding",
                      "✅ Extracted via <strong>Google Search Grounding</strong> — Real sub-queries from Gemini's search metadata"),
        "chatgpt": ("method-chatgpt",
                    f"🤖 Generated via <strong>ChatGPT ({selected_model})</strong> — AI-predicted fan-out queries"),
        "claude": ("method-claude",
                   f"🧊 Generated via <strong>Claude ({selected_model.split('-202')[0]})</strong> — AI-predicted fan-out queries"),
        "prompt": ("method-prompt",
                   "🧠 Generated via <strong>Gemini AI Prediction</strong> — Gemini predicted realistic fan-out queries"),
    }
    banner_class, banner_text = banners.get(method_used, banners["prompt"])
    st.markdown(f'<div class="method-banner {banner_class}">{banner_text}</div>', unsafe_allow_html=True)

    # ── Metric Cards ──
    total_queries = len(fan_out_queries)
    total_query_words = sum(len(q.split()) for q in fan_out_queries)
    total_answer_words = len(answer_text.split()) if answer_text else 0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f'<div class="metric-card">'
            f'<span class="metric-icon">🎯</span>'
            f'<div class="metric-value">{total_queries}</div>'
            f'<div class="metric-label">Queries Found</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="metric-card">'
            f'<span class="metric-icon">📝</span>'
            f'<div class="metric-value">{total_query_words}</div>'
            f'<div class="metric-label">Words in Queries</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="metric-card">'
            f'<span class="metric-icon">💬</span>'
            f'<div class="metric-value">{total_answer_words}</div>'
            f'<div class="metric-label">Words in Answer</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ── Query Results ──
    st.markdown(
        '<div class="section-title">'
        '<h3>🎯 Extracted Fan-Out Queries</h3>'
        '<div class="title-line"></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    for idx, query_text in enumerate(fan_out_queries, 1):
        delay = f"animation-delay: {idx * 0.05}s;"
        st.markdown(
            f'<div class="query-row" style="{delay}">'
            f'<div class="query-number">{idx}</div>'
            f'<div class="query-text">{query_text}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ── CSV Export ──
    df = pd.DataFrame({
        "No.": list(range(1, total_queries + 1)),
        "Fan-Out Query": fan_out_queries,
        "Original Query": [user_query] * total_queries,
        "Method": [method_used] * total_queries,
        "Model": [selected_model] * total_queries,
        "Provider": [ai_provider] * total_queries,
    })

    csv_data = df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV Report",
        data=csv_data,
        file_name=f"fanout_queries_{user_query[:30].replace(' ', '_')}.csv",
        mime="text/csv",
        use_container_width=True,
    )

    # ── AI Answer Expander ──
    if answer_text:
        label_map = {"chatgpt": "🤖 View ChatGPT's Full Answer", "claude": "🧊 View Claude's Full Answer"}
        expander_label = label_map.get(method_used, "🤖 View Gemini's Full Answer")
        with st.expander(expander_label, expanded=False):
            st.markdown(answer_text)

    # ── Footer ──
    st.markdown(
        '<div class="app-footer">Built with ❤️ by <strong>Amir</strong> · '
        'Powered by Gemini, ChatGPT & Claude</div>',
        unsafe_allow_html=True,
    )
