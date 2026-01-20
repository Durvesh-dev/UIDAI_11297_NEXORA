import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from model_utils import run_model_pipeline, load_model, make_predictions, get_model_metrics
from chat_engine import respond_to_query, get_dynamic_suggestions, get_auto_insights, get_chat_answer

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="UIDAI Aadhaar Analytics",
    page_icon="🆔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- API KEY CHECK --------------------
if not os.getenv("GEMINI_API_KEY"):
    st.error("Gemini API key not configured. Please set GEMINI_API_KEY.")
    st.stop()

# -------------------- THEME STATE --------------------
if "theme" not in st.session_state:
    st.session_state.theme = "light"

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

is_dark = st.session_state.theme == "dark"

# -------------------- THEME COLORS --------------------
if is_dark:
    colors = {
        "bg": "#0f172a",
        "sidebar_bg": "#1e293b",
        "card_bg": "#1e293b",
        "card_border": "#334155",
        "text": "#f1f5f9",
        "text_secondary": "#cbd5e1",
        "text_muted": "#94a3b8",
        "divider": "#334155",
        "input_bg": "#334155",
        "hover_bg": "#334155",
        "active_bg": "#1e40af",
        "chart_bg": "rgba(30,41,59,1)",
        "grid_color": "#334155"
    }
else:
    colors = {
        "bg": "#f8fafc",
        "sidebar_bg": "#1e293b",
        "card_bg": "#ffffff",
        "card_border": "#e2e8f0",
        "text": "#0f172a",
        "text_secondary": "#334155",
        "text_muted": "#64748b",
        "divider": "#334155",
        "input_bg": "#f1f5f9",
        "hover_bg": "#334155",
        "active_bg": "#3b82f6",
        "chart_bg": "rgba(255,255,255,1)",
        "grid_color": "#e2e8f0"
    }

# -------------------- STYLES --------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}}

#MainMenu, footer {{visibility: hidden;}}

[data-testid="collapsedControl"] {{
    position: fixed !important;
    top: 0.75rem !important;
    left: 0.75rem !important;
    z-index: 999999 !important;
    background: linear-gradient(135deg, #f97316, #ea580c) !important;
    border-radius: 10px !important;
    padding: 10px !important;
    box-shadow: 0 4px 15px rgba(249, 115, 22, 0.4) !important;
}}

[data-testid="collapsedControl"] svg {{
    fill: white !important;
    stroke: white !important;
}}

section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0c1929 0%, #1a2d47 100%) !important;
    border-right: none;
    box-shadow: 4px 0 20px rgba(0,0,0,0.15);
}}

section[data-testid="stSidebar"] > div {{
    padding: 0 !important;
}}

section[data-testid="stSidebar"] > div > div {{
    padding: 1.5rem 1rem !important;
}}

section[data-testid="stSidebar"] * {{
    color: #cbd5e1 !important;
}}

section[data-testid="stSidebar"] hr {{
    border-color: rgba(255,255,255,0.1) !important;
    margin: 1.25rem 0;
}}

section[data-testid="stSidebar"] .stRadio > div {{
    gap: 4px;
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
    padding: 6px;
}}

section[data-testid="stSidebar"] .stRadio > div > label {{
    background: transparent;
    padding: 0.875rem 1rem;
    border-radius: 10px;
    margin: 0;
    transition: all 0.2s ease;
    cursor: pointer;
    font-weight: 500;
    font-size: 0.9rem;
}}

section[data-testid="stSidebar"] .stRadio > div > label:hover {{
    background: rgba(255,255,255,0.08);
}}

section[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {{
    background: linear-gradient(135deg, #f97316, #ea580c) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 15px rgba(249, 115, 22, 0.3);
}}

section[data-testid="stSidebar"] [data-testid="stFileUploader"] {{
    background: rgba(255,255,255,0.05);
    border: 1px dashed rgba(255,255,255,0.2);
    border-radius: 12px;
    padding: 1rem;
}}

section[data-testid="stSidebar"] [data-testid="stFileUploader"] button {{
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
}}

section[data-testid="stSidebar"] .stAlert {{
    background: rgba(16, 185, 129, 0.15) !important;
    border: 1px solid rgba(16, 185, 129, 0.3) !important;
    border-radius: 10px;
}}

.main .block-container {{
    padding: 1.25rem 2rem 2rem;
    max-width: 1500px;
}}

.stApp {{
    background: {colors["bg"]};
}}

.page-header {{
    background: {"linear-gradient(135deg, #1e293b 0%, #334155 100%)" if is_dark else "linear-gradient(135deg, #1e3a5f 0%, #1e40af 100%)"};
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    color: white;
}}

.page-title {{
    font-size: 1.75rem;
    font-weight: 700;
    margin: 0;
}}

.page-subtitle {{
    font-size: 0.9rem;
    opacity: 0.85;
    margin-top: 0.25rem;
}}

.kpi-card {{
    background: {colors["card_bg"]};
    border-radius: 16px;
    padding: 1.25rem;
    border: 1px solid {colors["card_border"]};
    box-shadow: {"0 2px 8px rgba(0,0,0,0.15)" if is_dark else "0 2px 8px rgba(0,0,0,0.04)"};
    position: relative;
    overflow: hidden;
}}

.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
}}

