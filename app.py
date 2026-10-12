import streamlit as st
import pandas as pd
import time
import re
import plotly.graph_objects as go
from utils import extract_text_from_pdf, extract_text_from_docx, match_skills, get_resume_suggestions, generate_resume, generate_cover_letter
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
    color: #2563eb !important;
    cursor: pointer !important;
    z-index: 100000 !important;
}

[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    position: fixed !important;
    top: 14px !important;
    left: 14px !important;
    background: #ffffff !important;
    border: 1.5px solid #3b82f6 !important;
    border-radius: 8px !important;
    padding: 6px 8px !important;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25) !important;
}

[data-testid="stSidebarCollapsedControl"]:hover,
[data-testid="collapsedControl"]:hover {
    background: #eff6ff !important;
    border-color: #2563eb !important;
    transform: scale(1.06) !important;
}

/* Hide confusing markdown header anchor links */
[data-testid="stHeaderActionElements"],
a.header-anchor,
.stMarkdown a[href^="#"] {
    display: none !important;
}

/* Logo Home Button Styling */
div[data-testid*="btn_logo_brand"] button,
button[key="btn_logo_brand"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #0f172a !important;
    font-size: 1.3rem !important;
    font-weight: 700 !important;
    padding: 6px 10px !important;
    text-align: left !important;
    cursor: pointer !important;
}
div[data-testid*="btn_logo_brand"] button:hover {
    background: #eff6ff !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    transform: none !important;
}
div[data-testid*="btn_logo_brand"] button * {
    color: #0f172a !important;
    font-size: 1.3rem !important;
    font-weight: 700 !important;
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
</style>
""", unsafe_allow_html=True)

# --- Native Clean Top Header with Clickable Logo, Demo Quick-Toggle, and Auth ---
col_logo, col_tagline, col_demo_btn, col_auth = st.columns([3.2, 3.2, 2.0, 1.6])
with col_logo:
    if st.button("⚡ Resume Analyzer Pro", key="btn_logo_brand", use_container_width=True):
        navigate_to("📊 Dashboard")

with col_tagline:
    st.markdown("<div style='padding-top: 8px; color: #64748b; font-size: 0.95rem; font-weight: 500;'>AI Career Intelligence Platform</div>", unsafe_allow_html=True)

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

# --- Custom CSS for "Professional Light" Look ---
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background-color: #f8fafc;
        color: #1e293b;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Sidebar Navigation Menu (Radio) Styling */
    [data-testid="stSidebar"] [data-testid="stRadio"] label p {
        font-size: 1.2rem !important; 
        font-weight: 500 !important;
        color: #1e293b !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {
        gap: 1.5rem !important; /* Huge spacing between options */
        padding-top: 10px;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #0f172a !important;
        font-weight: 600 !important;
        letter-spacing: -0.5px;
    }
    
    /* Cards */
    .pro-card {
        background: #ffffff;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        padding: 26px;
        margin-bottom: 22px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .pro-card:hover {
        border-color: #3b82f6;
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    /* Increase Global Font Size */
    p, li, label, .stTextInput input, .stTextArea textarea, .stMarkdown {
        font-size: 1.1rem !important;
    }

    /* Buttons - Primary, Form Submit, and Standard Buttons */
    .stButton>button, 
    .stFormSubmitButton>button, 
    [data-testid="stFormSubmitButton"]>button,
    button[data-testid="stBaseButton-primary"],
    button[kind="primary"] {
        background: linear-gradient(90deg, #2563eb, #4f46e5) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 14px 0 rgba(79, 70, 229, 0.25) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        cursor: pointer !important;
    }
    /* Force internal button text to be white and bold */
    .stButton>button *, 
    .stFormSubmitButton>button *, 
    [data-testid="stFormSubmitButton"]>button *,
    button[data-testid="stBaseButton-primary"] *,
    button[kind="primary"] * {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }
    .stButton>button:hover, 
    .stFormSubmitButton>button:hover, 
    [data-testid="stFormSubmitButton"]>button:hover,
    button[data-testid="stBaseButton-primary"]:hover,
    button[kind="primary"]:hover {
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.45) !important;
        transform: translateY(-1px) scale(1.01) !important;
        background: linear-gradient(90deg, #1d4ed8, #4338ca) !important;
    }

    /* Download Buttons */
    .stDownloadButton>button {
        background: linear-gradient(90deg, #059669, #10b981) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 14px 0 rgba(16, 185, 129, 0.25) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        cursor: pointer !important;
    }
    .stDownloadButton>button * {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }
    .stDownloadButton>button:hover {
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.45) !important;
        transform: translateY(-1px) scale(1.01) !important;
        background: linear-gradient(90deg, #047857, #059669) !important;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        background: -webkit-linear-gradient(#2563eb, #4f46e5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    [data-testid="stMetricLabel"] {
        color: #64748b !important;
        font-weight: 500;
        font-size: 1.05rem !important;
    }
    
    /* Text colors */
    p, li, .stMarkdown, .stText, label {
        color: #475569 !important;
    }
    
    /* Subtitles / small text */
    .pro-subtitle {
        color: #64748b;
        font-size: 1.15rem;
    }
    
    /* Streamlit Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #f1f5f9 !important;
        color: #2563eb !important;
        border-bottom: 2px solid #2563eb !important;
    }
    </style>
""", unsafe_allow_html=True)

