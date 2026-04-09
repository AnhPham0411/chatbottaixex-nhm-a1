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
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/chat")
FEEDBACK_URL = os.getenv("FEEDBACK_URL", "http://localhost:8000/feedback")

# --- BRANDING & ULTRA-PREMIUM CSS ---
st.set_page_config(
    page_title="Xanh SM Driver Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Signature CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --xanh-primary: #008D96;
        --xanh-secondary: #00B4BF;
        --xanh-accent: #7FFFD4;
        --xanh-bg: #F8FAFC;
        --text-dark: #0F172A;
        --text-muted: #64748B;
        --glass-bg: rgba(255, 255, 255, 0.7);
        --glass-border: rgba(255, 255, 255, 0.4);
    }

    * {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Background Gradient */
    .stApp {
        background: radial-gradient(circle at 0% 0%, rgba(0, 141, 150, 0.05) 0%, transparent 50%),
                    radial-gradient(circle at 100% 100%, rgba(0, 180, 191, 0.05) 0%, transparent 50%),
                    #FFFFFF;
    }

    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid var(--glass-border) !important;
    }

    /* Header Styling */
    .premium-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem 2rem;
        background: rgba(255, 255, 255, 0.4);
        backdrop-filter: blur(12px);
        border-bottom: 1px solid var(--glass-border);
        border-radius: 0 0 24px 24px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.02);
    }

    .brand-title {
        font-weight: 800;
        font-size: 1.5rem;
        background: linear-gradient(135deg, var(--xanh-primary), var(--xanh-secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }

    /* Enhanced Chat Bubbles */
    .chat-bubble {
        padding: 1.25rem;
        border-radius: 20px;
        margin-bottom: 1rem;
        max-width: 85%;
        line-height: 1.6;
        font-size: 0.95rem;
        position: relative;
        animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .user-bubble {
        background: var(--xanh-primary);
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 4px;
        box-shadow: 0 10px 15px -3px rgba(0, 141, 150, 0.2);
    }

    .bot-bubble {
        background: white;
        color: var(--text-dark);
        margin-right: auto;
        border-bottom-left-radius: 4px;
        border: 1px solid rgba(0, 141, 150, 0.1);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
    }

    /* Confidence Badge */
    .confidence-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    .conf-low {
        background: #FEF9C3;
        color: #854D0E;
        border: 1px solid #FDE047;
    }
    
    .conf-high {
        background: #DCFCE7;
        color: #166534;
        border: 1px solid #BBF7D0;
    }

    /* Hotline Button Style */
    .hotline-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        background: #EF4444;
        color: white !important;
        padding: 12px 20px;
        border-radius: 12px;
        text-decoration: none;
        font-weight: 700;
        margin-top: 10px;
        transition: transform 0.2s;
    }
    
    .hotline-btn:hover {
        transform: scale(1.02);
        background: #DC2626;
    }

    /* Sources Section */
    .source-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid rgba(0, 0, 0, 0.05);
    }

    .source-tag {
        font-size: 0.7rem;
        background: #F1F5F9;
        color: #64748B;
        padding: 4px 8px;
        border-radius: 6px;
        border: 1px solid #E2E8F0;
    }

    /* Pulse Status */
    .status-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.8rem;
        color: var(--text-muted);
        background: white;
        padding: 6px 12px;
        border-radius: 20px;
        border: 1px solid var(--glass-border);
    }

    .pulse-dot {
        width: 8px;
        height: 8px;
        background: #22C55E;
        border-radius: 50%;
        box-shadow: 0 0 0 rgba(34, 197, 94, 0.4);
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }
        100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
    }

    /* Hide Streamlit components for premium feel */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "failure_count" not in st.session_state:
    st.session_state.failure_count = 0
if "search_only" not in st.session_state:
    st.session_state.search_only = False

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Xanh_SM_logo.svg/2560px-Xanh_SM_logo.svg.png", width=150)
    st.markdown("### 🚖 Trợ Lý Tài Xế")
    
    # Path 4: Recovery (Proactive Hotline in Sidebar too)
    if st.session_state.failure_count >= 2:
        st.error("🆘 Bạn cần hỗ trợ gấp?")
        st.markdown('<a href="tel:19002088" class="hotline-btn">📞 GỌI HOTLINE NGAY</a>', unsafe_allow_html=True)
    else:
        st.markdown('<a href="tel:19002088" class="hotline-btn" style="background: var(--xanh-primary);">📞 Hotline: 1900 2088</a>', unsafe_allow_html=True)

    st.divider()
    
    # Information Hub
    st.subheader("📚 Thông tin hữu ích")
    with st.expander("Quy định & Chính sách", expanded=False):
        st.button("📜 Bộ quy tắc ứng xử", use_container_width=True)
        st.button("💵 Phí & Chiết khấu", use_container_width=True)
        st.button("🔋 Quy định sạc xe", use_container_width=True)
    
    st.divider()
    
    # Settings (Path 3 Toggle)
    st.session_state.search_only = st.toggle("🔍 Chế độ chỉ tra cứu", value=st.session_state.search_only, 
                                            help="Tắt tóm tắt AI, chỉ hiển thị tài liệu gốc.")
    
    st.spacer = st.empty()
    st.caption("Phiên bản 3.0 Enterprise | NHM Team")