.kpi-card.orange::before {{ background: linear-gradient(90deg, #f97316, #fb923c); }}
.kpi-card.blue::before {{ background: linear-gradient(90deg, #3b82f6, #60a5fa); }}
.kpi-card.green::before {{ background: linear-gradient(90deg, #10b981, #34d399); }}
.kpi-card.purple::before {{ background: linear-gradient(90deg, #8b5cf6, #a78bfa); }}

.kpi-icon {{
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    margin-bottom: 0.75rem;
}}

.kpi-icon.orange {{ background: rgba(249, 115, 22, 0.15); }}
.kpi-icon.blue {{ background: rgba(59, 130, 246, 0.15); }}
.kpi-icon.green {{ background: rgba(16, 185, 129, 0.15); }}
.kpi-icon.purple {{ background: rgba(139, 92, 246, 0.15); }}

.kpi-value {{
    font-size: 1.75rem;
    font-weight: 800;
    color: {colors["text"]};
    line-height: 1.2;
}}

.kpi-label {{
    font-size: 0.8rem;
    color: {colors["text_muted"]};
    margin-top: 0.25rem;
    font-weight: 500;
}}

.demo-card {{
    border-radius: 16px;
    padding: 1.5rem;
    color: white;
    position: relative;
    overflow: hidden;
}}

.demo-card.card-1 {{ background: linear-gradient(135deg, #6366f1, #8b5cf6); }}
.demo-card.card-2 {{ background: linear-gradient(135deg, #14b8a6, #06b6d4); }}
.demo-card.card-3 {{ background: linear-gradient(135deg, #f97316, #eab308); }}

.demo-label {{
    font-size: 0.85rem;
    opacity: 0.9;
    font-weight: 500;
}}

.demo-value {{
    font-size: 2.25rem;
    font-weight: 800;
    margin: 0.5rem 0 0.25rem;
}}

.demo-icon {{
    font-size: 2rem;
    margin-bottom: 0.5rem;
    opacity: 0.9;
}}

.demo-pct {{
    font-size: 0.75rem;
    opacity: 0.85;
    margin-top: 0.25rem;
}}

.state-card {{
    background: {colors["card_bg"]};
    border: 1px solid {colors["card_border"]};
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
    transition: all 0.2s ease;
}}

.state-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    border-color: #f97316;
}}

.state-name {{
    font-size: 0.85rem;
    font-weight: 600;
    color: {colors["text"]};
    margin-bottom: 0.5rem;
}}

.state-value {{
    font-size: 1.25rem;
    font-weight: 700;
    color: #f97316;
}}

.state-label {{
    font-size: 0.7rem;
    color: {colors["text_muted"]};
    margin-top: 0.25rem;
}}

.state-rank {{
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    background: {colors["input_bg"]};
    color: {colors["text_muted"]};
    margin-bottom: 0.5rem;
}}

.state-rank.gold {{
    background: linear-gradient(135deg, #fbbf24, #f59e0b);
    color: #451a03;
}}

.state-rank.silver {{
    background: linear-gradient(135deg, #94a3b8, #64748b);
    color: white;
}}

.state-rank.bronze {{
    background: linear-gradient(135deg, #ea580c, #c2410c);
    color: white;
}}

.chart-card {{
    background: {colors["card_bg"]};
    border: 1px solid {colors["card_border"]};
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: {"0 2px 8px rgba(0,0,0,0.15)" if is_dark else "0 2px 8px rgba(0,0,0,0.04)"};
}}

.chart-card-header {{
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid {colors["card_border"]};
}}

.chart-card-title {{
    font-size: 1rem;
    font-weight: 600;
    color: {colors["text"]};
}}

.filter-label {{
    font-size: 0.85rem;
    font-weight: 600;
    color: {colors["text"]};
}}

.section-title {{
    font-size: 1.1rem;
    font-weight: 700;
    color: {colors["text"]};
    margin: 1.75rem 0 1rem;
}}

.insight-box {{
    background: {colors["card_bg"]};
    border-radius: 16px;
    padding: 1.5rem;
    border-left: 5px solid #3b82f6;
    box-shadow: {"0 2px 8px rgba(0,0,0,0.15)" if is_dark else "0 2px 8px rgba(0,0,0,0.04)"};
    margin-bottom: 1rem;
}}

.insight-tag {{
    display: inline-block;
    background: {"rgba(59, 130, 246, 0.15)" if is_dark else "#dbeafe"};
    color: {"#60a5fa" if is_dark else "#1d4ed8"};
    padding: 0.35rem 0.875rem;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 1rem;
}}

.insight-section-title {{
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.35rem;
}}

.insight-section-title.finding {{ color: #3b82f6; }}
.insight-section-title.impact {{ color: #f59e0b; }}
.insight-section-title.rec {{ color: #10b981; }}

.insight-section-text {{
    font-size: 0.9rem;
    color: {colors["text_secondary"]};
    line-height: 1.7;
    margin-bottom: 1rem;
}}

.question-box {{
    background: {"rgba(15, 23, 42, 0.5)" if is_dark else "#f1f5f9"};
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    border: 1px solid {colors["card_border"]};
}}

.q-label {{
    font-size: 0.7rem;
    color: {colors["text_muted"]};
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
    margin-bottom: 0.35rem;
}}

.q-text {{
    font-size: 1rem;
    color: {colors["text"]};
    font-weight: 600;
}}

.config-box {{
    background: {"rgba(15, 23, 42, 0.5)" if is_dark else "#f8fafc"};
    border-radius: 14px;
    padding: 1.25rem;
    text-align: center;
    border: 1px solid {colors["card_border"]};
}}

.config-value {{
    font-size: 1.1rem;
    font-weight: 700;
    color: {colors["text"]};
}}

.config-label {{
    font-size: 0.75rem;
    color: {colors["text_muted"]};
    margin-top: 0.35rem;
    font-weight: 500;
}}

.help-card {{
    background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    margin-top: 1.5rem;
}}

.help-icon {{
    width: 56px;
    height: 56px;
    background: rgba(255,255,255,0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1rem;
    font-size: 1.5rem;
}}

.help-title {{
    font-weight: 700;
    color: #ffffff;
    font-size: 1rem;
    margin-bottom: 0.35rem;
}}

.help-text {{
    font-size: 0.8rem;
    color: rgba(255,255,255,0.8);
    line-height: 1.5;
}}

.stMultiSelect [data-baseweb="tag"] {{
    background: linear-gradient(135deg, #f97316, #ea580c) !important;
    color: white !important;
    border-radius: 8px !important;
}}

.stTextInput > div > div > input {{
    background: {colors["card_bg"]} !important;
    border: 1px solid {colors["card_border"]} !important;
    border-radius: 10px !important;
    color: {colors["text"]} !important;
    padding: 0.75rem 1rem !important;
}}

.stTextInput > div > div > input:focus {{
    border-color: #f97316 !important;
    box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.15) !important;
}}

.stButton > button {{
    background: linear-gradient(135deg, #f97316, #ea580c) !important;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    box-shadow: 0 4px 15px rgba(249, 115, 22, 0.3);
    transition: all 0.2s ease;
}}

.stButton > button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(249, 115, 22, 0.4);
}}

.stAlert {{
    background: {"rgba(59, 130, 246, 0.1)" if is_dark else "#eff6ff"} !important;
    border: 1px solid {"rgba(59, 130, 246, 0.3)" if is_dark else "#bfdbfe"} !important;
    border-radius: 12px !important;
    color: {"#93c5fd" if is_dark else "#1e40af"} !important;
}}

.empty-state {{
    text-align: center;
    padding: 4rem 2rem;
    color: {colors["text_muted"]};
}}

.empty-state-icon {{
    font-size: 4rem;
    margin-bottom: 1.25rem;
    opacity: 0.5;
}}

.empty-state-title {{
    font-size: 1.1rem;
    font-weight: 600;
    color: {colors["text_secondary"]};
    margin-bottom: 0.5rem;
}}

.empty-state-text {{
    font-size: 0.9rem;
}}

.answer-box {{
    background: {colors["card_bg"]};
    border-radius: 16px;
    padding: 1.5rem;
    border: 1px solid {colors["card_border"]};
    margin-top: 1rem;
    box-shadow: {"0 2px 8px rgba(0,0,0,0.15)" if is_dark else "0 2px 8px rgba(0,0,0,0.04)"};
}}

.answer-label {{
    font-size: 0.75rem;
    font-weight: 600;
    color: #f97316;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}}

.answer-text {{
    font-size: 1rem;
    color: {colors["text"]};
    line-height: 1.7;
}}

/* Modern Theme Toggle Switch */
.theme-toggle-container {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1));
    border-radius: 12px;
    margin: 0.5rem 0;
    border: 1px solid rgba(99, 102, 241, 0.2);
}}

.theme-toggle-label {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.85rem;
    font-weight: 500;
    color: #e2e8f0;
}}

.theme-toggle-icon {{
    font-size: 1.1rem;
}}

.toggle-switch {{
    position: relative;
    width: 56px;
    height: 28px;
    background: {'linear-gradient(135deg, #6366f1, #8b5cf6)' if is_dark else 'linear-gradient(135deg, #f97316, #fbbf24)'};
    border-radius: 30px;
    cursor: pointer;
    transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    box-shadow: 0 4px 15px {'rgba(99, 102, 241, 0.4)' if is_dark else 'rgba(249, 115, 22, 0.4)'};
    border: 2px solid {'rgba(139, 92, 246, 0.5)' if is_dark else 'rgba(251, 191, 36, 0.5)'};
}}

.toggle-switch:hover {{
    transform: scale(1.05);
    box-shadow: 0 6px 20px {'rgba(99, 102, 241, 0.5)' if is_dark else 'rgba(249, 115, 22, 0.5)'};
}}

.toggle-slider {{
    position: absolute;
    top: 2px;
    left: {'26px' if is_dark else '2px'};
    width: 20px;
    height: 20px;
    background: white;
    border-radius: 50%;
    transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}}

.toggle-slider::after {{
    content: '{'🌙' if is_dark else '☀️'}';
    font-size: 11px;
}}

.theme-status {{
    font-size: 0.7rem;
    color: #94a3b8;
    margin-top: 0.25rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* Theme Toggle Button Styling */
section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:has(p:contains("Toggle")) {{
    background: {'linear-gradient(135deg, #6366f1, #8b5cf6)' if is_dark else 'linear-gradient(135deg, #f97316, #ea580c)'} !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    padding: 0.6rem 1rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px {'rgba(99, 102, 241, 0.4)' if is_dark else 'rgba(249, 115, 22, 0.4)'} !important;
}}

section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:has(p:contains("Toggle")):hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px {'rgba(99, 102, 241, 0.5)' if is_dark else 'rgba(249, 115, 22, 0.5)'} !important;
}}
</style>
""", unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0 1rem;">
        <div style="font-size: 2.5rem; margin-bottom: 0.25rem;">🆔</div>
        <div style="font-size: 1.1rem; font-weight: 700; color: #f97316;">UIDAI Analytics</div>
        <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 0.25rem;">Aadhaar Insights Platform</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Modern Theme Toggle
    st.markdown(f'''
    <div class="theme-toggle-container">
        <div class="theme-toggle-label">
            <span class="theme-toggle-icon">{'🌙' if is_dark else '☀️'}</span>
            <div>
                <div>{'Dark Mode' if is_dark else 'Light Mode'}</div>
                <div class="theme-status">{'Night theme active' if is_dark else 'Day theme active'}</div>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Hidden button for toggle functionality
    if st.button("🔄 Toggle Theme", key="theme_btn", use_container_width=True):
        toggle_theme()
        st.rerun()
    
    st.divider()
    
    st.markdown('<p style="font-size: 0.75rem; color: #64748b; margin-bottom: 0.5rem; font-weight: 600;">NAVIGATION</p>', unsafe_allow_html=True)
    page = st.radio("nav", ["📊 Dashboard", "🔮 Predictive Model", "💬 Insight Chat"], label_visibility="collapsed")
    
    st.divider()
    
    st.markdown('<p style="font-size: 0.75rem; color: #64748b; margin-bottom: 0.5rem; font-weight: 600;">DATA SOURCE</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")
    
    if uploaded_file:
        st.success("✓ Data loaded successfully")
    
    st.markdown("""
    <div class="help-card">
        <div class="help-icon">🛈</div>
        <div class="help-title">Need Assistance?</div>
        <div class="help-text">Contact UIDAI Support Team for technical help and guidance.</div>
    </div>
    """, unsafe_allow_html=True)

# -------------------- LOAD DATA --------------------
df = None
if uploaded_file:
    df = pd.read_csv(uploaded_file)

# -------------------- HELPERS --------------------
def fmt(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.0f}K"
    return str(int(n))

def show_insight(text):
    parts = {"Finding": "", "Impact": "", "Recommendation": ""}
    curr = None
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        for k in parts:
            if line.startswith(k):
                curr = k
                parts[k] = line.replace(f"{k}:", "").strip()
                break
        else:
            if curr:
                parts[curr] += " " + line
    
    st.markdown(f"""
    <div class="insight-box">
        <span class="insight-tag">AI Insight</span>
        <div class="insight-section">
            <div class="insight-section-title finding">Finding</div>
            <div class="insight-section-text">{parts["Finding"]}</div>
        </div>
        <div class="insight-section">
            <div class="insight-section-title impact">Impact</div>
            <div class="insight-section-text">{parts["Impact"]}</div>
        </div>
        <div class="insight-section">
            <div class="insight-section-title rec">Recommendation</div>
            <div class="insight-section-text">{parts["Recommendation"]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_suggestions_card(text):
    st.markdown(f"""
    <div class="insight-box" style="border-left-color: #10b981;">
        <span class="insight-tag" style="background: rgba(16, 185, 129, 0.15); color: #10b981;">Strategic Suggestions</span>
        <div class="insight-section-text">{text.replace("Suggestions:", "").strip()}</div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# DASHBOARD
# =====================================================
if page == "📊 Dashboard":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">📊 Analytics Dashboard</div>
        <div class="page-subtitle">Dynamic data analysis and visualization for Aadhaar data</div>
    </div>
    """, unsafe_allow_html=True)
    
    if df is None:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📁</div>
            <div class="empty-state-title">No Data Loaded</div>
            <div class="empty-state-text">Upload a CSV dataset from the sidebar to view analytics</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Get column types
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Column Selection Section
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.markdown('<span class="filter-label">⚙️ Configure Analysis Columns</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        config_cols = st.columns(3)
        with config_cols[0]:
            primary_metric = st.selectbox(
                "📊 Primary Metric (Numeric)",
                numeric_cols,
                index=0 if numeric_cols else None,
                help="Main numeric column for KPIs and charts"
            )
        with config_cols[1]:
            group_col = st.selectbox(
                "🏷️ Group By (Category)",
                categorical_cols if categorical_cols else ["No categorical columns"],
                index=0 if categorical_cols else None,
                help="Column to group data by"
            )
        with config_cols[2]:
            additional_metrics = st.multiselect(
                "📈 Additional Metrics",
                [c for c in numeric_cols if c != primary_metric],
                default=[],
                help="Select additional numeric columns to display in charts"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if not numeric_cols:
            st.warning("⚠️ No numeric columns found in your dataset. Please upload a dataset with numeric values.")
        else:
            # Calculate dynamic stats
            total = df[primary_metric].sum() if primary_metric else 0
            avg_val = df[primary_metric].mean() if primary_metric else 0
            max_val = df[primary_metric].max() if primary_metric else 0
            min_val = df[primary_metric].min() if primary_metric else 0
            record_count = len(df)
            
            # Group-based stats
            has_groups = group_col and group_col != "No categorical columns" and group_col in df.columns
            if has_groups:
                unique_groups = df[group_col].nunique()
                top_group = df.groupby(group_col)[primary_metric].sum().idxmax() if primary_metric else "N/A"
            else:
                unique_groups = 0
                top_group = "N/A"
            
            # Filter Section (if categorical column exists)
            if has_groups:
                filter_cols = st.columns([3, 1])
                with filter_cols[0]:
                    st.markdown(f'<span class="filter-label">🔍 Filter by {group_col}</span>', unsafe_allow_html=True)
                    selected = st.multiselect(
                        "Select items", 
                        sorted(df[group_col].dropna().unique()),
                        label_visibility="collapsed",
                        placeholder=f"All {group_col}s Selected"
                    )
                with filter_cols[1]:
                    st.markdown('<span class="filter-label">📊 Showing</span>', unsafe_allow_html=True)
                    st.info(f"{len(selected) if selected else unique_groups} Groups")
                st.markdown('</div>', unsafe_allow_html=True)
                
                fdf = df if not selected else df[df[group_col].isin(selected)]
            else:
                fdf = df
                selected = []
            
            # KPI Cards Grid
            st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"""
                <div class="kpi-card orange">
                    <div class="kpi-icon">📊</div>
                    <div class="kpi-value">{fmt(total)}</div>
                    <div class="kpi-label">Total {primary_metric[:20] if primary_metric else 'Value'}</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="kpi-card blue">
                    <div class="kpi-icon">📋</div>
                    <div class="kpi-value">{fmt(record_count)}</div>
                    <div class="kpi-label">Total Records</div>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                if has_groups:
                    st.markdown(f"""
                    <div class="kpi-card green">
                        <div class="kpi-icon">🏆</div>
                        <div class="kpi-value">{str(top_group)[:12]}</div>
                        <div class="kpi-label">Top {group_col[:15]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="kpi-card green">
                        <div class="kpi-icon">📈</div>
                        <div class="kpi-value">{fmt(max_val)}</div>
                        <div class="kpi-label">Max Value</div>
                    </div>
                    """, unsafe_allow_html=True)
            with c4:
                if has_groups:
                    st.markdown(f"""
                    <div class="kpi-card purple">
                        <div class="kpi-icon">🏷️</div>
                        <div class="kpi-value">{unique_groups}</div>
                        <div class="kpi-label">Unique {group_col[:12]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="kpi-card purple">
                        <div class="kpi-icon">📉</div>
                        <div class="kpi-value">{fmt(avg_val)}</div>
                        <div class="kpi-label">Average Value</div>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Age Demographics (if available)
            age_cols = ['age_0_5', 'age_5_17', 'age_18_greater']
            if all(col in fdf.columns for col in age_cols):
                st.markdown('<div class="section-title">👥 Age Demographics</div>', unsafe_allow_html=True)
                demo_cols = st.columns(3)
                
                age_0_5 = fdf['age_0_5'].sum()
                age_5_17 = fdf['age_5_17'].sum()
                age_18_plus = fdf['age_18_greater'].sum()
                total_age = age_0_5 + age_5_17 + age_18_plus
                
                with demo_cols[0]:
                    pct = (age_0_5 / total_age * 100) if total_age > 0 else 0
                    st.markdown(f'<div class="demo-card card-1"><div class="demo-icon">👶</div><div class="demo-value">{fmt(age_0_5)}</div><div class="demo-label">Age 0-5 Years</div><div class="demo-pct">{pct:.1f}% of total</div></div>', unsafe_allow_html=True)
                with demo_cols[1]:
                    pct = (age_5_17 / total_age * 100) if total_age > 0 else 0
                    st.markdown(f'<div class="demo-card card-2"><div class="demo-icon">🧒</div><div class="demo-value">{fmt(age_5_17)}</div><div class="demo-label">Age 5-17 Years</div><div class="demo-pct">{pct:.1f}% of total</div></div>', unsafe_allow_html=True)
                with demo_cols[2]:
                    pct = (age_18_plus / total_age * 100) if total_age > 0 else 0
                    st.markdown(f'<div class="demo-card card-3"><div class="demo-icon">👨</div><div class="demo-value">{fmt(age_18_plus)}</div><div class="demo-label">Age 18+ Years</div><div class="demo-pct">{pct:.1f}% of total</div></div>', unsafe_allow_html=True)
            
            # Visualizations
            st.markdown('<div class="section-title">📈 Visualizations</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            
            with c1:
                if has_groups and primary_metric:
                    st.markdown(f'<div class="chart-card"><div class="chart-card-header"><div class="chart-card-title">🏆 Top 10 {group_col} by {primary_metric}</div></div></div>', unsafe_allow_html=True)
                    sdata = fdf.groupby(group_col)[primary_metric].sum().reset_index()
                    sdata = sdata.sort_values(primary_metric, ascending=True).tail(10)
                    
                    fig = px.bar(sdata, y=group_col, x=primary_metric, orientation="h", color_discrete_sequence=["#f97316"])
                    fig.update_layout(plot_bgcolor=colors["chart_bg"], paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=10, b=0), height=320, xaxis=dict(title="", gridcolor=colors["grid_color"], showgrid=True, color=colors["text_muted"]), yaxis=dict(title="", color=colors["text_muted"]), font=dict(color=colors["text_secondary"]), showlegend=False)
                    fig.update_traces(marker=dict(cornerradius=6))
                    st.plotly_chart(fig, use_container_width=True)
            
            with c2:
                if all(col in fdf.columns for col in age_cols):
                    st.markdown('<div class="chart-card"><div class="chart-card-header"><div class="chart-card-title">📊 Age Distribution</div></div></div>', unsafe_allow_html=True)
                    pie_data = pd.DataFrame({"Age Group": ["0-5 Years", "5-17 Years", "18+ Years"], "Count": [age_0_5, age_5_17, age_18_plus]})
                    
                    fig = px.pie(pie_data, values="Count", names="Age Group", hole=0.65, color_discrete_sequence=["#6366f1", "#14b8a6", "#f97316"])
                    fig.update_layout(plot_bgcolor=colors["chart_bg"], paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=10, b=0), height=320, showlegend=True, font=dict(color=colors["text_secondary"]), legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5))
                    st.plotly_chart(fig, use_container_width=True)
                elif additional_metrics:
                    st.markdown('<div class="chart-card"><div class="chart-card-header"><div class="chart-card-title">📊 Metrics Distribution</div></div></div>', unsafe_allow_html=True)
                    pie_data = pd.DataFrame({"Metric": additional_metrics[:5], "Value": [fdf[m].sum() for m in additional_metrics[:5]]})
                    
                    fig = px.pie(pie_data, values="Value", names="Metric", hole=0.65, color_discrete_sequence=["#6366f1", "#14b8a6", "#f97316", "#8b5cf6", "#ec4899"])
                    fig.update_layout(plot_bgcolor=colors["chart_bg"], paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=10, b=0), height=320, showlegend=True, font=dict(color=colors["text_secondary"]), legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5))
                    st.plotly_chart(fig, use_container_width=True)
            
            # Group Performance Grid Section (if has groups)
            if has_groups:
                st.markdown(f'<div class="section-title">🗺️ {group_col} Performance</div>', unsafe_allow_html=True)
                
                group_data = fdf.groupby(group_col)[primary_metric].sum().reset_index()
                group_data = group_data.sort_values(primary_metric, ascending=False)
                
                st.markdown('<div class="state-grid">', unsafe_allow_html=True)
                cols = st.columns(4)
                for idx, row in enumerate(group_data.head(12).itertuples()):
                    col_idx = idx % 4
                    with cols[col_idx]:
                        rank = idx + 1
                        rank_class = "gold" if rank == 1 else ("silver" if rank == 2 else ("bronze" if rank == 3 else ""))
                        group_name = str(getattr(row, group_col))[:18] if hasattr(row, group_col) else str(row[1])[:18]
                        group_value = getattr(row, primary_metric) if hasattr(row, primary_metric) else row[2]
                        st.markdown(f"""
                        <div class="state-card">
                            <div class="state-rank {rank_class}">#{rank}</div>
                            <div class="state-name">{group_name}</div>
                            <div class="state-value">{fmt(group_value)}</div>
                            <div class="state-label">Total {primary_metric[:15]}</div>
                        </div>
                        """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Data Preview Section
            st.markdown('<div class="section-title">📋 Data Preview</div>', unsafe_allow_html=True)
            st.dataframe(fdf.head(20), use_container_width=True)

# =====================================================
# PREDICTIVE MODEL
# =====================================================
elif page == "🔮 Predictive Model":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">🔮 Predictive Model</div>
        <div class="page-subtitle">Machine learning model for Aadhaar activity prediction</div>
    </div>
    """, unsafe_allow_html=True)
    
    if df is None:
        st.markdown('<div class="empty-state"><div class="empty-state-icon">🔮</div><div class="empty-state-title">No Data Loaded</div><div class="empty-state-text">Upload a CSV dataset from the sidebar to train the model</div></div>', unsafe_allow_html=True)
    else:
        model_data = load_model()
        model_exists = model_data is not None
        
        if model_exists:
            st.success("✅ Model loaded from aadhaar_model.pkl (using saved model)")
            stored_r2, stored_mae = get_model_metrics()
            if stored_r2 is not None:
                st.session_state.model_metrics = (stored_r2, stored_mae)
        else:
            st.warning("⚠️ No trained model found. Train a new model below.")
        
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown('<div class="config-box"><div class="config-value">RandomForest</div><div class="config-label">Algorithm</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="config-box"><div class="config-value">100</div><div class="config-label">Estimators</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="config-box"><div class="config-value">20%</div><div class="config-label">Test Split</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown('<div class="config-box"><div class="config-value">total_activity</div><div class="config-label">Target Variable</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🚀 Train Model", use_container_width=True):
                with st.spinner("Training model with full pipeline..."):
                    r2, mae = run_model_pipeline(df)
                    st.session_state.model_metrics = (r2, mae)
                    st.success("✅ Model trained and saved!")
                    st.rerun()
        
        with col2:
            if model_exists and st.button("📊 Generate Predictions", use_container_width=True):
                with st.spinner("Generating predictions..."):
                    try:
                        predictions_df, predictions = make_predictions(df)
                        st.session_state.predictions_df = predictions_df
                        st.success(f"Generated {len(predictions)} predictions")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        if hasattr(st.session_state, 'model_metrics') and st.session_state.model_metrics[0] is not None:
            r2, mae = st.session_state.model_metrics
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="demo-card card-1"><div class="demo-icon">📊</div><div class="demo-value">{r2:.4f}</div><div class="demo-label">R² Score</div><div class="demo-pct">{"Excellent" if r2 > 0.8 else "Good" if r2 > 0.6 else "Fair"}</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="demo-card card-2"><div class="demo-icon">📉</div><div class="demo-value">{fmt(mae)}</div><div class="demo-label">Mean Absolute Error</div><div class="demo-pct">Average prediction error</div></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="demo-card card-3"><div class="demo-icon">✅</div><div class="demo-value">{r2*100:.1f}%</div><div class="demo-label">Variance Explained</div><div class="demo-pct">Model accuracy</div></div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            quality_text = "The model shows excellent predictive power and can be used reliably." if r2 > 0.8 else "The model shows good predictive power with room for improvement." if r2 > 0.6 else "Consider adding more relevant features to improve accuracy."
            st.markdown(f'''
            <div class="insight-box">
                <span class="insight-tag">Model Interpretation</span>
                <div class="insight-section">
                    <div class="insight-section-title finding">Key Finding</div>
                    <div class="insight-section-text">The RandomForest model predicts <b>total_activity</b> with {r2*100:.1f}% accuracy using lag features and clustering.</div>
                </div>
                <div class="insight-section">
                    <div class="insight-section-title impact">Model Quality</div>
                    <div class="insight-section-text">{quality_text}</div>
                </div>
                <div class="insight-section">
                    <div class="insight-section-title rec">Next Steps</div>
                    <div class="insight-section-text">Use the Insight Chat to generate AI-powered analysis and recommendations based on predictions.</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        if hasattr(st.session_state, 'predictions_df') and st.session_state.predictions_df is not None:
            st.markdown('<div class="section-title">📋 Prediction Results</div>', unsafe_allow_html=True)
            predictions_df = st.session_state.predictions_df
            display_cols = ['state', 'predicted_activity'] if 'state' in predictions_df.columns else ['predicted_activity']
            if 'total_activity' in predictions_df.columns:
                display_cols.append('total_activity')
            st.dataframe(predictions_df[display_cols].head(20), use_container_width=True)

# =====================================================
# INSIGHT CHAT
# =====================================================
elif page == "💬 Insight Chat":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">💬 AI Insights & Chat</div>
        <div class="page-subtitle">AI-powered analytics and data insights for Aadhaar</div>
    </div>
    """, unsafe_allow_html=True)
    
    if df is None:
        st.markdown('<div class="empty-state"><div class="empty-state-icon">💬</div><div class="empty-state-title">No Data Loaded</div><div class="empty-state-text">Upload a CSV dataset from the sidebar to enable AI insights</div></div>', unsafe_allow_html=True)
    else:
        model_status = load_model() is not None
        
        if model_status:
            st.success("✅ AI-powered insights enabled (using trained model)")
        else:
            st.warning("⚠️ Train the model first in 'Predictive Model' page for better insights.")
        
        if "auto_insights" not in st.session_state:
            st.session_state.auto_insights = None
        if "auto_suggestions" not in st.session_state:
            st.session_state.auto_suggestions = None
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        st.markdown('<div class="section-title">📊 Data Insights & Suggestions</div>', unsafe_allow_html=True)
        
        if st.button("🔄 Generate Insights from Data", type="primary", use_container_width=True):
            with st.spinner("🤖 Analyzing your data with AI..."):
                try:
                    insight, suggestions = get_auto_insights(df)
                    st.session_state.auto_insights = insight
                    st.session_state.auto_suggestions = suggestions
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating insights: {str(e)}")
        
        if st.session_state.auto_insights:
            col1, col2 = st.columns(2)
            with col1:
                show_insight(st.session_state.auto_insights)
            with col2:
                if st.session_state.auto_suggestions:
                    render_suggestions_card(st.session_state.auto_suggestions)
        else:
            st.info("👆 Click the button above to generate insights from your uploaded data.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">💭 Ask a Question</div>', unsafe_allow_html=True)
        
        user_query = st.text_input("Enter your question about Aadhaar data", placeholder="e.g. Which states have the highest predicted activity?", key="chat_input")
        
        if st.button("🚀 Get Answer", type="primary"):
            if user_query.strip():
                with st.spinner("🤖 Generating response..."):
                    try:
                        answer = get_chat_answer(user_query, df)
                        st.session_state.current_answer = answer
                        st.session_state.current_question = user_query
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("Please enter a question first.")
        
        if "current_answer" in st.session_state and st.session_state.current_answer:
            st.markdown(f'<div class="question-box"><div class="q-label">Your Question</div><div class="q-text">{st.session_state.get("current_question", "")}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="answer-box"><div class="answer-label">💡 Answer</div><div class="answer-text">{st.session_state.current_answer}</div></div>', unsafe_allow_html=True)
