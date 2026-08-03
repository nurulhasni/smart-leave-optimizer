import json
import requests
import pandas as pd
from solver.optimizer import simulate_scenario
from lang import t

def ask_ai_assistant(
    user_prompt: str,
    api_key: str,
    requests_df: pd.DataFrame,
    employees_df: pd.DataFrame,
    departments_df: pd.DataFrame,
    provider: str = "Built-in Smart Solver",
    alpha: float = 1.0,
    beta: float = 1.5,
    custom_min_staff_pct: float = None,
    lang: str = "id"
) -> str:
    """
    AI Assistant engine that processes natural language queries about leave approvals.
    Supports Anthropic (Claude), OpenAI (GPT-4o), and Built-in Smart Solver.
    """
    user_prompt_lower = user_prompt.lower()
    
    # Search if a specific Request ID or Employee Name is mentioned
    matched_req = None
    for _, row in requests_df.iterrows():
        r_id = row["request_id"].lower()
        emp_name = row["name"].lower()
        first_name = emp_name.split()[0]
        
        if r_id in user_prompt_lower or emp_name in user_prompt_lower or (len(first_name) > 2 and first_name in user_prompt_lower):
            matched_req = row
            break
            
    # Context payload for LLM APIs
    if lang == "en":
        system_context = f"""
        You are an Operations Research AI Assistant for Smart Leave Approval Optimizer.
        ILP Data Summary:
        - Total Leave Requests: {len(requests_df)}
        - Total Approved: {(requests_df['approved'] == 1).sum()}
        - Total Rejected: {(requests_df['approved'] == 0).sum()}
        - Departments: {', '.join(departments_df['department'].unique())}
        
        {t('ai_system_lang_instruction', lang)}
        """
    else:
        system_context = f"""
        Kamu adalah AI Assistant Operations Research untuk Smart Leave Approval Optimizer.
        Ringkasan Data ILP:
        - Total Request Cuti: {len(requests_df)}
        - Total Disetujui (Approved): {(requests_df['approved'] == 1).sum()}
        - Total Ditolak (Rejected): {(requests_df['approved'] == 0).sum()}
        - Departemen: {', '.join(departments_df['department'].unique())}
        
        {t('ai_system_lang_instruction', lang)}
        """
    
    sim_res = None
    if matched_req is not None:
        sim_res = simulate_scenario(
            matched_req["request_id"], requests_df, employees_df, departments_df,
            alpha, beta, custom_min_staff_pct, lang=lang
        )
        if lang == "en":
            system_context += f"\n\nScenario simulation result for {matched_req['request_id']} ({matched_req['name']}):\n"
            system_context += f"- Current ILP status: {'Approved' if matched_req['approved']==1 else 'Rejected'}\n"
            system_context += f"- Feasible to approve: {sim_res['feasible']}\n"
            system_context += f"- Impact message: {sim_res['message']}\n"
            if sim_res.get('bumped_requests'):
                system_context += f"- Displaced requests: {', '.join(sim_res['bumped_requests'])}\n"
        else:
            system_context += f"\n\nHasil simulasi skenario untuk {matched_req['request_id']} ({matched_req['name']}):\n"
            system_context += f"- Status ILP saat ini: {'Approved' if matched_req['approved']==1 else 'Rejected'}\n"
            system_context += f"- Feasible untuk di-approve: {sim_res['feasible']}\n"
            system_context += f"- Pesan Dampak: {sim_res['message']}\n"
            if sim_res.get('bumped_requests'):
                system_context += f"- Request tergeser: {', '.join(sim_res['bumped_requests'])}\n"

    clean_key = api_key.strip() if api_key else ""
    api_warning = ""
    
    # 1. OpenAI API Handler
    if provider.startswith("OpenAI") and clean_key:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {clean_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_context},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.3
            }
            res = requests.post(url, headers=headers, json=payload, timeout=10)
            if res.status_code == 200:
                res_data = res.json()
                return f"🤖 **OpenAI Assistant (GPT-4o)**:\n\n" + res_data["choices"][0]["message"]["content"]
            else:
                try:
                    err_msg = res.json().get("error", {}).get("message", f"HTTP {res.status_code}")
                except Exception:
                    err_msg = f"HTTP {res.status_code}"
                api_warning = t("ai_error_openai", lang, err=err_msg) + "\n\n---\n\n"
        except Exception as e:
            api_warning = t("ai_exception_openai", lang, err=str(e)) + "\n\n---\n\n"

    # 2. Anthropic API Handler
    if provider.startswith("Anthropic") and clean_key:
        try:
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": clean_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            payload = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 500,
                "system": system_context,
                "messages": [{"role": "user", "content": user_prompt}]
            }
            res = requests.post(url, headers=headers, json=payload, timeout=10)
            if res.status_code == 200:
                res_data = res.json()
                return f"🤖 **Anthropic Assistant (Claude 3.5)**:\n\n" + res_data["content"][0]["text"]
            else:
                try:
                    err_msg = res.json().get("error", {}).get("message", f"HTTP {res.status_code}")
                except Exception:
                    err_msg = f"HTTP {res.status_code}"
                api_warning = t("ai_error_anthropic", lang, err=err_msg) + "\n\n---\n\n"
        except Exception as e:
            api_warning = t("ai_exception_anthropic", lang, err=str(e)) + "\n\n---\n\n"

    # 3. Built-in Smart Reasoning Engine (Local Fallback)
    if matched_req is not None and sim_res is not None:
        rid = matched_req["request_id"]
        is_approved = (matched_req["approved"] == 1)
        status_text = t("ai_status_approved", lang) if is_approved else t("ai_status_rejected", lang)
        
        reply = api_warning + t("ai_analysis_header", lang, rid=rid, name=matched_req['name'], dept=matched_req['department']) + "\n\n"
        reply += f"- {t('ai_period_label', lang)}: {matched_req['start_date']} s/d {matched_req['end_date']} ({matched_req['duration_days']} Hari/Days)\n"
        reply += f"- {t('ai_status_label', lang)}: {status_text.upper()}\n"
        
        if not is_approved:
            reply += f"- {t('ai_reason_label', lang)}: {matched_req.get('rejection_reason', '-')}\n\n"
            
        reply += f"**{t('ai_scenario_label', lang)}**:\n{sim_res['message']}"
        
        if sim_res.get("bumped_requests"):
            reply += f"\n\n" + t("ai_bumped_note", lang, bumped_names=', '.join(sim_res['bumped_requests']))
            
        return reply
        
    # General Query Handling
    if "kritis" in user_prompt_lower or "paling banyak" in user_prompt_lower or "rekap" in user_prompt_lower or "critical" in user_prompt_lower or "summary" in user_prompt_lower or "most" in user_prompt_lower:
        dept_rej = requests_df[requests_df["approved"] == 0].groupby("department").size()
        worst_dept = dept_rej.idxmax() if not dept_rej.empty else "N/A"
        return (
            api_warning +
            t("ai_recap_header", lang) + "\n\n" +
            t("ai_recap_body", lang, total=len(requests_df), worst_dept=worst_dept)
        )
        
    if lang == "en":
        examples = (
            f"1. *\"Is it safe to approve {requests_df.iloc[0]['name']}'s leave on {requests_df.iloc[0]['start_date']}?\"*\n"
            f"2. *\"Why was request {requests_df[requests_df['approved']==0].iloc[0]['request_id']} rejected?\"*\n"
            f"3. *\"Which department has the most leave requests?\"*"
        )
    else:
        examples = (
            f"1. *\"Aman gak kalau saya approve cuti {requests_df.iloc[0]['name']} tanggal {requests_df.iloc[0]['start_date']}?\"*\n"
            f"2. *\"Kenapa request {requests_df[requests_df['approved']==0].iloc[0]['request_id']} ditolak?\"*\n"
            f"3. *\"Departemen mana yang paling banyak cuti?\"*"
        )

    return (
        api_warning +
        t("ai_ready_header", lang) + "\n\n" +
        t("ai_ready_body", lang) + "\n" +
        examples
    )
