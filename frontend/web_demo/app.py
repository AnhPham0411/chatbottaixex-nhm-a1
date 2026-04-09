import streamlit as st
import requests
import time
import os
import uuid
import datetime
from dotenv import load_dotenv

# Load environment variables if .env exists
load_dotenv()

# --- CONFIGURATION ---
# BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/chat")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/chat")

BRAND_COLOR = "#00CCBB"
LOGO_URL = "https://www.xanhsm.com/wp-content/uploads/2023/04/Logo-Xanh-SM.png"

# --- BRANDING & ULTRA-PREMIUM CSS ---
st.set_page_config(
    page_title="Xanh SM - Trợ Lý Đối Tác",
    page_icon="🚖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Signature CSS (Combined Cyan Brand + Glassmorphism)
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    :root {{
        --xanh-primary: {BRAND_COLOR};
        --xanh-secondary: #00B4BF;
        --xanh-accent: #7FFFD4;
        /* Using Streamlit theme variables */
        --st-bg: var(--background-color);
        --st-secondary-bg: var(--secondary-background-color);
        --st-text: var(--text-color);
    }}

    * {{
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}

    /* Background Gradient - Subtle in Dark Mode */
    .stApp {{
        background: radial-gradient(circle at 0% 0%, rgba(0, 204, 187, 0.03) 0%, transparent 50%),
                    radial-gradient(circle at 100% 100%, rgba(0, 180, 191, 0.03) 0%, transparent 50%),
                    var(--st-bg);
    }}

    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] {{
        background: var(--st-secondary-bg) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(128, 128, 128, 0.1) !important;
    }}

    /* Header Styling - Adaptive */
    .premium-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 1.5rem;
        background: rgba(128, 128, 128, 0.05);
        backdrop-filter: blur(12px);
        border-bottom: 1px solid rgba(128, 128, 128, 0.1);
        border-radius: 0 0 20px 20px;
        margin-bottom: 2rem;
    }}

    .brand-title {{
        font-weight: 800;
        font-size: 1.2rem;
        background: linear-gradient(135deg, var(--xanh-primary), var(--xanh-secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }}

    /* Adaptive Chat Bubbles */
    .chat-bubble {{
        padding: 1rem 1.25rem;
        border-radius: 18px;
        margin-bottom: 0.75rem;
        max-width: 85%;
        line-height: 1.5;
        font-size: 0.95rem;
        position: relative;
        animation: slideUp 0.3s ease-out;
    }}

    @keyframes slideUp {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    .user-bubble {{
        background: var(--xanh-primary);
        color: white !important;
        margin-left: auto;
        border-bottom-right-radius: 4px;
        box-shadow: 0 4px 15px rgba(0, 204, 187, 0.15);
    }}

    .bot-bubble {{
        background: var(--st-secondary-bg);
        color: var(--st-text);
        margin-right: auto;
        border-bottom-left-radius: 4px;
        border: 1px solid rgba(128, 128, 128, 0.1);
    }}

    /* Confidence Badge */
    .confidence-badge {{
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 8px;
    }}
    
    .conf-low {{ background: rgba(254, 249, 195, 0.2); color: #EAB308; border: 1px solid rgba(234, 179, 8, 0.3); }}
    .conf-high {{ background: rgba(220, 252, 231, 0.2); color: #22C55E; border: 1px solid rgba(34, 197, 94, 0.3); }}

    /* Hotline Button */
    .hotline-btn {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        background: #EF4444;
        color: white !important;
        padding: 10px 15px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: 700;
        font-size: 0.9rem;
        margin-top: 10px;
    }}

    /* Micro-buttons */
    .stButton > button[kind="secondary"] {{
        padding: 0.2rem 0.5rem !important;
        font-size: 0.8rem !important;
        border-radius: 8px !important;
    }}

    /* Adaptive Source Tags */
    .source-tag {{
        display: inline-block;
        padding: 2px 10px;
        margin: 5px 5px 0 0;
        background: rgba(0, 204, 187, 0.05);
        border: 1px solid rgba(0, 204, 187, 0.2);
        border-radius: 15px;
        font-size: 0.75rem;
        color: var(--xanh-primary);
    }}

    /* Clean UI */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "failure_count" not in st.session_state:
    st.session_state.failure_count = 0
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# --- SIDEBAR ---
with st.sidebar:
    st.image(LOGO_URL, width=150)
    st.markdown("### 🚖 Trợ Lý Đối Tác")
    st.info("Hỗ trợ Đối tác tra cứu quy định, chính sách và hướng dẫn vận hành nhanh chóng.")
    
    if st.button("🗑️ Xoá lịch sử chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

    if st.session_state.failure_count >= 2:
        st.error("🆘 Cần hỗ trợ gấp?")
        st.markdown('<a href="tel:19002088" class="hotline-btn">📞 GỌI HOTLINE NGAY</a>', unsafe_allow_html=True)

    st.divider()
    st.caption("Phiên bản 4.0 | Xanh SM NHM Team")

# --- MAIN HEADER ---
st.markdown(f"""
    <div class="premium-header">
        <div class="brand-title">Dịch Vụ Từ Trái Tim ❤️</div>
    </div>
""", unsafe_allow_html=True)

# --- CHAT DISPLAY ---
for idx, msg in enumerate(st.session_state.messages):
    role = msg["role"]
    content = msg["content"]
    sources = msg.get("sources", [])
    
    if role == "user":
        st.markdown(f'<div class="chat-bubble user-bubble">{content}</div>', unsafe_allow_html=True)
    else:
        with st.chat_message("assistant"):
            st.markdown(content)
            if sources:
                st.markdown('<div style="margin-top: 10px; font-weight: 600; font-size: 0.85rem;">📚 Nguồn tham khảo:</div>', unsafe_allow_html=True)
                for source in sources:
                    title = source.get("title", "") if isinstance(source, dict) else source
                    st.markdown(f'<span class="source-tag">{title}</span>', unsafe_allow_html=True)

# --- CHAT INPUT ---
if prompt := st.chat_input("Hỏi về quy định, chính sách..."):
    pass # logic below handles both input methods

if hasattr(st.session_state, "pending_prompt"):
    prompt = st.session_state.pending_prompt
    del st.session_state.pending_prompt

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Logic xử lý tin nhắn mới nhất
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_prompt = st.session_state.messages[-1]["content"]
    
    with st.chat_message("assistant"):
        with st.spinner("Xanh SM đang tra cứu..."):
            try:
                response = requests.post(
                    BACKEND_URL,
                    json={
                        "message": last_prompt,
                        "thread_id": st.session_state.thread_id
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("reply", "Dạ, tôi chưa có thông tin cụ thể về vấn đề này.")
                    sources = data.get("sources", [])
                    
                    st.markdown(answer)
                    if sources:
                        st.markdown('<div style="margin-top: 10px; font-weight: 600; font-size: 0.85rem;">📚 Nguồn tham khảo:</div>', unsafe_allow_html=True)
                        for source in sources:
                            st.markdown(f'<span class="source-tag">{source}</span>', unsafe_allow_html=True)
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                else:
                    st.error(f"❌ Lỗi kết nối Backend ({response.status_code})")
                    st.session_state.failure_count += 1
            except Exception as e:
                st.error(f"❌ Lỗi: {str(e)}")
                st.session_state.failure_count += 1
    st.rerun()
