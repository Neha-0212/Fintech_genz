import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Fintech GenZ Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# THEME COLORS
# ─────────────────────────────────────────────
PRIMARY   = "#6C63FF"
SUCCESS   = "#00C49A"
DANGER    = "#FF4B6E"
WARNING   = "#FFB347"
DARK      = "#1E1E2E"
CARD_BG   = "#262638"
TEXT      = "#E0E0F0"
MUTED     = "#9090B0"

CHANNEL_COLORS  = {"Referral": SUCCESS, "Organic": PRIMARY, "Ads": DANGER}
RISK_COLORS     = {"Low Risk": SUCCESS, "Medium Risk": WARNING, "High Risk": DANGER}
REGION_COLORS   = {"Tier1": PRIMARY, "Tier2": SUCCESS, "Tier3": WARNING}
AGE_COLORS      = {"Gen Z": PRIMARY, "Millennial+": SUCCESS}

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    background-color: {DARK};
    color: {TEXT};
}}
.stApp {{ background-color: {DARK}; }}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background: #16162a !important;
    border-right: 1px solid #2e2e4a;
}}
section[data-testid="stSidebar"] * {{ color: {TEXT} !important; }}

/* KPI Cards */
.kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }}
.kpi-card {{
    background: {CARD_BG};
    border-radius: 12px;
    padding: 20px 24px;
    border: 1px solid #2e2e4a;
    position: relative;
    overflow: hidden;
}}
.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--accent);
}}
.kpi-label {{ font-size: 12px; font-weight: 500; color: {MUTED}; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px; }}
.kpi-value {{ font-size: 32px; font-weight: 700; color: {TEXT}; line-height: 1; }}
.kpi-sub   {{ font-size: 12px; color: {MUTED}; margin-top: 6px; }}
.kpi-delta {{ font-size: 13px; font-weight: 600; margin-top: 6px; }}
.delta-up   {{ color: {SUCCESS}; }}
.delta-down {{ color: {DANGER}; }}

/* Section headers */
.section-header {{
    font-size: 18px; font-weight: 600; color: {TEXT};
    margin: 32px 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid #2e2e4a;
    display: flex; align-items: center; gap: 8px;
}}

/* Insight box */
.insight-box {{
    background: #1a1a3a;
    border-left: 3px solid {PRIMARY};
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin: 12px 0;
    font-size: 13px;
    color: {TEXT};
    line-height: 1.6;
}}
.insight-box strong {{ color: {PRIMARY}; }}

/* Action box */
.action-box {{
    background: #1a2a1a;
    border-left: 3px solid {SUCCESS};
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 13px;
    color: {TEXT};
    line-height: 1.6;
}}
.action-box strong {{ color: {SUCCESS}; }}

/* Table styling */
.styled-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    background: {CARD_BG};
    border-radius: 8px;
    overflow: hidden;
}}
.styled-table th {{
    background: #1a1a3a;
    color: {MUTED};
    font-weight: 600;
    padding: 10px 14px;
    text-align: left;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}}
