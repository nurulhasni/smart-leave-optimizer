import os
import random
import pandas as pd
from datetime import datetime, timedelta

def generate_all_datasets(output_dir: str = "data", num_employees: int = 40, num_requests: int = 75, seed: int = 42):
    random.seed(seed)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Departments Configuration
    dept_names = ["Engineering", "Product", "Finance", "Operations", "HR"]
    # We will distribute employees among departments
    emp_per_dept_target = {
        "Engineering": 12,
        "Product": 8,
        "Finance": 7,
        "Operations": 8,
        "HR": 5
    }
    
    # Indonesian First and Last names for synthetic dataset
    first_names = [
        "Andi", "Budi", "Citra", "Dewi", "Eko", "Fajar", "Gita", "Hendra", "Indah", "Joko",
        "Kiki", "Lestari", "Maya", "Nugroho", "Oktavia", "Putra", "Qori", "Rahmat", "Siti", "Taufik",
        "Utami", "Vina", "Wahyu", "Xena", "Yusuf", "Zahra", "Agus", "Bambang", "Deni", "Eka",
        "Farhan", "Gilang", "Hani", "Irfan", "Jessica", "Kurniawan", "Lukman", "Mega", "Nadia", "Rian"
    ]
    last_names = [
        "Wijaya", "Santoso", "Pratama", "Hidayat", "Saputra", "Wibowo", "Kusuma", "Laksana", "Suryani", "Gunawan",
        "Nugraha", "Permana", "Utomo", "Suharto", "Handoko", "Setiawan", "Mahendra", "Wahyudi", "Firmansyah", "Ramadhan"
    ]
    
    # Generate Employees
    employees = []
    emp_counter = 1
    for dept in dept_names:
        count = emp_per_dept_target[dept]
        for _ in range(count):
            emp_id = f"EMP{emp_counter:03d}"
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            quota = random.randint(10, 20)
            seniority = random.randint(1, 10)
            employees.append({
                "employee_id": emp_id,
                "name": name,
                "department": dept,
                "quota_days": quota,
                "seniority": seniority
            })
            emp_counter += 1
            
    emp_df = pd.DataFrame(employees)
    
    # Generate Department Specs
    dept_specs = []
    for dept in dept_names:
        dept_emps = emp_df[emp_df["department"] == dept]
        total_staff = len(dept_emps)
        min_staff_pct = 0.70  # default 70% min staffing required on duty
        min_staff = int(round(total_staff * min_staff_pct))
        dept_specs.append({
            "department": dept,
            "total_staff": total_staff,
            "min_staff_pct": min_staff_pct,
            "min_staff": min_staff,
            "max_on_leave": total_staff - min_staff
        })
        
    dept_df = pd.DataFrame(dept_specs)
    
    # 3. Generate Leave Requests
    # Planning window: 30 days starting from 2026-08-05
    start_timeline = datetime(2026, 8, 5)
    planning_cutoff = datetime(2026, 8, 1) # baseline for waiting days calculation
    
    reasons = [
        "Liburan Keluarga", "Acara Pernikahan Keluarga", "Sakit / Medical Checkup",
        "Mudik & Acara Daerah", "Cuti Tahunan Impulsif", "Wisuda Anggota Keluarga",
        "Renovasi Rumah", "Urusan Dokumen Pribadi"
    ]
    
    requests = []
    req_counter = 1
    
    # We create overlapping clusters to deliberately trigger ILP staffing constraints
    # Peak dates around Aug 10-15 (Mid-month spike) and Aug 24-28 (End-month spike)
    peak_clusters = [
        (datetime(2026, 8, 10), datetime(2026, 8, 15)),
        (datetime(2026, 8, 24), datetime(2026, 8, 28))
    ]
    
    for i in range(num_requests):
        req_id = f"REQ{req_counter:03d}"
        emp = emp_df.sample(1, random_state=seed + i).iloc[0]
        
        # 40% of requests are drawn from peak overlap clusters to test staffing limits
        if random.random() < 0.45:
            cluster_start, cluster_end = random.choice(peak_clusters)
            duration = random.randint(2, 5)
            # Pick a start date within the cluster
            max_offset = (cluster_end - cluster_start).days
            offset = random.randint(0, max(0, max_offset - 1))
            req_start = cluster_start + timedelta(days=offset)
        else:
            offset = random.randint(0, 25)
            duration = random.randint(1, 4)
            req_start = start_timeline + timedelta(days=offset)
            
        req_end = req_start + timedelta(days=duration - 1)
        
        # Submission date: 1 to 20 days before Aug 1st
        submit_offset = random.randint(1, 20)
        submit_date = planning_cutoff - timedelta(days=submit_offset)
        waiting_days = (planning_cutoff - submit_date).days
        
        requests.append({
            "request_id": req_id,
            "employee_id": emp["employee_id"],
            "name": emp["name"],
            "department": emp["department"],
            "start_date": req_start.strftime("%Y-%m-%d"),
            "end_date": req_end.strftime("%Y-%m-%d"),
            "duration_days": duration,
            "submit_date": submit_date.strftime("%Y-%m-%d"),
            "waiting_days": waiting_days,
            "seniority": emp["seniority"],
            "reason": random.choice(reasons)
        })
        req_counter += 1
        
    req_df = pd.DataFrame(requests)
    
    # Save CSVs
    emp_path = os.path.join(output_dir, "employees.csv")
    dept_path = os.path.join(output_dir, "departments.csv")
    req_path = os.path.join(output_dir, "leave_requests.csv")
    
    emp_df.to_csv(emp_path, index=False)
    dept_df.to_csv(dept_path, index=False)
    req_df.to_csv(req_path, index=False)
    
    print(f"Dataset successfully generated in '{output_dir}/':")
    print(f" - Employees: {len(emp_df)} ({emp_path})")
    print(f" - Departments: {len(dept_df)} ({dept_path})")
    print(f" - Leave Requests: {len(req_df)} ({req_path})")
    
    return emp_df, dept_df, req_df

if __name__ == "__main__":
    generate_all_datasets()
