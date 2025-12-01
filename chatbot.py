
import os
import re
import streamlit as st
import pytz
import time
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime


# Load environment variables
load_dotenv()

# Initialize Groq Client with faster timeout
client = Groq(
    api_key="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",
    timeout=5.0
)

# Initialize session state for popup
if "popup_shown" not in st.session_state:
    st.session_state["popup_shown"] = False

# Show popup only if not dismissed
if not st.session_state["popup_shown"]:
    st.markdown("""
        <style>
            /* Centering the popup */
            .popup-container {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: #1E1E2E;
                color: white;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
                width: 90%;
                max-width: 400px;
                text-align: center;
                z-index: 9999;
            }

            /* Responsive text sizes */
            .popup-container h2 {
                color: #7C3AED;
                margin-bottom: 10px;
                font-size: 1.5rem;
            }
            .popup-container p {
                font-size: 1rem;
                opacity: 0.8;
            }

            /* Adjustments for small screens */
            @media (max-width: 480px) {
                .popup-container {
                    width: 80%;
                    max-width: 300px;
                    padding: 15px;
                }
                .popup-container h2 {
                    font-size: 1.3rem;
                }
                .popup-container p {
                    font-size: 0.9rem;
                }
            }
        </style>
        <div class="popup-container">
            <h2>👋 Welcome to AI Assistant Pro!</h2>
            <p>💼 Professional AI assistance for your business needs.</p>
            <p>🔹 Expert responses | 🔹 Reliable & efficient</p>
        </div>
    """, unsafe_allow_html=True)

    # Wait 2 seconds, then update session state
    time.sleep(1)
    st.session_state["popup_shown"] = True
    st.rerun()  # Refresh the page to remove popup


# Function to clean response
def clean_response(text):
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

