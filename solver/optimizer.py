import time
import pandas as pd
from datetime import datetime, timedelta
import pulp

def date_range(start_date, end_date):
    """Generates a list of datetime objects from start_date to end_date inclusive."""
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    days = (end_date - start_date).days + 1
    return [start_date + timedelta(days=i) for i in range(days)]

def build_approved_leave_by_day(requests_df: pd.DataFrame) -> dict:
    """
    Precompute: untuk tiap (department, date), siapa saja (request_id) yang
    approved dan sedang cuti pada tanggal itu.
    Return: dict[(department, date)] -> list of request_id
    """
    approved = requests_df[requests_df["approved"] == 1]
    by_day = {}
    for _, req in approved.iterrows():
        s_date = datetime.strptime(req["start_date"], "%Y-%m-%d") if isinstance(req["start_date"], str) else req["start_date"]
        e_date = datetime.strptime(req["end_date"], "%Y-%m-%d") if isinstance(req["end_date"], str) else req["end_date"]
        for d in date_range(s_date, e_date):
            d_str = d.strftime("%Y-%m-%d")
            key = (req["department"], d_str)
            by_day.setdefault(key, []).append(req["request_id"])
    return by_day

def check_quota_reason(request_row, employee_row, requests_df) -> str | None:
    """
    Cek apakah request ini kalau (secara hipotetis) diapprove akan melebihi
    sisa quota pegawai tsb, dihitung dari total durasi SEMUA request approved
    milik pegawai yang sama.
    """
    emp_id = request_row["employee_id"]
    approved_for_emp = requests_df[
        (requests_df["employee_id"] == emp_id) & (requests_df["approved"] == 1)
    ]
    used_days = approved_for_emp["duration_days"].sum()
    remaining = employee_row["quota_days"] - used_days
    if request_row["duration_days"] > remaining:
        return (
            f"Quota cuti tidak mencukupi: sisa quota {remaining} hari, "
            f"request ini membutuhkan {request_row['duration_days']} hari."
        )
    return None

def check_staffing_reason(request_row, departments_df, approved_by_day: dict) -> str | None:
    """
    Cek tanggal mana dalam rentang request ini yang staffing dept-nya sudah
    penuh oleh request lain yang approved, lalu sebut siapa yang 'menang'
    slot itu (untuk transparansi).
    """
    dept = request_row["department"]
    dept_row = departments_df[departments_df["department"] == dept].iloc[0]
    max_on_leave = dept_row["total_staff"] - dept_row["min_staff"]

    s_date = datetime.strptime(request_row["start_date"], "%Y-%m-%d") if isinstance(request_row["start_date"], str) else request_row["start_date"]
    e_date = datetime.strptime(request_row["end_date"], "%Y-%m-%d") if isinstance(request_row["end_date"], str) else request_row["end_date"]

    blocking_dates = []
    for d in date_range(s_date, e_date):
        d_str = d.strftime("%Y-%m-%d")
        approved_ids = approved_by_day.get((dept, d_str), [])
        if len(approved_ids) >= max_on_leave:
            blocking_dates.append((d_str, approved_ids))

    if not blocking_dates:
        return None

    worst_date_str, winners = max(blocking_dates, key=lambda t: len(t[1]))
    return (
        f"Kapasitas cuti Dept {dept} penuh pada tanggal {worst_date_str} "
        f"(maksimum {max_on_leave} orang cuti bersamaan agar min staff {dept_row['min_staff']} terpenuhi). "
        f"Slot terisi oleh {len(winners)} request berprioritas lebih tinggi: "
        f"{', '.join(map(str, winners[:3]))}{'...' if len(winners) > 3 else ''}. "
        f"Total {len(blocking_dates)} hari dalam request ini melanggar batas staffing."
    )

