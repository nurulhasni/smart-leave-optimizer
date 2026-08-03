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
    st.image("https://img.icons8.com/isometric/96/calendar--v2.png", width=64)
    st.title("⚙️ Control Panel")
    st.markdown("---")
    
    st.subheader("🎯 Solver Objectives Weight")
    alpha = st.slider("Weight α (Waktu Menunggu / Waiting Days)", 0.0, 5.0, 1.0, 0.1, help="Bobot prioritas untuk lama hari menanti keputusan")
    beta = st.slider("Weight β (Seniority Level)", 0.0, 5.0, 1.5, 0.1, help="Bobot prioritas untuk tingkat senioritas karyawan")
    
    st.markdown("---")
    st.subheader("🛡️ Staffing Constraint")
    min_staff_pct = st.slider("Min Staffing per Dept (%)", 50, 90, 70, 5, help="Persentase minimal karyawan yang harus tetap bertugas di tiap departemen") / 100.0
    
    st.markdown("---")
    st.subheader("🤖 AI Integration (Opsional)")
    ai_provider = st.selectbox(
        "Pilih AI Engine / Provider:",
        ["Built-in Smart Solver (Tanpa Key)", "OpenAI (GPT-4o)", "Anthropic (Claude)"],
        help="Pilih engine cerdas untuk menjawab query natural language."
    )
    
    ai_api_key = ""
    if ai_provider.startswith("OpenAI"):
        ai_api_key = st.text_input("🔑 OpenAI API Key:", type="password", help="Masukkan API Key OpenAI (sk-...)")
    elif ai_provider.startswith("Anthropic"):
        ai_api_key = st.text_input("🔑 Anthropic API Key:", type="password", help="Masukkan API Key Anthropic (sk-ant-...)")
    
    st.markdown("---")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        run_btn = st.button("🚀 Run ILP", use_container_width=True, type="primary")
    with col_btn2:
        reset_btn = st.button("🔄 Reset Data", use_container_width=True)

    if reset_btn:
        generate_all_datasets()
        st.cache_data.clear()
        st.session_state["optimization_results"] = None
        st.success("Dataset berhasil di-reset!")
        st.rerun()

# Header Banner
st.markdown("""
<div class="main-header">
    <div class="main-title">
        🗓️ Smart Leave Approval Optimizer
    </div>
    <div class="main-subtitle">
        Automated Integer Linear Programming (ILP) Leave Scheduler with Staffing Preservations & Decision Explainability
    </div>
</div>
""", unsafe_allow_html=True)

# Load data
emp_df, dept_df, req_df = load_data()

# Trigger optimization if requested or if state is empty
if run_btn or st.session_state["optimization_results"] is None:
    with st.spinner("⚡ Running PuLP Integer Linear Programming (ILP) Solver..."):
        results = solve_leave_optimization(
            req_df, emp_df, dept_df,
            alpha=alpha, beta=beta,
            custom_min_staff_pct=min_staff_pct
        )
        st.session_state["optimization_results"] = results

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
        <div class="metric-title">Total Requests</div>
        <div class="metric-value">{total_reqs}</div>
        <div class="metric-sub">Across 5 Depts</div>
    </div>
    """, unsafe_allow_html=True)
with kpi2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Disetujui (Approved)</div>
        <div class="metric-value" style="color: #2E7D32;">{approved_count}</div>
        <div class="metric-sub">Rate: {approval_rate}%</div>
    </div>
    """, unsafe_allow_html=True)
with kpi3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Ditolak (Rejected)</div>
        <div class="metric-value" style="color: #C62828;">{rejected_count}</div>
        <div class="metric-sub">Staffing & Quota Constraint</div>
    </div>
    """, unsafe_allow_html=True)
with kpi4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">ILP Execution Time</div>
        <div class="metric-value" style="color: #1565C0;">{solve_time * 1000:.1f} <span style="font-size: 1rem;">ms</span></div>
        <div class="metric-sub">Status: {status_str}</div>
    </div>
    """, unsafe_allow_html=True)
with kpi5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Objective Score</div>
        <div class="metric-value" style="color: #6A1B9A;">{obj_val:.1f}</div>
        <div class="metric-sub">Max Priority Score</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Main Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Optimization Dashboard & Staffing Heatmap",
    "🔍 Explainability Engine (Penjelasan Penolakan)",
    "💬 Scenario Simulator & AI Chatbot",
    "👥 Employee Directory & Staffing Rules"
])

