import streamlit as st
import pandas as pd
import time
import re
import plotly.graph_objects as go
from utils import (
    extract_text_from_pdf, 
    extract_text_from_docx, 
    match_skills, 
    get_resume_suggestions, 
    generate_resume, 
    generate_cover_letter,
    discover_career_opportunities,
    evaluate_universal_resume
)
import db_auth as auth
import demo_data

# Must be the first Streamlit command
st.set_page_config(page_title="Resume Analyzer Pro", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

# Initialize session state first
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''
if 'selected_page' not in st.session_state:
    st.session_state['selected_page'] = "📊 Dashboard"
if 'demo_mode_active' not in st.session_state:
    st.session_state['demo_mode_active'] = False
if 'analyzer_use_demo' not in st.session_state:
    st.session_state['analyzer_use_demo'] = False
if 'sample_profile_choice' not in st.session_state:
    st.session_state['sample_profile_choice'] = 'Tech & AI (Alex Morgan — Senior Engineer)'
if 'job_search_target' not in st.session_state:
    st.session_state['job_search_target'] = ''
if 'cl_use_demo' not in st.session_state:
    st.session_state['cl_use_demo'] = False

def navigate_to(page_name):
    st.session_state['selected_page'] = page_name
    st.rerun()

def activate_demo_data():
    demo_data.seed_demo_user()
    st.session_state['logged_in'] = True
    st.session_state['username'] = 'DemoUser'
    st.session_state['demo_mode_active'] = True
    st.session_state['analyzer_use_demo'] = True
    st.session_state['cl_use_demo'] = True
    for k, v in demo_data.SAMPLE_BUILDER_INPUTS.items():
        st.session_state[f'builder_{k}'] = v

def clear_demo_data():
    st.session_state['demo_mode_active'] = False
    st.session_state['analyzer_use_demo'] = False
    st.session_state['cl_use_demo'] = False
    if st.session_state.get('username') == 'DemoUser':
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');

/* Do NOT hide the header or toolbar so sidebar controls are never destroyed */
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 3.5rem !important;
    z-index: 99999 !important;
}

/* Hide deploy button, running status, and main menu */
.stDeployButton,
[data-testid="stStatusWidget"],
#MainMenu,
footer {
    display: none !important;
    visibility: hidden !important;
}

/* Ensure the top-left sidebar open arrow is ALWAYS visible and clickable */
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    color: #fbbf24 !important;
    cursor: pointer !important;
    z-index: 100000 !important;
}

[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    position: fixed !important;
    top: 14px !important;
    left: 14px !important;
    background: rgba(15, 20, 32, 0.9) !important;
    border: 1.5px solid #f59e0b !important;
    border-radius: 10px !important;
    padding: 6px 10px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.7), 0 0 15px rgba(245, 158, 11, 0.3) !important;
    backdrop-filter: blur(12px) !important;
}

[data-testid="stSidebarCollapsedControl"]:hover,
[data-testid="collapsedControl"]:hover {
    background: rgba(245, 158, 11, 0.2) !important;
    border-color: #fbbf24 !important;
    transform: scale(1.06) !important;
    box-shadow: 0 6px 25px rgba(245, 158, 11, 0.45) !important;
}

/* Hide confusing markdown header anchor links */
[data-testid="stHeaderActionElements"],
a.header-anchor,
.stMarkdown a[href^="#"] {
    display: none !important;
}