# Page config
st.set_page_config(
    page_title="AI Assistant Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)



# Custom CSS with fixed footer-style input and title
st.markdown("""
<style>
    /* Core Reset */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    /* Hide Streamlit Components */
    #MainMenu, footer, .stDeployButton, header {
        display: none !important;
    }

    .stApp {
        background: #1E1E2E;
    }

    /* Title Styling */
    .chat-title {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: #1A1A27;
        color: white;
        text-align: center;
        padding: 1rem;
        z-index: 1000;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    .chat-title h1 {
        font-size: 1.5rem;
        margin: 0;
        color: #7C3AED;
    }

    /* Main Chat Area */
    .chat-container {
        position: fixed;
        top: 60px; /* Height of title */
        left: 0;
        right: 0;
        bottom: 80px; /* Height of footer */
        overflow-y: auto;
        padding: 2rem 1rem 1rem;
    }

    /* Messages Styling */
    .message-wrapper {
        display: flex;
        margin: 1rem auto;
        max-width: 850px;
        animation: fadeIn 0.3s ease;
    }

    .user-message, .bot-message {
        padding: 1rem 1.5rem;
        border-radius: 1.5rem;
        max-width: 80%;
        line-height: 1.5;
        position: relative;
        font-size: 0.95rem;
    }

    .user-message {
        background: linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%);
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 0.3rem;
    }

    .bot-message {
        background: #2D2D3F;
        color: #E2E8F0;
        margin-right: auto;
        border-bottom-left-radius: 0.3rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Footer Input Area */
    .chat-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 80px;
        background: #1A1A27;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0 1rem;
        z-index: 1000;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }

    .footer-content {
        max-width: 850px;
        width: 100%;
        display: flex;
        gap: 1rem;
        padding: 0.5rem;
        background: #2D2D3F;
        border-radius: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Form Elements */
    .stForm {
        background: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
        flex-grow: 1;
    }

    .stTextArea > div > div > textarea {
        background: transparent !important;
        border: none !important;
        color: #E2E8F0 !important;
        font-size: 0.95rem !important;
        padding: 0.75rem !important;
        min-height: 68px !important;
        max-height: 68px !important;
        resize: none !important;
        margin: 0 !important;
        line-height: 1.5 !important;
        overflow-y: hidden !important;
    }

    .stTextArea > div > div > textarea:focus {
        outline: none !important;
        box-shadow: none !important;
    }

    /* Send Button */
    .stButton > button {
        background: #7C3AED !important;
        border: none !important;
        border-radius: 0.75rem !important;
        color: white !important;
        padding: 0.5rem 1.5rem !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        height: 45px !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        background: #6D28D9 !important;
        transform: translateY(-1px) !important;
    }

    /* Animations */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 5px;
    }

    ::-webkit-scrollbar-track {
        background: transparent;
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(124, 58, 237, 0.3);
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(124, 58, 237, 0.5);
    }

    /* Message Metadata */
    .message-metadata {
        font-size: 0.7rem;
        opacity: 0.7;
        margin-top: 0.5rem;
        text-align: right;
    }

    /* Code Blocks */
    pre {
        background: #1A1A27 !important;
        border-radius: 0.5rem !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
    }

    code {
        color: #E2E8F0 !important;
        font-size: 0.9rem !important;
    }

        /* Responsive Design */
    @media (max-width: 768px) {
        .chat-container {
            padding: 1rem 0.5rem;
            margin-bottom: 80px;
        }

        .footer-content {
            margin: 0 0.5rem;
        }

        .stTextArea > div > div > textarea {
            background: #2D2D3F !important;
            min-height: 45px !important;
            max-height: 45px !important;
            padding: 0.5rem !important;
        }

        /* Fix for mobile autocomplete background */
        input:-webkit-autofill,
        textarea:-webkit-autofill {
            -webkit-box-shadow: 0 0 0 1000px #2D2D3F inset !important;
            -webkit-text-fill-color: #E2E8F0 !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Add title
st.markdown('<div class="chat-title"><h1>AI Assistant Pro</h1></div>', unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Chat container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display chat history
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.markdown(f"""
            <div class='message-wrapper'>
                <div class='user-message'>
                    <div class='message-content'>{msg['content']}</div>
                    <div class='message-metadata'>{msg['timestamp']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class='message-wrapper'>
                <div class='bot-message'>
                    <div class='message-content'>{msg['content']}</div>
                    <div class='message-metadata'>{msg['timestamp']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Footer with input
st.markdown("""
    <div class="chat-footer">
        <div class="footer-content">
""", unsafe_allow_html=True)

def get_current_time():
    tz = pytz.timezone('Asia/Kolkata')  # Set your timezone here
    current_time = datetime.now(tz)
    return current_time.strftime("%I:%M %p")  # Returns time in 12-hour format with AM/PM

def process_input():
    user_input = st.session_state.get("user_input", "")
    if user_input:
        # Add user message
        st.session_state["messages"].append({
            "role": "user",
            "content": user_input,
            "timestamp": get_current_time()
        })
        
        try:
            # Get AI response
            completion = client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant. Provide concise, accurate responses."},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state["messages"][-5:]]
                ],
                temperature=0.7,
                max_tokens=500,
                top_p=0.95,
            )
            
            # Add bot response
            bot_response = clean_response(completion.choices[0].message.content.strip())
            st.session_state["messages"].append({
                "role": "assistant",
                "content": bot_response,
                "timestamp": get_current_time()
            })
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
        
        finally:
            st.session_state["user_input"] = ""

# Initialize session state for messages if it doesn't exist
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Input form
with st.form(key="chat_input_form", clear_on_submit=True):
    col1, col2 = st.columns([6,1])
    with col1:
        st.text_area(
            label="Message",
            key="user_input",
            label_visibility="collapsed",
            placeholder="Type a message...",
            height=100
        )
    with col2:
        submit_button = st.form_submit_button(
            label="Send",
            on_click=process_input,
            use_container_width=True
        )

st.markdown("</div></div>", unsafe_allow_html=True)


