TRANSLATIONS = {
    "id": {
        # --- App & Header ---
        "app_title": "Smart Leave Approval Optimizer",
        "app_subtitle": "Automated Integer Linear Programming (ILP) Leave Scheduler dengan Preservasi Staffing & Explainability Keputusan",
        "language_label": "🌐 Bahasa / Language",
        "sidebar_control_panel": "⚙️ Panel Kontrol Optimizer",
        "solver_objectives_title": "🎯 Bobot Objektif Solver",
        "slider_alpha": "Bobot α (Waktu Menunggu / Waiting Days)",
        "slider_beta": "Bobot β (Seniority Level)",
        "slider_min_staff": "Min Staffing per Dept (%)",
        "btn_run_ilp": "🚀 Jalankan ILP",
        "btn_reset_data": "🔄 Reset Data",
        "reset_success": "Dataset berhasil di-reset!",
        "sidebar_ai_section": "🤖 Integrasi AI (Opsional)",
        "ai_provider_label": "Pilih AI Engine / Provider:",
        "ai_key_openai": "🔑 OpenAI API Key:",
        "ai_key_anthropic": "🔑 Anthropic API Key:",

        # --- Tabs ---
        "tab_dashboard": "📊 Dashboard & Heatmap",
        "tab_explainability": "🔍 Explainability Engine",
        "tab_simulator": "💬 Scenario Simulator & AI Chatbot",
        "tab_directory": "👥 Employee Directory & Staffing Rules",

        # --- KPI cards ---
        "kpi_total_requests": "Total Request",
        "kpi_approved": "Disetujui (Approved)",
        "kpi_rejected": "Ditolak (Rejected)",
        "kpi_solve_time": "Waktu Solve ILP",
        "kpi_objective": "Objective Score",
        "kpi_sub_depts": "Di 5 Departemen",
        "kpi_sub_rate": "Tingkat: {rate}%",
        "kpi_sub_constraint": "Staffing & Quota Constraint",
        "kpi_sub_status": "Status: {status}",
        "kpi_sub_max_score": "Skor Prioritas Maksimal",

        # --- Dashboard Tab UI ---
        "heatmap_title": "🔥 Visualisasi Heatmap Staffing per Departemen",
        "heatmap_mode_label": "Mode Heatmap:",
        "heatmap_mode_after": "Sesudah ILP Optimization (Approved Leaves Only)",
        "heatmap_mode_before": "Sebelum Optimization (Semua Request Dianggap Cuti)",
        "chart_dept_summary_title": "📈 Ringkasan Keputusan Departemen",
        "table_pending_title": "📋 Daftar Request & Keputusan Optimizer",
        "filter_dept_label": "Filter Departemen:",
        "filter_dept_all": "Semua Departemen",
        "search_label": "🔍 Cari Nama Pegawai / Request ID:",
        
        # --- Explainability Tab UI ---
        "explainability_title": "🔍 Explainability Engine - Transparansi Keputusan ILP",
        "explainability_desc": (
            "> **Pendekatan Explainability (Heuristic-based)**:\n"
            "> Karena model ini menggunakan variabel Integer/Binary ($x_i \\in \\{0, 1\\}$), solver CBC tidak menghasilkan dual value (`.pi`) yang valid.\n"
            "> Sistem kami mengevaluasi penyebab penolakan secara instan berdasarkan:\n"
            "> 1. **Evaluasi Kuota Individual**: Cek apakah total hari disetujui melebihi sisa kuota pegawai.\n"
            "> 2. **Evaluasi Bottleneck Staffing Departemen**: Identifikasi tanggal puncak (*peak date*) di mana kapasitas cuti disetujui mencapai batas maksimum $\\text{total\\_staff} - \\text{min\\_staff}$."
        ),
        "no_rejections_msg": "🎉 Tidak ada request yang ditolak! Semua request dapat disetujui dengan batas constraint saat ini.",
        "showing_rejections_msg": "Menampilkan **{count}** request yang ditolak beserta penyebab detailnya:",
        "expander_seniority": "Seniority",
        "expander_waiting": "Lama Menunggu",
        "expander_priority_weight": "Weight Prioritas",
        "expander_reason": "Alasan Pengajuan",
        "expander_rejection_cause": "Penyebab Utama Penolakan",

        # --- Scenario Simulator & Chatbot UI ---
        "simulator_title": "💬 Scenario Simulator & AI Chatbot Assistant",
        "simulator_subtitle": "Penguji keputusan manajerial secara real-time via **Form Skenario** maupun **Tanya AI Assistant (Natural Language Query)**.",
        "simulator_desc": "Fitur simulasi interaktif untuk menguji keputusan manajerial secara real-time. Misalnya: \"Apakah aman jika saya memaksa approve cuti pegawai X di tanggal 10–15 Agustus?\"",
        "form_scenario_title": "🛠️ Form Simulasi Skenario",
        "select_req_label": "Pilih Request Cuti yang Ingin Diuji:",
        "req_detail_title": "Detail Request yang Dipilih:",
        "req_detail_name": "Nama",
        "req_detail_dept": "Departemen",
        "req_detail_dates": "Tanggal",
        "req_detail_status": "Status Saat Ini",
        "btn_force_approve": "⚡ Paksa Approve & Simulasikan",
        "sim_running_msg": "Menjalankan simulasi ILP untuk {rid}...",
        "sim_result_title": "📊 Hasil Analisis Dampak Skenario",
        "bumped_reqs_title": "Daftar Request yang Tergeser/Dibatalkan ({count}):",
        "sim_placeholder": "👈 Pilih request di sebelah kiri dan klik **\"Paksa Approve & Simulasikan\"** untuk melihat dampak constraint dan request mana yang tergeser.",
        "nl_chatbot_title": "🤖 Natural-Language Query Chatbot (OpenAI / Anthropic API / Smart Solver)",
        "nl_query_label": "💬 Pertanyaan Natural Language:",
        "nl_query_placeholder": "Contoh: Aman gak kalau saya approve cuti Andi 10-15 Agustus?",
        "btn_ask_ai": "🤖 Tanya AI",
        "ai_analyzing_msg": "🤖 AI Assistant sedang menganalisis data ILP & menjalankan solver...",

        # --- Employee Directory UI ---
        "directory_emp_title": "👥 Direktori Pegawai (40 Karyawan)",
        "directory_dept_title": "🏢 Aturan Minimum Staffing per Departemen",
        "footer_text": "Smart Leave Approval Optimizer — Built for <b>OrionHackathon 2026</b> (Operations Research Track) | Powered by Python, PuLP ILP Solver & Streamlit",

        # --- Table columns / common labels ---
        "col_request_id": "Req ID",
        "col_employee": "Nama Pegawai",
        "col_department": "Dept",
        "col_start_date": "Mulai",
        "col_end_date": "Selesai",
        "col_duration": "Durasi",
        "col_waiting": "Nunggu (Hari)",
        "col_seniority": "Seniority",
        "col_weight": "Weight Prioritas",
        "col_status": "Status",
        "col_reason": "Alasan (Jika Rejected)",
        "status_approved": "Approved",
        "status_rejected": "Rejected",
        "col_emp_id": "ID",
        "col_emp_quota": "Sisa Quota Cuti (Hari)",
        "col_emp_seniority": "Level Seniority (1-10)",
        "col_dept_total": "Total Karyawan",
        "col_dept_pct": "Min Staffing %",
        "col_dept_min": "Min Staff Wajib Hadir",
        "col_dept_max": "Maksimal Boleh Cuti Bersamaan",

        # --- Dynamic messages (dipakai .format() dengan kwargs) ---
        "quota_reason": "Quota cuti tidak mencukupi: sisa quota {remaining} hari, request ini membutuhkan {duration} hari.",
        "staffing_reason": (
            "Kapasitas cuti Dept {dept} penuh pada tanggal {date} "
            "(maksimum {max_on_leave} orang cuti bersamaan agar min staff {min_staff} terpenuhi). "
            "Slot terisi oleh {n_winners} request berprioritas lebih tinggi: {winners_list}. "
            "Total {n_blocking} hari dalam request ini melanggar batas staffing."
        ),
        "fallback_reason": (
            "Tidak disetujui karena objective function ILP memprioritaskan request lain "
            "dengan kombinasi waiting_days & seniority lebih tinggi pada slot kapasitas "
            "departemen yang terbatas."
        ),
        "infeasible_quota": (
            "❌ **TIDAK AMAN (Infeasible)**: Request {rid} ({name}) melebihi total quota "
            "cuti pegawai ({duration} hari > {quota} hari)."
        ),
        "infeasible_staffing": (
            "❌ **TIDAK AMAN (Infeasible)**: Menyetujui request {rid} ({name}) melanggar "
            "batas minimum staffing Departemen {dept} pada periode {start} s/d {end}."
        ),
        "feasible_with_impact": (
            "⚠️ **AMAN DENGAN IMPACT**: Request {rid} ({name}) BISA disetujui, namun "
            "menggeser (membatalkan) {n_bumped} request lain yang sebelumnya disetujui: {bumped_names}."
        ),
        "feasible_safe": (
            "✅ **SANGAT AMAN**: Request {rid} ({name}) dapat disetujui tanpa mengganggu "
            "staffing maupun request pegawai lain!"
        ),
        "request_not_found": "Request ID {rid} tidak ditemukan.",

        # --- AI assistant fallback ---
        "ai_analysis_header": "🤖 **Analisis Smart Solver Engine untuk Request {rid} ({name} - Dept {dept})**:",
        "ai_period_label": "**Periode Cuti**",
        "ai_status_label": "**Status Keputusan ILP**",
        "ai_reason_label": "**Alasan Penolakan**",
        "ai_scenario_label": "**Hasil Simulasi Skenario 'What-If'**",
        "ai_bumped_note": "⚠️ **Catatan**: Jika dipaksakan approve, request berikut akan tergeser: {bumped_names}.",
        "ai_status_approved": "sudah disetujui",
        "ai_status_rejected": "ditolak oleh solver",
        "ai_recap_header": "🤖 **Analisis Smart Solver Engine**:",
        "ai_recap_body": (
            "- Total **{total}** request cuti dievaluasi.\n"
            "- Departemen dengan jumlah penolakan tertinggi adalah **Dept {worst_dept}** "
            "akibat tingginya klaim cuti di tanggal puncak (peak date).\n"
            "- Anda dapat menyesuaikan bobot Seniority dan Waiting Days pada Control Panel di sidebar."
        ),
        "ai_ready_header": "🤖 **AI Assistant Ready!**",
        "ai_ready_body": "Anda dapat menanyakan hal-hal seperti:",
        "ai_error_openai": "⚠️ **OpenAI API Error**: {err}. Menggunakan Smart Solver Engine lokal...",
        "ai_error_anthropic": "⚠️ **Anthropic API Error**: {err}. Menggunakan Smart Solver Engine lokal...",
        "ai_exception_openai": "⚠️ **OpenAI API Exception**: {err}. Menggunakan Smart Solver Engine lokal...",
        "ai_exception_anthropic": "⚠️ **Anthropic API Exception**: {err}. Menggunakan Smart Solver Engine lokal...",
        "ai_system_lang_instruction": "PENTING: Jawab pertanyaan user dalam Bahasa Indonesia.",
    },
    "en": {
        # --- App & Header ---
        "app_title": "Smart Leave Approval Optimizer",
        "app_subtitle": "Automated Integer Linear Programming (ILP) Leave Scheduler with Staffing Preservations & Decision Explainability",
        "language_label": "🌐 Language / Bahasa",
        "sidebar_control_panel": "⚙️ Optimizer Control Panel",
        "solver_objectives_title": "🎯 Solver Objective Weights",
        "slider_alpha": "Weight α (Waiting Time)",
        "slider_beta": "Weight β (Seniority Level)",
        "slider_min_staff": "Min Staffing per Dept (%)",
        "btn_run_ilp": "🚀 Run ILP",
        "btn_reset_data": "🔄 Reset Data",
        "reset_success": "Dataset reset successfully!",
        "sidebar_ai_section": "🤖 AI Integration (Optional)",
        "ai_provider_label": "Select AI Engine / Provider:",
        "ai_key_openai": "🔑 OpenAI API Key:",
        "ai_key_anthropic": "🔑 Anthropic API Key:",

        # --- Tabs ---
        "tab_dashboard": "📊 Dashboard & Heatmap",
        "tab_explainability": "🔍 Explainability Engine",
        "tab_simulator": "💬 Scenario Simulator & AI Chatbot",
        "tab_directory": "👥 Employee Directory & Staffing Rules",

        # --- KPI cards ---
        "kpi_total_requests": "Total Requests",
        "kpi_approved": "Approved",
        "kpi_rejected": "Rejected",
        "kpi_solve_time": "ILP Solve Time",
        "kpi_objective": "Objective Score",
        "kpi_sub_depts": "Across 5 Depts",
        "kpi_sub_rate": "Rate: {rate}%",
        "kpi_sub_constraint": "Staffing & Quota Constraint",
        "kpi_sub_status": "Status: {status}",
        "kpi_sub_max_score": "Max Priority Score",

        # --- Dashboard Tab UI ---
        "heatmap_title": "🔥 Department Staffing Heatmap Visualization",
        "heatmap_mode_label": "Heatmap Mode:",
        "heatmap_mode_after": "After ILP Optimization (Approved Leaves Only)",
        "heatmap_mode_before": "Before Optimization (All Requests Counted)",
        "chart_dept_summary_title": "📈 Department Decisions Summary",
        "table_pending_title": "📋 Requests List & Optimizer Decisions",
        "filter_dept_label": "Filter Department:",
        "filter_dept_all": "All Departments",
        "search_label": "🔍 Search Employee Name / Request ID:",

        # --- Explainability Tab UI ---
        "explainability_title": "🔍 Explainability Engine - ILP Decision Transparency",
        "explainability_desc": (
            "> **Explainability Approach (Heuristic-based)**:\n"
            "> Because this model uses Integer/Binary variables ($x_i \\in \\{0, 1\\}$), the CBC solver does not yield valid dual values (`.pi`).\n"
            "> Our system evaluates rejection causes instantly based on:\n"
            "> 1. **Individual Quota Evaluation**: Checks if total approved days exceed remaining employee quota.\n"
            "> 2. **Department Staffing Bottleneck Evaluation**: Identifies peak dates where approved leave capacity reaches the maximum limit $\\text{total\\_staff} - \\text{min\\_staff}$."
        ),
        "no_rejections_msg": "🎉 No requests rejected! All requests can be approved under current constraints.",
        "showing_rejections_msg": "Displaying **{count}** rejected request(s) with detailed reasons:",
        "expander_seniority": "Seniority",
        "expander_waiting": "Waiting Time",
        "expander_priority_weight": "Priority Weight",
        "expander_reason": "Submission Reason",
        "expander_rejection_cause": "Primary Rejection Cause",

        # --- Scenario Simulator & Chatbot UI ---
        "simulator_title": "💬 Scenario Simulator & AI Chatbot Assistant",
        "simulator_subtitle": "Test managerial decisions in real-time via **Scenario Form** or **Ask AI Assistant (Natural Language Query)**.",
        "simulator_desc": "Interactive simulation feature to test managerial decisions in real-time. Example: \"Is it safe if I force-approve employee X's leave on Aug 10-15?\"",
        "form_scenario_title": "🛠️ Scenario Simulation Form",
        "select_req_label": "Select Leave Request to Test:",
        "req_detail_title": "Selected Request Details:",
        "req_detail_name": "Name",
        "req_detail_dept": "Department",
        "req_detail_dates": "Dates",
        "req_detail_status": "Current Status",
        "btn_force_approve": "⚡ Force Approve & Simulate",
        "sim_running_msg": "Running ILP simulation for {rid}...",
        "sim_result_title": "📊 Scenario Impact Analysis Results",
        "bumped_reqs_title": "Displaced/Cancelled Requests List ({count}):",
        "sim_placeholder": "👈 Select a request on the left and click **\"Force Approve & Simulate\"** to see constraint impact and displaced requests.",
        "nl_chatbot_title": "🤖 Natural-Language Query Chatbot (OpenAI / Anthropic API / Smart Solver)",
        "nl_query_label": "💬 Natural Language Question:",
        "nl_query_placeholder": "Example: Is it safe to approve Andi's leave Aug 10-15?",
        "btn_ask_ai": "🤖 Ask AI",
        "ai_analyzing_msg": "🤖 AI Assistant is analyzing ILP data & running solver...",

        # --- Employee Directory UI ---
        "directory_emp_title": "👥 Employee Directory (40 Staff)",
        "directory_dept_title": "🏢 Minimum Staffing Rules per Department",
        "footer_text": "Smart Leave Approval Optimizer — Built for <b>OrionHackathon 2026</b> (Operations Research Track) | Powered by Python, PuLP ILP Solver & Streamlit",

        # --- Table columns / common labels ---
        "col_request_id": "Req ID",
        "col_employee": "Employee Name",
        "col_department": "Dept",
        "col_start_date": "Start",
        "col_end_date": "End",
        "col_duration": "Duration",
        "col_waiting": "Waiting (Days)",
        "col_seniority": "Seniority",
        "col_weight": "Priority Weight",
        "col_status": "Status",
        "col_reason": "Reason (If Rejected)",
        "status_approved": "Approved",
        "status_rejected": "Rejected",
        "col_emp_id": "ID",
        "col_emp_quota": "Remaining Quota (Days)",
        "col_emp_seniority": "Seniority Level (1-10)",
        "col_dept_total": "Total Staff",
        "col_dept_pct": "Min Staffing %",
        "col_dept_min": "Min Staff Required",
        "col_dept_max": "Max Simultaneous Leave",

        # --- Dynamic messages (dipakai .format() dengan kwargs) ---
        "quota_reason": "Insufficient leave quota: {remaining} days remaining, this request needs {duration} days.",
        "staffing_reason": (
            "Dept {dept} leave capacity is full on {date} "
            "(max {max_on_leave} people on leave simultaneously to keep min staff {min_staff}). "
            "Slot taken by {n_winners} higher-priority requests: {winners_list}. "
            "A total of {n_blocking} days in this request violate the staffing limit."
        ),
        "fallback_reason": (
            "Not approved because the ILP objective function prioritized other requests "
            "with a higher combined waiting_days & seniority score for the limited "
            "department capacity slot."
        ),
        "infeasible_quota": (
            "❌ **NOT SAFE (Infeasible)**: Request {rid} ({name}) exceeds the employee's "
            "total leave quota ({duration} days > {quota} days)."
        ),
        "infeasible_staffing": (
            "❌ **NOT SAFE (Infeasible)**: Approving request {rid} ({name}) violates the "
            "minimum staffing limit for Dept {dept} during {start} to {end}."
        ),
        "feasible_with_impact": (
            "⚠️ **SAFE WITH IMPACT**: Request {rid} ({name}) CAN be approved, but it "
            "displaces (cancels) {n_bumped} other previously-approved request(s): {bumped_names}."
        ),
        "feasible_safe": (
            "✅ **FULLY SAFE**: Request {rid} ({name}) can be approved without affecting "
            "staffing or any other employee's request!"
        ),
        "request_not_found": "Request ID {rid} not found.",

        # --- AI assistant fallback ---
        "ai_analysis_header": "🤖 **Smart Solver Engine Analysis for Request {rid} ({name} - Dept {dept})**:",
        "ai_period_label": "**Leave Period**",
        "ai_status_label": "**ILP Decision Status**",
        "ai_reason_label": "**Rejection Reason**",
        "ai_scenario_label": "**'What-If' Scenario Simulation Result**",
        "ai_bumped_note": "⚠️ **Note**: If force-approved, the following requests will be displaced: {bumped_names}.",
        "ai_status_approved": "already approved",
        "ai_status_rejected": "rejected by solver",
        "ai_recap_header": "🤖 **Smart Solver Engine Analysis**:",
        "ai_recap_body": (
            "- A total of **{total}** leave requests were evaluated.\n"
            "- The department with the highest rejection count is **Dept {worst_dept}** "
            "due to high leave demand on peak dates.\n"
            "- You can adjust the Seniority and Waiting Days weights in the sidebar Control Panel."
        ),
        "ai_ready_header": "🤖 **AI Assistant Ready!**",
        "ai_ready_body": "You can ask things like:",
        "ai_error_openai": "⚠️ **OpenAI API Error**: {err}. Falling back to local Smart Solver Engine...",
        "ai_error_anthropic": "⚠️ **Anthropic API Error**: {err}. Falling back to local Smart Solver Engine...",
        "ai_exception_openai": "⚠️ **OpenAI API Exception**: {err}. Falling back to local Smart Solver Engine...",
        "ai_exception_anthropic": "⚠️ **Anthropic API Exception**: {err}. Falling back to local Smart Solver Engine...",
        "ai_system_lang_instruction": "IMPORTANT: Answer the user's question in English.",
    },
}


def t(key: str, lang: str = "id", **kwargs) -> str:
    """
    Ambil teks terjemahan berdasarkan key & lang. Kalau ada kwargs, otomatis
    di-.format(). Fallback ke 'id' kalau lang gak dikenali, fallback ke key
    itu sendiri kalau key gak ketemu.
    """
    text = TRANSLATIONS.get(lang, TRANSLATIONS["id"]).get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text
