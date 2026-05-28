import streamlit as st
import requests
import os

# Define dynamic backend URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

def extract_hashtags_and_metrics(text):
    if not text:
        return [], 0, 0, 0, "N/A"
    
    words = text.split()
    word_count = len(words)
    char_count = len(text)
    
    # Simple reading time
    read_time = f"{max(1, round(word_count / 200))} min" if word_count > 100 else f"{max(5, round(word_count * 0.3))} sec"
    
    # Emojis count
    common_emojis = ["🔥", "🚀", "💡", "📈", "🤖", "✨", "🎯", "📊", "🧠", "💼", "🙌", "✅", "⚠️", "🌟"]
    emoji_count = sum(text.count(emoji) for emoji in common_emojis)
    
    # Extract keywords for hashtags
    keywords = ["ai", "tech", "marketing", "business", "growth", "finance", "money", "startup", "design", "code", "dev", "data", "future", "productivity", "management", "strategy", "innovation", "creativity"]
    tags = []
    text_lower = text.lower()
    for kw in keywords:
        if kw in text_lower:
            tags.append(f"#{kw.capitalize()}")
    
    # Fallbacks if no keywords matched
    if not tags:
        tags = ["#ContentRepurposing", "#OmniContent", "#AICreator", "#ViralReach"]
        
    return list(set(tags))[:5], word_count, char_count, emoji_count, read_time


# ----------------------------------
# Page Config
# ----------------------------------

st.set_page_config(
    page_title="OmniContent Studio",
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
          radial-gradient(circle at 15% 20%, rgba(139, 92, 246, 0.18), transparent 45%),
          radial-gradient(circle at 85% 80%, rgba(6, 182, 212, 0.16), transparent 45%),
          radial-gradient(circle at 50% 15%, rgba(236, 72, 153, 0.12), transparent 40%),
          repeating-linear-gradient(45deg, rgba(255, 255, 255, 0.002) 0px, rgba(255, 255, 255, 0.002) 2px, transparent 2px, transparent 10px),
          linear-gradient(rgba(255, 255, 255, 0.004) 1px, transparent 1px),
          linear-gradient(90deg, rgba(255, 255, 255, 0.004) 1px, transparent 1px),
          #0b0c16;
        background-size: 100% 100%, 100% 100%, 100% 100%, 100% 100%, 40px 40px, 40px 40px;
        color: #f1f5f9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    section[data-testid="stSidebar"] {
        background: #04050b !important;
        border-right: 1px solid rgba(6, 182, 212, 0.1) !important;
    }

    .main-title {
        text-align: center;
        font-size: 50px;
        font-weight: 800;
        letter-spacing: -1.5px;
        background: linear-gradient(135deg, #ffffff 20%, #a855f7 60%, #06b6d4 100%);
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
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 12px 20px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: default;
        backdrop-filter: blur(8px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
    }

    .platform-card:hover {
        background: rgba(255, 255, 255, 0.04);
        border-color: rgba(6, 182, 212, 0.4);
        transform: translateY(-4px);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4), 0 0 20px rgba(6, 182, 212, 0.25);
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
        background-color: rgba(255, 255, 255, 0.015) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        transition: all 0.3s ease !important;
    }

    textarea:focus {
        border-color: #06b6d4 !important;
        background-color: rgba(255, 255, 255, 0.03) !important;
        box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.2) !important;
    }

    div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.015) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: white !important;
        transition: all 0.3s ease !important;
    }

    div[data-baseweb="select"] > div:hover {
        border-color: rgba(6, 182, 212, 0.3) !important;
    }

    /* Premium Action Button */
    div.stButton > button {
        width: 100%;
        height: 48px;
        border-radius: 10px;
        border: none;
        background: linear-gradient(135deg, #7c3aed 0%, #06b6d4 100%);
        color: white;
        font-size: 14px;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(6, 182, 212, 0.25);
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.45);
        background: linear-gradient(135deg, #8b5cf6 0%, #0ea5e9 100%);
    }

    /* Glass output */
    .generated-content {
        background: rgba(255, 255, 255, 0.015);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-left: 4px solid #a855f7;
        border-radius: 16px;
        padding: 24px;
        margin-top: 25px;
        line-height: 1.8;
        color: #cbd5e1;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
    }

    /* SEO Health Tags & Optimization Styles */
    .seo-tag {
        background: rgba(6, 182, 212, 0.08);
        border: 1px solid rgba(6, 182, 212, 0.25);
        color: #06b6d4;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 8px;
        display: inline-block;
        box-shadow: 0 2px 10px rgba(6, 182, 212, 0.05);
        transition: all 0.3s ease;
    }

    .seo-tag:hover {
        background: rgba(6, 182, 212, 0.15);
        border-color: #0ea5e9;
        transform: scale(1.05);
    }

    .tags-container {
        display: flex;
        flex-wrap: wrap;
        margin-top: 10px;
        margin-bottom: 20px;
    }

    .optimizer-placeholder {
        background: rgba(255, 255, 255, 0.008);
        border: 1px dashed rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 40px;
        text-align: center;
        color: #94a3b8;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 16px;
        margin-top: 20px;
        backdrop-filter: blur(8px);
    }

    .optimizer-placeholder svg {
        animation: pulse 2s infinite ease-in-out;
    }

    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.7; }
        50% { transform: scale(1.08); opacity: 1; }
        100% { transform: scale(1); opacity: 0.7; }
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------------
# Header
# ----------------------------------