def explain_all_rejections(requests_df: pd.DataFrame, employees_df: pd.DataFrame, departments_df: pd.DataFrame) -> pd.DataFrame:
    """
    Entry point utama explainability. Menambahkan kolom 'rejection_reason'
    ke requests_df untuk semua request dengan approved == 0.
    """
    approved_by_day = build_approved_leave_by_day(requests_df)
    reasons = {}

    rejected = requests_df[requests_df["approved"] == 0]
    for _, req in rejected.iterrows():
        emp_match = employees_df[employees_df["employee_id"] == req["employee_id"]]
        if emp_match.empty:
            continue
        emp_row = emp_match.iloc[0]

        # 1. Cek quota dulu
        reason = check_quota_reason(req, emp_row, requests_df)

        # 2. Kalau bukan quota, cek staffing
        if reason is None:
            reason = check_staffing_reason(req, departments_df, approved_by_day)

        # 3. Fallback
        if reason is None:
            reason = (
                "Tidak disetujui karena objective function ILP memprioritaskan "
                "request lain dengan kombinasi waiting_days & seniority lebih tinggi "
                "pada slot kapasitas departemen yang terbatas."
            )

        reasons[req["request_id"]] = reason

    requests_df["rejection_reason"] = requests_df["request_id"].map(reasons).fillna("-")
    return requests_df

def solve_leave_optimization(
    requests_df: pd.DataFrame,
    employees_df: pd.DataFrame,
    departments_df: pd.DataFrame,
    alpha: float = 1.0,
    beta: float = 1.5,
    custom_min_staff_pct: float = None
) -> dict:
    """
    Solves the ILP Leave Approval Optimization Problem using PuLP.
    
    Returns a dictionary containing:
    - 'requests_df': DataFrame with 'approved' (0/1), 'weight', 'rejection_reason'
    - 'solve_time_sec': Execution latency in seconds
    - 'objective_value': Total weighted objective value
    - 'status': Solver status string (e.g. 'Optimal')
    """
    start_time = time.time()
    
    req_df = requests_df.copy()
    emp_df = employees_df.copy()
    dept_df = departments_df.copy()
    
    if custom_min_staff_pct is not None:
        dept_df["min_staff_pct"] = custom_min_staff_pct
        dept_df["min_staff"] = (dept_df["total_staff"] * custom_min_staff_pct).apply(lambda x: int(round(x)))
        dept_df["max_on_leave"] = dept_df["total_staff"] - dept_df["min_staff"]
        
    # Calculate weight for each request: alpha * waiting_days + beta * seniority
    req_df["weight"] = alpha * req_df["waiting_days"] + beta * req_df["seniority"]
    
    # Initialize PuLP Problem
    prob = pulp.LpProblem("Leave_Approval_Optimization", pulp.LpMaximize)
    
    # Decision Variables x_i in {0, 1}
    x_vars = {}
    for idx, row in req_df.iterrows():
        r_id = row["request_id"]
        x_vars[r_id] = pulp.LpVariable(f"x_{r_id}", cat=pulp.LpBinary)
        
    # Objective Function: Maximize sum(weight_i * x_i)
    prob += pulp.lpSum([req_df.loc[req_df["request_id"] == r_id, "weight"].values[0] * x_vars[r_id] for r_id in x_vars]), "Total_Priority_Weight"
    
    # Constraint 1: Quota Constraint per Employee
    for _, emp in emp_df.iterrows():
        e_id = emp["employee_id"]
        quota = emp["quota_days"]
        emp_reqs = req_df[req_df["employee_id"] == e_id]
        if not emp_reqs.empty:
            prob += (
                pulp.lpSum([row["duration_days"] * x_vars[row["request_id"]] for _, row in emp_reqs.iterrows()]) <= quota,
                f"Quota_Emp_{e_id}"
            )
            
    # Constraint 2: Daily Staffing Constraint per Department
    # Collect all unique dates in request timeline
    all_dates = set()
    for _, row in req_df.iterrows():
        s_date = datetime.strptime(row["start_date"], "%Y-%m-%d") if isinstance(row["start_date"], str) else row["start_date"]
        e_date = datetime.strptime(row["end_date"], "%Y-%m-%d") if isinstance(row["end_date"], str) else row["end_date"]
        for d in date_range(s_date, e_date):
            all_dates.add(d.strftime("%Y-%m-%d"))
            
    for _, dept_row in dept_df.iterrows():
        dept = dept_row["department"]
        max_on_leave = dept_row["total_staff"] - dept_row["min_staff"]
        dept_reqs = req_df[req_df["department"] == dept]
        
        for d_str in all_dates:
            target_date = datetime.strptime(d_str, "%Y-%m-%d")
            active_req_ids = []
            for _, r_row in dept_reqs.iterrows():
                s_date = datetime.strptime(r_row["start_date"], "%Y-%m-%d") if isinstance(r_row["start_date"], str) else r_row["start_date"]
                e_date = datetime.strptime(r_row["end_date"], "%Y-%m-%d") if isinstance(r_row["end_date"], str) else r_row["end_date"]
                if s_date <= target_date <= e_date:
                    active_req_ids.append(r_row["request_id"])
                    
            if active_req_ids:
                prob += (
                    pulp.lpSum([x_vars[rid] for rid in active_req_ids]) <= max_on_leave,
                    f"Staffing_{dept}_{d_str}"
                )
                
    # Solve ILP model
    solver = pulp.PULP_CBC_CMD(msg=False)
    prob.solve(solver)
    
    solve_time = time.time() - start_time
    status_str = pulp.LpStatus[prob.status]
    obj_val = pulp.value(prob.objective) if prob.status == pulp.LpStatusOptimal else 0.0
    
    # Store decisions in DataFrame
    approved_map = {}
    for r_id, var in x_vars.items():
        approved_map[r_id] = 1 if (var.varValue is not None and var.varValue > 0.5) else 0
        
    req_df["approved"] = req_df["request_id"].map(approved_map)
    
    # Generate explainability reasons for rejected requests
    req_df = explain_all_rejections(req_df, emp_df, dept_df)
    
    return {
        "requests_df": req_df,
        "employees_df": emp_df,
        "departments_df": dept_df,
        "solve_time_sec": round(solve_time, 4),
        "objective_value": round(obj_val, 2) if obj_val else 0.0,
        "status": status_str
    }

