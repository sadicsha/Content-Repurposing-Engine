import streamlit as st
import requests
from streamlit_calendar import calendar
import os

# Define dynamic backend URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")


# ----------------------------------
# Page Config
# ----------------------------------

st.set_page_config(
    page_title="Content Repurposing Engine",
    layout="wide"
)

# ----------------------------------
# Session State Initialisation  ← FIX: persist output across reruns
# ----------------------------------

if "generated_content" not in st.session_state:
    st.session_state.generated_content = None

if "generation_success" not in st.session_state:
    st.session_state.generation_success = False

if "selected_item" not in st.session_state:
    st.session_state.selected_item = None

# ----------------------------------
# Custom Styling
# ----------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    .stApp {
        background: 
          radial-gradient(circle at 10% 20%, rgba(16, 185, 129, 0.15), transparent 45%),
          radial-gradient(circle at 90% 80%, rgba(6, 182, 212, 0.12), transparent 40%),
          linear-gradient(rgba(255, 255, 255, 0.003) 1px, transparent 1px),
          linear-gradient(90deg, rgba(255, 255, 255, 0.003) 1px, transparent 1px),
          #08090d;
        background-size: 100% 100%, 100% 100%, 40px 40px, 40px 40px;
        color: #f1f5f9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    section[data-testid="stSidebar"] {
        background: #04060a !important;
        border-right: 1px solid rgba(16, 185, 129, 0.1) !important;
    }

    .main-title {
        text-align: center;
        font-size: 50px;
        font-weight: 800;
        letter-spacing: -1.5px;
        background: linear-gradient(135deg, #ffffff 40%, #10b981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 15px;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 16px;
        margin-bottom: 30px;
        font-weight: 400;
    }

    /* Platform Logos Grid */
    .platform-logo-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        flex-wrap: wrap;
        margin-top: 10px;
        margin-bottom: 40px;
    }

    .platform-card {
        background: rgba(255, 255, 255, 0.015);
        border: 1px solid rgba(255, 255, 255, 0.06);
        padding: 12px 20px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: default;
    }

    .platform-card:hover {
        background: rgba(255, 255, 255, 0.03);
        border-color: rgba(16, 185, 129, 0.3);
        transform: translateY(-3px);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 0 15px rgba(16, 185, 129, 0.1);
    }

    .platform-card span {
        color: #cbd5e1;
        font-weight: 600;
        font-size: 13px;
        letter-spacing: -0.2px;
    }

    /* Glassmorphic Fields */
    textarea {
        border-radius: 14px !important;
        background-color: rgba(255, 255, 255, 0.02) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        transition: all 0.3s ease !important;
    }

    textarea:focus {
        border-color: #10b981 !important;
        background-color: rgba(255, 255, 255, 0.04) !important;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2) !important;
    }

    div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: white !important;
        transition: all 0.3s ease !important;
    }

    div[data-baseweb="select"] > div:hover {
        border-color: rgba(16, 185, 129, 0.3) !important;
    }

    /* Premium Action Button */
    div.stButton > button {
        width: 100%;
        height: 48px;
        border-radius: 10px;
        border: none;
        background: linear-gradient(135deg, #0d9488 0%, #10b981 100%);
        color: white;
        font-size: 14px;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.25);
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4);
        background: linear-gradient(135deg, #14b8a6 0%, #059669 100%);
    }

    /* Glass output */
    .generated-content {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-left: 4px solid #10b981;
        border-radius: 16px;
        padding: 24px;
        margin-top: 25px;
        line-height: 1.8;
        color: #cbd5e1;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }

    /* Calendar Styling */
    .fc {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        padding: 15px !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------------
# Header
# ----------------------------------

st.markdown(
    '<div class="main-title">Content Repurposing Engine</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Transform one piece of content into multiple platform-ready formats using AI</div>',
    unsafe_allow_html=True
)

# Supported Platform Showcase
st.markdown(
    """
    <div class="platform-logo-container">
        <div class="platform-card">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="28" height="28" fill="#0077b5"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.779-1.75-1.75s.784-1.75 1.75-1.75 1.75.779 1.75 1.75-.784 1.75-1.75 1.75zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
            <span>LinkedIn</span>
        </div>
        <div class="platform-card">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="28" height="28"><radialGradient id="ig-grad" cx="30%" cy="107%" r="130%"><stop offset="0%" stop-color="#fdf497"/><stop offset="5%" stop-color="#fdf497"/><stop offset="45%" stop-color="#fd5949"/><stop offset="60%" stop-color="#d6249f"/><stop offset="90%" stop-color="#285AEB"/></radialGradient><path fill="url(#ig-grad)" d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
            <span>Instagram</span>
        </div>
        <div class="platform-card">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="28" height="28" fill="#e2e8f0"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
            <span>Twitter / X</span>
        </div>
        <div class="platform-card">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="28" height="28" fill="#ff0000"><path d="M23.498 6.163a3.003 3.003 0 0 0-2.11-2.11C19.518 3.545 12 3.545 12 3.545s-7.518 0-9.388.508a3.003 3.003 0 0 0-2.11 2.11C0 8.033 0 12 0 12s0 3.967.502 5.837a3.003 3.003 0 0 0 2.11 2.11c1.87.508 9.388.508 9.388.508s7.518 0 9.388-.508a3.003 3.003 0 0 0 2.11-2.11C24 15.967 24 12 24 12s0-3.967-.502-5.837zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
            <span>YouTube</span>
        </div>
        <div class="platform-card">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="28" height="28" fill="#10b981"><path d="M12 0c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm0 2c5.514 0 10 4.486 10 10 0 1.223-.223 2.393-.623 3.483l-2.735-7.483h-1.642l-2.008 6.117-1.393-4.237c.504-.251.801-.762.801-1.38 0-.916-.834-1.5-1.9-1.5h-2.5v7h1.5v2.02l-1.36 4.02c-4.103-1.631-7-5.633-7-10.04 0-5.514 4.486-10 10-10zm2 18.96c.646-.07 1.267-.22 1.867-.442l-2.867-8.028v8.47zm-4.186.012c-.529-.684-1.258-2.222-1.258-3.472 0-1.636 1.055-2.784 2.193-2.784h.581l1.523 4.636c-1.026.966-2.057 1.492-3.039 1.62zm1.686-13.472c.491 0 .762.247.762.628 0 .341-.218.591-.762.591h-.9v-1.219h.9z"/></svg>
            <span>Web / Blog</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------------------------
# Sidebar History
# ----------------------------------

st.sidebar.markdown(
    "## Recent Generations"
)

try:

    history_response = requests.get(
        f"{BACKEND_URL}/history"
    )

    if history_response.status_code == 200:

        history = history_response.json()

        if len(history) == 0:
            st.sidebar.info(
                "No generated content yet"
            )

        for item in reversed(history):

            label = f"{item['platform']}"

            if st.sidebar.button(label, key=item['id']):
                # FIX: store in session_state instead of a local variable
                st.session_state.selected_item = item
                st.session_state.generated_content = None  # clear main output when viewing history

except Exception:
    st.sidebar.error(
        "Backend not connected"
    )

# ----------------------------------
# Main Dashboard
# ----------------------------------

st.subheader("Generate Content")

content = st.text_area(
    "Content Input",
    height=260,
    placeholder="Paste your blog, article, idea, transcript, or marketing content here..."
)

col1, col2 = st.columns(2)

with col1:

    platform = st.selectbox(
        "Platform",
        [
            "LinkedIn Post",
            "Instagram Caption",
            "Twitter Post",
            "Blog Summary",
            "YouTube Description"
        ]
    )

with col2:

    tone = st.selectbox(
        "Tone",
        [
            "Professional",
            "Casual",
            "Motivational",
            "Marketing",
            "Funny"
        ]
    )

if st.button("Generate AI Content"):

    # Clear any previously selected history item
    st.session_state.selected_item = None

    payload = {
        "content": content,
        "platform": platform,
        "tone": tone
    }

    try:

        with st.spinner("Generating content..."):
            response = requests.post(
                f"{BACKEND_URL}/generate",
                json=payload
            )

        if response.status_code == 200:

            result = response.json()

            # FIX: save result to session_state so it survives reruns
            st.session_state.generated_content = result["generated_content"]
            st.session_state.generation_success = True

        else:
            st.session_state.generated_content = None
            st.session_state.generation_success = False
            st.error("Failed to generate content")

    except Exception:
        st.session_state.generated_content = None
        st.session_state.generation_success = False
        st.error("Backend server not running")

# FIX: render output OUTSIDE the button block so it persists across reruns
if st.session_state.generated_content:

    st.success("Content generated successfully")

    st.markdown(
        f'''
        <div class="generated-content">
        {st.session_state.generated_content}
        </div>
        ''',
        unsafe_allow_html=True
    )

# ----------------------------------
# Previous Generation Viewer
# ----------------------------------

if st.session_state.selected_item:

    selected_item = st.session_state.selected_item

    st.markdown("---")

    st.subheader("Previous Generation")

    st.write(f"### {selected_item['platform']}")

    st.write(f"**Tone:** {selected_item['tone']}")

    st.write("#### Original Content")

    st.write(selected_item['original_content'])

    st.write("#### Generated Content")

    st.write(selected_item['generated_content'])

    if st.button("Delete Content"):

        delete_response = requests.delete(
            f"{BACKEND_URL}/delete/{selected_item['id']}"
        )

        if delete_response.status_code == 200:

            st.session_state.selected_item = None
            st.success("Content deleted successfully")
            st.rerun()

        else:
            st.error("Failed to delete content")

# ----------------------------------
# Monthly Calendar
# ----------------------------------

st.markdown("---")

st.subheader("Monthly Content Calendar")

calendar_options = {
    "initialView": "dayGridMonth",
    "height": 490,
}

left_space, center_calendar, right_space = st.columns([1, 3, 1])

with center_calendar:

    calendar(
        events=[],
        options=calendar_options
    )