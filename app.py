"""
Google Query Fan-Out Extractor
Extract hidden sub-queries that Google AI Overviews run internally.
Built with Streamlit + Google Gemini API + OpenAI ChatGPT.
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
    background: linear-gradient(135deg, #0a0a1a 0%, #0d1117 40%, #111827 100%);
    color: #e2e8f0;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(15,23,42,0.98) 0%, rgba(10,10,30,0.98) 100%);
    border-right: 1px solid rgba(99,102,241,0.15);
}
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #a5b4fc;
    font-weight: 700;
    letter-spacing: -0.02em;
}

/* ── Hero Header ── */
.hero-container {
    background: linear-gradient(135deg, rgba(99,102,241,0.12) 0%, rgba(168,85,247,0.08) 50%, rgba(236,72,153,0.06) 100%);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 20px;
    padding: 2.5rem 2rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(20px);
}
.hero-container::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 30% 50%, rgba(99,102,241,0.06) 0%, transparent 50%),
                radial-gradient(circle at 70% 80%, rgba(168,85,247,0.04) 0%, transparent 50%);
    animation: heroGlow 8s ease-in-out infinite alternate;
}
@keyframes heroGlow {
    0% { transform: translate(0, 0) rotate(0deg); }
    100% { transform: translate(-5%, 5%) rotate(3deg); }
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: linear-gradient(135deg, rgba(99,102,241,0.25), rgba(168,85,247,0.2));
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 50px;
    padding: 6px 16px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #a5b4fc;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 1rem;
    animation: badgePulse 3s ease-in-out infinite;
    position: relative;
    z-index: 1;
}
@keyframes badgePulse {
    0%, 100% { box-shadow: 0 0 15px rgba(99,102,241,0.2); }
    50% { box-shadow: 0 0 25px rgba(99,102,241,0.35); }
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #e2e8f0, #a5b4fc, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin-bottom: 0.5rem;
    position: relative;
    z-index: 1;
}
.hero-subtitle {
    font-size: 1rem;
    color: #94a3b8;
    font-weight: 400;
    line-height: 1.6;
    position: relative;
    z-index: 1;
}

/* ── Metric Cards ── */
.metric-card {
    background: linear-gradient(135deg, rgba(30,30,60,0.6), rgba(20,20,50,0.8));
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    backdrop-filter: blur(12px);
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
}
.metric-card:hover {
    border-color: rgba(99,102,241,0.4);
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(99,102,241,0.1);
}
.metric-value {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.metric-label {
    font-size: 0.8rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.3rem;
    font-weight: 600;
}

/* ── Query Row ── */
.query-row {
    display: flex;
    align-items: center;
    gap: 14px;
    background: linear-gradient(135deg, rgba(30,30,60,0.4), rgba(20,20,50,0.6));
    border: 1px solid rgba(99,102,241,0.1);
    border-radius: 14px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    animation: fadeSlideIn 0.4s ease-out forwards;
    opacity: 0;
}
.query-row:hover {
    border-color: rgba(99,102,241,0.35);
    background: linear-gradient(135deg, rgba(40,40,80,0.5), rgba(30,30,70,0.7));
    transform: translateX(6px);
    box-shadow: 0 4px 20px rgba(99,102,241,0.08);
}
@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}
.query-number {
    min-width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 50%;
    font-weight: 700;
    font-size: 0.85rem;
    color: white;
    flex-shrink: 0;
    box-shadow: 0 2px 10px rgba(99,102,241,0.3);
}
.query-text {
    color: #e2e8f0;
    font-size: 0.95rem;
    font-weight: 500;
    line-height: 1.4;
}

/* ── Success/Method Banner ── */
.method-banner {
    border-radius: 14px;
    padding: 1rem 1.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 600;
    font-size: 0.9rem;
    animation: fadeSlideIn 0.5s ease-out;
}
.method-grounding {
    background: linear-gradient(135deg, rgba(16,185,129,0.12), rgba(52,211,153,0.08));
    border: 1px solid rgba(16,185,129,0.25);
    color: #6ee7b7;
}
.method-prompt {
    background: linear-gradient(135deg, rgba(251,191,36,0.12), rgba(245,158,11,0.08));
    border: 1px solid rgba(251,191,36,0.25);
    color: #fcd34d;
}

/* ── Buttons ── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.3s ease !important;
}
.stDownloadButton > button:hover {
    box-shadow: 0 4px 20px rgba(99,102,241,0.4) !important;
    transform: translateY(-1px) !important;
}

/* ── Input Styling ── */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: rgba(30,30,60,0.6) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(99,102,241,0.5) !important;
    box-shadow: 0 0 15px rgba(99,102,241,0.15) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader,
div[data-testid="stExpander"] summary {
    background: rgba(30,30,60,0.4) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(99,102,241,0.15) !important;
    color: #a5b4fc !important;
    font-weight: 600 !important;
    overflow: visible !important;
    white-space: normal !important;
    padding: 1rem 1.2rem !important;
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

/* ── Download Button Fix ── */
.stDownloadButton {
    margin-top: 1rem;
    margin-bottom: 1rem;
}

/* ── General Text Visibility ── */
.stMarkdown, .stMarkdown p, .stMarkdown li {
    color: #e2e8f0 !important;
}
label, .stTextInput label, .stSelectbox label {
    color: #cbd5e1 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(99,102,241,0.5); }

/* ── Hide Streamlit Defaults ── */
#MainMenu { visibility: hidden; }
header { visibility: hidden; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─── Sidebar ───
with st.sidebar:
    st.markdown("### 🔐 Configuration")
    st.markdown("---")

    ai_provider = st.selectbox(
        "AI Provider",
        options=["Google Gemini", "ChatGPT (OpenAI)"],
        index=0,
        help="Choose which AI provider to use for extraction",
    )

    if ai_provider == "Google Gemini":
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
    else:
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="Paste your OpenAI API key (sk-…)",
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

    query_count = st.slider(
        "Number of Queries",
        min_value=5,
        max_value=30,
        value=15,
        step=1,
        help="AI Prediction mode mein kitni fan-out queries generate karni hain",
    )

    st.markdown("---")
    st.markdown(
        """
        <div style='padding:1rem; background:rgba(99,102,241,0.08); border-radius:12px;
                    border:1px solid rgba(99,102,241,0.15); font-size:0.8rem; color:#94a3b8;'>
            <strong style='color:#a5b4fc;'>💡 How It Works</strong><br><br>
            <strong>Gemini Mode 1:</strong> Google Search Grounding — extracts <em>real</em>
            sub-queries from Gemini's search metadata.<br><br>
            <strong>Gemini Mode 2:</strong> AI Prediction — if grounding quota is
            exceeded, Gemini predicts fan-out queries.<br><br>
            <strong>ChatGPT:</strong> AI Prediction only — generates realistic
            fan-out queries using OpenAI models.<br><br>
            Fallback runs automatically.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:#475569; font-size:0.7rem;'>"
        "Built with ❤️ by Amir • Powered by Gemini & ChatGPT</div>",
        unsafe_allow_html=True,
    )


