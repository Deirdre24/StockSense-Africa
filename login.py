import streamlit as st
from auth import sign_in, sign_up

def show_login_page():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        * { font-family: 'Inter', sans-serif; }
        #MainMenu, footer, header { visibility: hidden; }
        .stApp { background: linear-gradient(135deg, #0F2419 0%, #1B4332 100%); min-height: 100vh; }
        
        .block-container { 
            max-width: 480px !important; 
            padding-top: 40px !important;
            background: #FFFFFF !important;
            border-radius: 16px !important;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3) !important;
            margin-top: 40px !important;
        }        
        .block-container { max-width: 480px !important; padding-top: 60px !important; }

        .login-logo { text-align: center; font-size: 52px; margin-bottom: 10px; }
        .login-title { text-align: center; color: #34D399; font-size: 26px; font-weight: 800; margin: 0 0 4px; }
        .login-sub { text-align: center;  rgba(255,255,255,0.75); font-size: 13px; margin: 0 0 6px; }
        .gold-bar { width: 48px; height: 3px; background: linear-gradient(90deg, #D4A017, #F59E0B); border-radius: 2px; margin: 0 auto 28px; }

        .form-card {
            background: #FFFFFF;
            border-radius: 16px;
            padding: 32px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }

        .stTabs [data-baseweb="tab-list"] {
            background: #F3F4F6; border-radius: 10px; padding: 4px; gap: 4px; margin-bottom: 20px;
        }
        .stTabs [data-baseweb="tab"] {
            background: transparent; border-radius: 8px; color: #6B7280 !important;
            font-weight: 600; font-size: 14px; padding: 8px 0; border: none !important; flex: 1; justify-content: center;
        }
        .stTabs [aria-selected="true"] { background: #FFFFFF !important; color: #1B4332 !important; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
        .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

        .stTextInput label { color: #374151 !important; font-size: 13px !important; font-weight: 600 !important; }
        .stTextInput input { color: #1C1C1E !important; background: #F9FAFB !important; border: 1.5px solid #E5E7EB !important; border-radius: 8px !important; font-size: 14px !important; }

        .stSelectbox label { color: #374151 !important; font-size: 13px !important; font-weight: 600 !important; }
        div[data-baseweb="select"] > div { background: #F9FAFB !important; border: 1.5px solid #E5E7EB !important; border-radius: 8px !important; }
        div[data-baseweb="select"] * { color: #1C1C1E !important; }
        div[data-baseweb="popover"] * { color: #1C1C1E !important; background: #FFFFFF !important; }

        .stButton button {
            background: #1B4332 !important; color: #FFFFFF !important; border: none !important;
            border-radius: 10px !important; font-weight: 700 !important; font-size: 15px !important;
            padding: 14px !important; width: 100% !important; margin-top: 8px !important; transition: all 0.2s !important;
        }
        .stButton button:hover { background: #2D6A4F !important; transform: translateY(-1px) !important; box-shadow: 0 6px 20px rgba(27,67,50,0.35) !important; }

        .login-footer { text-align: center; color: rgba(255,255,255,0.35); font-size: 11px; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="login-logo">🌍</div>
    <p class="login-title">StockSense Africa</p>
    <p class="login-sub">Inventory & Procurement Intelligence</p>
    <div class="gold-bar"></div>
    """, unsafe_allow_html=True)

    # Form card
    st.markdown('<div class="form-card">', unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["  Sign In  ", "  Create Account  "])

    with tab_login:
        st.markdown("<br>", unsafe_allow_html=True)
        email = st.text_input("Email address", placeholder="you@example.com", key="login_email")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Sign In →", key="signin_btn"):
            if not email or not password:
                st.error("Please fill in all fields.")
            else:
                result = sign_in(email, password)
                if result["success"]:
                    st.session_state.user = result["user"]
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error(result["message"])

    with tab_signup:
        st.markdown("<br>", unsafe_allow_html=True)
        new_email = st.text_input("Email address", placeholder="you@example.com", key="signup_email")
        new_business = st.text_input("Business Name", placeholder="e.g. Thabo's General Store", key="signup_business")
        new_role = st.selectbox("I am a...", ["owner", "consultant"], key="signup_role",
            format_func=lambda x: "🏪 Shop Owner" if x == "owner" else "💼 Consultant")
        new_password = st.text_input("Password", type="password", placeholder="Min. 6 characters", key="signup_password")
        new_confirm = st.text_input("Confirm Password", type="password", placeholder="Repeat your password", key="signup_confirm")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Create Account →", key="signup_btn"):
            if not all([new_email, new_business, new_password, new_confirm]):
                st.error("Please fill in all fields.")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters.")
            elif new_password != new_confirm:
                st.error("Passwords do not match.")
            else:
                result = sign_up(new_email, new_password, new_business, new_role)
                if result["success"]:
                    st.success("✅ Account created! Please sign in.")
                else:
                    st.error(result["message"])

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<p class="login-footer">© 2026 StockSense Africa · Built for African SMEs</p>', unsafe_allow_html=True)