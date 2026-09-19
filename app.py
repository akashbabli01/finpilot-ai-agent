import os
import sys
import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Ensure finpilot modules are accessible
sys.path.insert(0, os.path.dirname(__file__))

from processing import load_and_process_csv
from categorizer import categorize_transactions
import analytics
from agent import run_agent_turn
from data_gen import generate_sample_data

# 1. Page Configuration
st.set_page_config(
    page_title="FinPilot - Autonomous Financial Decision Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# High-End Dark Cyberpunk / Pro-FinTech Glassmorphism CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* FIX: Hide/Transparent Top Streamlit Header Bar & Remove White Strip */
    header[data-testid="stHeader"], [data-testid="stHeader"] {
        background: transparent !important;
        background-color: transparent !important;
        z-index: 100;
    }
    div[data-testid="stToolbar"] {
        visibility: hidden !important;
        height: 0px !important;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }
    
    /* Deep Midnight Mesh Background */
    .stApp {
        background: radial-gradient(circle at 50% -20%, #1E1B4B 0%, #0F172A 45%, #090D16 100%);
        background-attachment: fixed;
        color: #F8FAFC;
    }
    
    /* Dark Glassmorphism Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(11, 15, 25, 0.95) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    
    /* File Uploader Dark Styling */
    [data-testid="stFileUploaderDropzone"] {
        background-color: rgba(15, 23, 42, 0.7) !important;
        border: 1px dashed rgba(99, 102, 241, 0.4) !important;
        border-radius: 14px !important;
        transition: all 0.3s ease;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: #6366F1 !important;
        box-shadow: 0 0 18px rgba(99, 102, 241, 0.3);
    }
    [data-testid="stFileUploaderDropzone"] * {
        color: #E2E8F0 !important;
    }
    
    /* Selectbox & Input Dark Styling */
    [data-baseweb="select"] > div, input[type="number"], input[type="text"] {
        background-color: rgba(15, 23, 42, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #F8FAFC !important;
    }
    
    /* Button Dark Styling */
    .stButton > button {
        background: linear-gradient(135deg, rgba(49, 46, 129, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%) !important;
        border: 1px solid rgba(99, 102, 241, 0.4) !important;
        color: #F8FAFC !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.25s ease !important;
    }
    .stButton > button:hover {
        border-color: #6366F1 !important;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.45) !important;
        transform: translateY(-2px);
    }
    
    /* Glass Container Box */
    .glass-card {
        background: rgba(15, 23, 42, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        margin-bottom: 1.5rem;
    }
    
    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(99, 102, 241, 0.4);
        border-radius: 20px;
        padding: 1.8rem 2.2rem;
        box-shadow: 0 16px 40px -10px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        margin-bottom: 1.5rem;
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 900;
        letter-spacing: -0.03em;
        margin: 0;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .hero-badge {
        font-size: 0.85rem;
        background: linear-gradient(90deg, #6366F1, #A855F7);
        padding: 0.25rem 0.85rem;
        border-radius: 20px;
        font-weight: 700;
        letter-spacing: 0.05em;
        box-shadow: 0 0 15px rgba(168, 85, 247, 0.4);
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #94A3B8;
        margin-top: 0.4rem;
        font-weight: 500;
    }

    /* Disclaimer Card */
    .disclaimer-card {
        background: rgba(245, 158, 11, 0.08);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-left: 5px solid #F59E0B;
        padding: 0.9rem 1.25rem;
        border-radius: 12px;
        font-size: 0.88rem;
        color: #FCD34D;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
    }
    
    /* Metric Cards */
    .metric-card-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.2rem;
        margin-bottom: 1.5rem;
    }
    .glass-metric-card {
        background: rgba(15, 23, 42, 0.75);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 1.35rem 1.1rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    .glass-metric-card:hover {
        transform: translateY(-3px);
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 12px 36px 0 rgba(99, 102, 241, 0.2);
    }
    .metric-label {
        font-size: 0.78rem;
        font-weight: 700;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.4rem;
    }
    .metric-val {
        font-size: 1.75rem;
        font-weight: 800;
        letter-spacing: -0.02em;
    }
    .metric-sub {
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.3rem;
    }
    .val-emerald { color: #34D399; text-shadow: 0 0 12px rgba(52, 211, 153, 0.25); }
    .val-rose { color: #F87171; text-shadow: 0 0 12px rgba(248, 113, 113, 0.25); }
    .val-cyan { color: #38BDF8; text-shadow: 0 0 12px rgba(56, 189, 248, 0.25); }
    .val-violet { color: #C084FC; text-shadow: 0 0 12px rgba(192, 132, 252, 0.25); }
    
    /* Dark Streamlit Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 6px;
        border-radius: 14px;
        backdrop-filter: blur(10px);
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        white-space: pre;
        border-radius: 10px;
        color: #94A3B8;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #312E81 0%, #1E1B4B 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(99, 102, 241, 0.4) !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3);
    }
    
    /* Sidebar Headers */
    .sidebar-header {
        font-size: 0.9rem;
        font-weight: 700;
        color: #CBD5E1;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header Render
def render_header():
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">⚡ FinPilot <span class="hero-badge">PRO AI AGENT</span></div>
        <div class="hero-subtitle">Autonomous Financial Decision Support & Multi-Month Transaction Intelligence</div>
    </div>
    <div class="disclaimer-card">
        <strong>⚠️ DISCLAIMER:</strong> FinPilot is strictly an informational decision-support and data visualization tool. 
        It does <strong>NOT</strong> provide investment, tax, legal, or formal financial advice. All analysis is derived strictly from historical transaction data.
    </div>
    """, unsafe_allow_html=True)

# Sidebar Setup
st.sidebar.markdown("<h2 style='color: #FFFFFF; font-weight: 900; margin-bottom: 0.1rem; letter-spacing: -0.02em;'>⚡ FinPilot Controls</h2>", unsafe_allow_html=True)
st.sidebar.caption("🔒 *Informational decision support only. Not financial advice.*")

st.sidebar.markdown("---")
st.sidebar.markdown("<div class='sidebar-header'>📁 1. Data Source</div>", unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader("Upload Bank/Credit Card CSV", type=["csv"])
use_sample_btn = st.sidebar.button("📊 Load Sample Data (6 Months / ~360 txns)", use_container_width=True)

if "df" not in st.session_state:
    st.session_state.df = None

if use_sample_btn or (st.session_state.df is None and not uploaded_file):
    sample_csv_path = os.path.join(os.path.dirname(__file__), "sample_transactions.csv")
    if not os.path.exists(sample_csv_path):
        generate_sample_data("sample_transactions.csv")
    try:
        raw_df = load_and_process_csv(sample_csv_path)
        with st.spinner("Categorizing multi-month transactions..."):
            st.session_state.df = categorize_transactions(raw_df)
        st.sidebar.success("Loaded 6-month sample dataset!")
    except Exception as e:
        st.sidebar.error(f"Error loading sample data: {e}")

elif uploaded_file is not None:
    try:
        raw_df = load_and_process_csv(uploaded_file)
        with st.spinner("Processing & categorizing uploaded CSV..."):
            st.session_state.df = categorize_transactions(raw_df)
        st.sidebar.success("Successfully uploaded & categorized CSV!")
    except Exception as e:
        st.sidebar.error(f"Error parsing uploaded CSV: {e}")

df = st.session_state.df

if df is None or df.empty:
    st.warning("No valid transaction data loaded. Upload a CSV or click 'Load Sample Data' in the sidebar.")
    st.stop()

# Available Months Selection
available_months = analytics.get_available_months(df)
selected_month = st.sidebar.selectbox("Active Month", available_months, index=len(available_months)-1 if available_months else 0)

st.sidebar.markdown("---")
st.sidebar.markdown("<div class='sidebar-header'>🎯 2. Category Budgets (₹)</div>", unsafe_allow_html=True)
default_budgets = {
    "Groceries": 20000.0,
    "Dining": 10000.0,
    "Transport": 8000.0,
    "Shopping": 15000.0,
    "Utilities": 5000.0,
    "Rent": 35000.0
}
budgets = {}
for cat, def_val in default_budgets.items():
    budgets[cat] = st.sidebar.number_input(f"{cat} Budget", min_value=0.0, value=def_val, step=1000.0)

st.sidebar.markdown("---")
st.sidebar.markdown("<div class='sidebar-header'>🚀 3. Savings Goal</div>", unsafe_allow_html=True)
goal_amount = st.sidebar.number_input("Target Goal (₹)", min_value=1000.0, value=100000.0, step=5000.0)
current_savings = st.sidebar.number_input("Current Savings (₹)", min_value=0.0, value=25000.0, step=5000.0)
target_date_val = st.sidebar.date_input("Target Date", value=datetime.date(2026, 12, 31))
goal_info = {
    "goal_amount": goal_amount,
    "current_savings": current_savings,
    "target_date": target_date_val.strftime("%Y-%m-%d")
}

# Main Application Layout
render_header()

tabs = st.tabs([
    "📊 Overview & Health",
    "📈 Multi-Month Trends",
    "🔄 Subscriptions",
    "💡 Insights & Goals",
    "🔍 Explorer",
    "💬 Ask FinPilot",
    "📄 Executive Report"
])

# ---------------------------------------------------------
# TAB 1: OVERVIEW & HEALTH
# ---------------------------------------------------------
with tabs[0]:
    summary = analytics.monthly_summary(df, selected_month)
    health = analytics.calculate_financial_health_score(df, selected_month, budgets)

    # Glassmorphism Dark Metric Cards
    st.markdown(f"""
    <div class="metric-card-container">
        <div class="glass-metric-card">
            <div class="metric-label">Total Income</div>
            <div class="metric-val val-emerald">₹{summary['income']:,.2f}</div>
            <div class="metric-sub val-emerald">↑ Inflow for {selected_month}</div>
        </div>
        <div class="glass-metric-card">
            <div class="metric-label">Total Expenses</div>
            <div class="metric-val val-rose">₹{summary['expenses']:,.2f}</div>
            <div class="metric-sub val-rose">↓ Outflow for {selected_month}</div>
        </div>
        <div class="glass-metric-card">
            <div class="metric-label">Net Savings</div>
            <div class="metric-val val-cyan">₹{summary['net_savings']:,.2f}</div>
            <div class="metric-sub val-cyan">Rate: {summary['savings_rate_pct']}%</div>
        </div>
        <div class="glass-metric-card">
            <div class="metric-label">Financial Health</div>
            <div class="metric-val val-violet">{health['score']} / 100</div>
            <div class="metric-sub val-violet">{health['rating']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    c1, c2 = st.columns([1.3, 1])

    with c1:
        st.subheader("📌 Category Expenditure Distribution")
        cat_spend = analytics.spend_by_category(df, selected_month)
        if cat_spend:
            cat_df = pd.DataFrame(list(cat_spend.items()), columns=["Category", "Amount"])
            total_expenses_val = sum(cat_spend.values())
            
            # Donut Chart with Center Total Summary
            fig_pie = go.Figure(data=[go.Pie(
                labels=cat_df["Category"],
                values=cat_df["Amount"],
                hole=0.6,
                marker=dict(colors=["#34D399", "#38BDF8", "#818CF8", "#C084FC", "#F472B6", "#FBBF24", "#F87171"], line=dict(color='#0F172A', width=2)),
                textposition='outside',
                textinfo='percent+label',
                hoverinfo='label+value+percent',
                hovertemplate='<b>%{label}</b><br>Spent: ₹%{value:,.2f}<br>Share: %{percent}<extra></extra>'
            )])
            
            fig_pie.update_layout(
                annotations=[
                    dict(text='Total Expenses', x=0.5, y=0.55, font_size=12, font_color='#94A3B8', showarrow=False, font_family='Plus Jakarta Sans'),
                    dict(text=f'₹{total_expenses_val:,.0f}', x=0.5, y=0.45, font_size=18, font_color='#FFFFFF', font_weight='bold', showarrow=False, font_family='Plus Jakarta Sans')
                ],
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#F8FAFC", family='Plus Jakarta Sans'),
                margin=dict(t=20, b=20, l=20, r=20),
                showlegend=False
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No debit transactions found for selected month.")

    with c2:
        st.subheader("🎯 Health Score Gauge & Breakdown")
        
        # Plotly Dark Health Gauge Chart
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = health['score'],
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94A3B8"},
                'bar': {'color': "#818CF8"},
                'bgcolor': "rgba(15, 23, 42, 0.8)",
                'borderwidth': 1,
                'bordercolor': "rgba(255, 255, 255, 0.1)",
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.2)'},
                    {'range': [50, 75], 'color': 'rgba(245, 158, 11, 0.2)'},
                    {'range': [75, 100], 'color': 'rgba(16, 185, 129, 0.2)'}
                ]
            }
        ))
        fig_gauge.update_layout(
            height=220,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#F8FAFC", family='Plus Jakarta Sans'),
            margin=dict(t=30, b=10, l=30, r=30)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        bd = health["breakdown"]
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; padding: 1.1rem;">
            <p style="margin: 0.3rem 0; color: #CBD5E1;">💰 <strong>Savings Rate:</strong> {bd['savings_rate_score']} / 30 pts</p>
            <p style="margin: 0.3rem 0; color: #CBD5E1;">🎯 <strong>Budget Adherence:</strong> {bd['budget_adherence_score']} / 30 pts</p>
            <p style="margin: 0.3rem 0; color: #CBD5E1;">🔄 <strong>Subscription Load:</strong> {bd['subscription_load_score']} / 20 pts</p>
            <p style="margin: 0.3rem 0; color: #CBD5E1;">🚨 <strong>Impulse Control:</strong> {bd['anomaly_score']} / 20 pts</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Re-designed 2-Subplot Pro-FinTech Cash Flow & Balance Chart
    st.subheader("📈 Pro Cash Flow & Cumulative Net Balance Dashboard")
    daily_cf = analytics.get_daily_cash_flow(df, selected_month)
    if not daily_cf.empty:
        # Create Subplots: Row 1 = Cumulative Balance Area Chart, Row 2 = Inflow/Outflow Bars
        fig_pro = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=("Cumulative Net Balance Trajectory (₹)", "Daily Inflow vs Outflow (₹)"),
            row_heights=[0.55, 0.45]
        )

        # Row 1: Glowing Gradient Net Balance Area Chart
        fig_pro.add_trace(
            go.Scatter(
                x=daily_cf['date'],
                y=daily_cf['cumulative_net'],
                name="Net Balance",
                fill='tozeroy',
                fillcolor='rgba(129, 140, 248, 0.15)',
                line=dict(color='#818CF8', width=3, shape='spline'),
                mode='lines+markers',
                marker=dict(size=6, color='#A5B4FC'),
                hovertemplate='<b>Date: %{x}</b><br>Cumulative Net: ₹%{y:,.2f}<extra></extra>'
            ),
            row=1, col=1
        )

        # Row 2: Inflow (Green) & Outflow (Red) Bars
        fig_pro.add_trace(
            go.Bar(
                x=daily_cf['date'],
                y=daily_cf['income'],
                name="Daily Income",
                marker=dict(color='#34D399', cornerradius=4),
                hovertemplate='Income: ₹%{y:,.2f}<extra></extra>'
            ),
            row=2, col=1
        )
        fig_pro.add_trace(
            go.Bar(
                x=daily_cf['date'],
                y=daily_cf['expenses'],
                name="Daily Expenses",
                marker=dict(color='#F87171', cornerradius=4),
                hovertemplate='Expense: ₹%{y:,.2f}<extra></extra>'
            ),
            row=2, col=1
        )

        fig_pro.update_layout(
            barmode='group',
            height=500,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#F8FAFC", family='Plus Jakarta Sans'),
            margin=dict(t=40, b=30, l=20, r=20),
            hovermode="x unified",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#CBD5E1"))
        )

        fig_pro.update_xaxes(gridcolor="rgba(255,255,255,0.05)", row=1, col=1)
        fig_pro.update_xaxes(gridcolor="rgba(255,255,255,0.05)", row=2, col=1)
        fig_pro.update_yaxes(gridcolor="rgba(255,255,255,0.05)", row=1, col=1)
        fig_pro.update_yaxes(gridcolor="rgba(255,255,255,0.05)", row=2, col=1)

        st.plotly_chart(fig_pro, use_container_width=True)

# ---------------------------------------------------------
# TAB 2: MULTI-MONTH TRENDS
# ---------------------------------------------------------
with tabs[1]:
    st.header("📈 Multi-Month Financial Trajectory Analysis")
    st.write(f"Analyzing spending patterns across **{len(available_months)} consecutive months** ({available_months[0]} to {available_months[-1]}).")

    trend_data = []
    for m in available_months:
        m_summary = analytics.monthly_summary(df, m)
        trend_data.append({
            "Month": m,
            "Income": m_summary["income"],
            "Expenses": m_summary["expenses"],
            "Net Savings": m_summary["net_savings"]
        })
    trend_df = pd.DataFrame(trend_data)

    fig_multi = go.Figure()
    fig_multi.add_trace(go.Scatter(x=trend_df['Month'], y=trend_df['Income'], name="Income", line=dict(color='#34D399', width=3, shape='spline'), mode='lines+markers'))
    fig_multi.add_trace(go.Scatter(x=trend_df['Month'], y=trend_df['Expenses'], name="Expenses", line=dict(color='#F87171', width=3, shape='spline'), mode='lines+markers'))
    fig_multi.add_trace(go.Scatter(x=trend_df['Month'], y=trend_df['Net Savings'], name="Net Savings", line=dict(color='#38BDF8', width=3, dash='dash', shape='spline'), mode='lines+markers'))

    fig_multi.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#F8FAFC", family='Plus Jakarta Sans'),
        margin=dict(t=30, b=30, l=20, r=20),
        hovermode="x unified",
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_multi, use_container_width=True)

    st.markdown("---")

    # Multi-month category spending stacked bar
    cat_trend_rows = []
    for m in available_months:
        c_spend = analytics.spend_by_category(df, m)
        for cat, val in c_spend.items():
            cat_trend_rows.append({"Month": m, "Category": cat, "Amount": val})
    
    cat_trend_df = pd.DataFrame(cat_trend_rows)
    if not cat_trend_df.empty:
        fig_cat_stack = px.bar(
            cat_trend_df, x="Month", y="Amount", color="Category",
            title="Category Spending Trajectory by Month",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_cat_stack.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#F8FAFC", family='Plus Jakarta Sans'),
            margin=dict(t=30, b=30, l=20, r=20),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)")
        )
        st.plotly_chart(fig_cat_stack, use_container_width=True)

# ---------------------------------------------------------
# TAB 3: SUBSCRIPTIONS
# ---------------------------------------------------------
with tabs[2]:
    st.header("🔄 Recurring Subscriptions & Fixed Cost Intelligence")

    subs = analytics.detect_subscriptions(df)
    
    c1, c2 = st.columns([1.3, 1])
    
    with c1:
        st.subheader("Detected Recurring Subscriptions & Bills")
        if subs:
            sub_df = pd.DataFrame(subs)
            sub_df = sub_df.rename(columns={
                "merchant": "Merchant",
                "category": "Category",
                "monthly_amount": "Monthly Cost (₹)",
                "last_date": "Last Payment",
                "next_expected_date": "Next Expected Date"
            })
            st.dataframe(sub_df[["Merchant", "Category", "Monthly Cost (₹)", "Last Payment", "Next Expected Date"]], use_container_width=True)
            
            total_sub_monthly = sum(s["monthly_amount"] for s in subs)
            total_sub_annual = total_sub_monthly * 12
            st.markdown(f"""
            <div style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.3); border-left: 5px solid #6366F1; padding: 1.1rem; border-radius: 12px; margin-top: 1rem; color: #A5B4FC;">
                <strong>💡 Monthly Recurring Commitment:</strong> ₹{total_sub_monthly:,.2f} per month (<strong>₹{total_sub_annual:,.2f} / year</strong>).
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No recurring subscriptions detected.")

    with c2:
        st.subheader("Upcoming Obligations (Next 30 Days)")
        upcoming = analytics.upcoming_obligations(df, days=30)
        if upcoming:
            up_df = pd.DataFrame(upcoming)
            up_df = up_df.rename(columns={
                "merchant": "Merchant",
                "amount": "Amount (₹)",
                "expected_date": "Due Date",
                "days_until": "Days Until Due"
            })
            st.dataframe(up_df[["Merchant", "Amount (₹)", "Due Date", "Days Until Due"]], use_container_width=True)
        else:
            st.info("No upcoming bill obligations found for the next 30 days.")

# ---------------------------------------------------------
# TAB 4: INSIGHTS & GOALS
# ---------------------------------------------------------
with tabs[3]:
    st.header("💡 Month-over-Month Insights & Goal Tracking")

    # Month-over-Month Comparison
    if len(available_months) >= 2:
        col_m1, col_m2 = st.columns(2)
        m_a = col_m1.selectbox("Base Month", available_months, index=max(0, len(available_months)-2))
        m_b = col_m2.selectbox("Comparison Month", available_months, index=len(available_months)-1)

        comp = analytics.compare_months(df, m_a, m_b)
        
        st.subheader(f"Spending Delta: {m_a} vs {m_b}")
        st.markdown(f"Total Change: **₹{comp['total_abs_change']:+,.2f}** ({comp['total_pct_change']:+.1f}%)")

        comp_data = []
        for cat, data in comp["category_comparison"].items():
            comp_data.append({"Category": cat, "Month": m_a, "Amount": data["month_a_spend"]})
            comp_data.append({"Category": cat, "Month": m_b, "Amount": data["month_b_spend"]})
        
        comp_df = pd.DataFrame(comp_data)
        fig_comp = px.bar(comp_df, x="Category", y="Amount", color="Month", barmode="group",
                          color_discrete_sequence=['#64748B', '#6366F1'])
        fig_comp.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#F8FAFC", family='Plus Jakarta Sans'),
            margin=dict(t=20, b=20, l=20, r=20),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)")
        )
        st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown("---")

    # Budget Progress & Anomalies
    col_b, col_a = st.columns(2)

    with col_b:
        st.subheader(f"Category Budget Status ({selected_month})")
        b_status = analytics.budget_status(df, selected_month, budgets)
        for cat, b in b_status.items():
            spent = b["spent"]
            limit = b["budget"]
            pct = min(1.0, spent / limit) if limit > 0 else 0.0
            
            st.write(f"**{cat}**: ₹{spent:,.2f} / ₹{limit:,.2f} ({b['pct_spent']}%) | Committed: ₹{b['committed_upcoming']:,.2f}")
            if b["over_budget"]:
                st.progress(pct, text=f"⚠️ Over budget by ₹{spent - limit:,.2f}")
            else:
                st.progress(pct)

    with col_a:
        st.subheader("🚨 Anomalies & Spending Spikes")
        anomalies = analytics.detect_anomalies(df)
        if anomalies:
            for ano in anomalies[:4]:
                st.error(
                    f"⚠️ **{ano['description']}** ({ano['date']})\n\n"
                    f"Category: **{ano['category']}** | Amount: **₹{ano['amount']:,.2f}**\n\n"
                    f"*(Exceeds category mean ₹{ano['category_mean']:,.2f} + 2σ threshold ₹{ano['threshold']:,.2f})*"
                )
        else:
            st.success("No unusual spending spikes detected across categories.")

    st.markdown("---")

    # Savings Goal Tracker
    st.subheader("🎯 Savings Goal Projection")
    goal_res = analytics.goal_projection(df, goal_amount, goal_info["target_date"], current_savings)
    
    g_c1, g_c2, g_c3, g_c4 = st.columns(4)
    g_c1.metric("Goal Target", f"₹{goal_res['goal_amount']:,.2f}")
    g_c2.metric("Target Date", goal_res['target_date'])
    g_c3.metric("Required Monthly Savings", f"₹{goal_res['required_monthly_savings']:,.2f}")
    g_c4.metric("Avg Actual Monthly Savings", f"₹{goal_res['avg_monthly_savings']:,.2f}")

    if goal_res["on_track"]:
        st.success(f"✅ **ON TRACK!** At your current average monthly savings of ₹{goal_res['avg_monthly_savings']:,.2f}, you are projected to reach your goal on **{goal_res['projected_reach_date']}**.")
    else:
        st.warning(f"⚠️ **OFF TRACK.** You have a monthly savings deficit of **₹{abs(goal_res['monthly_deficit_surplus']):,.2f}**. Increase monthly savings to ₹{goal_res['required_monthly_savings']:,.2f} to hit your goal by {goal_res['target_date']}.")

# ---------------------------------------------------------
# TAB 5: EXPLORER
# ---------------------------------------------------------
with tabs[4]:
    st.header("🔍 Interactive Transactions Explorer")
    st.write("Search, filter, and inspect your parsed transaction records.")

    fc1, fc2, fc3 = st.columns([1.5, 1, 1])
    search_q = fc1.text_input("Search Merchant Description", placeholder="e.g. Swiggy, Netflix, Uber...")
    cat_list = ["All"] + sorted(df['category'].unique().tolist())
    selected_cat = fc2.selectbox("Filter Category", cat_list)
    min_amount_val = fc3.number_input("Min Amount (₹)", min_value=0.0, value=0.0, step=500.0)

    filtered_txns = analytics.search_transactions(df, query=search_q, category=selected_cat, min_amt=min_amount_val)
    st.write(f"Showing **{len(filtered_txns)}** matching transactions:")
    if filtered_txns:
        st.dataframe(pd.DataFrame(filtered_txns), use_container_width=True)
    else:
        st.info("No transactions match the selected filters.")

# ---------------------------------------------------------
# TAB 6: ASK FINPILOT (CHAT AGENT)
# ---------------------------------------------------------
with tabs[5]:
    st.header("💬 Ask FinPilot AI Chat Agent")
    st.caption("Ask questions about your spending, subscriptions, health score, budgets, or goals.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! I'm FinPilot. Ask me anything about your transaction history, subscriptions, health score, or savings goals!"}
        ]

    st.write("**Quick Questions:**")
    quick_cols = st.columns(6)
    q1 = quick_cols[0].button("Top spend?", use_container_width=True)
    q2 = quick_cols[1].button("Subscriptions?", use_container_width=True)
    q3 = quick_cols[2].button("MoM increase?", use_container_width=True)
    q4 = quick_cols[3].button("Health score?", use_container_width=True)
    q5 = quick_cols[4].button("Committed budget?", use_container_width=True)
    q6 = quick_cols[5].button("Savings goal?", use_container_width=True)

    prompt = None
    if q1:
        prompt = "Where did I spend the most this month?"
    elif q2:
        prompt = "Which subscriptions am I paying for?"
    elif q3:
        prompt = "What expenses increased compared with last month?"
    elif q4:
        prompt = "What is my financial health score?"
    elif q5:
        prompt = "How much of my budget is already committed?"
    elif q6:
        prompt = "Can I reach my savings goal at this rate?"

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask a question about your financial data...")
    if user_input:
        prompt = user_input

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("FinPilot is analyzing your data..."):
                response_text = run_agent_turn(
                    user_query=prompt,
                    chat_history=st.session_state.messages[:-1],
                    df=df,
                    budgets=budgets,
                    goal_info=goal_info
                )
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})

# ---------------------------------------------------------
# TAB 7: EXECUTIVE REPORT
# ---------------------------------------------------------
with tabs[6]:
    st.header("📄 Executive Monthly Financial Report")
    st.write("Generate a comprehensive executive summary report with key observations and action items.")

    if st.button("🚀 Generate Executive Report", use_container_width=True):
        with st.spinner("Generating executive report from analytics outputs..."):
            summary_data = analytics.monthly_summary(df, selected_month)
            subs_data = analytics.detect_subscriptions(df)
            anom_data = analytics.detect_anomalies(df)
            health_data = analytics.calculate_financial_health_score(df, selected_month, budgets)
            goal_data = analytics.goal_projection(df, goal_amount, goal_info["target_date"], current_savings)

            report_md = f"""# ✈️ FinPilot Executive Financial Report ({selected_month})

> **Disclaimer:** FinPilot is an informational decision-support tool. This report is derived strictly from transaction analytics and does not constitute formal financial or investment advice.

---

## 1. Executive Summary & Health Score
- **Financial Health Score:** {health_data['score']}/100 ({health_data['rating']})
- **Total Income:** ₹{summary_data['income']:,.2f}
- **Total Expenses:** ₹{summary_data['expenses']:,.2f}
- **Net Savings:** ₹{summary_data['net_savings']:,.2f}
- **Savings Rate:** {summary_data['savings_rate_pct']}%

---

## 2. Top Spending Categories
"""
            for cat, amt in summary_data['top_categories'].items():
                report_md += f"- **{cat}:** ₹{amt:,.2f}\n"

            report_md += f"""
---

## 3. Recurring Subscriptions & Fixed Costs
- **Total Active Subscriptions:** {len(subs_data)}
- **Monthly Subscription Commitment:** ₹{sum(s['monthly_amount'] for s in subs_data):,.2f} (Annualized: ₹{sum(s['monthly_amount'] for s in subs_data)*12:,.2f}/yr)
"""
            for s in subs_data:
                report_md += f"  - {s['merchant']}: ₹{s['monthly_amount']:,.2f}/mo (Next due: {s['next_expected_date']})\n"

            report_md += f"""
---

## 4. Anomaly Alerts & Impulse Spikes
"""
            if anom_data:
                for a in anom_data[:3]:
                    report_md += f"- ⚠️ **{a['description']}** on {a['date']}: **₹{a['amount']:,.2f}** in {a['category']} (Category mean: ₹{a['category_mean']:,.2f})\n"
            else:
                report_md += "- No unusual spending spikes detected.\n"

            report_md += f"""
---

## 5. Savings Goal Outlook
- **Status:** {"✅ ON TRACK" if goal_data["on_track"] else "⚠️ OFF TRACK"}
- **Target Goal:** ₹{goal_data['goal_amount']:,.2f} by {goal_data['target_date']}
- **Required Monthly Savings:** ₹{goal_data['required_monthly_savings']:,.2f}
- **Actual Avg Monthly Savings:** ₹{goal_data['avg_monthly_savings']:,.2f}
- **Projected Target Reach Date:** {goal_data['projected_reach_date']}

---

## 6. Actionable Recommendations
1. Review top spending category (**{list(summary_data['top_categories'].keys())[0]}**) to optimize discretionary spend.
2. Audit active subscriptions to save up to ₹{sum(s['monthly_amount'] for s in subs_data)*0.2:,.2f}/mo on unused services.
3. {"Maintain current savings discipline to stay on track." if goal_data["on_track"] else "Increase monthly savings allocation by ₹" + f"{abs(goal_data['monthly_deficit_surplus']):,.2f}" + " to reach target goal."}
"""

            st.session_state.report_md = report_md
            st.success("Executive report generated successfully!")

    if "report_md" in st.session_state:
        st.markdown(st.session_state.report_md)
        st.download_button(
            label="📥 Download Report (.md)",
            data=st.session_state.report_md,
            file_name=f"FinPilot_Executive_Report_{selected_month}.md",
            mime="text/markdown",
            use_container_width=True
        )