def simulate_scenario(
    target_request_id: str,
    requests_df: pd.DataFrame,
    employees_df: pd.DataFrame,
    departments_df: pd.DataFrame,
    alpha: float = 1.0,
    beta: float = 1.5,
    custom_min_staff_pct: float = None
) -> dict:
    """
    Simulates forcing approval of a specific request ID (x_target = 1)
    and checks if it causes quota or staffing constraint violations or alters other approvals.
    """
    req_df = requests_df.copy()
    target_row = req_df[req_df["request_id"] == target_request_id]
    if target_row.empty:
        return {"feasible": False, "message": f"Request ID {target_request_id} tidak ditemukan."}
        
    req_row = target_row.iloc[0]
    emp_id = req_row["employee_id"]
    dept = req_row["department"]
    
    # 1. Run optimization with forced x_target = 1
    # We add a high fixed constraint x_target == 1
    req_df_copy = req_df.copy()
    
    # Solve standard first
    baseline = solve_leave_optimization(req_df, employees_df, departments_df, alpha, beta, custom_min_staff_pct)
    
    # Now solve scenario with forced x_target = 1
    start_time = time.time()
    dept_df = departments_df.copy()
    if custom_min_staff_pct is not None:
        dept_df["min_staff_pct"] = custom_min_staff_pct
        dept_df["min_staff"] = (dept_df["total_staff"] * custom_min_staff_pct).apply(lambda x: int(round(x)))
        dept_df["max_on_leave"] = dept_df["total_staff"] - dept_df["min_staff"]
        
    prob = pulp.LpProblem("Scenario_Simulation", pulp.LpMaximize)
    x_vars = {r_id: pulp.LpVariable(f"x_{r_id}", cat=pulp.LpBinary) for r_id in req_df_copy["request_id"]}
    
    # Force target request = 1
    prob += (x_vars[target_request_id] == 1, f"Force_Approve_{target_request_id}")
    
    # Objective Function
    req_df_copy["weight"] = alpha * req_df_copy["waiting_days"] + beta * req_df_copy["seniority"]
    prob += pulp.lpSum([req_df_copy.loc[req_df_copy["request_id"] == r_id, "weight"].values[0] * x_vars[r_id] for r_id in x_vars])
    
    # Quota constraints
    for _, emp in employees_df.iterrows():
        e_id = emp["employee_id"]
        quota = emp["quota_days"]
        emp_reqs = req_df_copy[req_df_copy["employee_id"] == e_id]
        if not emp_reqs.empty:
            prob += (pulp.lpSum([row["duration_days"] * x_vars[row["request_id"]] for _, row in emp_reqs.iterrows()]) <= quota)
            
    # Staffing constraints
    all_dates = set()
    for _, row in req_df_copy.iterrows():
        s_date = datetime.strptime(row["start_date"], "%Y-%m-%d") if isinstance(row["start_date"], str) else row["start_date"]
        e_date = datetime.strptime(row["end_date"], "%Y-%m-%d") if isinstance(row["end_date"], str) else row["end_date"]
        for d in date_range(s_date, e_date):
            all_dates.add(d.strftime("%Y-%m-%d"))
            
    for _, dept_row in dept_df.iterrows():
        d_name = dept_row["department"]
        max_on_leave = dept_row["total_staff"] - dept_row["min_staff"]
        dept_reqs = req_df_copy[req_df_copy["department"] == d_name]
        
        for d_str in all_dates:
            target_date = datetime.strptime(d_str, "%Y-%m-%d")
            active_req_ids = [r_row["request_id"] for _, r_row in dept_reqs.iterrows() 
                              if datetime.strptime(r_row["start_date"], "%Y-%m-%d") <= target_date <= datetime.strptime(r_row["end_date"], "%Y-%m-%d")]
            if active_req_ids:
                prob += (pulp.lpSum([x_vars[rid] for rid in active_req_ids]) <= max_on_leave)
                
    solver = pulp.PULP_CBC_CMD(msg=False)
    prob.solve(solver)
    
    if prob.status != pulp.LpStatusOptimal:
        # Infeasible: Forced approval strictly violates a constraint
        # Determine which constraint broke
        # Check quota
        emp_row = employees_df[employees_df["employee_id"] == emp_id].iloc[0]
        if req_row["duration_days"] > emp_row["quota_days"]:
            msg = f"❌ **TIDAK AMAN (Infeasible)**: Request {target_request_id} ({req_row['name']}) melebihi total quota cuti pegawai ({req_row['duration_days']} hari > {emp_row['quota_days']} hari)."
        else:
            msg = f"❌ **TIDAK AMAN (Infeasible)**: Menyetujui request {target_request_id} ({req_row['name']}) melanggar batas minimum staffing Departemen {dept} pada periode {req_row['start_date']} s/d {req_row['end_date']}."
        return {"feasible": False, "status": "Infeasible", "message": msg, "target_request": req_row.to_dict()}
    else:
        # Feasible scenario
        scen_approved_map = {r_id: (1 if var.varValue > 0.5 else 0) for r_id, var in x_vars.items()}
        req_df_copy["approved"] = req_df_copy["request_id"].map(scen_approved_map)
        
        # Compare baseline vs scenario approvals
        base_approved = set(baseline["requests_df"][baseline["requests_df"]["approved"] == 1]["request_id"])
        scen_approved = set(req_df_copy[req_df_copy["approved"] == 1]["request_id"])
        
        bumped_out = list(base_approved - scen_approved)
        
        if bumped_out:
            bumped_names = req_df[req_df["request_id"].isin(bumped_out)]["name"].tolist()
            msg = (
                f"⚠️ **AMAN DENGAN IMPACT**: Request {target_request_id} ({req_row['name']}) BISA disetujui, "
                f"namun menggeser (membatalkan) {len(bumped_out)} request lain yang sebelumnya disetujui: "
                f"{', '.join(bumped_names)}."
            )
        else:
            msg = f"✅ **SANGAT AMAN**: Request {target_request_id} ({req_row['name']}) dapat disetujui tanpa mengganggu staffing maupun request pegawai lain!"
            
        return {
            "feasible": True,
            "status": "Optimal",
            "message": msg,
            "bumped_requests": bumped_out,
            "target_request": req_row.to_dict()
        }
