import os
import time
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, timedelta

from data.generate_dataset import generate_all_datasets
from solver.optimizer import solve_leave_optimization, simulate_scenario, date_range
from solver.ai_assistant import ask_ai_assistant
from lang import t

# Page Configuration
st.set_page_config(
    page_title="Smart Leave Approval Optimizer | OrionHackathon 2026",
    page_icon="🗓️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Cream Aesthetics
st.markdown("""
<style>
    /* Main Theme Overrides - Warm Cream Palette */
    .stApp {
        background-color: #FDFBF7;
        color: #2D241E;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #F4EFE6 !important;
        border-right: 1px solid #E6DEC8;
    }
    [data-testid="stSidebar"] * {
        color: #2D241E !important;
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #2D241E !important;
    }
    
    /* Header Gradient Banner - Rich Warm Terracotta / Espresso / Warm Amber */
    .main-header {
        background: linear-gradient(135deg, #4A3B32 0%, #7C5C4B 50%, #9A7B66 100%);
        padding: 1.8rem 2.2rem;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(74, 59, 50, 0.25);
        border: 1px solid #C8B9A6;
        margin-bottom: 2rem;
    }
    .main-title {
        color: #FFFDF9;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .main-subtitle {
        color: #F0E6D8;
        font-size: 1.05rem;
        font-weight: 400;
        margin-top: 0.5rem;
    }
    
    /* Cream Metric Cards */
    .metric-card {
        background: #FFFFFF;
        border-radius: 14px;
        border: 1px solid #EAE3D2;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 4px 15px rgba(120, 90, 60, 0.06);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #C8B9A6;
        box-shadow: 0 6px 20px rgba(120, 90, 60, 0.12);
    }
    .metric-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #7A695D;
        font-weight: 600;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #2D241E;
        margin-top: 0.3rem;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #8C6D53;
        margin-top: 0.2rem;
    }

    /* Badges */
    .badge-approved {
        background-color: #E2F1E7;
        color: #1E6B38;
        border: 1px solid #B6E2C3;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-rejected {
        background-color: #FCE8E6;
        color: #C53030;
        border: 1px solid #F8B4B4;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-pending {
        background-color: #FFF4DF;
        color: #B7791F;
        border: 1px solid #FBD38D;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    /* Section Container */
    .section-box {
        background: #FFFFFF;
        border-radius: 14px;
        padding: 1.5rem;
        border: 1px solid #EAE3D2;
        box-shadow: 0 2px 10px rgba(120, 90, 60, 0.04);
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to load dataset
@st.cache_data
def load_data():
    if not os.path.exists("data/employees.csv") or not os.path.exists("data/leave_requests.csv"):
        generate_all_datasets()
    emp_df = pd.read_csv("data/employees.csv")
    dept_df = pd.read_csv("data/departments.csv")
    req_df = pd.read_csv("data/leave_requests.csv")
    return emp_df, dept_df, req_df

# Session state setup
if "optimization_results" not in st.session_state:
    st.session_state["optimization_results"] = None

# Sidebar Controls
with st.sidebar:
    lang_choice = st.radio(
        "🌐 Bahasa / Language", ["🇮🇩 Indonesia", "🇬🇧 English"],
        horizontal=True, key="lang_radio"
    )
    lang = "id" if lang_choice.startswith("🇮🇩") else "en"
    
    st.markdown("---")
    st.image("https://img.icons8.com/isometric/96/calendar--v2.png", width=64)
    st.title(t("sidebar_control_panel", lang))
    st.markdown("---")
    
    st.subheader(t("solver_objectives_title", lang))
    alpha = st.slider(t("slider_alpha", lang), 0.0, 5.0, 1.0, 0.1)
    beta = st.slider(t("slider_beta", lang), 0.0, 5.0, 1.5, 0.1)
    
    st.markdown("---")
    st.subheader("🛡️ Staffing Constraint")
    min_staff_pct = st.slider(t("slider_min_staff", lang), 50, 90, 70, 5) / 100.0
    
    st.markdown("---")
    st.subheader(t("sidebar_ai_section", lang))
    ai_provider = st.selectbox(
        t("ai_provider_label", lang),
        ["Built-in Smart Solver (Tanpa Key)", "OpenAI (GPT-4o)", "Anthropic (Claude)"]
    )
    
    ai_api_key = ""
    if ai_provider.startswith("OpenAI"):
        ai_api_key = st.text_input(t("ai_key_openai", lang), type="password")
    elif ai_provider.startswith("Anthropic"):
        ai_api_key = st.text_input(t("ai_key_anthropic", lang), type="password")
    
    st.markdown("---")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        run_btn = st.button(t("btn_run_ilp", lang), use_container_width=True, type="primary")
    with col_btn2:
        reset_btn = st.button(t("btn_reset_data", lang), use_container_width=True)

    if reset_btn:
        generate_all_datasets()
        st.cache_data.clear()
        st.session_state["optimization_results"] = None
        st.success(t("reset_success", lang))
        st.rerun()

# Header Banner
st.markdown(f"""
<div class="main-header">
    <div class="main-title">
        🗓️ {t("app_title", lang)}
    </div>
    <div class="main-subtitle">
        {t("app_subtitle", lang)}
    </div>
</div>
""", unsafe_allow_html=True)

# Load data
emp_df, dept_df, req_df = load_data()

# Trigger optimization if requested, state is empty, or language changed
lang_changed = st.session_state.get("last_solved_lang") != lang
if run_btn or st.session_state["optimization_results"] is None or lang_changed:
    with st.spinner("⚡ Running PuLP Integer Linear Programming (ILP) Solver..."):
        results = solve_leave_optimization(
            req_df, emp_df, dept_df,
            alpha=alpha, beta=beta,
            custom_min_staff_pct=min_staff_pct,
            lang=lang
        )
        st.session_state["optimization_results"] = results
        st.session_state["last_solved_lang"] = lang

res = st.session_state["optimization_results"]
opt_req_df = res["requests_df"]
opt_dept_df = res["departments_df"]
solve_time = res["solve_time_sec"]
status_str = res["status"]
obj_val = res["objective_value"]

total_reqs = len(opt_req_df)
approved_count = (opt_req_df["approved"] == 1).sum()
rejected_count = (opt_req_df["approved"] == 0).sum()
approval_rate = round((approved_count / total_reqs) * 100, 1) if total_reqs > 0 else 0

# KPI Metric Cards
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
with kpi1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{t("kpi_total_requests", lang)}</div>
        <div class="metric-value">{total_reqs}</div>
        <div class="metric-sub">{t("kpi_sub_depts", lang)}</div>
    </div>
    """, unsafe_allow_html=True)
with kpi2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{t("kpi_approved", lang)}</div>
        <div class="metric-value" style="color: #2E7D32;">{approved_count}</div>
        <div class="metric-sub">{t("kpi_sub_rate", lang, rate=approval_rate)}</div>
    </div>
    """, unsafe_allow_html=True)
with kpi3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{t("kpi_rejected", lang)}</div>
        <div class="metric-value" style="color: #C62828;">{rejected_count}</div>
        <div class="metric-sub">{t("kpi_sub_constraint", lang)}</div>
    </div>
    """, unsafe_allow_html=True)