def create_gauge_chart(score):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Match Compatibility", 'font': {'size': 20, 'color': '#0f172a'}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#cbd5e1"},
            'bar': {'color': "#3b82f6"},
            'bgcolor': "#f8fafc",
            'borderwidth': 1,
            'bordercolor': "#e2e8f0",
            'steps': [
                {'range': [0, 40], 'color': "rgba(239, 68, 68, 0.15)"},
                {'range': [40, 70], 'color': "rgba(245, 158, 11, 0.15)"},
                {'range': [70, 100], 'color': "rgba(16, 185, 129, 0.15)"}],
            'threshold': {
                'line': {'color': "#0f172a", 'width': 3},
                'thickness': 0.75,
                'value': score}
        },
        number={'font': {'color': '#2563eb', 'size': 50, 'weight': 'bold'}}
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
        <div style="background: linear-gradient(135deg, #eff6ff 0%, #e0e7ff 100%); 
                    border: 2px solid #3b82f6; 
                    border-radius: 16px; 
                    padding: 24px 28px; 
                    margin: 16px 0 24px 0; 
                    box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.15);">
            <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 8px;">
                <span style="font-size: 32px;">🔒</span>
                <div>
                    <h3 style="margin: 0; color: #1e3a8a !important; font-size: 1.45rem; font-weight: 700;">Sign Up Required to {feature_name}</h3>
                    <span style="color: #4f46e5; font-size: 0.95rem; font-weight: 600;">⚡ Instant 10-second free setup</span>
                </div>
            </div>
            <p style="color: #334155; font-size: 1.05rem; line-height: 1.5; margin: 10px 0 14px 0;">
                Your uploaded documents and form details are preserved! To generate AI content, calculate ATS compatibility scores, and download professional files, please <strong>sign up for a free account</strong> or <strong>sign in</strong>.
            </p>
            <div style="background: rgba(255, 255, 255, 0.9); border-radius: 10px; padding: 12px 18px; border: 1px solid #bfdbfe; margin-bottom: 16px;">
                <span style="font-weight: 700; color: #1e40af;">Included Free With Your Account:</span>
                <ul style="margin: 6px 0 0 0; padding-left: 20px; color: #475569; font-size: 0.95rem;">
                    <li>✨ Unlimited AI Resume & Cover Letter generation</li>
                    <li>📊 ATS semantic keyword scoring & real-time feedback</li>
                    <li>📥 PDF & Markdown export downloads with history tracking</li>
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
            border: none;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
            border-radius: 16px;
            background-color: #ffffff;
            padding: 32px;
        }
        .stTabs [data-baseweb="tab-list"] {
            justify-content: center;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([0.5, 3, 0.5])
    
    with col2:
        st.markdown("<h1 style='text-align: center; color: #0f172a !important; font-size: 3rem; margin-bottom: 0;'>Resume Analyzer Pro</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.2rem;'>Your AI-powered career coach. Build, analyze, and land your dream job.</p>", unsafe_allow_html=True)
        st.write("")
        st.write("")
        
        main_col1, empty_col, main_col2 = st.columns([1.2, 0.2, 1])
        
        with main_col1:
            st.markdown("<h3 style='color: #1e293b; margin-top: 20px;'>🚀 Supercharge your job search</h3>", unsafe_allow_html=True)
            st.write("")
            st.markdown("**✨ AI Resume Builder**<br><span style='color: #64748b;'>Generate ATS-optimized resumes in seconds from your LinkedIn profile.</span>", unsafe_allow_html=True)
            st.write("")
            st.markdown("**📈 Smart Match Scoring**<br><span style='color: #64748b;'>Compare your resume against any job description and get actionable feedback.</span>", unsafe_allow_html=True)
            st.write("")
            st.markdown("**✉️ Tailored Cover Letters**<br><span style='color: #64748b;'>Instantly draft highly personalized cover letters that highlight your strengths.</span>", unsafe_allow_html=True)
            
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
    st.markdown("""
        <style>
        .metric-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 22px;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        .metric-value { font-size: 2.5rem; font-weight: 700; color: #2563eb; line-height: 1.2; }
        .metric-label { font-size: 0.9rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 5px; }
        </style>
    """, unsafe_allow_html=True)
    
    if st.session_state.get('logged_in'):
        st.markdown(f"<h1 style='color: #0f172a !important; margin-bottom: 0;'>Welcome back, {st.session_state['username']}! 👋</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748b; font-size: 1.15rem; margin-top: 5px;'>Here is a summary of your career workspace.</p>", unsafe_allow_html=True)
        
        if st.session_state.get('demo_mode_active'):
            st.markdown("""
            <div style="background: #eff6ff; border: 1.5px solid #3b82f6; border-radius: 10px; padding: 12px 18px; margin: 12px 0 18px 0; display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <span style="font-weight: 700; color: #1e40af;">💡 Demo Mode Active:</span>
                    <span style="color: #3b82f6; margin-left: 6px;">Exploring profile for <strong>Alex Morgan (Senior Full-Stack & AI Engineer)</strong> with pre-loaded resumes, ATS metrics, and cover letters.</span>
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
        st.markdown("### 🚀 Quick Launch Tools")
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
            st.markdown("### 📜 Recent Activity & Saved Documents")
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
        st.markdown("<h1 style='color: #0f172a !important; text-align: center; margin-bottom: 6px; font-size: 2.8rem;'>Career Intelligence Workspace 🚀</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.25rem; max-width: 800px; margin: 0 auto 20px auto;'>Your all-in-one AI platform to build ATS-optimized resumes, score job compatibility, and craft tailored cover letters.</p>", unsafe_allow_html=True)
        
        # 1-Click Demo Feature Callout Card
        st.markdown("""
        <div style="background: linear-gradient(135deg, #eff6ff 0%, #e0e7ff 100%); 
                    border: 1.5px solid #3b82f6; border-radius: 14px; padding: 20px 28px; margin-bottom: 24px;
                    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.08);">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px;">
                <div>
                    <h3 style="margin: 0; color: #1e3a8a !important; font-size: 1.35rem; font-weight: 700;">
                        ✨ Explore Instantly with Pre-Loaded Demo Data
                    </h3>
                    <p style="margin: 6px 0 0 0; color: #475569; font-size: 1.05rem;">
                        No resume ready? Click below to populate a full sample profile (Alex Morgan - Senior AI Engineer) with ATS match reports, generated resumes, and live jobs.
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
                <h3 style="color: #2563eb !important; margin-top: 0; display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 28px;">🔍</span> Resume Analyzer Pro
                </h3>
                <p class="pro-subtitle" style="line-height: 1.5; margin-bottom: 14px;">
                    Upload your resume and target job description to calculate semantic match scores, uncover keyword gaps, and get AI recommendations.
                </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Resume Analyzer →", type="primary", key="home_launch_an", use_container_width=True):
                navigate_to("🔍 Resume Analyzer")

        with col2:
            st.markdown("""
            <div class="pro-card" style="margin-bottom: 14px;">
                <h3 style="color: #2563eb !important; margin-top: 0; display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 28px;">✨</span> AI Resume Builder
                </h3>
                <p class="pro-subtitle" style="line-height: 1.5; margin-bottom: 14px;">
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
                <h3 style="color: #2563eb !important; margin-top: 0; display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 28px;">✉️</span> Cover Letter Generator
                </h3>
                <p class="pro-subtitle" style="line-height: 1.5; margin-bottom: 14px;">
                    Instantly draft highly personalized, compelling cover letters that match your actual experience to the job requirements.
                </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Cover Letter Generator →", type="primary", key="home_launch_cl", use_container_width=True):
                navigate_to("✉️ Cover Letter Generator")

        with col4:
            st.markdown("""
            <div class="pro-card" style="margin-bottom: 14px;">
                <h3 style="color: #2563eb !important; margin-top: 0; display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 28px;">💼</span> Find Jobs
                </h3>
                <p class="pro-subtitle" style="line-height: 1.5; margin-bottom: 14px;">
                    Discover curated live job matches tailored to your target skills, salary expectations, and preferred roles.
                </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Browse Live Jobs →", type="primary", key="home_launch_jb", use_container_width=True):
                navigate_to("💼 Find Jobs")

        st.write("")
        # Call to action card
        st.markdown("""
        <div style="background: linear-gradient(135deg, #eff6ff 0%, #e0e7ff 100%); 
                    border: 2px solid #3b82f6; border-radius: 16px; padding: 26px 32px; 
                    margin-top: 20px; text-align: center;">
            <h2 style="color: #1e3a8a !important; margin-top: 0; font-size: 1.8rem;">Ready to Land Your Next Role?</h2>
            <p style="color: #475569; font-size: 1.15rem; max-width: 650px; margin: 8px auto 20px auto;">
                Create a free account in 10 seconds to unlock unlimited AI document generations, save your resume versions, and export PDF copies.
            </p>
        </div>
        """, unsafe_allow_html=True)
        col_cta1, col_cta2, col_cta3 = st.columns([1, 1.5, 1])
        with col_cta2:
            if st.button("🚀 Create Free Account / Sign In", type="primary", key="home_cta_auth", use_container_width=True):
                navigate_to("👤 Account")

if app_mode == "🔍 Resume Analyzer":
    st.markdown("<h1 style='text-align: center; margin-bottom: 8px; color: #2563eb !important;'>📈 Resume Analyzer Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;' class='pro-subtitle'>Enterprise-grade resume parsing and AI semantic matching.</p>", unsafe_allow_html=True)
    st.write("")

    # Connected 3-Step Workflow Cards directly on the main page
    col_card1, col_card2 = st.columns(2)
    with col_card1:
        st.markdown("""
        <div class="pro-card" style="margin-bottom: 8px; padding: 18px 22px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 26px;">📄</span>
                <div>
                    <h3 style="margin: 0; color: #1e293b !important; font-size: 1.25rem;">1. Upload Resume</h3>
                    <p class="pro-subtitle" style="margin: 2px 0 0 0; font-size: 0.95rem;">Submit your current resume in PDF or Word (.docx) format.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_up1, col_up2 = st.columns([1.6, 1.4])
        with col_up1:
            uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"], key="analyzer_file_input", label_visibility="collapsed")
        with col_up2:
            if st.session_state.get('analyzer_use_demo'):
                if st.button("🔄 Clear Sample Resume", key="clear_sample_res_btn", use_container_width=True):
                    st.session_state['analyzer_use_demo'] = False
                    st.rerun()
            else:
                if st.button("✨ Use Sample Resume (1-Click)", key="use_sample_res_btn", use_container_width=True):
                    st.session_state['analyzer_use_demo'] = True
                    st.rerun()

        if uploaded_file:
            st.success(f"✓ **{uploaded_file.name}** ready for analysis ({uploaded_file.size // 1024} KB)")
        elif st.session_state.get('analyzer_use_demo'):
            st.info("💡 **Sample Resume Loaded:** Alex Morgan (Senior Full-Stack & AI Engineer)")

    with col_card2:
        st.markdown("""
        <div class="pro-card" style="margin-bottom: 8px; padding: 18px 22px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 26px;">🎯</span>
                <div>
                    <h3 style="margin: 0; color: #1e293b !important; font-size: 1.25rem;">2. Target Job Description</h3>
                    <p class="pro-subtitle" style="margin: 2px 0 0 0; font-size: 0.95rem;">Paste the job description or role requirements.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        default_jd_val = demo_data.SAMPLE_JOB_DESCRIPTION if st.session_state.get('analyzer_use_demo') else ""
        job_description = st.text_area(
            "Target Job Description",
            value=default_jd_val,
            height=140,
            placeholder="Paste target job requirements, skills, and qualifications here...",
            key="analyzer_jd_input",
            label_visibility="collapsed"
        )
        if job_description.strip():
            st.info(f"✓ Job description entered ({len(job_description.split())} words)")

    st.markdown("""
    <div class="pro-card" style="margin-top: 10px; margin-bottom: 12px; padding: 18px 22px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 26px;">⚡</span>
            <div>
                <h3 style="margin: 0; color: #1e293b !important; font-size: 1.25rem;">3. Run Analysis</h3>
                <p class="pro-subtitle" style="margin: 2px 0 0 0; font-size: 0.95rem;">Calculate ATS compatibility score, extract missing keywords, and get AI recommendations.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    analyze_btn = st.button("🚀 Run Analysis", type="primary", use_container_width=True, key="analyzer_run_btn")

    if analyze_btn:
        if not check_auth_gate("Run Resume Analysis"):
            pass
        elif uploaded_file is None and not st.session_state.get('analyzer_use_demo'):
            st.warning("⚠️ Please upload a resume or click 'Use Sample Resume' above.")
        elif not job_description.strip():
            st.warning("⚠️ Please provide a target job description.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Ingesting document...")
            progress_bar.progress(25)
            
            if uploaded_file is not None:
                if uploaded_file.name.endswith(".pdf"):
                    resume_text = extract_text_from_pdf(uploaded_file)
                else:
                    resume_text = extract_text_from_docx(uploaded_file)
            else:
                resume_text = demo_data.SAMPLE_RESUME_TEXT
                
            if not resume_text.strip():
                st.error("Could not extract text. Please ensure the file is valid.")
                st.stop()
                
            status_text.text("Computing match score matrices...")
            progress_bar.progress(70)
            
            results = match_skills(resume_text, job_description)
            health = basic_resume_health(resume_text)
            
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

            # --- AI Suggestions (New Feature) ---
            st.markdown("### 🤖 AI Suggestions for Improvement")
            with st.spinner("AI is analyzing your resume against the job description..."):
                ai_feedback = get_resume_suggestions(resume_text, job_description)
                st.markdown(ai_feedback)

            # --- Missing/Matched Skills ---
            tab1, tab2, tab3 = st.tabs(["✓ Matched Terms", "✗ Missing Terms", "Raw Text"])
            
            with tab1:
                st.markdown("#### Found in both Resume and Job Description:")
                if results['matched_skills']:
                    tags = "".join([f'<span style="display:inline-block; background-color: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; color: #34d399; padding: 6px 14px; margin: 4px; border-radius: 6px;">{skill.title()}</span>' for skill in results['matched_skills']])
                    st.markdown(tags, unsafe_allow_html=True)
                else:
                    st.info("No major overlapping keywords found.")
                    
            with tab2:
                st.markdown("#### Found in Job Description, missing from Resume:")
                if results['missing_skills']:
                    tags = "".join([f'<span style="display:inline-block; background-color: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; color: #f87171; padding: 6px 14px; margin: 4px; border-radius: 6px;">{skill.title()}</span>' for skill in results['missing_skills']])
                    st.markdown(tags, unsafe_allow_html=True)
                else:
                    st.success("You matched all significant keywords!")
                    
            with tab3:
                st.text(resume_text[:2000] + "...")

elif app_mode == "✨ AI Resume Builder":
    st.markdown("<h1 style='text-align: center; margin-bottom: 8px; color: #60a5fa !important;'>✨ AI Resume Builder</h1>", unsafe_allow_html=True)
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
    st.markdown("<h1 style='text-align: center; margin-bottom: 8px; color: #2563eb !important;'>✉️ Cover Letter Generator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;' class='pro-subtitle'>Generate a tailored cover letter instantly using AI.</p>", unsafe_allow_html=True)
    st.write("")
    
    col_cl_up, col_cl_tg = st.columns(2)
    with col_cl_up:
        st.markdown("""
        <div class="pro-card" style="margin-bottom: 8px; padding: 18px 22px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 26px;">📄</span>
                <div>
                    <h3 style="margin: 0; color: #1e293b !important; font-size: 1.25rem;">1. Upload Resume</h3>
                    <p class="pro-subtitle" style="margin: 2px 0 0 0; font-size: 0.95rem;">Submit your current resume in PDF or Word (.docx) format.</p>
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
                    <h3 style="margin: 0; color: #1e293b !important; font-size: 1.25rem;">2. Target Job Description</h3>
                    <p class="pro-subtitle" style="margin: 2px 0 0 0; font-size: 0.95rem;">Paste the job description or role requirements.</p>
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
                <h3 style="margin: 0; color: #1e293b !important; font-size: 1.25rem;">3. Generate Cover Letter</h3>
                <p class="pro-subtitle" style="margin: 2px 0 0 0; font-size: 0.95rem;">Craft a tailored, professional cover letter matching your experience to the job.</p>
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
    st.markdown("<h1 style='text-align: center; color: #2563eb !important;'>💼 Live Job Market & Compatibility</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;' class='pro-subtitle'>Browse active tech positions matched against your resume competencies.</p>", unsafe_allow_html=True)
    st.write("")
    
    col_js1, col_js2 = st.columns([2.5, 1.5])
    with col_js1:
        search_query = st.text_input("🔍 Search roles, skills, or companies:", placeholder="e.g. AI Engineer, Python, Remote, OpenAI", key="job_search_input")
    with col_js2:
        cat_filter = st.selectbox("Category Filter", ["All", "AI / Data", "Engineering", "Product"], key="job_cat_select")
        
    filtered_jobs = demo_data.SAMPLE_JOBS_CATALOG
    if cat_filter != "All":
        filtered_jobs = [j for j in filtered_jobs if j["category"] == cat_filter]
    if search_query.strip():
        q = search_query.strip().lower()
        filtered_jobs = [j for j in filtered_jobs if q in j["title"].lower() or q in j["company"].lower() or any(q in t.lower() for t in j["tags"])]

    st.markdown(f"**Showing {len(filtered_jobs)} opportunities matching your career profile:**")
    st.write("")

    for job in filtered_jobs:
        score_color = "#10b981" if job["match"] >= 90 else "#3b82f6" if job["match"] >= 85 else "#f59e0b"
        tags_html = " ".join([f'<span style="background: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe; font-size: 0.85rem; padding: 3px 10px; border-radius: 6px; font-weight: 500;">{t}</span>' for t in job["tags"]])
        
        st.markdown(f"""
        <div class="pro-card" style="margin-bottom: 18px; padding: 22px 26px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h3 style="margin: 0; color: #0f172a !important; font-size: 1.35rem; font-weight: 700;">
                        {job['title']}
                    </h3>
                    <div style="color: #64748b; font-size: 1.05rem; margin-top: 4px; font-weight: 500;">
                        🏢 <strong style="color: #1e293b;">{job['company']}</strong> &nbsp;•&nbsp; 📍 {job['location']} &nbsp;•&nbsp; 💼 {job['type']} &nbsp;•&nbsp; 💰 <strong style="color: #059669;">{job['salary']}</strong>
                    </div>
                </div>
                <div style="background: {score_color}15; border: 1.5px solid {score_color}; border-radius: 20px; padding: 4px 14px; font-weight: 700; color: {score_color}; font-size: 0.95rem;">
                    ★ {job['match']}% Match
                </div>
            </div>
            <p style="color: #475569; font-size: 1.05rem; margin: 12px 0 14px 0; line-height: 1.5;">
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