.styled-table td {{
    padding: 9px 14px;
    border-top: 1px solid #2e2e4a;
    color: {TEXT};
}}
.styled-table tr:hover td {{ background: #1e1e38; }}

/* Badge */
.badge {{
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
}}
.badge-green  {{ background: #0d2d1f; color: {SUCCESS}; }}
.badge-red    {{ background: #2d0d18; color: {DANGER}; }}
.badge-yellow {{ background: #2d200d; color: {WARNING}; }}
.badge-purple {{ background: #1a1040; color: {PRIMARY}; }}

/* Page title */
.page-title {{
    font-size: 28px;
    font-weight: 700;
    color: {TEXT};
    margin-bottom: 4px;
}}
.page-subtitle {{
    font-size: 14px;
    color: {MUTED};
    margin-bottom: 24px;
}}

/* Threshold cards */
.threshold-card {{
    background: {CARD_BG};
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #2e2e4a;
    text-align: center;
}}
.threshold-card.recommended {{ border-color: {PRIMARY}; background: #1a1040; }}
.threshold-label {{ font-size: 13px; color: {MUTED}; margin-bottom: 12px; font-weight: 600; }}
.threshold-val   {{ font-size: 26px; font-weight: 700; color: {TEXT}; margin: 4px 0; }}
.threshold-meta  {{ font-size: 11px; color: {MUTED}; }}

div[data-testid="stMetric"] {{ display: none; }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DB CONNECTION
# ─────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "fintech_genz.db")

@st.cache_resource
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

@st.cache_data(ttl=300)
def query(sql: str) -> pd.DataFrame:
    conn = get_conn()
    return pd.read_sql_query(sql, conn)

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_all():
    customers = query("SELECT * FROM customers")
    onboarding = query("SELECT * FROM onboarding_events")
    transactions = query("SELECT * FROM transactions")
    risk = query("SELECT * FROM risk_profile")
    master = query("""
        SELECT c.*, o.onboarding_step, o.onboarding_status, o.conversion_flag,
               t.transaction_count, t.avg_transaction_value, t.total_volume,
               t.transaction_intensity, t.high_value_flag,
               r.credit_score, r.risk_band, r.default_flag, r.fraud_flag,
               r.high_risk_flag, r.est_revenue, r.est_loss, r.net_value
        FROM customers c
        JOIN onboarding_events o USING (customer_id)
        JOIN transactions t USING (customer_id)
        JOIN risk_profile r USING (customer_id)
    """)
    return customers, onboarding, transactions, risk, master

customers_df, onboarding_df, transactions_df, risk_df, master_df = load_all()

# ─────────────────────────────────────────────
# CHART HELPERS
# ─────────────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color=TEXT, size=12),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#2e2e4a", borderwidth=1),
    xaxis=dict(gridcolor="#2e2e4a", zerolinecolor="#2e2e4a"),
    yaxis=dict(gridcolor="#2e2e4a", zerolinecolor="#2e2e4a"),
)

def apply_layout(fig, title="", height=360):
    fig.update_layout(title=dict(text=title, font=dict(size=14, color=TEXT)),
                      height=height, **PLOT_LAYOUT)
    return fig

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='padding:16px 0 8px 0'>
        <div style='font-size:20px;font-weight:700;color:{TEXT}'> Fintech GenZ</div>
        <div style='font-size:11px;color:{MUTED};margin-top:2px'>Customer Intelligence Platform</div>
    </div>
    <hr style='border-color:#2e2e4a;margin:8px 0 16px 0'>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        [" Executive Overview",
         " Funnel Analysis",
         " Segment Intelligence",
         " Risk & Credit",
         " Channel P&L",
         " Micro-Segments",
         " Credit Threshold Simulator",
         " Customer Explorer"],
        label_visibility="collapsed"
    )

    st.markdown(f"<hr style='border-color:#2e2e4a;margin:16px 0'>", unsafe_allow_html=True)

    # Global filters
    st.markdown(f"<div style='font-size:11px;font-weight:600;color:{MUTED};text-transform:uppercase;letter-spacing:0.8px;margin-bottom:8px'>Global Filters</div>", unsafe_allow_html=True)
    sel_channel = st.multiselect("Channel", master_df["acquisition_channel"].unique(), default=list(master_df["acquisition_channel"].unique()))
    sel_region  = st.multiselect("Region",  master_df["region"].unique(), default=list(master_df["region"].unique()))
    sel_occ     = st.multiselect("Occupation", master_df["occupation"].unique(), default=list(master_df["occupation"].unique()))

    st.markdown(f"<hr style='border-color:#2e2e4a;margin:12px 0'>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:11px;color:{MUTED}'>1,000 customers · Jan 2024 cohort</div>", unsafe_allow_html=True)

# Filter master
df = master_df[
    master_df["acquisition_channel"].isin(sel_channel) &
    master_df["region"].isin(sel_region) &
    master_df["occupation"].isin(sel_occ)
].copy()

# ─────────────────────────────────────────────
# KPI HELPER
# ─────────────────────────────────────────────
def kpi_card(label, value, sub="", delta="", delta_positive=True, accent=PRIMARY):
    delta_html = ""
    if delta:
        cls = "delta-up" if delta_positive else "delta-down"
        arrow = "▲" if delta_positive else "▼"
        delta_html = f'<div class="kpi-delta {cls}">{arrow} {delta}</div>'
    return f"""
    <div class="kpi-card" style="--accent:{accent}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {f'<div class="kpi-sub">{sub}</div>' if sub else ''}
        {delta_html}
    </div>"""

# ══════════════════════════════════════════════
# PAGE 1 — EXECUTIVE OVERVIEW
# ══════════════════════════════════════════════
if page == " Executive Overview":
    st.markdown('<div class="page-title">Executive Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Top-line KPIs and portfolio health for the Jan 2024 Gen Z cohort</div>', unsafe_allow_html=True)

    # KPIs
    total        = len(df)
    conv_rate    = df["conversion_flag"].mean() * 100
    default_rate = df["default_flag"].mean() * 100
    fraud_rate   = df["fraud_flag"].mean() * 100
    total_net    = df["net_value"].sum()
    avg_cs       = df["credit_score"].mean()
    genz_conv    = df[df["age_group"]=="Gen Z"]["conversion_flag"].mean()*100
    other_conv   = df[df["age_group"]!="Gen Z"]["conversion_flag"].mean()*100
    gap          = other_conv - genz_conv

    st.markdown(f"""
    <div class="kpi-grid">
        {kpi_card("Total Customers", f"{total:,}", "Jan 2024 cohort", accent=PRIMARY)}
        {kpi_card("Overall Conversion", f"{conv_rate:.1f}%", "Onboarding completed", accent=SUCCESS)}
        {kpi_card("Portfolio Default Rate", f"{default_rate:.1f}%", "Credit defaults", accent=DANGER)}
        {kpi_card("Fraud Rate", f"{fraud_rate:.1f}%", "Flagged accounts", accent=WARNING)}
    </div>
    <div class="kpi-grid">
        {kpi_card("Total Net Value", f"₹{total_net:,.0f}", "Est. portfolio value", accent=SUCCESS)}
        {kpi_card("Avg Credit Score", f"{avg_cs:.0f}", "Portfolio average", accent=PRIMARY)}
        {kpi_card("Gen Z Conversion", f"{genz_conv:.1f}%", f"vs {other_conv:.1f}% others", delta=f"{gap:.1f}pp gap", delta_positive=False, accent=DANGER)}
        {kpi_card("High-Risk Customers", f"{df['high_risk_flag'].sum():,}", "Flagged for review", accent=DANGER)}
    </div>
    """, unsafe_allow_html=True)

    # Row 1: Conversion funnel + Risk distribution
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header"> Onboarding Funnel</div>', unsafe_allow_html=True)
        funnel = df.groupby("onboarding_step")["conversion_flag"].agg(["sum","count"]).reset_index()
        funnel.columns = ["step","converted","total"]
        funnel["conv_pct"] = funnel["converted"] / funnel["total"] * 100
        funnel = funnel.sort_values("conv_pct")
        fig = go.Figure(go.Bar(
            x=funnel["conv_pct"], y=funnel["step"], orientation="h",
            marker_color=[SUCCESS if v > 70 else WARNING if v > 55 else DANGER for v in funnel["conv_pct"]],
            text=[f"{v:.1f}%" for v in funnel["conv_pct"]], textposition="outside"
        ))
        apply_layout(fig, "Conversion % by Onboarding Step", 280)
        fig.update_layout(xaxis_title="Conversion %", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header"> Risk Band Distribution</div>', unsafe_allow_html=True)
        risk_dist = df["risk_band"].value_counts().reset_index()
        risk_dist.columns = ["risk_band","count"]
        colors = [RISK_COLORS.get(r, PRIMARY) for r in risk_dist["risk_band"]]
        fig2 = go.Figure(go.Pie(
            labels=risk_dist["risk_band"], values=risk_dist["count"],
            hole=0.55, marker_colors=colors,
            textinfo="label+percent", textfont=dict(color=TEXT)
        ))
        apply_layout(fig2, "Portfolio Risk Band Breakdown", 280)
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Row 2: Channel net value + Gen Z paradox
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-header"> Net Value by Channel</div>', unsafe_allow_html=True)
        ch = df.groupby("acquisition_channel").agg(net_value=("net_value","sum"), customers=("customer_id","count")).reset_index()
        colors_ch = [CHANNEL_COLORS.get(c, PRIMARY) for c in ch["acquisition_channel"]]
        fig3 = go.Figure(go.Bar(
            x=ch["acquisition_channel"], y=ch["net_value"],
            marker_color=colors_ch,
            text=[f"₹{v:,.0f}" for v in ch["net_value"]], textposition="outside"
        ))
        apply_layout(fig3, "Total Net Value by Acquisition Channel", 280)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown('<div class="section-header"> Gen Z Paradox</div>', unsafe_allow_html=True)
        seg = df.groupby("age_group").agg(
            conversion_rate=("conversion_flag","mean"),
            avg_net_value=("net_value","mean"),
        ).reset_index()
        seg["conversion_rate"] *= 100
        colors_ag = [AGE_COLORS.get(g, PRIMARY) for g in seg["age_group"]]
        fig4 = make_subplots(specs=[[{"secondary_y": True}]])
        fig4.add_trace(go.Bar(name="Conversion %", x=seg["age_group"], y=seg["conversion_rate"],
                              marker_color=colors_ag, opacity=0.85), secondary_y=False)
        fig4.add_trace(go.Scatter(name="Avg Net Value (₹)", x=seg["age_group"], y=seg["avg_net_value"],
                                  mode="lines+markers", line=dict(color=WARNING, width=3),
                                  marker=dict(size=10)), secondary_y=True)
        fig4.update_yaxes(title_text="Conversion %", secondary_y=False, gridcolor="#2e2e4a", color=TEXT)
        fig4.update_yaxes(title_text="Avg Net Value (₹)", secondary_y=True, color=TEXT)
        apply_layout(fig4, "Conversion vs Net Value — The Gen Z Paradox", 280)
        st.plotly_chart(fig4, use_container_width=True)

    # Key insight
    st.markdown(f"""
    <div class="insight-box">
        <strong> Key Finding:</strong> Gen Z converts <strong>20pp below</strong> older cohorts (46.7% vs 66.9%) —
        yet active Gen Z users generate <strong>higher net value (₹226 vs ₹198)</strong>.
        The problem is onboarding friction, not customer quality.
    </div>
    <div class="action-box">
        <strong> Recommended Action:</strong> Fix the KYC and OTP verification UX before changing your audience targeting strategy.
        Reducing drop-off by 15% could recover <strong>₹{total_net * 0.08:,.0f}+</strong> in unrealized net value.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PAGE 2 — FUNNEL ANALYSIS
# ══════════════════════════════════════════════
elif page == " Funnel Analysis":
    st.markdown('<div class="page-title">Onboarding Funnel Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Step-by-step drop-off analysis — where customers abandon the onboarding flow</div>', unsafe_allow_html=True)

    funnel_q = query("""
        SELECT o.onboarding_step,
               COUNT(*) AS total_users,
               SUM(CASE WHEN o.onboarding_status='Completed' THEN 1 ELSE 0 END) AS converted,
               SUM(CASE WHEN o.onboarding_status='Dropped'   THEN 1 ELSE 0 END) AS dropped,
               ROUND(100.0*SUM(CASE WHEN o.onboarding_status='Completed' THEN 1 ELSE 0 END)/COUNT(*),1) AS conversion_pct,
               ROUND(100.0*SUM(CASE WHEN o.onboarding_status='Dropped'   THEN 1 ELSE 0 END)/COUNT(*),1) AS drop_rate_pct
        FROM onboarding_events o GROUP BY o.onboarding_step ORDER BY conversion_pct ASC
    """)

    col1, col2, col3 = st.columns(3)
    worst = funnel_q.loc[funnel_q["conversion_pct"].idxmin()]
    best  = funnel_q.loc[funnel_q["conversion_pct"].idxmax()]
    total_dropped = funnel_q["dropped"].sum()

    col1.markdown(kpi_card("Worst Step", worst["onboarding_step"], f"{worst['conversion_pct']}% conversion", accent=DANGER), unsafe_allow_html=True)
    col2.markdown(kpi_card("Best Step",  best["onboarding_step"],  f"{best['conversion_pct']}% conversion",  accent=SUCCESS), unsafe_allow_html=True)
    col3.markdown(kpi_card("Total Dropped", f"{total_dropped:,}", "across all steps", accent=WARNING), unsafe_allow_html=True)

    st.markdown('<div class="section-header"> Conversion & Drop Rate by Step</div>', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Converted", x=funnel_q["onboarding_step"], y=funnel_q["converted"],
                         marker_color=SUCCESS, text=funnel_q["converted"], textposition="inside"))
    fig.add_trace(go.Bar(name="Dropped",   x=funnel_q["onboarding_step"], y=funnel_q["dropped"],
                         marker_color=DANGER, text=funnel_q["dropped"], textposition="inside"))
    apply_layout(fig, "Converted vs Dropped by Onboarding Step", 380)
    fig.update_layout(barmode="stack", xaxis_title="Onboarding Step", yaxis_title="Customers")
    st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        fig2 = go.Figure(go.Bar(
            y=funnel_q["onboarding_step"], x=funnel_q["drop_rate_pct"], orientation="h",
            marker_color=[DANGER if v > 40 else WARNING if v > 30 else SUCCESS for v in funnel_q["drop_rate_pct"]],
            text=[f"{v}%" for v in funnel_q["drop_rate_pct"]], textposition="outside"
        ))
        apply_layout(fig2, "Drop Rate % by Step", 300)
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        # Funnel by channel
        ch_funnel = df.groupby(["acquisition_channel","onboarding_step"])["conversion_flag"].mean().reset_index()
        ch_funnel["conversion_pct"] = ch_funnel["conversion_flag"] * 100
        fig3 = px.bar(ch_funnel, x="onboarding_step", y="conversion_pct", color="acquisition_channel",
                      barmode="group",
                      color_discrete_map=CHANNEL_COLORS)
        apply_layout(fig3, "Conversion % by Step × Channel", 300)
        fig3.update_layout(yaxis_title="Conversion %", xaxis_title="")
        st.plotly_chart(fig3, use_container_width=True)

    # Detailed table
    st.markdown('<div class="section-header"> Step-by-Step Breakdown</div>', unsafe_allow_html=True)
    rows_html = ""
    for _, row in funnel_q.iterrows():
        conv_badge = f'<span class="badge badge-{"green" if row["conversion_pct"]>65 else "yellow" if row["conversion_pct"]>50 else "red"}">{row["conversion_pct"]}%</span>'
        drop_badge = f'<span class="badge badge-{"red" if row["drop_rate_pct"]>40 else "yellow" if row["drop_rate_pct"]>30 else "green"}">{row["drop_rate_pct"]}%</span>'
        rows_html += f"<tr><td>{row['onboarding_step']}</td><td>{row['total_users']}</td><td>{row['converted']}</td><td>{row['dropped']}</td><td>{conv_badge}</td><td>{drop_badge}</td></tr>"

    st.markdown(f"""
    <table class="styled-table">
        <thead><tr><th>Step</th><th>Total</th><th>Converted</th><th>Dropped</th><th>Conv %</th><th>Drop %</th></tr></thead>
        <tbody>{rows_html}</tbody>
    </table>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="insight-box" style="margin-top:16px">
        <strong> Insight:</strong> KYC and OTP Verification are the highest-friction steps.
        These steps require document uploads and phone verification — both high-effort tasks on mobile.
        Small UX improvements here could recover <strong>100–200 customers per cohort</strong>.
    </div>
    <div class="action-box">
        <strong> Actions:</strong> (1) Simplify KYC to camera-based auto-fill. (2) Add progress indicator at OTP step.
        (3) Send push reminders 24h after drop for re-engagement.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PAGE 3 — SEGMENT INTELLIGENCE
# ══════════════════════════════════════════════
elif page == " Segment Intelligence":

    st.markdown(
        '<div class="page-title">Segment Intelligence</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Gen Z vs Millennial+ behavioral, risk, and profitability analysis'
        '</div>',
        unsafe_allow_html=True
    )

    # ------------------------------------------
    # EMPTY DATA CHECK
    # ------------------------------------------
    if df.empty:
        st.warning("No data available for current filters.")
        st.stop()

    # ------------------------------------------
    # SEGMENT AGGREGATION
    # ------------------------------------------
    seg = (
        df.groupby("age_group", dropna=False)
        .agg(
            customers=("customer_id", "count"),
            avg_age=("age", "mean"),
            avg_income=("income", "mean"),
            conversion_rate=("conversion_flag", "mean"),
            default_rate=("default_flag", "mean"),
            fraud_rate=("fraud_flag", "mean"),
            avg_credit_score=("credit_score", "mean"),
            avg_tx_count=("transaction_count", "mean"),
            avg_tx_value=("avg_transaction_value", "mean"),
            avg_net_value=("net_value", "mean"),
            total_net_value=("net_value", "sum"),
        )
        .reset_index()
    )

    # ------------------------------------------
    # FORMAT %
    # ------------------------------------------
    pct_cols = ["conversion_rate", "default_rate", "fraud_rate"]

    for col in pct_cols:
        seg[col] = seg[col] * 100

    # ------------------------------------------
    # KPI CARDS
    # ------------------------------------------
    st.markdown("### Segment Overview")

    for _, row in seg.iterrows():

        age_group = row["age_group"]
        accent = AGE_COLORS.get(age_group, PRIMARY)

        c1, c2, c3, c4 = st.columns(4)

        c1.markdown(
            kpi_card(
                f"{age_group} Customers",
                f"{int(row['customers']):,}",
                f"Avg Age {row['avg_age']:.0f}",
                accent=accent
            ),
            unsafe_allow_html=True
        )

        c2.markdown(
            kpi_card(
                f"{age_group} Conversion",
                f"{row['conversion_rate']:.1f}%",
                f"Income ₹{row['avg_income']:,.0f}",
                accent=accent
            ),
            unsafe_allow_html=True
        )

        c3.markdown(
            kpi_card(
                f"{age_group} Default Rate",
                f"{row['default_rate']:.1f}%",
                f"Credit Score {row['avg_credit_score']:.0f}",
                accent=DANGER if row["default_rate"] > 18 else SUCCESS
            ),
            unsafe_allow_html=True
        )

        c4.markdown(
            kpi_card(
                f"{age_group} Avg Net Value",
                f"₹{row['avg_net_value']:.0f}",
                f"Portfolio ₹{row['total_net_value']:,.0f}",
                accent=SUCCESS
            ),
            unsafe_allow_html=True
        )

    st.markdown("---")

    # ------------------------------------------
    # RATE COMPARISON CHART
    # ------------------------------------------
    col1, col2 = st.columns(2)

    with col1:

        fig = go.Figure()

        metric_labels = {
            "conversion_rate": "Conversion %",
            "default_rate": "Default %",
            "fraud_rate": "Fraud %",
        }

        for _, row in seg.iterrows():

            fig.add_trace(
                go.Bar(
                    name=row["age_group"],
                    x=list(metric_labels.values()),
                    y=[row[m] for m in metric_labels.keys()],
                    marker_color=AGE_COLORS.get(row["age_group"], PRIMARY)
                )
            )

        apply_layout(fig, "Risk & Conversion Comparison", 320)

        fig.update_layout(
            barmode="group",
            yaxis_title="%"
        )

        st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------
    # BEHAVIORAL PROFILE
    # ------------------------------------------
    with col2:

        fig2 = go.Figure()

        metric_labels_2 = {
            "avg_tx_count": "Avg Tx Count",
            "avg_tx_value": "Avg Tx Value",
            "avg_credit_score": "Credit Score",
        }

        for _, row in seg.iterrows():

            fig2.add_trace(
                go.Bar(
                    name=row["age_group"],
                    x=list(metric_labels_2.values()),
                    y=[row[m] for m in metric_labels_2.keys()],
                    marker_color=AGE_COLORS.get(row["age_group"], PRIMARY)
                )
            )

        apply_layout(fig2, "Behavioral & Credit Profile", 320)

        fig2.update_layout(
            barmode="group",
            yaxis_title="Value"
        )

        st.plotly_chart(fig2, use_container_width=True)

    # ------------------------------------------
    # HEATMAP
    # ------------------------------------------
    st.markdown(
        '<div class="section-header">'
        ' Conversion Heatmap — Channel × Age Group'
        '</div>',
        unsafe_allow_html=True
    )

    heatmap_df = (
        df.groupby(["acquisition_channel", "age_group"])
        ["conversion_flag"]
        .mean()
        .unstack(fill_value=0)
        * 100
    )

    if not heatmap_df.empty:

        fig3 = go.Figure(
            go.Heatmap(
                z=heatmap_df.values,
                x=heatmap_df.columns.tolist(),
                y=heatmap_df.index.tolist(),
                colorscale=[
                    [0, DANGER],
                    [0.5, WARNING],
                    [1, SUCCESS]
                ],
                text=[
                    [f"{v:.1f}%" for v in row]
                    for row in heatmap_df.values
                ],
                texttemplate="%{text}",
                colorbar=dict(
                    title="Conversion %",
                    tickfont=dict(color=TEXT)
                )
            )
        )

        apply_layout(
            fig3,
            "Conversion Rate by Channel & Segment",
            300
        )

        st.plotly_chart(fig3, use_container_width=True)

    else:
        st.info("Insufficient data for heatmap.")

    # ------------------------------------------
    # INSIGHTS
    # ------------------------------------------
    if len(seg) >= 2:

        top_segment = seg.sort_values(
            "avg_net_value",
            ascending=False
        ).iloc[0]

        low_conv = seg.sort_values(
            "conversion_rate"
        ).iloc[0]

        st.markdown(
            f"""
            <div class="insight-box">
                <strong> Key Insight:</strong>
                {top_segment['age_group']} delivers the highest
                average net value at
                <strong>₹{top_segment['avg_net_value']:.0f}</strong>,
                while {low_conv['age_group']} has the weakest
                onboarding conversion at
                <strong>{low_conv['conversion_rate']:.1f}%</strong>.
            </div>

            <div class="action-box">
                <strong> Recommendation:</strong>
                Improve onboarding UX instead of reducing acquisition
                spend for low-converting cohorts.
                Portfolio profitability is driven more by
                post-conversion value than raw signup volume.
            </div>
            """,
            unsafe_allow_html=True
        )

# ══════════════════════════════════════════════
# PAGE 4 — RISK & CREDIT
# ══════════════════════════════════════════════
elif page == " Risk & Credit":
    st.markdown('<div class="page-title">Risk & Credit Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Risk band profiling, default patterns, and credit score distribution</div>', unsafe_allow_html=True)

    risk_seg = df.groupby("risk_band").agg(
        customers=("customer_id","count"),
        avg_credit_score=("credit_score","mean"),
        avg_tx_count=("transaction_count","mean"),
        avg_tx_value=("avg_transaction_value","mean"),
        avg_total_volume=("total_volume","mean"),
        default_rate=("default_flag","mean"),
        avg_net_value=("net_value","mean"),
    ).reset_index()
    risk_seg["default_rate"] *= 100

    cols = st.columns(len(risk_seg))

    for col, (_, row) in zip(cols, risk_seg.iterrows()):

        accent = RISK_COLORS.get(row["risk_band"], PRIMARY)

        col.markdown(
            kpi_card(
                row["risk_band"],
                f"{row['default_rate']:.1f}%",
                f"{row['customers']} customers · Avg CS {row['avg_credit_score']:.0f}",
                accent=accent
            ),
            unsafe_allow_html=True
    )

    col_a, col_b = st.columns(2)
    with col_a:
        fig = px.histogram(df, x="credit_score", nbins=30, color="risk_band",
                           color_discrete_map=RISK_COLORS)
        apply_layout(fig, "Credit Score Distribution by Risk Band", 320)
        fig.update_layout(barmode="overlay", xaxis_title="Credit Score", yaxis_title="Customers")
        fig.update_traces(opacity=0.75)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="Avg Net Value (₹)",
                              x=risk_seg["risk_band"], y=risk_seg["avg_net_value"],
                              marker_color=[RISK_COLORS.get(r, PRIMARY) for r in risk_seg["risk_band"]]))
        fig2.add_trace(go.Scatter(name="Default Rate %", x=risk_seg["risk_band"], y=risk_seg["default_rate"],
                                   mode="lines+markers", line=dict(color=DANGER, width=3),
                                   marker=dict(size=10), yaxis="y2"))
        fig2.update_layout(yaxis2=dict(overlaying="y", side="right", title="Default %", color=TEXT, gridcolor="#2e2e4a"))
        apply_layout(fig2, "Net Value vs Default Rate by Risk Band", 320)
        st.plotly_chart(fig2, use_container_width=True)

    # Transaction behavior by risk
    st.markdown('<div class="section-header"> Transaction Behavior vs Risk Band</div>', unsafe_allow_html=True)
    col_c, col_d = st.columns(2)
    with col_c:
        fig3 = px.box(df, x="risk_band", y="transaction_count",
                      color="risk_band", color_discrete_map=RISK_COLORS)
        apply_layout(fig3, "Transaction Count Distribution by Risk Band", 300)
        fig3.update_layout(showlegend=False, xaxis_title="", yaxis_title="Transaction Count")
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        fig4 = px.scatter(df, x="credit_score", y="net_value", color="risk_band",
                          color_discrete_map=RISK_COLORS, opacity=0.5,
                          hover_data=["occupation","region","age_group"])
        apply_layout(fig4, "Credit Score vs Net Value", 300)
        fig4.update_layout(xaxis_title="Credit Score", yaxis_title="Net Value (₹)")
        st.plotly_chart(fig4, use_container_width=True)

    # High risk table
    st.markdown('<div class="section-header"> High-Risk Customer Review List (Top 25)</div>', unsafe_allow_html=True)
    high_risk = df[df["high_risk_flag"]==1].sort_values(["credit_score","default_flag"], ascending=[True,False]).head(25)
    rows_html = ""
    for _, r in high_risk.iterrows():
        d_badge = f'<span class="badge badge-red">Default</span>' if r["default_flag"] else ""
        f_badge = f'<span class="badge badge-yellow">Fraud</span>' if r["fraud_flag"] else ""
        rows_html += f"<tr><td>{int(r['customer_id'])}</td><td>{r['age_group']}</td><td>{r['occupation']}</td><td>{r['region']}</td><td>{r['acquisition_channel']}</td><td>{r['risk_band']}</td><td>{r['credit_score']}</td><td>{d_badge}{f_badge}</td><td>₹{r['net_value']:.0f}</td></tr>"

    st.markdown(f"""
    <table class="styled-table">
        <thead><tr><th>ID</th><th>Segment</th><th>Occupation</th><th>Region</th><th>Channel</th><th>Risk Band</th><th>Credit Score</th><th>Flags</th><th>Net Value</th></tr></thead>
        <tbody>{rows_html}</tbody>
    </table>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="insight-box" style="margin-top:16px">
        <strong> Insight:</strong> Transaction count and value do NOT significantly differ by risk band —
        default risk is <strong>credit-score-driven, not behavior-driven</strong>.
        Transaction monitoring alone won't catch defaulters early.
    </div>
    <div class="action-box">
        <strong> Action:</strong> Keep credit score as the primary risk gate. Layer in bureau data
        and income verification for borderline CS 550–650 applicants rather than relying on transaction signals.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PAGE 5 — CHANNEL P&L
# ══════════════════════════════════════════════
elif page == " Channel P&L":
    st.markdown('<div class="page-title">Channel P&L Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Full profitability breakdown by acquisition channel — conversion, default, revenue, loss, net value</div>', unsafe_allow_html=True)

    ch_pnl = df.groupby("acquisition_channel").agg(
        total_customers=("customer_id","count"),
        converted=("conversion_flag","sum"),
        conversion_rate=("conversion_flag","mean"),
        default_rate=("default_flag","mean"),
        total_revenue=("est_revenue","sum"),
        total_loss=("est_loss","sum"),
        total_net_value=("net_value","sum"),
        avg_net_per_customer=("net_value","mean"),
    ).reset_index()
    ch_pnl["conversion_rate"] *= 100
    ch_pnl["default_rate"] *= 100
    ch_pnl = ch_pnl.sort_values("total_net_value", ascending=False)

    col1, col2, col3 = st.columns(3)
    best_ch  = ch_pnl.iloc[0]
    worst_ch = ch_pnl.iloc[-1]
    col1.markdown(kpi_card("Best Channel (Net Value)", best_ch["acquisition_channel"],
                            f"₹{best_ch['total_net_value']:,.0f} total net", accent=SUCCESS), unsafe_allow_html=True)
    col2.markdown(kpi_card("Worst Channel ROI", worst_ch["acquisition_channel"],
                            f"₹{worst_ch['total_net_value']:,.0f} — {worst_ch['conversion_rate']:.1f}% conv", accent=DANGER), unsafe_allow_html=True)
    col3.markdown(kpi_card("Total Portfolio Net Value", f"₹{ch_pnl['total_net_value'].sum():,.0f}",
                            "Across all channels", accent=PRIMARY), unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Revenue", x=ch_pnl["acquisition_channel"], y=ch_pnl["total_revenue"],
                             marker_color=SUCCESS))
        fig.add_trace(go.Bar(name="Loss",    x=ch_pnl["acquisition_channel"], y=-ch_pnl["total_loss"],
                             marker_color=DANGER))
        fig.add_trace(go.Bar(name="Net Value", x=ch_pnl["acquisition_channel"], y=ch_pnl["total_net_value"],
                             marker_color=PRIMARY))
        apply_layout(fig, "Revenue / Loss / Net Value by Channel", 340)
        fig.update_layout(barmode="group", yaxis_title="₹ Value")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=ch_pnl["conversion_rate"], y=ch_pnl["avg_net_per_customer"],
            mode="markers+text",
            text=ch_pnl["acquisition_channel"],
            textposition="top center",
            marker=dict(size=ch_pnl["total_customers"] / 15,
                        color=[CHANNEL_COLORS.get(c, PRIMARY) for c in ch_pnl["acquisition_channel"]],
                        line=dict(width=1, color=TEXT)),
        ))
        apply_layout(fig2, "Conversion Rate vs Avg Net Value per Customer", 340)
        fig2.update_layout(xaxis_title="Conversion Rate %", yaxis_title="Avg Net Value per Customer (₹)")
        st.plotly_chart(fig2, use_container_width=True)

    # Table
    st.markdown('<div class="section-header"> Full Channel P&L Table</div>', unsafe_allow_html=True)
    rows_html = ""
    for _, row in ch_pnl.iterrows():
        conv_badge = f'<span class="badge badge-{"green" if row["conversion_rate"]>65 else "yellow" if row["conversion_rate"]>55 else "red"}">{row["conversion_rate"]:.1f}%</span>'
        def_badge  = f'<span class="badge badge-{"red" if row["default_rate"]>20 else "yellow" if row["default_rate"]>15 else "green"}">{row["default_rate"]:.1f}%</span>'
        rows_html += f"""<tr>
            <td>{row['acquisition_channel']}</td>
            <td>{row['total_customers']}</td><td>{row['converted']:.0f}</td>
            <td>{conv_badge}</td><td>{def_badge}</td>
            <td>₹{row['total_revenue']:,.0f}</td>
            <td>₹{row['total_loss']:,.0f}</td>
            <td>₹{row['total_net_value']:,.0f}</td>
            <td>₹{row['avg_net_per_customer']:.0f}</td>
        </tr>"""

    st.markdown(f"""
    <table class="styled-table">
        <thead><tr><th>Channel</th><th>Customers</th><th>Converted</th><th>Conv %</th><th>Default %</th>
        <th>Revenue</th><th>Loss</th><th>Net Value</th><th>Avg/Customer</th></tr></thead>
        <tbody>{rows_html}</tbody>
    </table>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="insight-box" style="margin-top:16px">
        <strong> Insight:</strong> Referral generates the most net value. Ads has the <strong>lowest conversion rate</strong>
        with a similar default rate — worst acquisition ROI in the portfolio.
    </div>
    <div class="action-box">
        <strong> Action:</strong> Shift 30–40% of Ads budget to Referral incentive programs.
        Model suggests a ₹500–₹1,000 referral bonus would still be net-positive given avg net value per converted referral customer.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PAGE 6 — MICRO-SEGMENTS
# ══════════════════════════════════════════════
elif page == " Micro-Segments":
    st.markdown('<div class="page-title">Micro-Segment Profitability</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Occupation × Region cross-analysis — identifying highest-value targeting opportunities</div>', unsafe_allow_html=True)

    micro = df.groupby(["occupation","region"]).agg(
        customers=("customer_id","count"),
        avg_credit_score=("credit_score","mean"),
        default_rate=("default_flag","mean"),
        total_revenue=("est_revenue","sum"),
        total_loss=("est_loss","sum"),
        total_net_value=("net_value","sum"),
        avg_net_per_customer=("net_value","mean"),
    ).reset_index()
    micro["default_rate"] *= 100
    micro = micro.sort_values("total_net_value", ascending=False)

    # Heatmap of net value
    pivot_net = micro.pivot(index="occupation", columns="region", values="avg_net_per_customer").fillna(0)
    fig = go.Figure(go.Heatmap(
        z=pivot_net.values,
        x=pivot_net.columns.tolist(),
        y=pivot_net.index.tolist(),
        colorscale=[[0, "#1a1a3a"],[0.5, PRIMARY],[1, SUCCESS]],
        text=[[f"₹{v:.0f}" for v in row] for row in pivot_net.values],
        texttemplate="%{text}",
        showscale=True,
        colorbar=dict(title="Avg Net Value", tickfont=dict(color=TEXT))
    ))
    apply_layout(fig, "Avg Net Value per Customer — Occupation × Region", 320)
    st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        pivot_def = micro.pivot(index="occupation", columns="region", values="default_rate").fillna(0)
        fig2 = go.Figure(go.Heatmap(
            z=pivot_def.values,
            x=pivot_def.columns.tolist(),
            y=pivot_def.index.tolist(),
            colorscale=[[0, SUCCESS],[0.5, WARNING],[1, DANGER]],
            text=[[f"{v:.1f}%" for v in row] for row in pivot_def.values],
            texttemplate="%{text}",
            colorbar=dict(title="Default %", tickfont=dict(color=TEXT))
        ))
        apply_layout(fig2, "Default Rate % — Occupation × Region", 300)
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        fig3 = px.scatter(micro, x="default_rate", y="avg_net_per_customer",
                          size="customers", color="occupation",
                          text=micro["occupation"] + " · " + micro["region"],
                          color_discrete_sequence=[PRIMARY, SUCCESS, WARNING])
        apply_layout(fig3, "Default Rate vs Net Value — Micro-Segments", 300)
        fig3.update_traces(textposition="top center")
        fig3.update_layout(xaxis_title="Default Rate %", yaxis_title="Avg Net Value per Customer (₹)")
        st.plotly_chart(fig3, use_container_width=True)

    # Top 10 table
    st.markdown('<div class="section-header"> Top 10 Micro-Segments by Net Value</div>', unsafe_allow_html=True)
    rows_html = ""
    for i, (_, row) in enumerate(micro.head(10).iterrows()):
        rank_badge = f'<span class="badge badge-{"purple" if i<3 else "green"}"># {i+1}</span>'
        def_badge  = f'<span class="badge badge-{"red" if row["default_rate"]>20 else "yellow" if row["default_rate"]>15 else "green"}">{row["default_rate"]:.1f}%</span>'
        rows_html += f"""<tr>
            <td>{rank_badge}</td>
            <td>{row['occupation']}</td><td>{row['region']}</td>
            <td>{row['customers']}</td>
            <td>{row['avg_credit_score']:.0f}</td>
            <td>{def_badge}</td>
            <td>₹{row['total_net_value']:,.0f}</td>
            <td>₹{row['avg_net_per_customer']:.0f}</td>
        </tr>"""

    st.markdown(f"""
    <table class="styled-table">
        <thead><tr><th>Rank</th><th>Occupation</th><th>Region</th><th>Customers</th>
        <th>Avg CS</th><th>Default %</th><th>Total Net Value</th><th>Avg/Customer</th></tr></thead>
        <tbody>{rows_html}</tbody>
    </table>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="insight-box" style="margin-top:16px">
        <strong> Insight:</strong> Freelancer + Tier1 and Salaried + Tier1 are top micro-segments.
        Tier2 cities show <strong>comparable avg net values with lower default rates</strong> — an underserved, high-potential market.
    </div>
    <div class="action-box">
        <strong> Action:</strong> Launch Tier2-targeted campaigns using the Referral channel.
        Freelancer + Tier2 offers the best risk-adjusted return profile for growth expansion.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PAGE 7 — CREDIT THRESHOLD SIMULATOR
# ══════════════════════════════════════════════
elif page == " Credit Threshold Simulator":
    st.markdown('<div class="page-title">Credit Threshold Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Model the business trade-offs of different credit score approval thresholds in real time</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="insight-box">
        <strong>How it works:</strong> Adjust the credit score threshold below.
        The simulator instantly shows approval rate, default rate, and total net value
        for the filtered cohort — helping you find the optimal risk-growth balance.
    </div>
    """, unsafe_allow_html=True)

    threshold = st.slider("Credit Score Threshold (approve customers ≥ this score)",
                           min_value=550, max_value=799, value=650, step=5,
                           help="Drag to simulate different approval policies")

    approved = df[df["credit_score"] >= threshold]
    rejected = df[df["credit_score"] <  threshold]

    approval_rate = len(approved) / len(df) * 100
    default_rate  = approved["default_flag"].mean() * 100
    net_value     = approved["net_value"].sum()
    avg_net       = approved["net_value"].mean()
    rejected_nv   = rejected["net_value"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(kpi_card("Approved Customers", f"{len(approved):,}", f"{approval_rate:.1f}% approval rate", accent=SUCCESS), unsafe_allow_html=True)
    col2.markdown(kpi_card("Default Rate", f"{default_rate:.1f}%", f"{approved['default_flag'].sum():.0f} defaults", accent=DANGER if default_rate > 20 else WARNING if default_rate > 12 else SUCCESS), unsafe_allow_html=True)
    col3.markdown(kpi_card("Portfolio Net Value", f"₹{net_value:,.0f}", f"₹{avg_net:.0f} avg/customer", accent=PRIMARY), unsafe_allow_html=True)
    col4.markdown(kpi_card("Net Value Left Out", f"₹{rejected_nv:,.0f}", f"{len(rejected)} customers rejected", accent=WARNING), unsafe_allow_html=True)

    st.markdown("---")

    # Comparison: current vs 3 benchmarks
    benchmarks = [
        ("Conservative (CS ≥ 750)", 750),
        ("Recommended (CS ≥ 650)",  650),
        ("Aggressive (CS ≥ 550)",   550),
        (f"Your Setting (CS ≥ {threshold})", threshold),
    ]

    cols = st.columns(4)
    for (label, thresh), col in zip(benchmarks, cols):
        seg_ = df[df["credit_score"] >= thresh]
        ar   = len(seg_) / len(df) * 100
        dr   = seg_["default_flag"].mean() * 100
        nv   = seg_["net_value"].sum()
        is_rec = thresh == 650
        cls  = "recommended" if is_rec else ""
        col.markdown(f"""
        <div class="threshold-card {cls}">
            <div class="threshold-label"> {label}</div>
            <div class="threshold-val">{ar:.0f}%</div>
            <div class="threshold-meta">Approval Rate</div>
            <div class="threshold-val" style="font-size:20px;margin-top:12px;color:{'#FF4B6E' if dr>20 else '#FFB347' if dr>12 else '#00C49A'}">{dr:.1f}%</div>
            <div class="threshold-meta">Default Rate</div>
            <div class="threshold-val" style="font-size:18px;margin-top:12px;color:#6C63FF">₹{nv:,.0f}</div>
            <div class="threshold-meta">Net Value</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Dynamic threshold sweep chart
    thresholds = range(550, 800, 10)
    sweep = []
    for t in thresholds:
        seg_ = df[df["credit_score"] >= t]
        sweep.append({
            "threshold": t,
            "approval_rate": len(seg_) / len(df) * 100,
            "default_rate":  seg_["default_flag"].mean() * 100 if len(seg_) > 0 else 0,
            "net_value":     seg_["net_value"].sum(),
        })
    sweep_df = pd.DataFrame(sweep)

    col_a, col_b = st.columns(2)
    with col_a:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=sweep_df["threshold"], y=sweep_df["approval_rate"],
                                 name="Approval Rate %", line=dict(color=SUCCESS, width=2)))
        fig.add_trace(go.Scatter(x=sweep_df["threshold"], y=sweep_df["default_rate"],
                                 name="Default Rate %", line=dict(color=DANGER, width=2)))
        fig.add_vline(x=threshold, line=dict(color=WARNING, dash="dash", width=1.5),
                      annotation_text=f"CS={threshold}", annotation_font_color=WARNING)
        apply_layout(fig, "Approval Rate vs Default Rate Across Thresholds", 320)
        fig.update_layout(xaxis_title="Credit Score Threshold", yaxis_title="%")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=sweep_df["threshold"], y=sweep_df["net_value"],
                                  fill="tozeroy", fillcolor="rgba(108,99,255,0.15)",
                                  line=dict(color=PRIMARY, width=2), name="Net Value"))
        fig2.add_vline(x=threshold, line=dict(color=WARNING, dash="dash", width=1.5),
                       annotation_text=f"CS={threshold}", annotation_font_color=WARNING)
        apply_layout(fig2, "Total Net Value Captured vs Threshold", 320)
        fig2.update_layout(xaxis_title="Credit Score Threshold", yaxis_title="Net Value (₹)")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown(f"""
    <div class="insight-box">
        <strong> Insight:</strong> CS ≥ 650 is the optimal threshold — captures ~75% of approvals at ~12% default rate.
        CS ≥ 750 is overly conservative and leaves significant net value unrealized.
        CS ≥ 550 spikes default rates to 25%+ with only marginal net value gain.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PAGE 8 — CUSTOMER EXPLORER
# ══════════════════════════════════════════════
elif page == " Customer Explorer":
    st.markdown('<div class="page-title">Customer Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Search and filter individual customer profiles with full risk and transaction details</div>', unsafe_allow_html=True)

    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        f_risk = st.multiselect("Risk Band", df["risk_band"].unique(), default=list(df["risk_band"].unique()))
    with col_f2:
        f_occ  = st.multiselect("Occupation", df["occupation"].unique(), default=list(df["occupation"].unique()))
    with col_f3:
        f_reg  = st.multiselect("Region", df["region"].unique(), default=list(df["region"].unique()))
    with col_f4:
        f_flags = st.multiselect("Flags", ["Default","Fraud","High Risk","None"], default=["Default","Fraud","High Risk","None"])
    st.markdown(
        "<style>.stSlider label {color: white !important;}</style>",
        unsafe_allow_html=True
    )

    cs_min, cs_max = st.slider(
        "Credit Score Range",
        550,
        799,
        (550, 799)
    )

    filtered = df[
        df["risk_band"].isin(f_risk) &
        df["occupation"].isin(f_occ) &
        df["region"].isin(f_reg) &
        df["credit_score"].between(cs_min, cs_max)
    ].copy()

    if "Default" not in f_flags:
        filtered = filtered[filtered["default_flag"]==0]
    if "Fraud" not in f_flags:
        filtered = filtered[filtered["fraud_flag"]==0]
    if "High Risk" not in f_flags:
        filtered = filtered[filtered["high_risk_flag"]==0]

    st.markdown(f"<div style='font-size:13px;color:{MUTED};margin:8px 0'>Showing {len(filtered):,} of {len(df):,} customers</div>", unsafe_allow_html=True)

    col_k1, col_k2, col_k3, col_k4 = st.columns(4)
    col_k1.markdown(kpi_card("Filtered Customers", f"{len(filtered):,}", accent=PRIMARY), unsafe_allow_html=True)
    col_k2.markdown(kpi_card("Avg Net Value", f"₹{filtered['net_value'].mean():.0f}" if len(filtered) else "—", accent=SUCCESS), unsafe_allow_html=True)
    col_k3.markdown(kpi_card("Default Rate", f"{filtered['default_flag'].mean()*100:.1f}%" if len(filtered) else "—", accent=DANGER), unsafe_allow_html=True)
    col_k4.markdown(kpi_card("Avg Credit Score", f"{filtered['credit_score'].mean():.0f}" if len(filtered) else "—", accent=WARNING), unsafe_allow_html=True)

    if len(filtered) > 0:
        # Mini charts
        col_a, col_b = st.columns(2)
        with col_a:
            rb_dist = filtered["risk_band"].value_counts().reset_index()
            rb_dist.columns = ["risk_band","count"]
            fig = px.pie(rb_dist, names="risk_band", values="count",
                         color="risk_band", color_discrete_map=RISK_COLORS, hole=0.5)
            apply_layout(fig, "Risk Band Distribution", 260)
            fig.update_layout(showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            fig2 = px.histogram(filtered, x="credit_score", nbins=20,
                                color="risk_band", color_discrete_map=RISK_COLORS)
            apply_layout(fig2, "Credit Score Distribution", 260)
            fig2.update_layout(barmode="overlay", xaxis_title="Credit Score", yaxis_title="Count")
            fig2.update_traces(opacity=0.75)
            st.plotly_chart(fig2, use_container_width=True)

        # Table
        st.markdown('<div class="section-header"> Customer Records</div>', unsafe_allow_html=True)
        display_cols = ["customer_id","age_group","occupation","region","acquisition_channel",
                        "onboarding_status","credit_score","risk_band","transaction_count",
                        "avg_transaction_value","net_value","default_flag","fraud_flag"]
        show_df = filtered[display_cols].sort_values("net_value", ascending=False).head(100)

        rows_html = ""
        for _, r in show_df.iterrows():
            d_badge = f'<span class="badge badge-red">Default</span>' if r["default_flag"] else ""
            f_badge = f'<span class="badge badge-yellow">Fraud</span>'   if r["fraud_flag"]  else ""
            rb_cls  = "green" if r["risk_band"]=="Low Risk" else "yellow" if r["risk_band"]=="Medium Risk" else "red"
            conv_cls = "green" if r["onboarding_status"]=="Completed" else "red"
            rows_html += f"""<tr>
                <td>{int(r['customer_id'])}</td>
                <td>{r['age_group']}</td>
                <td>{r['occupation']}</td>
                <td>{r['region']}</td>
                <td>{r['acquisition_channel']}</td>
                <td><span class="badge badge-{conv_cls}">{r['onboarding_status']}</span></td>
                <td>{r['credit_score']}</td>
                <td><span class="badge badge-{rb_cls}">{r['risk_band']}</span></td>
                <td>{r['transaction_count']}</td>
                <td>₹{r['avg_transaction_value']:,}</td>
                <td>₹{r['net_value']:.0f}</td>
                <td>{d_badge}{f_badge}</td>
            </tr>"""

        st.markdown(f"""
        <div style="max-height:480px;overflow-y:auto;border-radius:8px">
        <table class="styled-table">
            <thead><tr><th>ID</th><th>Segment</th><th>Occupation</th><th>Region</th><th>Channel</th>
            <th>Onboarding</th><th>CS</th><th>Risk Band</th><th>Tx Count</th><th>Avg Tx Value</th>
            <th>Net Value</th><th>Flags</th></tr></thead>
            <tbody>{rows_html}</tbody>
        </table></div>""", unsafe_allow_html=True)

        if st.button(" Export filtered customers as CSV"):
            csv_data = filtered[display_cols].to_csv(index=False)
            st.download_button("Download CSV", data=csv_data,
                               file_name="filtered_customers.csv", mime="text/csv")
    else:
        st.markdown(f"<div style='color:{MUTED};padding:40px;text-align:center'>No customers match the current filters.</div>", unsafe_allow_html=True)