# --- MAIN HEADER ---
st.markdown(f"""
    <div class="premium-header">
        <div class="brand-title">Xanh SM Assistant</div>
        <div class="status-indicator">
            <span class="pulse-dot"></span>
            <span>Hệ thống trực tuyến</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- INTERACTION PATHS DISPLAY ---
for idx, msg in enumerate(st.session_state.messages):
    role = msg["role"]
    content = msg["content"]
    thought = msg.get("thought", "")
    sources = msg.get("sources", [])
    confidence = msg.get("confidence", 1.0)
    timestamp = msg.get("timestamp", datetime.datetime.now().strftime("%H:%M %d/%m/%Y"))
    
    if role == "user":
        st.markdown(f'<div class="chat-bubble user-bubble">{content}</div>', unsafe_allow_html=True)
    else:
        # BOT MESSAGE CONTAINER
        with st.container():
            # Path 2: Low Confidence Badge
            if confidence < 0.7:
                st.markdown('<div class="confidence-badge conf-low">⚠️ Cần xác nhận từ CSKH</div>', unsafe_allow_html=True)
            elif confidence > 0.9:
                st.markdown('<div class="confidence-badge conf-high">✅ Đã kiểm chứng</div>', unsafe_allow_html=True)

            # Thought Process (Expandable)
            if thought:
                with st.expander("🔍 Luồng suy nghĩ của AI", expanded=False):
                    st.info(thought)

            # Main Content
            st.markdown(f'<div class="chat-bubble bot-bubble">{content}</div>', unsafe_allow_html=True)
            
            # Path 1: Sources & Path 2: Hotline in bubble
            col1, col2 = st.columns([3, 1])
            with col1:
                if sources:
                    html_sources = "".join([f'<span class="source-tag">📄 {s}</span>' for s in sources])
                    st.markdown(f'<div class="source-container">{html_sources}</div>', unsafe_allow_html=True)
                    st.caption(f"Cập nhật lúc: {timestamp}")
            
            with col2:
                if confidence < 0.7:
                     st.markdown('<a href="tel:19002088" style="font-size: 0.7rem; color: #EF4444; font-weight: 700;">📞 Gọi Hotline</a>', unsafe_allow_html=True)

            # Path 3: Feedback Rating
            if idx == len(st.session_state.messages) - 1:
                fcol1, fcol2, fcol3 = st.columns([1,1,4])
                if fcol1.button("👍", key=f"up_{idx}"):
                    st.toast("Cảm ơn bạn đã phản hồi!")
                if fcol2.button("👎", key=f"down_{idx}"):
                    st.session_state.failure_count += 1
                    with st.popover("❌ Báo lỗi nội dung"):
                        reason = st.radio("Lý do sai:", ["Thông tin cũ", "Không liên quan", "Sai số tiền", "Khác"])
                        if st.button("Gửi báo cáo", key=f"send_{idx}"):
                            st.success("Đã ghi nhận! Chúng tôi sẽ kiểm tra lại.")
                            # Trigger Path 4 check
                            if st.session_state.failure_count >= 2:
                                st.rerun()

# --- CHAT INPUT ---
if prompt := st.chat_input("Hỏi về quy định, chính sách, hoặc hỗ trợ..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Process Response
    with st.spinner("Đang truy xuất dữ liệu..."):
        try:
            # Simulate real backend behavior
            payload = {
                "message": prompt,
                "driver_id": "DRV_123456",
                "search_only": st.session_state.search_only
            }
            
            response = requests.post(BACKEND_URL, json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                # Mock missing fields for demo if not present
                reply = data.get("reply", "Xin lỗi, tôi gặp trục trặc khi xử lý câu trả lời.")
                thought = data.get("thought", "Hệ thống đang phân tích dựa trên Vector DB...")
                sources = data.get("sources", ["Sổ tay tài xế 2024"])
                confidence = data.get("confidence", 0.95) # Default high
                
                # Logic to trigger Path 2 for specific demo keywords if needed
                if "tiền" in prompt.lower() or "phạt" in prompt.lower():
                    confidence = 0.65 # Mock low confidence for sensitive topics
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reply,
                    "thought": thought,
                    "sources": sources,
                    "confidence": confidence,
                    "timestamp": datetime.datetime.now().strftime("%H:%M %d/%m/%Y")
                })
            else:
                st.error("Backend không phản hồi. Đang sử dụng chế độ dự phòng.")
                st.session_state.failure_count += 1
        except Exception as e:
            st.error(f"Lỗi kết nối: {str(e)}")
            st.session_state.failure_count += 1
    
    st.rerun()