# ─── Hero Header ───
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">✨ AI-Powered SEO Intelligence</div>
    <div class="hero-title">Google Query Fan-Out Extractor</div>
    <div class="hero-subtitle">
        Discover the hidden sub-queries that Google AI Overviews secretly run behind
        the scenes. Target these queries to rank in Google AIO & AI Mode.
    </div>
</div>
""", unsafe_allow_html=True)


# ─── Search Input ───
col_input, col_btn = st.columns([4, 1])
with col_input:
    user_query = st.text_input(
        "Enter your search query",
        placeholder="e.g.  best laptops for programming 2026",
        label_visibility="collapsed",
    )
with col_btn:
    extract_btn = st.button("🔍 Extract Queries", use_container_width=True, type="primary")


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
    """Shared prompt for both Gemini and ChatGPT."""
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


def run_extraction(api_key: str, model: str, query: str, num_queries: int = 15, provider: str = "Google Gemini"):
    """Smart dual-mode extraction with automatic fallback."""

    # ── ChatGPT path (prompt-only) ──
    if provider == "ChatGPT (OpenAI)":
        fan_out_queries, answer_text = extract_via_chatgpt(api_key, model, query, num_queries)
        return fan_out_queries, answer_text, "chatgpt"

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
        if any(kw in error_str for kw in ["quota", "rate", "limit", "429", "503", "resource_exhausted", "grounding", "unavailable", "overloaded", "capacity", "high demand"]):
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
            st.error(
                "⚠️ Please enter your Gemini API Key in the sidebar.  \n"
                "Get a free key → [Google AI Studio](https://aistudio.google.com/apikey)"
            )
        else:
            st.error(
                "⚠️ Please enter your OpenAI API Key in the sidebar.  \n"
                "Get your key → [OpenAI Platform](https://platform.openai.com/api-keys)"
            )
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
            if "api_key" in error_msg.lower() or "invalid" in error_msg.lower() or "401" in error_msg or "incorrect api key" in error_msg.lower():
                if ai_provider == "Google Gemini":
                    st.error(
                        "❌ **Invalid API Key.** Please check your Gemini key and try again.  \n"
                        "Get a free key → [Google AI Studio](https://aistudio.google.com/apikey)"
                    )
                else:
                    st.error(
                        "❌ **Invalid API Key.** Please check your OpenAI key and try again.  \n"
                        "Get your key → [OpenAI Platform](https://platform.openai.com/api-keys)"
                    )
            else:
                st.error(f"❌ An error occurred: {error_msg}")
            st.stop()

    if not fan_out_queries:
        st.warning("No fan-out queries were extracted. Try a different search query.")
        st.stop()

    # ── Method Banner ──
    if method_used == "grounding":
        st.markdown(
            '<div class="method-banner method-grounding">'
            '✅ Extracted via <strong>Google Search Grounding</strong> — '
            'Real sub-queries from Gemini\'s search metadata'
            '</div>',
            unsafe_allow_html=True,
        )
    elif method_used == "chatgpt":
        st.markdown(
            '<div class="method-banner" style="background:linear-gradient(135deg,rgba(16,163,127,0.12),rgba(16,163,127,0.06));'
            'border:1px solid rgba(16,163,127,0.25);color:#4ade80;">'
            '🤖 Generated via <strong>ChatGPT (' + selected_model + ')</strong> — '
            'AI-predicted fan-out queries for this topic'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="method-banner method-prompt">'
            '🧠 Generated via <strong>Gemini AI Prediction</strong> — '
            'Gemini predicted realistic fan-out queries for this topic'
            '</div>',
            unsafe_allow_html=True,
        )

    # ── Metric Cards ──
    total_queries = len(fan_out_queries)
    total_query_words = sum(len(q.split()) for q in fan_out_queries)
    total_answer_words = len(answer_text.split()) if answer_text else 0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value">{total_queries}</div>'
            f'<div class="metric-label">Queries Found</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value">{total_query_words}</div>'
            f'<div class="metric-label">Words in Queries</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value">{total_answer_words}</div>'
            f'<div class="metric-label">Words in Answer</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Query Results ──
    st.markdown(
        "<h3 style='color:#a5b4fc; font-weight:700; margin-bottom:1rem;'>"
        "🎯 Extracted Fan-Out Queries</h3>",
        unsafe_allow_html=True,
    )

    for idx, query_text in enumerate(fan_out_queries, 1):
        delay = f"animation-delay: {idx * 0.06}s;"
        st.markdown(
            f'<div class="query-row" style="{delay}">'
            f'<div class="query-number">{idx}</div>'
            f'<div class="query-text">{query_text}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── CSV Export ──
    df = pd.DataFrame({
        "No.": list(range(1, total_queries + 1)),
        "Fan-Out Query": fan_out_queries,
        "Original Query": [user_query] * total_queries,
        "Method": [method_used] * total_queries,
        "Model": [selected_model] * total_queries,
    })

    csv_data = df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV Report",
        data=csv_data,
        file_name=f"fanout_queries_{user_query[:30].replace(' ', '_')}.csv",
        mime="text/csv",
        use_container_width=True,
    )

    # ── Gemini/ChatGPT Answer Expander ──
    if answer_text:
        expander_label = "🤖 View ChatGPT's Full Answer" if method_used == "chatgpt" else "🤖 View Gemini's Full Answer"
        with st.expander(expander_label, expanded=False):
            st.markdown(answer_text)
