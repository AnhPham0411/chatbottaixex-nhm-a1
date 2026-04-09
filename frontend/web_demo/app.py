import streamlit as st
import requests
import uuid

# --- CONFIGURATION ---
BACKEND_URL = "http://localhost:8000/chat"
BRAND_COLOR = "#00CCBB"
LOGO_URL = "https://www.xanhsm.com/wp-content/uploads/2023/04/Logo-Xanh-SM.png"

st.set_page_config(
    page_title="Xanh SM - Trợ Lý Đối Tác",
    page_icon="🚖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR PREMIUM LOOK ---
st.markdown(f"""
    <style>
    /* Main branding color */
    :root {{
        --primary-color: {BRAND_COLOR};
    }}
    
    .stApp {{
        background-color: transparent;
    }}
    
    /* Header styling */
    .main-header {{
        font-size: 2.2rem;
        font-weight: 700;
        color: {BRAND_COLOR};
        margin-bottom: 0.5rem;
    }}
    
    .sub-header {{
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }}
    
    /* Chat message styling */
    .stChatMessage {{
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }}
    
    /* Sidebar styling */
    .css-1d391kg {{
        background-color: #f8f9fa;
    }}
    
    /* Source tags */
    .source-tag {{
        display: inline-block;
        padding: 2px 10px;
        margin: 5px 5px 0 0;
        background-color: rgba(0, 204, 187, 0.1);
        border: 1px solid {BRAND_COLOR};
        border-radius: 20px;
        font-size: 0.8rem;
        color: {BRAND_COLOR};
        font-weight: 500;
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

# --- SIDEBAR ---
with st.sidebar:
    st.image(LOGO_URL, width=150)
    st.markdown("---")
    st.title("🚖 Trợ Lý Xanh SM")
    st.info("Hỗ trợ Đối tác tra cứu quy định, chính sách và hướng dẫn vận hành nhanh chóng.")
    
    st.markdown("### 💡 Câu hỏi gợi ý")
    suggestions = [
        "Quy định về hành lý?",
        "Chính sách giá cước?",
        "Làm sao để đăng ký đối tác?",
        "Quy định về thú cưng?"
    ]
    
    for suggestion in suggestions:
        if st.button(suggestion, use_container_width=True):
            st.session_state.pending_prompt = suggestion

    st.markdown("---")
    if st.button("🗑️ Xóa lịch sử chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

# --- MAIN UI ---
st.markdown('<div class="main-header">Dịch Vụ Từ Trái Tim ❤️</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Hệ thống giải đáp thông tin chính thức dành cho Đối tác Xanh SM.</div>', unsafe_allow_html=True)

# Hiển thị lịch sử chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            st.markdown('<div style="margin-top: 10px;"><b>📚 Nguồn tham khảo:</b></div>', unsafe_allow_html=True)
            cols = st.columns(len(message["sources"]))
            for idx, source in enumerate(message["sources"]):
                st.markdown(f'<span class="source-tag">{source}</span>', unsafe_allow_html=True)

# Xử lý input
prompt = st.chat_input("Nhập câu hỏi của bạn tại đây...")

# Nếu có prompt từ nút gợi ý
if hasattr(st.session_state, "pending_prompt"):
    prompt = st.session_state.pending_prompt
    del st.session_state.pending_prompt

if prompt:
    # Thêm user message vào UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gọi API Backend
    with st.chat_message("assistant"):
        with st.spinner("Xanh SM đang tra cứu..."):
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
                    answer = data.get("answer", "Dạ, tôi không tìm thấy câu trả lời.")
                    sources = data.get("sources", [])
                    
                    st.markdown(answer)
                    
                    if sources:
                        st.markdown('<div style="margin-top: 10px;"><b>📚 Nguồn tham khảo:</b></div>', unsafe_allow_html=True)
                        for source in sources:
                            st.markdown(f'<span class="source-tag">{source}</span>', unsafe_allow_html=True)
                    
                    # Lưu lại lịch sử
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "sources": sources
                    })
                else:
                    error_msg = f"❌ Lỗi kết nối ({response.status_code})."
                    st.error(error_msg)
            except Exception as e:
                st.error(f"❌ Không thể kết nối tới máy chủ AI. Vui lòng thử lại sau. ({str(e)})")