/* Logo Home Button Styling with metallic gold sheen */
div[data-testid*="btn_logo_brand"] button,
button[key="btn_logo_brand"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 6px 10px !important;
    text-align: left !important;
    cursor: pointer !important;
}
div[data-testid*="btn_logo_brand"] button:hover {
    background: rgba(245, 158, 11, 0.08) !important;
    border-radius: 10px !important;
    box-shadow: 0 0 20px rgba(245, 158, 11, 0.15) !important;
    transform: none !important;
}
div[data-testid*="btn_logo_brand"] button * {
    background: linear-gradient(135deg, #ffffff 0%, #fef08a 40%, #f59e0b 80%, #fbbf24 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    font-size: 1.45rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.5px !important;
}

/* Top Nav Pills styling */
[data-testid="stPills"] {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}

.block-container {
    padding-top: 1.5rem !important;
}

/* Custom scrollbars with gold glow */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: #07090e;
}
::-webkit-scrollbar-thumb {
    background: rgba(245, 158, 11, 0.3);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(245, 158, 11, 0.6);
}
</style>
""", unsafe_allow_html=True)

# --- Native Clean Top Header with Clickable Logo, Demo Quick-Toggle, and Auth ---
col_logo, col_tagline, col_demo_btn, col_auth = st.columns([3.4, 3.0, 2.0, 1.6])
with col_logo:
    if st.button("👑 Resume Analyzer Pro", key="btn_logo_brand", use_container_width=True):
        navigate_to("📊 Dashboard")

with col_tagline:
    st.markdown("<div style='padding-top: 10px; color: #fbbf24; font-size: 0.95rem; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase;'>✦ AI CAREER INTELLIGENCE PLATFORM</div>", unsafe_allow_html=True)

with col_demo_btn:
    if st.session_state.get('demo_mode_active'):
        if st.button("🔄 Reset Demo", key="hdr_reset_demo_btn", use_container_width=True):
            clear_demo_data()
            navigate_to("📊 Dashboard")
    else:
        if st.button("✨ Load Demo Data", key="hdr_load_demo_btn", use_container_width=True):
            activate_demo_data()
            navigate_to("📊 Dashboard")

with col_auth:
    if st.session_state.get('logged_in'):
        if st.button(f"Logout ({st.session_state['username']})", use_container_width=True, key="hdr_logout_btn"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = ''
            st.session_state['demo_mode_active'] = False
            navigate_to("📊 Dashboard")
    else:
        if st.button("🚀 Sign In", use_container_width=True, key="hdr_signin_btn"):
            st.session_state['redirect_after_login'] = st.session_state.get('selected_page', '📊 Dashboard')
            navigate_to("👤 Account")
st.markdown("---")

# --- Custom CSS for "Lavish Dark Luxury" Look ---
st.markdown("""
    <style>
    /* Main luxury background with deep mesh radial lighting */
    .stApp {
        background: radial-gradient(circle at 12% 15%, rgba(139, 92, 246, 0.12) 0%, transparent 45%),
                    radial-gradient(circle at 88% 85%, rgba(217, 119, 6, 0.12) 0%, transparent 50%),
                    radial-gradient(circle at 50% 40%, rgba(99, 102, 241, 0.08) 0%, transparent 60%),
                    #07090e !important;
        background-attachment: fixed !important;
        color: #f1f5f9 !important;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Sidebar: Obsidian velvet with gold edge */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #07090e 0%, #0d121e 100%) !important;
        border-right: 1px solid rgba(245, 158, 11, 0.2) !important;
        box-shadow: 10px 0 30px rgba(0, 0, 0, 0.5) !important;
    }
    
    /* Sidebar Navigation Menu (Radio) Styling */
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        transition: all 0.25s ease !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: rgba(245, 158, 11, 0.12) !important;
        border-color: rgba(251, 191, 36, 0.45) !important;
        transform: translateX(4px) !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label p {
        font-size: 1.15rem !important; 
        font-weight: 600 !important;
        color: #f8fafc !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {
        gap: 1.1rem !important;
        padding-top: 10px;
    }
    
    /* Headers with shimmering metallic finish */
    h1, h2, h3, h4, h5, h6 {
        color: #f8fafc !important;
        font-weight: 700 !important;
        letter-spacing: -0.3px;
    }
    
    /* Cards: Frosted Obsidian Glass with 24K Gold Rim */
    .pro-card {
        background: linear-gradient(135deg, rgba(20, 26, 42, 0.75) 0%, rgba(13, 18, 30, 0.88) 100%) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(245, 158, 11, 0.22) !important;
        border-radius: 16px !important;
        padding: 26px !important;
        margin-bottom: 22px !important;
        box-shadow: 0 12px 35px -8px rgba(0, 0, 0, 0.7), 0 0 20px rgba(245, 158, 11, 0.06), inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    .pro-card:hover {
        border-color: rgba(251, 191, 36, 0.5) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 20px 45px -10px rgba(0, 0, 0, 0.85), 0 0 30px rgba(245, 158, 11, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
    }
    
    /* Increase Global Font Size */
    p, li, label, .stTextInput input, .stTextArea textarea, .stMarkdown {
        font-size: 1.08rem !important;
    }

    /* Buttons - Gilded Champagne Gold with Rich Luster */
    .stButton>button, 
    .stFormSubmitButton>button, 
    [data-testid="stFormSubmitButton"]>button,
    button[data-testid="stBaseButton-primary"],
    button[kind="primary"] {
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 50%, #d97706 100%) !important;
        color: #090d16 !important;
        border: 1px solid rgba(254, 240, 138, 0.6) !important;
        border-radius: 10px !important;
        padding: 0.65rem 1.4rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.2px !important;
        box-shadow: 0 4px 20px rgba(245, 158, 11, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.4) !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
        width: 100% !important;
        cursor: pointer !important;
    }
    /* Force internal button text to be dark obsidian and bold for crisp contrast */
    .stButton>button *, 
    .stFormSubmitButton>button *, 
    [data-testid="stFormSubmitButton"]>button *,
    button[data-testid="stBaseButton-primary"] *,
    button[kind="primary"] * {
        color: #090d16 !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }
    .stButton>button:hover, 
    .stFormSubmitButton>button:hover, 
    [data-testid="stFormSubmitButton"]>button:hover,
    button[data-testid="stBaseButton-primary"]:hover,
    button[kind="primary"]:hover {
        box-shadow: 0 8px 30px rgba(245, 158, 11, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.6) !important;
        transform: translateY(-2px) scale(1.01) !important;
        background: linear-gradient(135deg, #fef08a 0%, #fbbf24 50%, #f59e0b 100%) !important;
    }

    /* Download Buttons - Radiant Jewel Emerald */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #059669 0%, #10b981 50%, #34d399 100%) !important;
        color: #062419 !important;
        border: 1px solid rgba(110, 231, 183, 0.5) !important;
        border-radius: 10px !important;
        padding: 0.65rem 1.4rem !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
        transition: all 0.25s ease !important;
        width: 100% !important;
        cursor: pointer !important;
    }
    .stDownloadButton>button * {
        color: #062419 !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }
    .stDownloadButton>button:hover {
        box-shadow: 0 8px 30px rgba(16, 185, 129, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.5) !important;
        transform: translateY(-2px) scale(1.01) !important;
        background: linear-gradient(135deg, #10b981 0%, #34d399 60%, #6ee7b7 100%) !important;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 2.3rem !important;
        background: linear-gradient(135deg, #ffffff 0%, #fde047 40%, #f59e0b 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        font-weight: 800;
    }
    [data-testid="stMetricLabel"] {
        color: #cbd5e1 !important;
        font-weight: 600;
        font-size: 1.05rem !important;
    }
    
    /* Text colors */
    p, li, .stMarkdown, .stText, label {
        color: #cbd5e1 !important;
    }
    
    /* Subtitles / small text */
    .pro-subtitle {
        color: #94a3b8 !important;
        font-size: 1.15rem;
    }
    
    /* Form Inputs and Textareas */
    .stTextInput input, 
    .stTextArea textarea, 
    .stSelectbox [data-baseweb="select"] {
        background-color: rgba(13, 18, 30, 0.85) !important;
        border: 1px solid rgba(245, 158, 11, 0.25) !important;
        border-radius: 10px !important;
        color: #f8fafc !important;
        font-size: 1.05rem !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.4) !important;
        transition: all 0.2s ease !important;
    }
    .stTextInput input:focus, 
    .stTextArea textarea:focus,
    .stSelectbox [data-baseweb="select"]:focus-within {
        border-color: #fbbf24 !important;
        box-shadow: 0 0 16px rgba(245, 158, 11, 0.35), inset 0 2px 4px rgba(0, 0, 0, 0.4) !important;
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] section {
        background: rgba(13, 18, 30, 0.6) !important;
        border: 1.5px dashed rgba(245, 158, 11, 0.35) !important;
        border-radius: 12px !important;
    }
    [data-testid="stFileUploader"] section:hover {
        border-color: #fbbf24 !important;
        background: rgba(245, 158, 11, 0.08) !important;
    }
    
    /* Streamlit Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 16px;
        border-bottom: 1px solid rgba(245, 158, 11, 0.2) !important;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        background-color: transparent !important;
        border-radius: 8px 8px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: #94a3b8 !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #fde047 !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(180deg, rgba(245, 158, 11, 0.12) 0%, rgba(245, 158, 11, 0.02) 100%) !important;
        color: #fbbf24 !important;
        border-bottom: 2px solid #f59e0b !important;
    }
    
    /* Expanders */
    [data-testid="stExpander"] {
        background: rgba(15, 20, 32, 0.7) !important;
        border: 1px solid rgba(245, 158, 11, 0.2) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4) !important;
    }
    
    /* Dividers with gold gradient laser fade */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(245, 158, 11, 0.45), transparent) !important;
        margin: 1.8rem 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

def create_gauge_chart(score):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Match Compatibility", 'font': {'size': 20, 'color': '#f8fafc', 'family': 'Plus Jakarta Sans, sans-serif'}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
            'bar': {'color': "#f59e0b"},
            'bgcolor': "rgba(15, 23, 42, 0.65)",
            'borderwidth': 1,
            'bordercolor': "rgba(245, 158, 11, 0.3)",
            'steps': [
                {'range': [0, 40], 'color': "rgba(239, 68, 68, 0.25)"},
                {'range': [40, 70], 'color': "rgba(245, 158, 11, 0.25)"},
                {'range': [70, 100], 'color': "rgba(16, 185, 129, 0.25)"}],
            'threshold': {
                'line': {'color': "#fbbf24", 'width': 3},
                'thickness': 0.75,
                'value': score}
        },
        number={'font': {'color': '#fbbf24', 'size': 50, 'family': 'Plus Jakarta Sans, sans-serif'}}
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=320, margin=dict(l=15, r=15, t=50, b=15))
    return fig


def basic_resume_health(text):
    has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+', text))
    has_phone = bool(re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text))
    word_count = len(text.split())
    return {
        "email": has_email,
        "phone": has_phone,
        "word_count": word_count
    }

auth.create_usertable()
auth.create_history_table()