st.markdown(
    '<div class="main-title">OmniContent Studio</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Repurpose a single draft into high-impact posts for LinkedIn, Instagram, X, and YouTube in one click</div>',
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
# Real-time Content Health & SEO Performance Cockpit
# ----------------------------------

st.markdown("---")

st.subheader("⚡ Real-time Content Optimizer & SEO Cockpit")

# Active content to analyze
active_text = None
active_platform = "Generic"
active_tone = "Professional"

if st.session_state.generated_content:
    active_text = st.session_state.generated_content
    active_platform = platform
    active_tone = tone
elif st.session_state.selected_item:
    active_text = st.session_state.selected_item["generated_content"]
    active_platform = st.session_state.selected_item["platform"]
    active_tone = st.session_state.selected_item["tone"]

if active_text:
    tags, word_count, char_count, emoji_count, read_time = extract_hashtags_and_metrics(active_text)
    
    # Layout columns
    opt_col1, opt_col2 = st.columns([1, 1])
    
    with opt_col1:
        st.markdown("#### 📊 Performance Metrics")
        
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.metric("Word Count", f"{word_count} words")
            st.metric("Emoji Density", f"{emoji_count} active")
        with m_col2:
            st.metric("Est. Reading Time", read_time)
            # Simulated reach based on tone and platform
            reach_score = 85
            if active_tone in ["Motivational", "Marketing"]:
                reach_score += 10
            if char_count > 1500:
                reach_score -= 5
            st.metric("Estimated Reach Score", f"{min(98, reach_score)}%")
            
        st.markdown("#### 🏷️ AI Extracted SEO Tags")
        tags_html = " ".join([f'<span class="seo-tag">{tag}</span>' for tag in tags])
        st.markdown(
            f'<div class="tags-container">{tags_html}</div>',
            unsafe_allow_html=True
        )
        
    with opt_col2:
        st.markdown("#### 🎯 Platform Optimization Health")
        
        # Check optimization statuses
        has_emojis = emoji_count > 0
        has_hashtags = len(tags) > 0
        
        if "LinkedIn" in active_platform:
            st.write("**LinkedIn Optimization Check**")
            st.markdown(f"✅ Length: {char_count} chars (Optimized: LinkedIn posts perform best between 500-1500 chars)")
            st.markdown(f"{'✅' if has_emojis else '⚠️'} Rich Formatting: {'Includes engaging emojis' if has_emojis else 'Add 1-3 emojis to boost readability'}")
            st.markdown(f"{'✅' if has_hashtags else '⚠️'} Hashtags: {'Includes relevant hashtags' if has_hashtags else 'Add 2-3 broad tags for organic distribution'}")
        elif "Twitter" in active_platform or "X" in active_platform:
            st.write("**X (Twitter) Optimization Check**")
            is_valid_tweet = char_count <= 280
            st.markdown(f"{'✅' if is_valid_tweet else '⚠️'} Single Tweet Limit: {char_count}/280 chars ({'Perfect length' if is_valid_tweet else 'Exceeds 280 character limit - will require Twitter Blue or thread structure'})")
            st.markdown(f"✅ Tone: {active_tone} (Tone is highly engaging for digital feeds)")
        elif "Instagram" in active_platform:
            st.write("**Instagram Optimization Check**")
            st.markdown(f"✅ Emojis: {emoji_count} (High visual density triggers feed retention)")
            st.markdown(f"{'✅' if has_hashtags else '⚠️'} Discoverability: {'Hashtags active' if has_hashtags else 'Instagram requires 5-10 hashtags in description'}")
        else:
            st.write("**Universal Format Optimization Check**")
            st.markdown(f"✅ Content Tone matches target profile: **{active_tone}**")
            st.markdown(f"✅ Structure: Clear paragraphs and actionable lines")
            
else:
    # Beautiful empty placeholder
    st.markdown(
        """
        <div class="optimizer-placeholder">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-activity"><polyline points="22 12 18 20 15 10 11 22 8 14 4 18"></polyline><path d="M22 12h-4l-2 8-3-10-4 12-3-8-4 4"></path></svg>
            <p>Generate AI content or select an item from history to activate real-time SEO & Health Optimization checks.</p>
        </div>
        """,
        unsafe_allow_html=True
    )