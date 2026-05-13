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
# Custom Styling
# ----------------------------------

st.markdown(
    """
    <style>

    .stApp {
        background:
        radial-gradient(circle at top left, rgba(59,130,246,0.18), transparent 22%),
        radial-gradient(circle at bottom right, rgba(168,85,247,0.16), transparent 22%),
        linear-gradient(135deg, #020617, #0f172a, #111827);

        color: white;
    }

    section[data-testid="stSidebar"] {
        background: rgba(2,6,23,0.95);
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    .main-title {
        font-size: 58px;
        font-weight: 800;
        color: white;
        letter-spacing: -1px;
        margin-bottom: 8px;
    }

    .subtitle {
        color: #94a3b8;
        font-size: 18px;
        margin-bottom: 35px;
    }

    textarea {
        border-radius: 18px !important;
        background-color: rgba(255,255,255,0.04) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }

    div[data-baseweb="select"] > div {
        background-color: rgba(255,255,255,0.04) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }

    div.stButton > button {

        width: 100%;
        height: 50px;
        border-radius: 14px;
        border: none;
        background:
        linear-gradient(to right, #2563eb, #7c3aed);
        color: white;
        font-size: 14px;
        font-weight: 500;
        transition: 0.3s ease;
        box-shadow:
        0 10px 25px rgba(37,99,235,0.25);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        padding: 6px 10px;
    }

    div.stButton > button:hover {

        transform: translateY(-2px);

        box-shadow:
        0 10px 22px rgba(124,58,237,0.30);
    }

    .generated-content {
        background: rgba(15,23,42,0.8);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 22px;
        padding: 24px;
        margin-top: 25px;
        line-height: 1.8;
        color: #e2e8f0;
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

selected_item = None

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

            label = (
                f"{item['platform']}"
            )

            if st.sidebar.button(
                label,
                key=item['id']
            ):
                selected_item = item

except:
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

    payload = {
        "content": content,
        "platform": platform,
        "tone": tone
    }

    try:

        response = requests.post(
            "http://127.0.0.1:8000/generate",
            json=payload
        )

        if response.status_code == 200:

            result = response.json()

            st.success(
                "Content generated successfully"
            )

            st.markdown(
                f'''
                <div class="generated-content">
                {result["generated_content"]}
                </div>
                ''',
                unsafe_allow_html=True
            )

        else:
            st.error(
                "Failed to generate content"
            )

    except:
        st.error(
            "Backend server not running"
        )

# ----------------------------------
# Previous Generation Viewer
# ----------------------------------

if selected_item:

    st.markdown("---")

    st.subheader(
        "Previous Generation"
    )

    st.write(
        f"### {selected_item['platform']}"
    )

    st.write(
        f"**Tone:** {selected_item['tone']}"
    )

    st.write(
        "#### Original Content"
    )

    st.write(
        selected_item['original_content']
    )

    st.write(
        "#### Generated Content"
    )

    st.write(
        selected_item['generated_content']
    )

    if st.button(
        "Delete Content"
    ):

        delete_response = requests.delete(
            f"http://127.0.0.1:8000/delete/{selected_item['id']}"
        )

        if delete_response.status_code == 200:

            st.success(
                "Content deleted successfully"
            )

            st.rerun()

        else:
            st.error(
                "Failed to delete content"
            )

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