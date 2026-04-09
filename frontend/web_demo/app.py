import streamlit as st
import requests
import uuid
import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/chat")
BRAND_COLOR = "#00CCBB"
LOGO_URL = "https://iptime.com.vn/wp-content/uploads/2025/01/logo-XanhSM-01.jpg"

st.set_page_config(
    page_title="Xanh SM - Trợ Lý Đối Tác",
    page_icon="🚖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR PREMIUM LOOK ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    :root {{
        --xanh-primary: {BRAND_COLOR};
        --xanh-border: rgba(0, 204, 187, 0.2);
        --text-dark: #1E293B;
        --text-muted: #64748B;
    }}

    * {{
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}

    .stApp {{
        background: radial-gradient(circle at 0% 0%, rgba(0, 204, 187, 0.05) 0%, transparent 50%),
                    radial-gradient(circle at 100% 100%, rgba(0, 204, 187, 0.05) 0%, transparent 50%);
    }}

    /* Sidebar Glassmorphism */
    [data-testid="stSidebar"] {{
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(0, 204, 187, 0.1);
    }}

    /* Header styling */
    .main-header {{
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, {BRAND_COLOR}, #008D96);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }}
    
    .sub-header {{
        font-size: 1.1rem;
        color: var(--text-muted);
        margin-bottom: 2.5rem;
        font-weight: 400;
    }}
    
    /* Source tags */
    .source-tag {{
        display: inline-block;
        padding: 4px 12px;
        margin: 8px 8px 0 0;
        background-color: rgba(0, 204, 187, 0.05);
        border: 1px solid var(--xanh-primary);
        border-radius: 20px;
        font-size: 0.75rem;
        color: var(--xanh-primary);
        font-weight: 600;
        transition: all 0.2s;
    }}
    .source-tag:hover {{
        background-color: var(--xanh-primary);
        color: white;
    }}

    /* Hotline Button */
    .hotline-btn {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        background: #EF4444;
        color: white !important;
        padding: 12px;
        border-radius: 12px;
        text-decoration: none;
        font-weight: 700;
        margin-top: 15px;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
    }}

    /* Micro-buttons for feedback */
    .stButton > button[kind="secondary"] {{
        padding: 0.2rem 0.5rem !important;
        font-size: 0.8rem !important;
        min-height: 24px !important;
        line-height: 1 !important;
        border-radius: 8px !important;
    }}

    /* Hide Streamlit elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "failure_count" not in st.session_state:
    st.session_state.failure_count = 0

# --- SIDEBAR ---
with st.sidebar:
    st.image(LOGO_URL, width=160)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🚖 Trợ Lý Tài Xế Xanh SM")
    st.info("Hỗ trợ đối tác tra cứu quy định, chính sách và giải đáp thắc mắc dịch vụ.")
    
    st.markdown("---")
    st.markdown("#### 💡 Câu hỏi thường gặp")
    suggestions = [
        "Quy định về hành lý?",
        "Chính sách giá cước?",
        "Quy định sạc xe điện?",
        "Chính sách thú cưng?"
    ]
    
    for suggestion in suggestions:
        if st.button(suggestion, use_container_width=True):
            st.session_state.pending_prompt = suggestion

    st.markdown("---")
    if st.button("🗑️ Xóa hội thoại", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.failure_count = 0
        st.rerun()
    
    if st.session_state.failure_count >= 2:
        st.error("🆘 Cần hỗ trợ trực tiếp?")
        st.markdown('<a href="tel:19002088" class="hotline-btn">📞 GỌI TỔNG ĐÀI 1900 2088</a>', unsafe_allow_html=True)

    st.divider()
    st.caption("Phiên bản 4.2 | NHM Team")

# --- MAIN UI ---
st.markdown('<div class="main-header">Dịch Vụ Từ Trái Tim ❤️</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Trợ lý ảo thông minh hỗ trợ Đối tác Xanh SM vận hành hiệu quả.</div>', unsafe_allow_html=True)

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            st.markdown('<div style="margin-top: 15px; font-weight: 700; font-size: 0.85rem; opacity: 0.8;">📚 Nguồn tham khảo:</div>', unsafe_allow_html=True)
            for source in message["sources"]:
                st.markdown(f'<span class="source-tag">📄 {source}</span>', unsafe_allow_html=True)
        
        # Feedback Display in History
        if message["role"] == "assistant":
            _, col1, col2 = st.columns([12, 1, 1])
            with col1:
                st.button("👍", key=f"up_{st.session_state.messages.index(message)}", help="Hữu ích")
            with col2:
                st.button("👎", key=f"down_{st.session_state.messages.index(message)}", help="Không hữu ích")

# Chat Input
prompt = st.chat_input("Hỏi tôi bất cứ điều gì về quy định Xanh SM...")

# Handle suggested questions
if hasattr(st.session_state, "pending_prompt"):
    prompt = st.session_state.pending_prompt
    del st.session_state.pending_prompt

if prompt:
    # Append User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process AI Message
    with st.chat_message("assistant"):
        with st.spinner("Đang kết nối hệ thống RAG..."):
            try:
                response = requests.post(
                    BACKEND_URL,
                    json={
                        "prompt": prompt,
                        "thread_id": st.session_state.thread_id
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "Dạ, hệ thống đang gặp chút gián đoạn. Bạn vui lòng thử lại sau.")
                    sources = data.get("sources", [])
                    
                    st.markdown(answer)
                    
                    if sources:
                        st.markdown('<div style="margin-top: 15px; font-weight: 700; font-size: 0.85rem; opacity: 0.8;">📚 Nguồn tham khảo:</div>', unsafe_allow_html=True)
                        for source in sources:
                            st.markdown(f'<span class="source-tag">📄 {source}</span>', unsafe_allow_html=True)
                    
                    # Feedback for current message
                    _, fcol1, fcol2 = st.columns([10, 1, 1])
                    if fcol1.button("👍", key="current_up"):
                        st.toast("Cảm ơn bạn đã phản hồi!")
                    if fcol2.button("👎", key="current_down"):
                        st.session_state.failure_count += 1
                        with st.popover("❌ Báo lỗi"):
                            st.radio("Lý do:", ["Thông tin cũ", "Không liên quan", "Sai số", "Khác"], key="fail_reason")
                            if st.button("Gửi"):
                                st.success("Đã ghi nhận!")
                                if st.session_state.failure_count >= 2:
                                    st.rerun()

                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "sources": sources
                    })
                else:
                    st.error(f"❌ Lỗi kết nối máy chủ ({response.status_code}).")
                    st.session_state.failure_count += 1
            except Exception as e:
                st.error(f"❌ Không thể kết nối tới Backend. ({str(e)})")
                st.session_state.failure_count += 1