# ==================== TAB 1: DASHBOARD & HEATMAP ====================
with tab1:
    col_lh, col_rh = st.columns([1.8, 1])
    
    with col_lh:
        st.subheader("🔥 Visualisasi Heatmap Staffing per Departemen")
        heatmap_mode = st.radio("Mode Heatmap:", ["Sesudah ILP Optimization (Approved Leaves Only)", "Sebelum Optimization (Semua Request Dianggap Cuti)"], horizontal=True)
        
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
            if heatmap_mode.startswith("Sesudah"):
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
            labels=dict(x="Tanggal", y="Departemen", color="Jumlah Cuti"),
            color_continuous_scale="Oranges" if heatmap_mode.startswith("Sesudah") else "YlOrRd",
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
        st.subheader("📈 Ringkasan Keputusan Departemen")
        dept_summary = opt_req_df.groupby(["department", "approved"]).size().unstack(fill_value=0).reset_index()
        if 1 not in dept_summary.columns: dept_summary[1] = 0
        if 0 not in dept_summary.columns: dept_summary[0] = 0
        dept_summary.columns = ["Department", "Rejected", "Approved"]
        
        fig_bar = px.bar(
            dept_summary,
            x="Department",
            y=["Approved", "Rejected"],
            title="Approved vs Rejected per Dept",
            color_discrete_map={"Approved": "#2E7D32", "Rejected": "#C62828"},
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
    st.subheader("📋 Daftar Pending Request & Keputusan Optimizer")
    
    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        selected_dept = st.selectbox("Filter Departemen:", ["Semua Departemen"] + depts)
    with col_f2:
        search_query = st.text_input("🔍 Cari Nama Pegawai / Request ID:")
        
    filtered_df = opt_req_df.copy()
    if selected_dept != "Semua Departemen":
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
    
    display_df["Status Keputusan"] = display_df["approved"].apply(lambda x: "🟢 Approved" if x == 1 else "🔴 Rejected")
    display_df["Weight Prioritas"] = display_df["weight"].apply(lambda x: f"{x:.1f}")
    
    st.dataframe(
        display_df[[
            "request_id", "name", "department", "start_date", "end_date",
            "duration_days", "waiting_days", "seniority", "Weight Prioritas", "Status Keputusan", "rejection_reason"
        ]],
        column_config={
            "request_id": st.column_config.TextColumn("Req ID", width="small"),
            "name": st.column_config.TextColumn("Nama Pegawai", width="medium"),
            "department": st.column_config.TextColumn("Dept", width="small"),
            "start_date": st.column_config.TextColumn("Mulai", width="small"),
            "end_date": st.column_config.TextColumn("Selesai", width="small"),
            "duration_days": st.column_config.NumberColumn("Durasi", width="small"),
            "waiting_days": st.column_config.NumberColumn("Nunggu (Hari)", width="small"),
            "seniority": st.column_config.NumberColumn("Seniority", width="small"),
            "Status Keputusan": st.column_config.TextColumn("Status", width="small"),
            "rejection_reason": st.column_config.TextColumn("Alasan (Jika Rejected)", width="large"),
        },
        hide_index=True,
        use_container_width=True
    )

# ==================== TAB 2: EXPLAINABILITY ENGINE ====================
with tab2:
    st.subheader("🔍 Explainability Engine - Transparansi Keputusan ILP")
    st.markdown(r"""
    > **Pendekatan Explainability (Heuristic-based)**:
    > Karena model ini menggunakan variabel Integer/Binary ($x_i \in \{0, 1\}$), solver CBC tidak menghasilkan dual value (`.pi`) yang valid.
    > Sistem kami mengevaluasi penyebab penolakan secara instan berdasarkan:
    > 1. **Evaluasi Kuota Individual**: Cek apakah total hari disetujui melebihi sisa sisa kuota pegawai.
    > 2. **Evaluasi Bottleneck Staffing Departemen**: Identifikasi tanggal puncak (*peak date*) di mana kapasitas cuti disetujui mencapai batas maksimum $\text{total\_staff} - \text{min\_staff}$.
    """)
    
    rejected_requests = opt_req_df[opt_req_df["approved"] == 0]
    
    if rejected_requests.empty:
        st.success("🎉 Tidak ada request yang ditolak! Semua request dapat disetujui dengan batas constraint saat ini.")
    else:
        st.write(f"Menampilkan **{len(rejected_requests)}** request yang ditolak beserta penyebab detailnya:")
        
        for idx, req in rejected_requests.iterrows():
            with st.expander(f"🔴 **{req['request_id']}** - {req['name']} ({req['department']}) | Tanggal: {req['start_date']} s/d {req['end_date']} ({req['duration_days']} Hari)"):
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    st.write(f"**Seniority**: Level {req['seniority']}")
                    st.write(f"**Lama Menunggu**: {req['waiting_days']} Hari")
                with c2:
                    st.write(f"**Weight Prioritas**: `{req['weight']:.2f}`")
                    st.write(f"**Alasan Pengajuan**: {req['reason']}")
                with c3:
                    st.error(f"**Penyebab Utama Penolakan**:\n{req['rejection_reason']}")

# ==================== TAB 3: SCENARIO SIMULATOR & AI CHATBOT ====================
with tab3:
    st.subheader("💬 Scenario Simulator & AI Chatbot Assistant")
    st.markdown("""
    Penguji keputusan manajerial secara *real-time* via **Form Skenario** maupun **Tanya AI Assistant (Natural Language Query)**.
    """)
    
    scen_col1, scen_col2 = st.columns([1.5, 2])
    
    with scen_col1:
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        st.write("##### 🛠️ Form Simulasi Skenario")
        all_req_options = opt_req_df["request_id"] + " - " + opt_req_df["name"] + " (" + opt_req_df["department"] + ")"
        selected_option = st.selectbox("Pilih Request Cuti yang Ingin Diuji:", all_req_options)
        
        target_rid = selected_option.split(" - ")[0]
        target_info = opt_req_df[opt_req_df["request_id"] == target_rid].iloc[0]
        
        st.info(f"""
        **Detail Request yang Dipilih:**
        - **Nama**: {target_info['name']}
        - **Departemen**: {target_info['department']}
        - **Tanggal**: {target_info['start_date']} s/d {target_info['end_date']} ({target_info['duration_days']} hari)
        - **Status Saat Ini**: {'🟢 Approved' if target_info['approved'] == 1 else '🔴 Rejected'}
        """)
        
        sim_btn = st.button("⚡ Paksa Approve & Simulasikan", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with scen_col2:
        if sim_btn:
            with st.spinner(f"Menjalankan simulasi ILP untuk {target_rid}..."):
                sim_res = simulate_scenario(
                    target_rid, req_df, emp_df, dept_df,
                    alpha=alpha, beta=beta, custom_min_staff_pct=min_staff_pct
                )
                
                st.markdown("<div class='section-box'>", unsafe_allow_html=True)
                st.write("##### 📊 Hasil Analisis Dampak Skenario")
                
                if not sim_res["feasible"]:
                    st.error(sim_res["message"])
                else:
                    st.success(sim_res["message"])
                    if sim_res.get("bumped_requests"):
                        st.warning(f"**Daftar Request yang Tergeser/Dibatalkan ({len(sim_res['bumped_requests'])}):**")
                        bumped_df = opt_req_df[opt_req_df["request_id"].isin(sim_res["bumped_requests"])]
                        st.dataframe(bumped_df[["request_id", "name", "department", "start_date", "end_date", "weight"]], hide_index=True)
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='section-box' style='text-align: center; padding: 3rem;'>
                <p style='color: #7A695D; font-size: 1.1rem;'>
                    👈 Pilih request di sebelah kiri dan klik <b>"Paksa Approve & Simulasikan"</b> untuk melihat dampak constraint dan request mana yang tergeser.
                </p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🤖 Natural-Language Query Chatbot (Anthropic API / Smart Solver AI)")
    
    nl_col1, nl_col2 = st.columns([2, 1])
    with nl_col1:
        user_query = st.text_input(
            "💬 Pertanyaan Natural Language:",
            placeholder="Contoh: Aman gak kalau saya approve cuti Andi 10-15 Agustus?",
            key="user_ai_query"
        )
    with nl_col2:
        st.write("&nbsp;")
        ask_btn = st.button("🤖 Tanya AI", type="primary", use_container_width=True)
        
    if ask_btn and user_query:
        with st.spinner("🤖 AI Assistant sedang menganalisis data ILP & menjalankan solver..."):
            ai_reply = ask_ai_assistant(
                user_query,
                api_key=ai_api_key,
                requests_df=opt_req_df,
                employees_df=emp_df,
                departments_df=dept_df,
                provider=ai_provider,
                alpha=alpha,
                beta=beta,
                custom_min_staff_pct=min_staff_pct
            )
            st.markdown("<div class='section-box'>", unsafe_allow_html=True)
            st.markdown(ai_reply)
            st.markdown("</div>", unsafe_allow_html=True)

# ==================== TAB 4: EMPLOYEE DIRECTORY ====================
with tab4:
    col_d1, col_d2 = st.columns([1, 1])
    with col_d1:
        st.subheader("👥 Direktori Pegawai (40 Karyawan)")
        st.dataframe(
            emp_df,
            column_config={
                "employee_id": "ID",
                "name": "Nama Pegawai",
                "department": "Departemen",
                "quota_days": "Sisa Quota Cuti (Hari)",
                "seniority": "Level Seniority (1-10)"
            },
            hide_index=True,
            use_container_width=True
        )
    with col_d2:
        st.subheader("🏢 Aturan Minimum Staffing per Departemen")
        st.dataframe(
            opt_dept_df,
            column_config={
                "department": "Departemen",
                "total_staff": "Total Karyawan",
                "min_staff_pct": "Min Staffing %",
                "min_staff": "Min Staff Wajib Hadir",
                "max_on_leave": "Maksimal Boleh Cuti Bersamaan"
            },
            hide_index=True,
            use_container_width=True
        )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7A695D; font-size: 0.85rem;'>
    Smart Leave Approval Optimizer — Built for <b>OrionHackathon 2026</b> (Operations Research Track) | Powered by Python, PuLP ILP Solver & Streamlit
</div>
""", unsafe_allow_html=True)