def check_auth_gate(feature_name="this feature"):
    """
    Checks if user is logged in. If not, displays an enticing sign-up call-to-action
    gate banner and inline authentication so users can register/sign in immediately
    without losing their context.
    """
    if not st.session_state.get('logged_in'):
        st.session_state['redirect_after_login'] = st.session_state.get('selected_page', '🔍 Resume Analyzer')
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(26, 20, 48, 0.9) 0%, rgba(13, 18, 30, 0.95) 100%); 
                    border: 1.5px solid rgba(245, 158, 11, 0.4); 
                    border-radius: 18px; 
                    padding: 26px 30px; 
                    margin: 16px 0 24px 0; 
                    box-shadow: 0 14px 40px -8px rgba(0, 0, 0, 0.7), 0 0 25px rgba(245, 158, 11, 0.12);
                    backdrop-filter: blur(16px);">
            <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 10px;">
                <span style="font-size: 34px; filter: drop-shadow(0 0 10px rgba(245, 158, 11, 0.4));">👑</span>
                <div>
                    <h3 style="margin: 0; background: linear-gradient(135deg, #ffffff 0%, #fde047 60%, #f59e0b 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.5rem; font-weight: 700;">Sign Up Required to {feature_name}</h3>
                    <span style="color: #fbbf24; font-size: 0.95rem; font-weight: 600;">⚡ Instant 10-second free VIP setup</span>
                </div>
            </div>
            <p style="color: #cbd5e1; font-size: 1.05rem; line-height: 1.6; margin: 10px 0 16px 0;">
                Your uploaded documents and form details are safely preserved! To generate AI content, calculate ATS compatibility scores, and download high-grade professional files, please <strong>sign up for a free account</strong> or <strong>sign in</strong>.
            </p>
            <div style="background: rgba(10, 14, 24, 0.7); border-radius: 12px; padding: 14px 20px; border: 1px solid rgba(245, 158, 11, 0.25); margin-bottom: 16px;">
                <span style="font-weight: 700; color: #fde047;">✦ Included Free With Your VIP Account:</span>
                <ul style="margin: 8px 0 0 0; padding-left: 20px; color: #cbd5e1; font-size: 0.95rem;">
                    <li>✨ Unlimited AI Resume & Cover Letter generation</li>
                    <li>📊 ATS semantic keyword scoring & real-time feedback</li>
                    <li>📥 Formatted PDF & Markdown export downloads with history tracking</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1.3, 1.7])
        with col1:
            if st.button("🚀 Go to Account Page (Sign Up / Sign In)", type="primary", key=f"btn_goto_auth_{feature_name}", use_container_width=True):
                navigate_to("👤 Account")
                
        with st.expander("⚡ Or Quick Sign In / Create Account right here (Instant Access)", expanded=True):
            tab_in, tab_up = st.tabs(["Sign In", "Create Free Account"])
            with tab_in:
                with st.form(f"gate_login_form_{feature_name}"):
                    u_val = st.text_input("Username", key=f"gate_u_{feature_name}")
                    p_val = st.text_input("Password", type="password", key=f"gate_p_{feature_name}")
                    if st.form_submit_button("Sign In & Continue", type="primary", use_container_width=True):
                        if u_val and p_val:
                            hashed = auth.make_hashes(p_val)
                            if auth.login_user(u_val, hashed):
                                st.session_state['logged_in'] = True
                                st.session_state['username'] = u_val
                                st.success(f"Welcome back, {u_val}!")
                                st.rerun()
                            else:
                                st.error("Invalid username or password.")
                        else:
                            st.warning("Please enter your username and password.")
            with tab_up:
                with st.form(f"gate_signup_form_{feature_name}"):
                    new_u = st.text_input("Choose Username", key=f"gate_new_u_{feature_name}")
                    new_p = st.text_input("Choose Password", type="password", key=f"gate_new_p_{feature_name}")
                    if st.form_submit_button("Create Account & Continue", type="primary", use_container_width=True):
                        if new_u and new_p:
                            auth.add_userdata(new_u, auth.make_hashes(new_p))
                            st.session_state['logged_in'] = True
                            st.session_state['username'] = new_u
                            st.success(f"Account created! Welcome, {new_u}!")
                            st.rerun()
                        else:
                            st.warning("Please provide a valid username and password.")
        return False
    return True

# --- Sidebar Navigation ---
with st.sidebar:
    st.markdown("### 🧭 Choose Tool")
    nav_tools = ["📊 Dashboard", "🔍 Resume Analyzer", "✨ AI Resume Builder", "✉️ Cover Letter Generator", "💼 Find Jobs"]
    if not st.session_state.get('logged_in'):
        options = nav_tools + ["👤 Account"]
    else:
        options = nav_tools
    
    if st.session_state.get('selected_page') not in options:
        st.session_state['selected_page'] = options[0]

    # Pre-sync the radio value with selected_page BEFORE instantiating the widget
    st.session_state['sidebar_nav_radio'] = st.session_state['selected_page']

    def on_sidebar_radio_change():
        st.session_state['selected_page'] = st.session_state['sidebar_nav_radio']

    st.radio(
        "🛠️ Choose Tool",
        options,
        key="sidebar_nav_radio",
        on_change=on_sidebar_radio_change,
        label_visibility="collapsed"
    )
    st.markdown("---")

app_mode = st.session_state.get('selected_page', '📊 Dashboard')

