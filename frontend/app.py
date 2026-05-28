import streamlit as st
import requests
from streamlit_calendar import calendar

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
          radial-gradient(circle at 80% 20%, rgba(99, 102, 241, 0.12), transparent 50%),
          radial-gradient(circle at 20% 80%, rgba(168, 85, 247, 0.08), transparent 40%),
          linear-gradient(rgba(255, 255, 255, 0.005) 1px, transparent 1px),
          linear-gradient(90deg, rgba(255, 255, 255, 0.005) 1px, transparent 1px),
          #020617;
        background-size: 100% 100%, 100% 100%, 30px 30px, 30px 30px;
        color: #f1f5f9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    section[data-testid="stSidebar"] {
        background: #030816 !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
    }

    .main-title {
        text-align: center;
        font-size: 50px;
        font-weight: 800;
        letter-spacing: -1.5px;
        background: linear-gradient(135deg, #ffffff 40%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 15px;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 16px;
        margin-bottom: 35px;
        font-weight: 400;
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
        border-color: #8b5cf6 !important;
        background-color: rgba(255, 255, 255, 0.04) !important;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2) !important;
    }

    div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: white !important;
        transition: all 0.3s ease !important;
    }

    div[data-baseweb="select"] > div:hover {
        border-color: rgba(139, 92, 246, 0.3) !important;
    }

    /* Premium Action Button */
    div.stButton > button {
        width: 100%;
        height: 48px;
        border-radius: 10px;
        border: none;
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
        color: white;
        font-size: 14px;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.25);
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(124, 58, 237, 0.4);
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
    }

    /* Glass output */
    .generated-content {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
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

# ----------------------------------
# Sidebar History
# ----------------------------------

st.sidebar.markdown(
    "## Recent Generations"
)

try:

    history_response = requests.get(
        "http://127.0.0.1:8000/history"
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
                "http://127.0.0.1:8000/generate",
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
            f"http://127.0.0.1:8000/delete/{selected_item['id']}"
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