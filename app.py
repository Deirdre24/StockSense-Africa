import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq
import os
from agent import run_procurement_agent
from dotenv import load_dotenv
from login import show_login_page

load_dotenv("config.env")

# ---- AUTH GATE ----
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    show_login_page()
    st.stop()

# ---- GET CURRENT USER ----
user = st.session_state.user
business_name = user["business_name"]
role = user["role"]

st.set_page_config(page_title="StockSense Africa", page_icon="🌍", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif; }
    #MainMenu, footer, header { visibility: hidden; }
    .stApp { background-color: #F0F2F5; }

    [data-testid="stSidebar"] { background: #0F2419 !important; border-right: none !important; }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] .sidebar-brand-name,
    [data-testid="stSidebar"] .sidebar-section { color: #E5E7EB !important; }
    [data-testid="stSidebar"] label { color: #9CA3AF !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 1px; }

    div[data-baseweb="select"] * { color: #1C1C1E !important; }
    div[data-baseweb="select"] > div { background: #FFFFFF !important; }
    [data-testid="stSidebar"] div[data-baseweb="select"] * { color: #1C1C1E !important; background: #FFFFFF !important; }
    [data-testid="stSidebar"] div[data-baseweb="select"] div { background: #FFFFFF !important; }
    div[data-baseweb="popover"] * { color: #1C1C1E !important; background: #FFFFFF !important; }
    div[data-baseweb="input"] input { color: #1C1C1E !important; background: #FFFFFF !important; }

    [data-testid="stFileUploader"] { background: rgba(255,255,255,0.05) !important; border: 1px dashed rgba(255,255,255,0.3) !important; border-radius: 8px !important; padding: 8px !important; }
    [data-testid="stFileUploader"] span { color: black !important; }
    [data-testid="stFileUploader"] p { color: black !important; }
    [data-testid="stFileUploader"] small { color: #9CA3AF !important; }
    [data-testid="stFileUploader"] button { color: #1C1C1E !important; background: #FFFFFF !important; }

    .stDateInput input { color: #1C1C1E !important; background: #FFFFFF !important; }
    input[type="number"] { color: #1C1C1E !important; background: #FFFFFF !important; }
    input[type="text"] { color: #1C1C1E !important; background: #FFFFFF !important; }
    .stTextInput input { color: #1C1C1E !important; }
    .stNumberInput input { color: #1C1C1E !important; }

    .sidebar-brand { padding: 24px 16px 20px; border-bottom: 1px solid rgba(212,160,23,0.3); margin-bottom: 20px; }
    .sidebar-brand-name { color: #FFFFFF !important; font-size: 18px; font-weight: 800; margin: 6px 0 2px; }
    .sidebar-brand-tag { color: #D4A017 !important; font-size: 10px; text-transform: uppercase; letter-spacing: 2px; margin: 0 0 6px; }
    p.sidebar-brand-tag { color: #D4A017 !important; } 
    .sidebar-user { color: #86EFAC !important; font-size: 11px; margin: 12px 0 0; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.08); }              
    .sidebar-user { color: #86EFAC !important; font-size: 11px; margin: 4px  0; }
    .sidebar-section { color: #6B7280 !important; font-size: 10px !important; text-transform: uppercase; letter-spacing: 1.5px; margin: 20px 0 8px; font-weight: 600; }

    .topbar {
        background: linear-gradient(135deg, #1B4332 0%, #0F2419 100%);
        border-radius: 14px; padding: 22px 28px; margin-bottom: 20px;
        display: flex; align-items: center; justify-content: space-between;
        box-shadow: 0 4px 20px rgba(27,67,50,0.25);
    }
    .topbar-left h1 { color: #FFFFFF; font-size: 22px; font-weight: 800; margin: 0 0 4px; }
    .topbar-left p { color: #86EFAC; font-size: 12px; margin: 0; font-weight: 500; }
    .topbar-right { display: flex; align-items: center; gap: 12px; }
    .topbar-role { color: #86EFAC; font-size: 12px; font-weight: 500; }
    .topbar-badge { background: #D4A017; color: #FFFFFF; font-size: 11px; font-weight: 700; padding: 6px 16px; border-radius: 20px; }

    .stTabs [data-baseweb="tab-list"] { background: #FFFFFF; border-radius: 10px; padding: 6px; gap: 4px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); margin-bottom: 20px; }
    .stTabs [data-baseweb="tab"] { background: transparent; border-radius: 8px; color: #6B7280 !important; font-weight: 600; font-size: 13px; padding: 8px 20px; border: none !important; }
    .stTabs [aria-selected="true"] { background: #1B4332 !important; color: #FFFFFF !important; }
    .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

    .kpi-card { background: #FFFFFF; border-radius: 12px; padding: 20px 22px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); border-top: 3px solid #1B4332; transition: all 0.2s ease; cursor: default; }
    .kpi-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(27,67,50,0.12); }
    .kpi-card.gold { border-top-color: #D4A017; }
    .kpi-card.gold:hover { box-shadow: 0 8px 24px rgba(212,160,23,0.15); }
    .kpi-icon { font-size: 24px; margin-bottom: 12px; }
    .kpi-label { color: #9CA3AF; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
    .kpi-value { color: #111827; font-size: 28px; font-weight: 800; margin: 0; }
    .kpi-sub { color: #6B7280; font-size: 11px; margin-top: 4px; }

    .sec-title { font-size: 15px; font-weight: 700; color: #111827; margin: 24px 0 14px; display: flex; align-items: center; gap: 8px; }
    .sec-title::after { content: ''; flex: 1; height: 1px; background: #E5E7EB; margin-left: 8px; }

    .alert-card { background: #FFFFFF; border-radius: 10px; padding: 14px 18px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 3px rgba(0,0,0,0.05); transition: all 0.2s; border-left: 4px solid #E5E7EB; }
    .alert-card:hover { transform: translateX(4px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    .alert-card.red { border-left-color: #EF4444; }
    .alert-card.yellow { border-left-color: #F59E0B; }
    .alert-card.green { border-left-color: #10B981; }
    .alert-product { font-weight: 600; color: #111827; font-size: 14px; }
    .alert-days { font-size: 13px; color: #6B7280; margin-top: 2px; }
    .badge { padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 700; }
    .badge.red { background: #FEE2E2; color: #991B1B; }
    .badge.yellow { background: #FEF3C7; color: #92400E; }
    .badge.green { background: #D1FAE5; color: #065F46; }

    .supplier-card { background: #FFFFFF; border-radius: 12px; padding: 18px 22px; margin-bottom: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); transition: all 0.2s; display: flex; align-items: center; justify-content: space-between; }
    .supplier-card:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(0,0,0,0.1); }
    .supplier-name { font-weight: 700; color: #111827; font-size: 14px; }
    .supplier-product { color: #6B7280; font-size: 12px; margin-top: 2px; }
    .supplier-price { font-size: 20px; font-weight: 800; color: #1B4332; }
    .supplier-price-label { font-size: 10px; color: #9CA3AF; text-align: right; }
    .best-badge { background: #D1FAE5; color: #065F46; font-size: 10px; font-weight: 700; padding: 3px 10px; border-radius: 20px; margin-left: 8px; }

    .ai-result { background: #FFFFFF; border-radius: 12px; padding: 28px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); border-left: 4px solid #1B4332; margin-top: 16px; }
    .ai-result h4 { color: #1B4332; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px; }
    .ai-result p { color: #374151; line-height: 1.9; font-size: 14px; margin: 0; }

    .stButton button { background: #1B4332 !important; color: #FFFFFF !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; font-size: 14px !important; padding: 10px 28px !important; transition: all 0.2s !important; }
    .stButton button:hover { background: #2D6A4F !important; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(27,67,50,0.3) !important; }
    .stDataFrame { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ---- SIDEBAR ----
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-brand">
        <div style="font-size:32px;">🌍</div>
        <p class="sidebar-brand-name">StockSense Africa</p>
        <p class="sidebar-brand-tag">Inventory Intelligence</p>
        <p class="sidebar-user">{business_name}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="sidebar-section">Data Source</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv","xlsx"], label_visibility="collapsed")
    st.markdown('<p class="sidebar-section">Filters</p>', unsafe_allow_html=True)

# ---- LOAD DATA ----
if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
else:
    df = pd.read_csv("sample_data.csv")

df['date'] = pd.to_datetime(df['date'])
df['revenue'] = df['quantity_sold'] * df['unit_price']

# ---- SIDEBAR FILTERS ----
with st.sidebar:
    products = ["All Products"] + list(df['product'].unique())
    selected_product = st.selectbox("Product", products)
    date_range = st.date_input("Date Range",
        value=[df['date'].min(), df['date'].max()],
        min_value=df['date'].min().date(),
        max_value=df['date'].max().date())
    st.markdown("---")
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.agent_result = None
        st.rerun()
    st.markdown('<p style="color:#4B5563;font-size:11px;text-align:center;">StockSense Africa v1.0<br/>Built for African SMEs</p>', unsafe_allow_html=True)

# ---- APPLY FILTERS ----
fdf = df.copy()
if selected_product != "All Products":
    fdf = fdf[fdf['product'] == selected_product]
if len(date_range) == 2:
    fdf = fdf[(fdf['date'] >= pd.to_datetime(date_range[0])) & (fdf['date'] <= pd.to_datetime(date_range[1]))]

# ---- COMPUTE INVENTORY STATS ----
avg = fdf.groupby('product').agg(
    avg_daily=('quantity_sold', 'mean'),
    total_units=('quantity_sold', 'sum'),
    total_revenue=('revenue', 'sum')
).reset_index()
avg['days_left'] = (50 / avg['avg_daily']).round(1)
avg['avg_daily'] = avg['avg_daily'].round(1)
avg['status'] = avg['days_left'].apply(lambda x: 'red' if x < 5 else ('yellow' if x < 10 else 'green'))
avg['status_label'] = avg['days_left'].apply(lambda x: '🔴 Reorder Now' if x < 5 else ('🟡 Reorder Soon' if x < 10 else '🟢 In Stock'))

critical = avg[avg['status'] == 'red']
warning = avg[avg['status'] == 'yellow']
top_product = avg.sort_values('total_revenue', ascending=False).iloc[0]['product']
lowest_stock = avg.sort_values('days_left').iloc[0]

# ---- TOP BAR ----
st.markdown(f"""
<div class="topbar">
    <div class="topbar-left">
        <h1>🌍 StockSense Africa</h1>
        <p>AI-powered inventory & procurement intelligence for African SMEs</p>
    </div>
    <div class="topbar-right">
        <span class="topbar-role">{'🏪 Shop Owner' if role == 'owner' else '💼 Consultant'}</span>
        <span class="topbar-badge">LIVE DEMO</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---- TABS ----
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📦 Inventory", "🏪 Procurement", "🤖 Insights"])

# ========== TAB 1: OVERVIEW ==========
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-icon">📦</div><div class="kpi-label">Total Products</div><div class="kpi-value">{fdf["product"].nunique()}</div><div class="kpi-sub">tracked items</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="kpi-card gold"><div class="kpi-icon">💰</div><div class="kpi-label">Total Revenue</div><div class="kpi-value">P {fdf["revenue"].sum():,.0f}</div><div class="kpi-sub">Botswana Pula</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-icon">🛒</div><div class="kpi-label">Units Sold</div><div class="kpi-value">{fdf["quantity_sold"].sum():,}</div><div class="kpi-sub">total units</div></div>', unsafe_allow_html=True)
    with col4:
        days = max((fdf['date'].max() - fdf['date'].min()).days + 1, 1)
        st.markdown(f'<div class="kpi-card gold"><div class="kpi-icon">📅</div><div class="kpi-label">Days of Data</div><div class="kpi-value">{days}</div><div class="kpi-sub">date range</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([2,1])
    with col_l:
        st.markdown('<div class="sec-title">📈 Revenue Trend</div>', unsafe_allow_html=True)
        daily = fdf.groupby('date')['revenue'].sum().reset_index()
        fig = px.area(daily, x='date', y='revenue', color_discrete_sequence=["#1B4332"])
        fig.update_traces(fillcolor='rgba(27,67,50,0.08)', line_color='#1B4332', line_width=2.5)
        fig.update_layout(paper_bgcolor='white', plot_bgcolor='white', margin=dict(l=0,r=0,t=10,b=0),
            yaxis_title="Revenue (BWP)", xaxis_title="", font=dict(family="Inter", color="#374151"),
            yaxis=dict(gridcolor='#F3F4F6'), xaxis=dict(gridcolor='#F3F4F6'))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="sec-title">🏆 Revenue by Product</div>', unsafe_allow_html=True)
        fig2 = px.bar(avg.sort_values('total_revenue'), x='total_revenue', y='product',
            orientation='h', color_discrete_sequence=["#D4A017"])
        fig2.update_layout(paper_bgcolor='white', plot_bgcolor='white', margin=dict(l=0,r=0,t=10,b=0),
            xaxis_title="Revenue (BWP)", yaxis_title="", font=dict(family="Inter", color="#374151"),
            xaxis=dict(gridcolor='#F3F4F6'), yaxis=dict(color='#374151'))
        st.plotly_chart(fig2, use_container_width=True)

# ========== TAB 2: INVENTORY ==========
with tab2:
    st.markdown('<div class="sec-title">⚠️ Stock Health Monitor</div>', unsafe_allow_html=True)

    for _, row in avg.sort_values('days_left').iterrows():
        st.markdown(f"""
        <div class="alert-card {row['status']}">
            <div>
                <div class="alert-product">{row['product']}</div>
                <div class="alert-days">~{row['avg_daily']} units/day &nbsp;·&nbsp; <strong>{row['days_left']} days</strong> of stock remaining</div>
            </div>
            <span class="badge {row['status']}">{row['status_label']}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📊 Units Sold by Product</div>', unsafe_allow_html=True)
    fig3 = px.bar(avg.sort_values('total_units', ascending=False), x='product', y='total_units',
        color='total_units', color_continuous_scale=[[0,'#86EFAC'],[0.5,'#1B4332'],[1,'#0F2419']],
        text='total_units')
    fig3.update_traces(textposition='outside')
    fig3.update_layout(paper_bgcolor='white', plot_bgcolor='white', margin=dict(l=0,r=0,t=10,b=0),
        yaxis_title="Units Sold", xaxis_title="", font=dict(family="Inter", color="#374151"),
        coloraxis_showscale=False, yaxis=dict(gridcolor='#F3F4F6'), xaxis=dict(color='#374151'))
    st.plotly_chart(fig3, use_container_width=True)

# ========== TAB 3: PROCUREMENT ==========
with tab3:
    st.markdown('<div class="sec-title">🏪 Supplier Price Tracker</div>', unsafe_allow_html=True)
    st.caption("Compare supplier prices to always get the best deal for your shop.")

    if 'suppliers' not in st.session_state:
        st.session_state.suppliers = [
            {"name": "Choppies Wholesale", "product": "Rice (50kg)", "price": 420, "best": True},
            {"name": "Sefalana Cash & Carry", "product": "Rice (50kg)", "price": 445, "best": False},
            {"name": "Metro Wholesale", "product": "Cooking Oil (5L)", "price": 58, "best": True},
            {"name": "Choppies Wholesale", "product": "Cooking Oil (5L)", "price": 64, "best": False},
        ]

    for s in st.session_state.suppliers:
        best_html = '<span class="best-badge">✓ Best Price</span>' if s['best'] else ''
        st.markdown(f"""
        <div class="supplier-card">
            <div>
                <div class="supplier-name">{s['name']} {best_html}</div>
                <div class="supplier-product">{s['product']}</div>
            </div>
            <div style="text-align:right">
                <div class="supplier-price">P {s['price']}</div>
                <div class="supplier-price-label">per unit</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec-title">➕ Add Supplier</div>', unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns(3)
    with col_a: new_name = st.text_input("Supplier Name", placeholder="e.g. Sefalana")
    with col_b: new_product = st.text_input("Product", placeholder="e.g. Sugar (2kg)")
    with col_c: new_price = st.number_input("Price (BWP)", min_value=0.0, step=0.5)

    if st.button("Add Supplier"):
        if new_name and new_product and new_price:
            st.session_state.suppliers.append({"name": new_name, "product": new_product, "price": new_price, "best": False})
            st.success(f"✅ {new_name} added!")
            st.rerun()

# ========== TAB 4: INSIGHTS ==========
with tab4:
    st.markdown('<div class="sec-title">🤖 AI Procurement Brief</div>', unsafe_allow_html=True)
    st.caption("An autonomous AI agent analyzes your live inventory and generates a full procurement brief.")

    # ---- RUN AGENT ONCE PER SESSION ----
    if "agent_result" not in st.session_state:
        with st.spinner("🤖 Running procurement agent..."):
            st.session_state.agent_result = run_procurement_agent(
                avg,
                st.session_state.get("suppliers", []),
                business_name
            )

    agent = st.session_state.agent_result

    # ---- AGENT OUTPUT ----
    st.markdown(f"""
    <div class="ai-result">
        <h4>🤖 Autonomous Procurement Report — {business_name}</h4>
        <p>{agent["output"].replace(chr(10), "<br>")}</p>
    </div>
    """, unsafe_allow_html=True)

    col_dl, col_regen, _ = st.columns([1, 1, 2])
    with col_dl:
        st.download_button("📥 Download Report", agent["output"], file_name="procurement_report.txt")
    with col_regen:
        if st.button("🔄 Regenerate"):
            with st.spinner("Re-running agent..."):
                st.session_state.agent_result = run_procurement_agent(
                    avg,
                    st.session_state.get("suppliers", []),
                    business_name
                )
            st.rerun()