if app_mode == "👤 Account":
    st.write("")
    
    # Custom CSS for the login form card
    st.markdown("""
        <style>
        [data-testid="stForm"] {
            border: 1px solid rgba(245, 158, 11, 0.3) !important;
            box-shadow: 0 16px 45px -10px rgba(0, 0, 0, 0.8), 0 0 25px rgba(245, 158, 11, 0.12) !important;
            border-radius: 18px !important;
            background: linear-gradient(135deg, rgba(20, 26, 42, 0.9) 0%, rgba(13, 18, 30, 0.95) 100%) !important;
            backdrop-filter: blur(16px) !important;
            padding: 32px !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            justify-content: center;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([0.5, 3, 0.5])
    
    with col2:
        st.markdown("<h1 style='text-align: center; background: linear-gradient(135deg, #ffffff 0%, #fef08a 40%, #f59e0b 80%, #fbbf24 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3.2rem; font-weight: 800; margin-bottom: 0;'>Resume Analyzer Pro</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #cbd5e1; font-size: 1.2rem;'>Your AI-powered executive career suite. Build, analyze, and land your dream job.</p>", unsafe_allow_html=True)
        st.write("")
        st.write("")
        
        main_col1, empty_col, main_col2 = st.columns([1.2, 0.2, 1])
        
        with main_col1:
            st.markdown("<h3 style='background: linear-gradient(135deg, #ffffff 0%, #fde047 60%, #f59e0b 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-top: 20px;'>✦ Supercharge Your Career</h3>", unsafe_allow_html=True)
            st.write("")
            st.markdown("<strong style='color: #fbbf24;'>✨ AI Resume Builder</strong><br><span style='color: #cbd5e1;'>Generate ATS-optimized resumes in seconds from your LinkedIn profile.</span>", unsafe_allow_html=True)
            st.write("")
            st.markdown("<strong style='color: #fbbf24;'>📈 Smart Match Scoring</strong><br><span style='color: #cbd5e1;'>Compare your resume against any job description and get actionable feedback.</span>", unsafe_allow_html=True)
            st.write("")
            st.markdown("<strong style='color: #fbbf24;'>✉️ Tailored Cover Letters</strong><br><span style='color: #cbd5e1;'>Instantly draft highly personalized cover letters that highlight your strengths.</span>", unsafe_allow_html=True)
            
        with main_col2:
            tab1, tab2 = st.tabs(["Sign In", "Create Account"])
            
            with tab1:
                with st.form("login_form", clear_on_submit=False):
                    username = st.text_input("Username", placeholder="Enter your username")
                    password = st.text_input("Password", type='password', placeholder="••••••••")
                    st.write("")
                    submitted = st.form_submit_button("Sign In →", type="primary", use_container_width=True)
                    
                    if submitted:
                        hashed_pswd = auth.make_hashes(password)
                        result = auth.login_user(username, hashed_pswd)
                        if result:
                            st.session_state['logged_in'] = True
                            st.session_state['username'] = username
                            target_page = st.session_state.get('redirect_after_login', '📊 Dashboard')
                            if target_page == "👤 Account":
                                target_page = "📊 Dashboard"
                            navigate_to(target_page)
                        else:
                            st.error("Incorrect Username or Password")
                            
            with tab2:
                with st.form("signup_form", clear_on_submit=True):
                    new_user = st.text_input("New Username", placeholder="Choose a username")
                    new_password = st.text_input("New Password", type='password', placeholder="Create a strong password")
                    st.write("")
                    submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)
                    
                    if submitted:
                        if new_user and new_password:
                            hashed_new_password = auth.make_hashes(new_password)
                            auth.add_userdata(new_user, hashed_new_password)
                            st.session_state['logged_in'] = True
                            st.session_state['username'] = new_user
                            target_page = st.session_state.get('redirect_after_login', '📊 Dashboard')
                            if target_page == "👤 Account":
                                target_page = "📊 Dashboard"
                            navigate_to(target_page)
                        else:
                            st.warning("Please provide a valid username and password.")

if app_mode == "📊 Dashboard":
    if st.session_state.get('logged_in'):
        st.markdown(f"<h1 style='background: linear-gradient(135deg, #ffffff 0%, #fef08a 40%, #f59e0b 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0;'>Welcome back, {st.session_state['username']}! 👑</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #cbd5e1; font-size: 1.15rem; margin-top: 5px;'>Here is your executive career command center.</p>", unsafe_allow_html=True)
        
        if st.session_state.get('demo_mode_active'):
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(26, 20, 50, 0.85) 0%, rgba(13, 18, 30, 0.95) 100%); border: 1.5px solid rgba(245, 158, 11, 0.35); border-radius: 14px; padding: 14px 22px; margin: 12px 0 22px 0; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 8px 25px -5px rgba(0, 0, 0, 0.6), 0 0 15px rgba(245, 158, 11, 0.1);">
                <div>
                    <span style="font-weight: 700; color: #fde047;">✨ Demo Suite Active:</span>
                    <span style="color: #cbd5e1; margin-left: 8px;">Exploring executive profile for <strong style="color: #fbbf24;">Alex Morgan (Senior Full-Stack & AI Engineer)</strong> with pre-loaded resumes, ATS metrics, and cover letters.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.write("")
        
        history = auth.get_history(st.session_state['username'])
        total_docs = len(history) if history else 0
        resumes_count = sum(1 for h in history if h[0] == "Resume") if history else 0
        cl_count = sum(1 for h in history if h[0] == "Cover Letter") if history else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{total_docs}</div><div class="metric-label">Total Documents</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{resumes_count}</div><div class="metric-label">Resumes Built</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{cl_count}</div><div class="metric-label">Cover Letters</div></div>', unsafe_allow_html=True)
        with col4:
            avg_score = "89%" if total_docs > 0 else "0%"
            st.markdown(f'<div class="metric-card"><div class="metric-value">{avg_score}</div><div class="metric-label">Avg Compatibility</div></div>', unsafe_allow_html=True)
            
        st.write("")
        st.markdown("### ✦ Executive Quick Launch")
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        with col_t1:
            if st.button("🔍 Resume Analyzer", type="primary", use_container_width=True, key="dash_btn_an"):
                navigate_to("🔍 Resume Analyzer")
        with col_t2:
            if st.button("✨ AI Resume Builder", type="primary", use_container_width=True, key="dash_btn_bld"):
                navigate_to("✨ AI Resume Builder")
        with col_t3:
            if st.button("✉️ Cover Letter", type="primary", use_container_width=True, key="dash_btn_cl"):
                navigate_to("✉️ Cover Letter Generator")
        with col_t4:
            if st.button("💼 Find Jobs", type="primary", use_container_width=True, key="dash_btn_jb"):
                navigate_to("💼 Find Jobs")

        st.write("---")
        col_hist_h, col_hist_btn = st.columns([3, 1])
        with col_hist_h:
            st.markdown("### 📜 Saved Documents & Dossiers")
        with col_hist_btn:
            if not history or not st.session_state.get('demo_mode_active'):
                if st.button("✨ Load Sample History", key="dash_load_sample_hist", use_container_width=True):
                    activate_demo_data()
                    st.rerun()

        if not history:
            st.info("You haven't generated any documents yet. Click 'Load Sample History' above or use the tools to generate your first document!")
        else:
            for idx, (doc_type, content, timestamp) in enumerate(history):
                icon = "📄" if doc_type == "Resume" else "✉️"
                with st.expander(f"{icon} {doc_type} — {timestamp}", expanded=(idx == 0)):
                    st.markdown(content)
                    st.download_button(
                        f"📥 Download {doc_type} (Markdown)",
                        data=content,
                        file_name=f"{doc_type}_{idx+1}.md",
                        mime="text/markdown",
                        key=f"hist_dl_{idx}"
                    )

    else:
        # Welcoming Guest Home Dashboard with 1-Click Demo Showcase!
        st.markdown("<h1 style='text-align: center; margin-bottom: 8px; font-size: 3.2rem; font-weight: 800; background: linear-gradient(135deg, #ffffff 0%, #fef08a 40%, #f59e0b 80%, #fbbf24 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Career Intelligence Workspace ✦</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #cbd5e1; font-size: 1.25rem; max-width: 820px; margin: 0 auto 24px auto;'>The premier executive platform to build ATS-optimized resumes, score job compatibility with AI, and craft high-converting cover letters.</p>", unsafe_allow_html=True)
        
        # 1-Click Demo Feature Callout Card
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(26, 20, 50, 0.85) 0%, rgba(13, 18, 30, 0.95) 100%); 
                    border: 1.5px solid rgba(245, 158, 11, 0.35); border-radius: 16px; padding: 22px 30px; margin-bottom: 24px;
                    box-shadow: 0 12px 36px -6px rgba(0, 0, 0, 0.6), 0 0 25px rgba(245, 158, 11, 0.12);
                    backdrop-filter: blur(16px);">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px;">
                <div>
                    <h3 style="margin: 0; background: linear-gradient(135deg, #ffffff 0%, #fde047 60%, #f59e0b 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.45rem; font-weight: 700;">
                        ✦ Explore Instantly with Pre-Loaded Demo Suite
                    </h3>
                    <p style="margin: 8px 0 0 0; color: #cbd5e1; font-size: 1.05rem;">
                        No resume ready? Click below to populate an executive sample profile (<strong style="color: #fbbf24;">Alex Morgan — Senior AI Engineer</strong>) complete with ATS match reports, generated resumes, and live jobs.
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        col_demo_c1, col_demo_c2, col_demo_c3 = st.columns([1, 1.8, 1])
        with col_demo_c2:
            if st.button("⚡ One-Click Explore with Demo Data", type="primary", key="home_hero_demo_btn", use_container_width=True):
                activate_demo_data()
                navigate_to("📊 Dashboard")

        st.write("")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="pro-card" style="margin-bottom: 14px;">
                <h3 style="background: linear-gradient(135deg, #ffffff 0%, #fde047 50%, #f59e0b 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-top: 0; display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 28px; -webkit-text-fill-color: initial;">🔍</span> Resume Analyzer Pro
                </h3>
                <p class="pro-subtitle" style="line-height: 1.6; margin-bottom: 14px; color: #cbd5e1;">
                    Upload your resume and target job description to calculate semantic match scores, uncover keyword gaps, and get AI recommendations.
                </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Resume Analyzer →", type="primary", key="home_launch_an", use_container_width=True):
                navigate_to("🔍 Resume Analyzer")

        with col2:
            st.markdown("""
            <div class="pro-card" style="margin-bottom: 14px;">
                <h3 style="background: linear-gradient(135deg, #ffffff 0%, #fde047 50%, #f59e0b 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-top: 0; display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 28px; -webkit-text-fill-color: initial;">✨</span> AI Resume Builder
                </h3>
                <p class="pro-subtitle" style="line-height: 1.6; margin-bottom: 14px; color: #cbd5e1;">
                    Don't have an ATS resume? Import your LinkedIn export or enter rough notes to generate an executive-ready resume.
                </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Resume Builder →", type="primary", key="home_launch_bld", use_container_width=True):
                navigate_to("✨ AI Resume Builder")

        st.write("")
        col3, col4 = st.columns(2)
        with col3:
            st.markdown("""
            <div class="pro-card" style="margin-bottom: 14px;">
                <h3 style="background: linear-gradient(135deg, #ffffff 0%, #fde047 50%, #f59e0b 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-top: 0; display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 28px; -webkit-text-fill-color: initial;">✉️</span> Cover Letter Generator
                </h3>
                <p class="pro-subtitle" style="line-height: 1.6; margin-bottom: 14px; color: #cbd5e1;">
                    Instantly draft highly personalized, compelling cover letters that match your actual experience to the job requirements.
                </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Cover Letter Generator →", type="primary", key="home_launch_cl", use_container_width=True):
                navigate_to("✉️ Cover Letter Generator")

        with col4:
            st.markdown("""
            <div class="pro-card" style="margin-bottom: 14px;">
                <h3 style="background: linear-gradient(135deg, #ffffff 0%, #fde047 50%, #f59e0b 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-top: 0; display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 28px; -webkit-text-fill-color: initial;">💼</span> Find Jobs
                </h3>
                <p class="pro-subtitle" style="line-height: 1.6; margin-bottom: 14px; color: #cbd5e1;">
                    Discover curated live job matches tailored to your target skills, salary expectations, and preferred roles.
                </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Browse Live Jobs →", type="primary", key="home_launch_jb", use_container_width=True):
                navigate_to("💼 Find Jobs")

        st.write("")
        # Call to action card
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(30, 27, 75, 0.85) 0%, rgba(13, 18, 30, 0.95) 100%); 
                    border: 1.5px solid rgba(245, 158, 11, 0.4); border-radius: 18px; padding: 30px 36px; 
                    margin-top: 24px; text-align: center;
                    box-shadow: 0 14px 40px -8px rgba(0, 0, 0, 0.7), 0 0 30px rgba(245, 158, 11, 0.15);
                    backdrop-filter: blur(16px);">
            <h2 style="background: linear-gradient(135deg, #ffffff 0%, #fde047 50%, #f59e0b 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-top: 0; font-size: 2.2rem; font-weight: 800;">Ready to Elevate Your Career?</h2>
            <p style="color: #cbd5e1; font-size: 1.15rem; max-width: 680px; margin: 10px auto 22px auto;">
                Create a free account in 10 seconds to unlock unlimited AI document generations, save your resume versions, and export PDF copies.
            </p>
        </div>
        """, unsafe_allow_html=True)
        col_cta1, col_cta2, col_cta3 = st.columns([1, 1.5, 1])
        with col_cta2:
            if st.button("🚀 Create Free Account / Sign In", type="primary", key="home_cta_auth", use_container_width=True):
                navigate_to("👤 Account")

if app_mode == "🔍 Resume Analyzer":
    st.markdown("<h1 style='text-align: center; margin-bottom: 8px; background: linear-gradient(135deg, #ffffff 0%, #fef08a 40%, #f59e0b 80%, #fbbf24 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.8rem; font-weight: 800;'>📈 Resume Analyzer & Career Discovery Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;' class='pro-subtitle'>Universal resume analysis, career fit discovery, and AI ATS semantic matching for all academic degrees and professional paths.</p>", unsafe_allow_html=True)
    st.write("")

    # Connected 3-Step Workflow Cards directly on the main page
    col_card1, col_card2 = st.columns(2)
    with col_card1:
        st.markdown("""
        <div class="pro-card" style="margin-bottom: 8px; padding: 18px 22px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 26px;">📄</span>
                <div>
                    <h3 style="margin: 0; background: linear-gradient(135deg, #ffffff 0%, #fde047 60%, #f59e0b 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.25rem; font-weight: 700;">1. Upload Resume</h3>
                    <p class="pro-subtitle" style="margin: 2px 0 0 0; font-size: 0.95rem; color: #cbd5e1;">Any degree or course: B.Com, BBA, Tech, Arts, Sciences, Law & more.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"], key="analyzer_file_input", label_visibility="collapsed")
        
        st.markdown("<p style='font-size: 0.88rem; color: #94a3b8; margin: 8px 0 4px 0;'>Or test with pre-built candidate degrees:</p>", unsafe_allow_html=True)
        col_prof1, col_prof2 = st.columns([2.2, 1.2])
        with col_prof1:
            sample_profile = st.selectbox(
                "Sample Profile Degree",
                [
                    "Commerce & Finance (Priya Sharma — B.Com Honours)",
                    "Business & Marketing (Rahul Verma — BBA Graduate)",
                    "Tech & AI (Alex Morgan — Senior Engineer)"
                ],
                key="sample_profile_choice",
                label_visibility="collapsed"
            )
        with col_prof2:
            if st.session_state.get('analyzer_use_demo'):
                if st.button("🔄 Clear Sample", key="clear_sample_res_btn", use_container_width=True):
                    st.session_state['analyzer_use_demo'] = False
                    st.rerun()
            else:
                if st.button("✨ Load Sample", key="use_sample_res_btn", use_container_width=True):
                    st.session_state['analyzer_use_demo'] = True
                    st.rerun()

        if uploaded_file:
            st.success(f"✓ **{uploaded_file.name}** ready for analysis ({uploaded_file.size // 1024} KB)")
        elif st.session_state.get('analyzer_use_demo'):
            st.info(f"💡 **Sample Profile Active:** {sample_profile}")

    with col_card2:
        st.markdown("""
        <div class="pro-card" style="margin-bottom: 8px; padding: 18px 22px;">
            <div style="display: flex; align-items: center; justify-content: space-between; gap: 10px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 26px;">🎯</span>
                    <div>
                        <h3 style="margin: 0; background: linear-gradient(135deg, #ffffff 0%, #fde047 60%, #f59e0b 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.25rem; font-weight: 700;">
                            2. Target Job Description 
                            <span style="font-size: 0.8rem; vertical-align: middle; padding: 2px 8px; border-radius: 6px; background: rgba(245, 158, 11, 0.2); color: #fde047; border: 1px solid rgba(245, 158, 11, 0.4); margin-left: 6px;">Optional</span>
                        </h3>
                        <p class="pro-subtitle" style="margin: 2px 0 0 0; font-size: 0.95rem; color: #cbd5e1;">Leave empty to auto-discover what jobs you are qualified to do!</p>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        default_jd_val = ""
        # If user explicitly loaded the Tech sample profile and hasn't cleared it, pre-fill tech JD; for B.Com/BBA keep empty to highlight career discovery!
        if st.session_state.get('analyzer_use_demo') and "Tech" in st.session_state.get('sample_profile_choice', ''):
            default_jd_val = demo_data.SAMPLE_JOB_DESCRIPTION
            
        job_description = st.text_area(
            "Target Job Description",
            value=default_jd_val,
            height=140,
            placeholder="Paste target job requirements here for ATS matching... OR leave completely blank to let AI discover what jobs you are qualified to do across all industries!",
            key="analyzer_jd_input",
            label_visibility="collapsed"
        )
        if job_description.strip():
            st.info(f"✓ Job description entered ({len(job_description.split())} words) — Direct ATS Matching mode active.")
        else:
            st.markdown("<p style='font-size: 0.88rem; color: #34d399; margin: 4px 0 0 0;'>💡 <strong>Universal Career Discovery Mode:</strong> No JD needed! AI will evaluate your resume and recommend suitable career roles across all industries (Commerce, BBA, Tech, Arts, Healthcare, etc.).</p>", unsafe_allow_html=True)

    has_jd = bool(job_description.strip())
    st.markdown(f"""
    <div class="pro-card" style="margin-top: 10px; margin-bottom: 12px; padding: 18px 22px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 26px;">{'🎯' if has_jd else '🧭'}</span>
            <div>
                <h3 style="margin: 0; background: linear-gradient(135deg, #ffffff 0%, #fde047 60%, #f59e0b 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.25rem; font-weight: 700;">
                    3. {'Run Targeted ATS Match' if has_jd else 'Discover Career Roles & Analyze Resume'}
                </h3>
                <p class="pro-subtitle" style="margin: 2px 0 0 0; font-size: 0.95rem; color: #cbd5e1;">
                    {'Calculate ATS compatibility score, extract missing keywords, and get AI recommendations.' if has_jd else 'Analyze candidate qualification across any degree (B.Com, BBA, Tech, Arts, Sciences) and discover top matching job roles!'}
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    btn_label = "🚀 Run Targeted ATS Analysis" if has_jd else "🧭 Discover What Jobs I Can Do & Analyze Resume"
    analyze_btn = st.button(btn_label, type="primary", use_container_width=True, key="analyzer_run_btn")

    if analyze_btn:
        if not check_auth_gate("Run Resume Analysis"):
            pass
        elif uploaded_file is None and not st.session_state.get('analyzer_use_demo'):
            st.warning("⚠️ Please upload a resume or click 'Load Sample' above.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Ingesting document and extracting content...")
            progress_bar.progress(20)
            
            if uploaded_file is not None:
                if uploaded_file.name.endswith(".pdf"):
                    resume_text = extract_text_from_pdf(uploaded_file)
                else:
                    resume_text = extract_text_from_docx(uploaded_file)
            else:
                prof = st.session_state.get('sample_profile_choice', 'Tech & AI (Alex Morgan — Senior Engineer)')
                if "Commerce" in prof or "B.Com" in prof:
                    resume_text = demo_data.SAMPLE_COMMERCE_RESUME_TEXT
                elif "BBA" in prof or "Business" in prof:
                    resume_text = demo_data.SAMPLE_BBA_RESUME_TEXT
                else:
                    resume_text = demo_data.SAMPLE_RESUME_TEXT
                
            if not resume_text.strip():
                st.error("Could not extract text. Please ensure the file is valid and readable.")
                st.stop()

            # --- DUAL MODE BRANCHING ---
            if not job_description.strip():
                # MODE 1: Universal Career Discovery for ALL Courses & Degrees
                status_text.text("Auditing resume health and extracting candidate competencies...")
                progress_bar.progress(50)
                eval_data = evaluate_universal_resume(resume_text)
                
                status_text.text("Consulting AI Executive Talent Advisor for recommended job roles...")
                progress_bar.progress(80)
                career_report = discover_career_opportunities(resume_text)
                
                if st.session_state.get('logged_in'):
                    auth.save_history(st.session_state['username'], "Career Discovery", career_report)
                    
                progress_bar.progress(100)
                status_text.empty()
                progress_bar.empty()
                
                # --- Results Dashboard ---
                st.markdown("<h2 style='text-align: center; margin-top: 15px; margin-bottom: 4px; background: linear-gradient(135deg, #ffffff 0%, #fde047 50%, #f59e0b 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>✦ Candidate Intelligence & Career Fit</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; color: #cbd5e1; font-size: 1.05rem;'>Comprehensive career evaluation for all academic disciplines: Commerce, Management, Arts, Science, and Technology.</p>", unsafe_allow_html=True)
                st.write("")
                
                col_u1, col_u2 = st.columns([1, 1.5])
                with col_u1:
                    st.plotly_chart(create_gauge_chart(eval_data['readiness_score']), width='stretch')
                    st.markdown("<p style='text-align: center; color: #cbd5e1; font-size: 0.95rem; margin-top: -15px;'>Overall Resume ATS Readiness Score</p>", unsafe_allow_html=True)
                    
                with col_u2:
                    st.markdown("""
                    <div class="pro-card" style="padding: 20px 24px; margin-bottom: 12px;">
                        <h3 style="margin-top: 0; background: linear-gradient(135deg, #ffffff 0%, #fde047 50%, #f59e0b 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.3rem;">
                            📋 Resume Structure & Health Audit
                        </h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    hc1, hc2, hc3 = st.columns(3)
                    hc1.metric("Email Address", "Found ✓" if eval_data['has_email'] else "Missing ✗")
                    hc2.metric("Phone Number", "Found ✓" if eval_data['has_phone'] else "Missing ✗")
                    hc3.metric("Word Count", f"{eval_data['word_count']} words")
                    
                    st.markdown("<div style='margin-top: 12px;'><strong>Detected Core Sections:</strong></div>", unsafe_allow_html=True)
                    sec_cols = st.columns(len(eval_data['sections']))
                    for idx, (sec_name, sec_present) in enumerate(eval_data['sections'].items()):
                        with sec_cols[idx]:
                            badge_color = "#34d399" if sec_present else "#f87171"
                            st.markdown(f"<span style='color: {badge_color}; font-size: 0.9rem; font-weight: 600;'>{'✓' if sec_present else '✗'} {sec_name.split('/')[0]}</span>", unsafe_allow_html=True)

                st.write("")
                
                # --- AI Career Discovery Report ---
                st.markdown("""
                <div class="pro-card" style="padding: 24px 28px; margin-bottom: 20px;">
                    <h3 style="margin-top: 0; background: linear-gradient(135deg, #ffffff 0%, #fde047 50%, #f59e0b 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.45rem;">
                        🎯 AI Career Roles & Opportunity Analysis
                    </h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(career_report)
                
                # --- Extracted Transferable Keywords Pill Box ---
                st.write("")
                st.markdown("#### 🔑 Extracted Competencies & Keywords from Resume:")
                if eval_data['extracted_keywords']:
                    tags = "".join([f'<span style="display:inline-block; background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(217, 119, 6, 0.25)); border: 1px solid rgba(245, 158, 11, 0.45); color: #fde047; padding: 6px 14px; margin: 4px; border-radius: 8px; font-weight: 600;">{k}</span>' for k in eval_data['extracted_keywords']])
                    st.markdown(tags, unsafe_allow_html=True)
                else:
                    st.info("No distinct keywords identified.")
                    
                st.write("")
                # Direct Action CTA to Find Jobs
                st.markdown("""
                <div style="background: linear-gradient(135deg, rgba(26, 20, 50, 0.85) 0%, rgba(13, 18, 30, 0.95) 100%); 
                            border: 1.5px solid rgba(245, 158, 11, 0.4); border-radius: 16px; padding: 22px 28px; margin-top: 24px;
                            box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px;">
                        <div>
                            <h4 style="margin: 0; background: linear-gradient(135deg, #ffffff 0%, #fde047 60%, #f59e0b 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.25rem;">
                                💼 Ready to Explore Live Opportunities?
                            </h4>
                            <p style="margin: 4px 0 0 0; color: #cbd5e1; font-size: 0.95rem;">
                                Explore curated positions matching your background in our multi-industry job catalog.
                            </p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                col_c1, col_c2, col_c3 = st.columns([1, 1.6, 1])
                with col_c2:
                    if st.button("💼 Browse Matching Jobs in Catalog →", type="primary", key="btn_goto_jobs_from_discovery", use_container_width=True):
                        navigate_to("💼 Find Jobs")

            else:
                # MODE 2: Targeted ATS Semantic Match (When Job Description is provided)
                status_text.text("Computing match score matrices...")
                progress_bar.progress(60)
                
                results = match_skills(resume_text, job_description)
                health = basic_resume_health(resume_text)
                
                status_text.text("Generating AI feedback and skill gap analysis...")
                progress_bar.progress(85)
                
                ai_feedback = get_resume_suggestions(resume_text, job_description)
                if st.session_state.get('logged_in'):
                    auth.save_history(st.session_state['username'], "Targeted ATS Analysis", ai_feedback)
                    
                progress_bar.progress(100)
                status_text.empty()
                progress_bar.empty()
                
                # --- Results Dashboard ---
                score = results['similarity_score']
                
                col1, col2 = st.columns([1, 1.5])
                with col1:
                    st.plotly_chart(create_gauge_chart(score), width='stretch')
                    
                with col2:
                    st.subheader("Analysis Summary")
                    if score >= 75:
                        st.markdown("**Excellent Match!** Your resume satisfies the core requirements.")
                    elif score >= 50:
                        st.markdown("**Moderate Alignment.** You have a baseline match. Add missing keywords.")
                    else:
                        st.markdown("**Needs Realignment.** Consider revisions if applying for this specific role.")
                    
                    st.markdown("---")
                    hc1, hc2, hc3 = st.columns(3)
                    hc1.metric("Email Address", "Found" if health['email'] else "Missing")
                    hc2.metric("Phone Number", "Found" if health['phone'] else "Missing")
                    hc3.metric("Word Count", f"{health['word_count']}")

                # --- AI Suggestions ---
                st.markdown("### 🤖 AI Suggestions for Improvement")
                st.markdown(ai_feedback)

                # --- Missing/Matched Skills ---
                tab1, tab2, tab3 = st.tabs(["✓ Matched Terms", "✗ Missing Terms", "Raw Text"])
                
                with tab1:
                    st.markdown("#### Found in both Resume and Job Description:")
                    if results['matched_skills']:
                        tags = "".join([f'<span style="display:inline-block; background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(5, 150, 105, 0.25)); border: 1px solid rgba(52, 211, 153, 0.45); color: #6ee7b7; padding: 6px 14px; margin: 4px; border-radius: 8px; font-weight: 600;">{skill.title()}</span>' for skill in results['matched_skills']])
                        st.markdown(tags, unsafe_allow_html=True)
                    else:
                        st.info("No major overlapping keywords found.")
                        
                with tab2:
                    st.markdown("#### Found in Job Description, missing from Resume:")
                    if results['missing_skills']:
                        tags = "".join([f'<span style="display:inline-block; background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(185, 28, 28, 0.25)); border: 1px solid rgba(248, 113, 113, 0.45); color: #fca5a5; padding: 6px 14px; margin: 4px; border-radius: 8px; font-weight: 600;">{skill.title()}</span>' for skill in results['missing_skills']])
                        st.markdown(tags, unsafe_allow_html=True)
                    else:
                        st.success("You matched all significant keywords!")
                        
                with tab3:
                    st.text(resume_text[:2000] + "...")

elif app_mode == "✨ AI Resume Builder":
    st.markdown("<h1 style='text-align: center; margin-bottom: 8px; background: linear-gradient(135deg, #ffffff 0%, #fef08a 40%, #f59e0b 80%, #fbbf24 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.8rem; font-weight: 800;'>✨ AI Resume Builder</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;' class='pro-subtitle'>Don't have a resume? Let AI generate an ATS-friendly draft for you.</p>", unsafe_allow_html=True)
    st.write("")
    
    st.markdown("#### 1. Import from LinkedIn (Optional)")
    linkedin_file = st.file_uploader("Upload LinkedIn Profile (PDF Export)", type=["pdf"])
    linkedin_text = ""
    if linkedin_file:
        linkedin_text = extract_text_from_pdf(linkedin_file)
        st.success("LinkedIn Profile Imported! We'll use this data automatically.")
    
    col_bld_title, col_bld_sample = st.columns([2.5, 1.5])
    with col_bld_title:
        st.markdown("#### 2. Manual Details")
    with col_bld_sample:
        if st.button("✨ Fill Form with Sample Profile", key="btn_sample_builder", use_container_width=True):
            for k, v in demo_data.SAMPLE_BUILDER_INPUTS.items():
                st.session_state[f'builder_{k}'] = v
            st.rerun()

    with st.form("resume_builder_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", value=st.session_state.get('builder_name', ''))
            target_role = st.text_input("Target Role (e.g. Data Scientist)", value=st.session_state.get('builder_target_role', ''))
        with col2:
            contact = st.text_input("Contact Info (Email, Phone, LinkedIn)", value=st.session_state.get('builder_contact', ''))
            skills = st.text_input("Core Skills (comma separated)", value=st.session_state.get('builder_skills', ''))
            
        education = st.text_area("Education Details (Degrees, Universities)", value=st.session_state.get('builder_education', ''))
        experience = st.text_area("Experience (Describe your past jobs, companies, and responsibilities loosely. AI will format it.)", value=st.session_state.get('builder_experience', ''), height=160)
        
        submit_build = st.form_submit_button("Generate Resume with AI", type="primary", use_container_width=True)

    if submit_build:
        if not check_auth_gate("Generate Resume with AI"):
            pass
        elif not name or not experience:
            st.warning("Please provide at least your Name and Experience.")
        else:
            with st.spinner("🧠 AI is drafting your professional resume..."):
                details = {
                    "name": name,
                    "contact": contact,
                    "target_role": target_role,
                    "skills": skills,
                    "education": education,
                    "experience": experience + "\n\nLinkedIn Data:\n" + linkedin_text
                }
                resume_output = generate_resume(details)
                if st.session_state.get('logged_in'):
                    auth.save_history(st.session_state['username'], "Resume", resume_output)
                
            st.markdown("### 🎉 Your Generated Resume")
            edited_resume = st.text_area("Live Editor (Edit your resume here before downloading):", value=resume_output, height=400)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.download_button("Download Markdown", edited_resume, file_name="AI_Resume.md", mime="text/markdown", use_container_width=True)
            with col_b:
                from utils import create_pdf
                pdf_bytes = create_pdf(edited_resume)
                if pdf_bytes:
                    st.download_button("Download PDF", data=pdf_bytes, file_name="AI_Resume.pdf", mime="application/pdf", use_container_width=True)
                else:
                    st.error("PDF generation failed.")

elif app_mode == "✉️ Cover Letter Generator":
    st.markdown("<h1 style='text-align: center; margin-bottom: 8px; background: linear-gradient(135deg, #ffffff 0%, #fef08a 40%, #f59e0b 80%, #fbbf24 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.8rem; font-weight: 800;'>✉️ Cover Letter Generator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;' class='pro-subtitle'>Generate a tailored cover letter instantly using AI.</p>", unsafe_allow_html=True)
    st.write("")
    
    col_cl_up, col_cl_tg = st.columns(2)
    with col_cl_up:
        st.markdown("""
        <div class="pro-card" style="margin-bottom: 8px; padding: 18px 22px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 26px;">📄</span>
                <div>
                    <h3 style="margin: 0; background: linear-gradient(135deg, #ffffff 0%, #fde047 60%, #f59e0b 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.25rem; font-weight: 700;">1. Upload Resume</h3>
                    <p class="pro-subtitle" style="margin: 2px 0 0 0; font-size: 0.95rem; color: #cbd5e1;">Submit your current resume in PDF or Word (.docx) format.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_cup1, col_cup2 = st.columns([1.6, 1.4])
        with col_cup1:
            uploaded_file = st.file_uploader("Resume (PDF/DOCX)", type=["pdf", "docx"], label_visibility="collapsed", key="cl_resume_input")
        with col_cup2:
            if st.session_state.get('cl_use_demo'):
                if st.button("🔄 Clear Sample Resume", key="cl_clear_sample_btn", use_container_width=True):
                    st.session_state['cl_use_demo'] = False
                    st.rerun()
            else:
                if st.button("✨ Use Sample Resume", key="cl_use_sample_btn", use_container_width=True):
                    st.session_state['cl_use_demo'] = True
                    st.rerun()

        if uploaded_file:
            st.success(f"✓ **{uploaded_file.name}** uploaded ({uploaded_file.size // 1024} KB)")
        elif st.session_state.get('cl_use_demo'):
            st.info("💡 **Sample Resume Loaded:** Alex Morgan (Senior Full-Stack & AI Engineer)")
            
    with col_cl_tg:
        st.markdown("""
        <div class="pro-card" style="margin-bottom: 8px; padding: 18px 22px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 26px;">🎯</span>
                <div>
                    <h3 style="margin: 0; background: linear-gradient(135deg, #ffffff 0%, #fde047 60%, #f59e0b 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.25rem; font-weight: 700;">2. Target Job Description</h3>
                    <p class="pro-subtitle" style="margin: 2px 0 0 0; font-size: 0.95rem; color: #cbd5e1;">Paste the job description or role requirements.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        default_cl_jd = demo_data.SAMPLE_JOB_DESCRIPTION if st.session_state.get('cl_use_demo') else ""
        job_description = st.text_area("Job Description", value=default_cl_jd, height=140, placeholder="Paste target job requirements and key responsibilities...", key="cl_jd_input", label_visibility="collapsed")
        if job_description.strip():
            st.info(f"✓ Job description entered ({len(job_description.split())} words)")
            
    st.markdown("""
    <div class="pro-card" style="margin-top: 10px; margin-bottom: 12px; padding: 18px 22px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 26px;">✉️</span>
            <div>
                <h3 style="margin: 0; background: linear-gradient(135deg, #ffffff 0%, #fde047 60%, #f59e0b 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.25rem; font-weight: 700;">3. Generate Cover Letter</h3>
                <p class="pro-subtitle" style="margin: 2px 0 0 0; font-size: 0.95rem; color: #cbd5e1;">Craft a tailored, professional cover letter matching your experience to the job.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    generate_cl_btn = st.button("🚀 Generate Cover Letter", type="primary", use_container_width=True, key="cl_gen_btn_main")
    
    if generate_cl_btn:
        if not check_auth_gate("Generate Cover Letter"):
            pass
        elif uploaded_file is None and not st.session_state.get('cl_use_demo'):
            st.warning("⚠️ Please upload a resume or click 'Use Sample Resume' above.")
        elif not job_description.strip():
            st.warning("⚠️ Please provide a job description.")
        else:
            with st.spinner("🧠 AI is crafting your tailored cover letter..."):
                if uploaded_file is not None:
                    if uploaded_file.name.endswith(".pdf"):
                        resume_text = extract_text_from_pdf(uploaded_file)
                    else:
                        resume_text = extract_text_from_docx(uploaded_file)
                else:
                    resume_text = demo_data.SAMPLE_RESUME_TEXT
                    
                if not resume_text.strip():
                    st.error("Could not extract text. Please ensure the file is valid.")
                else:
                    cover_letter = generate_cover_letter(resume_text, job_description)
                    if st.session_state.get('logged_in'):
                        auth.save_history(st.session_state['username'], "Cover Letter", cover_letter)
                    
                    st.markdown("### 🎉 Your Tailored Cover Letter")
                    edited_cl = st.text_area("Live Editor (Edit your cover letter here before downloading):", value=cover_letter, height=350)
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.download_button("Download Markdown", edited_cl, file_name="Cover_Letter.md", mime="text/markdown", use_container_width=True)
                    with col_b:
                        from utils import create_pdf
                        pdf_bytes = create_pdf(edited_cl)
                        if pdf_bytes:
                            st.download_button("Download PDF", data=pdf_bytes, file_name="Cover_Letter.pdf", mime="application/pdf", use_container_width=True)
                        else:
                            st.error("PDF generation failed.")

elif app_mode == "💼 Find Jobs":
    st.markdown("<h1 style='text-align: center; background: linear-gradient(135deg, #ffffff 0%, #fef08a 40%, #f59e0b 80%, #fbbf24 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.8rem; font-weight: 800;'>💼 Live Job Market & Multi-Discipline Roles</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;' class='pro-subtitle'>Browse active positions across Finance, Business, Marketing, HR, Healthcare, Tech & Design matched against candidate competencies.</p>", unsafe_allow_html=True)
    st.write("")
    
    col_js1, col_js2 = st.columns([2.5, 1.5])
    with col_js1:
        default_search = st.session_state.get('job_search_target', '')
        search_query = st.text_input("🔍 Search roles, skills, or companies:", value=default_search, placeholder="e.g. Finance, Marketing, BBA, B.Com, Python, Deloitte, Zomato", key="job_search_input")
    with col_js2:
        cat_options = [
            "All", 
            "Finance & Accounting", 
            "Business & Strategy", 
            "Marketing & Media", 
            "HR & People", 
            "Healthcare & Science", 
            "AI & Tech", 
            "Product & Design"
        ]
        cat_filter = st.selectbox("Category Filter", cat_options, key="job_cat_select")
        
    filtered_jobs = demo_data.SAMPLE_JOBS_CATALOG
    if cat_filter != "All":
        filtered_jobs = [j for j in filtered_jobs if j["category"] == cat_filter]
    if search_query.strip():
        q = search_query.strip().lower()
        filtered_jobs = [j for j in filtered_jobs if q in j["title"].lower() or q in j["company"].lower() or any(q in t.lower() for t in j["tags"])]

    st.markdown(f"**Showing {len(filtered_jobs)} opportunities matching your career profile:**")
    st.write("")

    for job in filtered_jobs:
        score_color = "#34d399" if job["match"] >= 90 else "#fbbf24" if job["match"] >= 85 else "#f97316"
        tags_html = " ".join([f'<span style="background: rgba(245, 158, 11, 0.12); color: #fde047; border: 1px solid rgba(245, 158, 11, 0.3); font-size: 0.85rem; padding: 4px 12px; border-radius: 8px; font-weight: 600;">{t}</span>' for t in job["tags"]])
        
        st.markdown(f"""
        <div class="pro-card" style="margin-bottom: 18px; padding: 22px 26px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h3 style="margin: 0; background: linear-gradient(135deg, #ffffff 0%, #fde047 50%, #f59e0b 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.35rem; font-weight: 700;">
                        {job['title']}
                    </h3>
                    <div style="color: #cbd5e1; font-size: 1.05rem; margin-top: 5px; font-weight: 500;">
                        🏢 <strong style="color: #ffffff;">{job['company']}</strong> &nbsp;•&nbsp; 📍 {job['location']} &nbsp;•&nbsp; 💼 {job['type']} &nbsp;•&nbsp; 💰 <strong style="color: #34d399; font-weight: 700;">{job['salary']}</strong>
                    </div>
                </div>
                <div style="background: {score_color}22; border: 1.5px solid {score_color}; border-radius: 20px; padding: 5px 16px; font-weight: 700; color: {score_color}; font-size: 0.95rem; box-shadow: 0 0 12px {score_color}44;">
                    ★ {job['match']}% Match
                </div>
            </div>
            <p style="color: #cbd5e1; font-size: 1.05rem; margin: 12px 0 14px 0; line-height: 1.6;">
                {job['description']}
            </p>
            <div style="margin-bottom: 12px;">
                {tags_html}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_app1, col_app2 = st.columns([1.2, 2.8])
        with col_app1:
            if st.button(f"⚡ One-Click Apply ({job['company']})", key=f"btn_apply_{job['id']}", type="primary", use_container_width=True):
                if check_auth_gate(f"Apply to {job['title']} at {job['company']}"):
                    st.success(f"🎉 Application packet (ATS Resume & Tailored Cover Letter) submitted to {job['company']}!")
        st.write("")