with kpi4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{t("kpi_solve_time", lang)}</div>
        <div class="metric-value" style="color: #1565C0;">{solve_time * 1000:.1f} <span style="font-size: 1rem;">ms</span></div>
        <div class="metric-sub">{t("kpi_sub_status", lang, status=status_str)}</div>
    </div>
    """, unsafe_allow_html=True)
with kpi5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{t("kpi_objective", lang)}</div>
        <div class="metric-value" style="color: #6A1B9A;">{obj_val:.1f}</div>
        <div class="metric-sub">{t("kpi_sub_max_score", lang)}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Main Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    t("tab_dashboard", lang),
    t("tab_explainability", lang),
    t("tab_simulator", lang),
    t("tab_directory", lang)
])

# ==================== TAB 1: DASHBOARD & HEATMAP ====================
with tab1:
    col_lh, col_rh = st.columns([1.8, 1])
    
    with col_lh:
        st.subheader(t("heatmap_title", lang))
        heatmap_mode = st.radio(
            t("heatmap_mode_label", lang),
            [t("heatmap_mode_after", lang), t("heatmap_mode_before", lang)],
            horizontal=True
        )
        
        # Calculate daily leave count per department
        all_dates_sorted = sorted(list(set(
            date for _, row in opt_req_df.iterrows()
            for date in [d.strftime("%Y-%m-%d") for d in date_range(row["start_date"], row["end_date"])]
        )))
        
        depts = opt_dept_df["department"].tolist()
        matrix_data = []
        
        for dept in depts:
            row_vals = []
            dept_reqs = opt_req_df[opt_req_df["department"] == dept]
            if heatmap_mode == t("heatmap_mode_after", lang):
                dept_reqs = dept_reqs[dept_reqs["approved"] == 1]
                
            for d_str in all_dates_sorted:
                t_date = datetime.strptime(d_str, "%Y-%m-%d")
                cnt = 0
                for _, r in dept_reqs.iterrows():
                    s_d = datetime.strptime(r["start_date"], "%Y-%m-%d") if isinstance(r["start_date"], str) else r["start_date"]
                    e_d = datetime.strptime(r["end_date"], "%Y-%m-%d") if isinstance(r["end_date"], str) else r["end_date"]
                    if s_d <= t_date <= e_d:
                        cnt += 1
                row_vals.append(cnt)
            matrix_data.append(row_vals)
            
        fig_heat = px.imshow(
            matrix_data,
            x=all_dates_sorted,
            y=depts,
            labels=dict(x=t("col_start_date", lang), y=t("col_department", lang), color="Count"),
            color_continuous_scale="Oranges" if heatmap_mode == t("heatmap_mode_after", lang) else "YlOrRd",
            aspect="auto"
        )
        fig_heat.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#2D241E"),
            margin=dict(l=20, r=20, t=30, b=20),
            height=320
        )
        st.plotly_chart(fig_heat, use_container_width=True)
        
    with col_rh:
        st.subheader(t("chart_dept_summary_title", lang))
        dept_summary = opt_req_df.groupby(["department", "approved"]).size().unstack(fill_value=0).reset_index()
        if 1 not in dept_summary.columns: dept_summary[1] = 0
        if 0 not in dept_summary.columns: dept_summary[0] = 0
        dept_summary.columns = ["Department", t("status_rejected", lang), t("status_approved", lang)]
        
        fig_bar = px.bar(
            dept_summary,
            x="Department",
            y=[t("status_approved", lang), t("status_rejected", lang)],
            title="",
            color_discrete_map={t("status_approved", lang): "#2E7D32", t("status_rejected", lang): "#C62828"},
            barmode="stack"
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#2D241E"),
            legend_title="",
            margin=dict(l=10, r=10, t=40, b=10),
            height=320
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
    st.markdown("---")
    st.subheader(t("table_pending_title", lang))
    
    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        selected_dept = st.selectbox(t("filter_dept_label", lang), [t("filter_dept_all", lang)] + depts)
    with col_f2:
        search_query = st.text_input(t("search_label", lang))
        
    filtered_df = opt_req_df.copy()
    if selected_dept != t("filter_dept_all", lang):
        filtered_df = filtered_df[filtered_df["department"] == selected_dept]
    if search_query:
        filtered_df = filtered_df[
            filtered_df["name"].str.contains(search_query, case=False, na=False) |
            filtered_df["request_id"].str.contains(search_query, case=False, na=False)
        ]
        
    # Format table display
    display_df = filtered_df[[
        "request_id", "name", "department", "start_date", "end_date",
        "duration_days", "waiting_days", "seniority", "weight", "approved", "rejection_reason"
    ]].copy()
    
    display_df["Status Keputusan"] = display_df["approved"].apply(lambda x: "🟢 " + t("status_approved", lang) if x == 1 else "🔴 " + t("status_rejected", lang))
    display_df["Weight Prioritas"] = display_df["weight"].apply(lambda x: f"{x:.1f}")
    
    st.dataframe(
        display_df[[
            "request_id", "name", "department", "start_date", "end_date",
            "duration_days", "waiting_days", "seniority", "Weight Prioritas", "Status Keputusan", "rejection_reason"
        ]],
        column_config={
            "request_id": st.column_config.TextColumn(t("col_request_id", lang), width="small"),
            "name": st.column_config.TextColumn(t("col_employee", lang), width="medium"),
            "department": st.column_config.TextColumn(t("col_department", lang), width="small"),
            "start_date": st.column_config.TextColumn(t("col_start_date", lang), width="small"),
            "end_date": st.column_config.TextColumn(t("col_end_date", lang), width="small"),
            "duration_days": st.column_config.NumberColumn(t("col_duration", lang), width="small"),
            "waiting_days": st.column_config.NumberColumn(t("col_waiting", lang), width="small"),
            "seniority": st.column_config.NumberColumn(t("col_seniority", lang), width="small"),
            "Status Keputusan": st.column_config.TextColumn(t("col_status", lang), width="small"),
            "rejection_reason": st.column_config.TextColumn(t("col_reason", lang), width="large"),
        },
        hide_index=True,
        use_container_width=True
    )

# ==================== TAB 2: EXPLAINABILITY ENGINE ====================
with tab2:
    st.subheader(t("explainability_title", lang))
    st.markdown(t("explainability_desc", lang))
    
    rejected_requests = opt_req_df[opt_req_df["approved"] == 0]
    
    if rejected_requests.empty:
        st.success(t("no_rejections_msg", lang))
    else:
        st.write(t("showing_rejections_msg", lang, count=len(rejected_requests)))
        
        for idx, req in rejected_requests.iterrows():
            with st.expander(f"🔴 **{req['request_id']}** - {req['name']} ({req['department']}) | {t('col_start_date', lang)}: {req['start_date']} - {req['end_date']} ({req['duration_days']} {t('col_duration', lang)})"):
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    st.write(f"**{t('expander_seniority', lang)}**: Level {req['seniority']}")
                    st.write(f"**{t('expander_waiting', lang)}**: {req['waiting_days']} Days")
                with c2:
                    st.write(f"**{t('expander_priority_weight', lang)}**: `{req['weight']:.2f}`")
                    st.write(f"**{t('expander_reason', lang)}**: {req['reason']}")
                with c3:
                    st.error(f"**{t('expander_rejection_cause', lang)}**:\n{req['rejection_reason']}")

# ==================== TAB 3: SCENARIO SIMULATOR & AI CHATBOT ====================
with tab3:
    st.subheader(t("simulator_title", lang))
    st.markdown(t("simulator_subtitle", lang))
    
    scen_col1, scen_col2 = st.columns([1.5, 2])
    
    with scen_col1:
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        st.write(f"##### {t('form_scenario_title', lang)}")
        all_req_options = opt_req_df["request_id"] + " - " + opt_req_df["name"] + " (" + opt_req_df["department"] + ")"
        selected_option = st.selectbox(t("select_req_label", lang), all_req_options)
        
        target_rid = selected_option.split(" - ")[0]
        target_info = opt_req_df[opt_req_df["request_id"] == target_rid].iloc[0]
        
        st.info(f"""
        **{t('req_detail_title', lang)}**
        - **{t('req_detail_name', lang)}**: {target_info['name']}
        - **{t('req_detail_dept', lang)}**: {target_info['department']}
        - **{t('req_detail_dates', lang)}**: {target_info['start_date']} s/d {target_info['end_date']} ({target_info['duration_days']} days)
        - **{t('req_detail_status', lang)}**: {'🟢 ' + t('status_approved', lang) if target_info['approved'] == 1 else '🔴 ' + t('status_rejected', lang)}
        """)
        
        sim_btn = st.button(t("btn_force_approve", lang), type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with scen_col2:
        if sim_btn:
            with st.spinner(t("sim_running_msg", lang, rid=target_rid)):
                sim_res = simulate_scenario(
                    target_rid, req_df, emp_df, dept_df,
                    alpha=alpha, beta=beta, custom_min_staff_pct=min_staff_pct,
                    lang=lang
                )
                
                st.markdown("<div class='section-box'>", unsafe_allow_html=True)
                st.write(f"##### {t('sim_result_title', lang)}")
                
                if not sim_res["feasible"]:
                    st.error(sim_res["message"])
                else:
                    st.success(sim_res["message"])
                    if sim_res.get("bumped_requests"):
                        st.warning(t("bumped_reqs_title", lang, count=len(sim_res['bumped_requests'])))
                        bumped_df = opt_req_df[opt_req_df["request_id"].isin(sim_res["bumped_requests"])]
                        st.dataframe(bumped_df[["request_id", "name", "department", "start_date", "end_date", "weight"]], hide_index=True)
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='section-box' style='text-align: center; padding: 3rem;'>
                <p style='color: #7A695D; font-size: 1.1rem;'>
                    {t('sim_placeholder', lang)}
                </p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader(t("nl_chatbot_title", lang))
    
    nl_col1, nl_col2 = st.columns([2, 1])
    with nl_col1:
        user_query = st.text_input(
            t("nl_query_label", lang),
            placeholder=t("nl_query_placeholder", lang),
            key="user_ai_query"
        )
    with nl_col2:
        st.write("&nbsp;")
        ask_btn = st.button(t("btn_ask_ai", lang), type="primary", use_container_width=True)
        
    if ask_btn and user_query:
        with st.spinner(t("ai_analyzing_msg", lang)):
            ai_reply = ask_ai_assistant(
                user_query,
                api_key=ai_api_key,
                requests_df=opt_req_df,
                employees_df=emp_df,
                departments_df=dept_df,
                provider=ai_provider,
                alpha=alpha,
                beta=beta,
                custom_min_staff_pct=min_staff_pct,
                lang=lang
            )
            st.markdown("<div class='section-box'>", unsafe_allow_html=True)
            st.markdown(ai_reply)
            st.markdown("</div>", unsafe_allow_html=True)

# ==================== TAB 4: EMPLOYEE DIRECTORY ====================
with tab4:
    col_d1, col_d2 = st.columns([1, 1])
    with col_d1:
        st.subheader(t("directory_emp_title", lang))
        st.dataframe(
            emp_df,
            column_config={
                "employee_id": t("col_emp_id", lang),
                "name": t("col_employee", lang),
                "department": t("col_department", lang),
                "quota_days": t("col_emp_quota", lang),
                "seniority": t("col_emp_seniority", lang)
            },
            hide_index=True,
            use_container_width=True
        )
    with col_d2:
        st.subheader(t("directory_dept_title", lang))
        st.dataframe(
            opt_dept_df,
            column_config={
                "department": t("col_department", lang),
                "total_staff": t("col_dept_total", lang),
                "min_staff_pct": t("col_dept_pct", lang),
                "min_staff": t("col_dept_min", lang),
                "max_on_leave": t("col_dept_max", lang)
            },
            hide_index=True,
            use_container_width=True
        )

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #7A695D; font-size: 0.85rem;'>
    {t("footer_text", lang)}
</div>
""", unsafe_allow_html=True)
