# ============================================================
# main.py  —  Home Page (entry point of the Streamlit app)
# Run this file with:  streamlit run main.py
# ============================================================

import streamlit as st
from utils.db_connection import create_tables

# --- Page config (must be the FIRST streamlit command) ---
st.set_page_config(
    page_title="Cricbuzz LiveStats",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Create DB tables on first run ---
create_tables()

# --- Custom CSS for a nicer look ---
st.markdown("""
    <style>
        .main-title {
            font-size: 3rem;
            font-weight: 800;
            color: #1a1a2e;
        }
        .subtitle {
            font-size: 1.2rem;
            color: #555;
            margin-bottom: 2rem;
        }
        .feature-card {
            background: #f8f9fa;
            border-left: 4px solid #0066cc;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("# 🏏 Cricbuzz LiveStats")
st.markdown("### Real-Time Cricket Insights & SQL-Based Analytics")
st.divider()

# --- Introduction ---
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("## Welcome!")
    st.write("""
    This dashboard brings together **live cricket data** from the Cricbuzz API 
    and **SQL-powered analytics** into one interactive platform.
    
    Navigate using the **sidebar** on the left to explore all features.
    """)

    st.markdown("### What you can do here:")

    features = [
        ("🔴 Live Matches",     "Watch live scorecard updates in real time"),
        ("📊 Player Stats",     "Browse top batting & bowling rankings by format"),
        ("🔍 SQL Analytics",    "Run 25 pre-built queries on the cricket database"),
        ("🛠️ CRUD Operations", "Add, update, or delete player and match records"),
    ]

    for icon_title, desc in features:
        st.markdown(f"""
        <div class="feature-card">
            <strong>{icon_title}</strong><br>
            <span style="color:#555;">{desc}</span>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("### Tech Stack")
    st.markdown("""
    | Tool | Purpose |
    |------|---------|
    | 🐍 Python | Core language |
    | 🌐 Streamlit | Web UI |
    | 🗄️ SQLite | Database |
    | 📡 Cricbuzz API | Live data |
    | 🐼 Pandas | Data display |
    """)

    st.markdown("### Project Info")
    st.info("**Domain:** Sports Analytics\n\n**Pages:** 5\n\n**SQL Queries:** 25")

st.divider()

# --- Quick Start Guide ---
st.markdown("## Quick Start")

step1, step2, step3 = st.columns(3)

with step1:
    st.markdown("#### Step 1 — Setup")
    st.code("pip install streamlit requests pandas", language="bash")
    st.write("Install all required libraries.")

with step2:
    st.markdown("#### Step 2 — API Key")
    st.write("Get your free API key from [RapidAPI Cricbuzz](https://rapidapi.com/cricketapilive/api/cricbuzz-cricket/) and add it to `utils/api_helper.py`.")

with step3:
    st.markdown("#### Step 3 — Run")
    st.code("streamlit run main.py", language="bash")
    st.write("Open your browser at `http://localhost:8501`.")

st.divider()
st.caption("Built with Python · Streamlit · SQLite · Cricbuzz API")
