# 🗓️ Smart Leave Approval Optimizer

> **Track**: Operations Research (ILP Optimization & Decision Intelligence)

**🌐 Languages:** [🇬🇧 English](#-english) | [🇮🇩 Bahasa Indonesia](#-bahasa-indonesia)

---

<a name="english"></a>
## 🇬🇧 English

### 📌 Problem Context & Executive Summary

Manual employee leave approval often creates operational bottlenecks:
1. **Overlapping Leave Peaks**: Multiple employees in the same department request leave on the same dates (e.g. mid-month or long holidays), pushing on-duty staff below the minimum operational threshold (under-staffing).
2. **Lack of Objectivity**: Approval decisions made without a clear mathematical basis risk perceived unfairness or favoritism.
3. **Lack of Explainability**: Rejected requests are often given no concrete, rational reason.

**Smart Leave Approval Optimizer** solves this by formulating leave approval as an **Integer Linear Programming (ILP)** problem using the `PuLP` library. The system automates approvals instantly (< 2 seconds for 100 requests), guarantees minimum staffing per department, and presents detailed, transparent rejection reasons through an interactive Streamlit dashboard.

---

### ✨ Key Features

- **ILP-based automated decision engine** (PuLP / CBC solver)
- **Explainability engine** — every rejection comes with a concrete, data-driven reason (not a black box)
- **"What-If" Scenario Simulator** — test forcing a specific request to be approved and instantly see the trade-off impact
- **AI Chatbot (optional)** — natural-language query support via OpenAI or Anthropic API, with a rule-based local fallback when no API key is provided
- **Bilingual UI (🇮🇩/🇬🇧)** — full interface and dynamic explanation messages switch language via a sidebar toggle, powered by a centralized `lang.py` translation module

---

### ⚙️ Operations Research Mathematical Formulation (ILP)

#### 1. Decision Variable
$$\forall i \in \text{Requests}, \quad x_i \in \{0, 1\}$$
- $x_i = 1$: Leave request $i$ is **Approved**.
- $x_i = 0$: Leave request $i$ is **Rejected**.

#### 2. Objective Function (Maximize Total Priority Score)
$$\max \sum_{i \in \text{Requests}} w_i \cdot x_i$$

Where the priority weight $w_i$ is a linear combination of how long the request has been waiting and the employee's seniority level:
$$w_i = \alpha \cdot \text{waiting\_days}_i + \beta \cdot \text{seniority}_i$$
- $\text{waiting\_days}_i$: Number of days since the request was submitted, up to the evaluation date.
- $\text{seniority}_i$: Employee seniority level (scale 1–10).
- $\alpha, \beta$: Adjustable weight parameters, tunable live from the dashboard.

---

#### 3. Constraints

**A. Daily Departmental Staffing Constraint**
For every department $d$ and every date $t$ in the planning horizon:
$$\sum_{i \in \text{Dept}(d), \, t \in [\text{start}_i, \text{end}_i]} x_i \le \text{total\_staff}_d - \text{min\_staff}_d$$
*Meaning: the number of employees in department $d$ allowed to be on leave simultaneously on date $t$ cannot exceed the maximum leave capacity ($\text{max\_on\_leave}_d = \text{total\_staff}_d - \text{min\_staff}_d$).*

**B. Employee Quota Constraint**
For every employee $e$:
$$\sum_{i \in \text{Reqs}(e)} \text{duration\_days}_i \cdot x_i \le \text{remaining\_quota}_e$$
*Meaning: the total approved leave duration for employee $e$ cannot exceed their remaining annual leave quota.*

---

### 🔍 Explainability Engine (Why a Data-Driven Heuristic?)

**The MIP vs. Dual Values / Shadow Prices Challenge**
In pure Linear Programming (LP), shadow prices (`constraint.pi`) are used to measure constraint sensitivity. However, because this model uses **Integer/Binary variables** ($x_i \in \{0, 1\}$), it is a **Mixed Integer Programming (MIP)** problem. PuLP's default CBC solver **does not produce valid dual values** for integer constraints.

**Solution Approach: Post-Solve Heuristic Attribution**
To provide instant explanations without repeated re-solving, we implemented a data-driven attribution algorithm:

1. **Individual Quota Check**: Check whether the employee's total approved leave duration plus this rejected request would exceed their quota.
   - *Example reason*: `Insufficient leave quota: X days remaining, this request needs Y days.`
2. **Departmental Staffing Bottleneck Check**: If quota is sufficient, check which dates within the request's range have already hit the department's maximum leave capacity ($\text{max\_on\_leave}_d$).
   - *Example reason*: `Dept Product leave capacity is full on 2026-08-11 (max 2 people on leave simultaneously to keep min staff 6). Slot taken by 2 higher-priority requests (REQ003, REQ037).`
3. **Priority Trade-off Attribution**: If both checks pass, the rejection is attributed to a global priority trade-off in the objective function.

---

### 🛠️ Project Structure & Tech Stack

**Tech Stack**
- **Python 3.11+**
- **PuLP**: Integer Linear Programming (ILP) solver, CBC backend
- **Streamlit**: Web dashboard & interface
- **OpenAI / Anthropic API (optional)**: Natural-language chatbot for questions like *"Is it safe to approve Andi's leave Aug 10–15?"* (with a Built-in Smart Reasoning Engine fallback)
- **Pandas & NumPy**: Data processing & matrix calculations
- **Plotly Express**: Staffing capacity heatmaps & bar charts

**Folder Structure**
```
smart-leave-optimizer/
├── data/
│   ├── generate_dataset.py   # Synthetic data generator (employees, depts, requests)
│   ├── employees.csv         # Employee data (40 people)
│   ├── departments.csv       # Department minimum staffing rules
│   └── leave_requests.csv    # 75 pending leave requests
├── solver/
│   ├── optimizer.py          # PuLP ILP formulation, solver logic & explainability engine
│   └── ai_assistant.py       # AI chatbot engine (OpenAI/Anthropic API / smart fallback)
├── lang.py                   # Centralized ID/EN translation dictionary + t() helper
├── app.py                    # Streamlit dashboard UI & AI Assistant
├── requirements.txt          # Library dependencies
└── README.md                 # This documentation
```

---

### 🚀 Installation & Running Guide

**1. Clone & Setup Environment**
```bash
git clone https://github.com/nurulhasni/smart-leave-optimizer.git
cd smart-leave-optimizer
```

**2. Install Dependencies**
```bash
pip install -r requirements.txt
```

**3. (Optional) Regenerate Synthetic Dataset**
```bash
python data/generate_dataset.py
```

**4. Run the Streamlit Dashboard**
```bash
python -m streamlit run app.py
```
The app opens automatically in your browser at `http://localhost:8501`.
*(Using `python -m streamlit` ensures it runs smoothly even if the streamlit executable isn't on Windows PATH.)*

---

### 🧪 Acceptance Criteria Validation

| Criteria | Status | Test Result |
| :--- | :---: | :--- |
| **Dataset Generator** | ✅ PASSED | `generate_dataset.py` successfully produces 40 employees, 5 departments, and 75 overlapping requests. |
| **Solver Speed (< 2s)** | ✅ PASSED | PuLP solver resolves 75–100 requests in **1.10 seconds** (Status: *Optimal*). |
| **Decision Explainability** | ✅ PASSED | Every rejected request includes a detailed reason (date bottleneck & winning priority). |
| **Streamlit Dashboard** | ✅ PASSED | Interactive dashboard with Before/After heatmap, filters, and What-If Scenario Simulator. |
| **Bilingual Support** | ✅ PASSED | UI and all dynamic explanation/chatbot messages switch fully between Indonesian and English. |
| **OR Documentation** | ✅ PASSED | README presents the mathematical formulation, decision variables, constraints, and explainability flow. |

---

### 🔮 Future Work

Features intentionally left out of this MVP prototype's scope, proposed for future development:
1. **Real-time HRIS / SAP Integration**: Sync real employee data and leave balances via REST API / Webhook.
2. **Partial-Day / Half-Day Leave Support**: Accommodate continuous variables for half-day (4-hour) leave.
3. **Authentication & Multi-Role Access**: OAuth SSO login for Employee, Department Manager, and HR Admin roles.
4. **Fairness Consecutive Rejection Limit**: Additional constraint $\sum_{t=1}^k (1 - x_{i,t}) \le \text{max\_consecutive\_rejects}$ to ensure no employee is rejected too many times in a row.

---
---

<a name="bahasa-indonesia"></a>
## 🇮🇩 Bahasa Indonesia

### 📌 Problem Context & Executive Summary

Persetujuan cuti karyawan secara manual sering kali menimbulkan kemacetan operasional (*operational bottleneck*):
1. **Bentrokan Cuti (Overlapping Leave Peak)**: Beberapa karyawan di departemen yang sama mengajukan cuti pada tanggal yang bersamaan (seperti mid-month atau libur panjang), yang menyebabkan jumlah staf bertugas di bawah batas minimum operasional (*under-staffing*).
2. **Kurangnya Objektivitas**: Keputusan persetujuan tanpa acuan matematis yang jelas berisiko menimbulkan rasa ketidakadilan (favoritisme).
3. **Kurangnya Transparansi (Explainability)**: Cuti yang ditolak sering kali tidak disertai alasan konkret yang spesifik dan rasional.

**Smart Leave Approval Optimizer** menyelesaikan tantangan ini dengan memformulasikan persetujuan cuti sebagai **Integer Linear Programming (ILP)** menggunakan library `PuLP`. Sistem mengotomatisasi persetujuan secara instan (< 2 detik untuk 100 request), menjamin *minimum staffing* per departemen, serta menyajikan alasan penolakan yang rinci dan transparan melalui dashboard interaktif Streamlit.

---

### ✨ Fitur Utama

- **Mesin keputusan otomatis berbasis ILP** (PuLP / CBC solver)
- **Explainability engine** — setiap penolakan disertai alasan konkret berbasis data (bukan black box)
- **Scenario Simulator "What-If"** — uji paksa-approve satu request tertentu dan langsung lihat dampak trade-off-nya
- **AI Chatbot (opsional)** — dukungan pertanyaan natural language via OpenAI atau Anthropic API, dengan fallback rule-based lokal kalau tidak ada API key
- **UI Bilingual (🇮🇩/🇬🇧)** — seluruh antarmuka dan pesan penjelasan dinamis berganti bahasa lewat toggle di sidebar, didukung modul translasi terpusat `lang.py`

---

### ⚙️ Formulasi Matematis Operations Research (ILP)

#### 1. Decision Variable
$$\forall i \in \text{Requests}, \quad x_i \in \{0, 1\}$$
- $x_i = 1$: Request cuti ke-$i$ **disetujui (Approved)**.
- $x_i = 0$: Request cuti ke-$i$ **ditolak (Rejected)**.

#### 2. Objective Function (Maximize Total Priority Score)
$$\max \sum_{i \in \text{Requests}} w_i \cdot x_i$$

Di mana bobot prioritas $w_i$ dihitung sebagai kombinasi linear dari lama menunggu keputusan dan tingkat senioritas karyawan:
$$w_i = \alpha \cdot \text{waiting\_days}_i + \beta \cdot \text{seniority}_i$$
- $\text{waiting\_days}_i$: Jumlah hari sejak request diajukan hingga tanggal evaluasi.
- $\text{seniority}_i$: Level senioritas karyawan (skala 1–10).
- $\alpha, \beta$: Parameter bobot fleksibel yang dapat disesuaikan pada dashboard.

---

#### 3. Constraints (Batas Kendala)

**A. Daily Departmental Staffing Constraint**
Untuk setiap departemen $d$ dan setiap tanggal $t$ dalam periode perencanaan:
$$\sum_{i \in \text{Dept}(d), \, t \in [\text{start}_i, \text{end}_i]} x_i \le \text{total\_staff}_d - \text{min\_staff}_d$$
*Artinya: Jumlah karyawan di departemen $d$ yang diizinkan cuti bersamaan pada tanggal $t$ tidak boleh melebihi batas maksimum cuti ($\text{max\_on\_leave}_d = \text{total\_staff}_d - \text{min\_staff}_d$).*

**B. Employee Quota Constraint**
Untuk setiap karyawan $e$:
$$\sum_{i \in \text{Reqs}(e)} \text{duration\_days}_i \cdot x_i \le \text{sisa\_quota\_cuti}_e$$
*Artinya: Total durasi hari cuti yang disetujui untuk karyawan $e$ tidak boleh melebihi sisa jatah kuota cuti tahunan.*

---

### 🔍 Explainability Engine (Mengapa Heuristic Data-Driven?)

**Tantangan MIP vs Dual Values / Shadow Prices**
Pada Linear Programming (LP) murni, *shadow price* (`constraint.pi`) digunakan untuk mengukur sensitivitas constraint. Namun, karena model ini menggunakan variabel **Integer/Binary** ($x_i \in \{0, 1\}$), model ini termasuk **Mixed Integer Programming (MIP)**. Solver CBC default PuLP **tidak menghasilkan dual value (`.pi`) yang valid** untuk kendala integer.

**Pendekatan Solusi: Post-Solve Heuristic Attribution**
Untuk memberikan penjelasan yang instan tanpa perlunya re-solve berulang kali, kami menerapkan algoritma atribusi data-driven:

1. **Pengecekan Kuota Individual**: Cek apakah total durasi request approved milik karyawan + request yang ditolak melebihi kuota karyawan.
   - *Output Alasan*: `Quota tidak cukup: sisa quota X hari, request ini butuh Y hari.`
2. **Pengecekan Bottleneck Staffing Departemen**: Jika kuota cukup, periksa tanggal-tanggal dalam rentang request di mana jumlah cuti disetujui telah mencapai kapasitas maksimum ($\text{max\_on\_leave}_d$).
   - *Output Alasan*: `Kapasitas cuti Dept Product penuh pada tanggal 2026-08-11 (maksimum 2 orang cuti bersamaan agar min staff 6 terpenuhi). Slot terisi oleh 2 request berprioritas lebih tinggi (REQ003, REQ037).`
3. **Priority Trade-off Attribution**: Jika kedua pengecekan di atas lolos, penolakan disebabkan trade-off prioritas global pada objective function.

---

### 🛠️ Project Structure & Tech Stack

**Tech Stack**
- **Python 3.11+**
- **PuLP**: Solver Integer Linear Programming (ILP) CBC
- **Streamlit**: Web Dashboard & Interface
- **OpenAI / Anthropic API (Opsional)**: AI Natural-Language Query Chatbot untuk menjawab pertanyaan *"Aman gak kalau saya approve cuti Andi 10-15 Agustus?"* (dengan fallback *Built-in Smart Reasoning Engine*)
- **Pandas & NumPy**: Data processing & matrix calculations
- **Plotly Express**: Staffing capacity heatmaps & bar charts

**Struktur Folder**
```
smart-leave-optimizer/
├── data/
│   ├── generate_dataset.py   # Script generator data sintetis karyawan, dept, & request
│   ├── employees.csv         # Data karyawan (40 orang)
│   ├── departments.csv       # Rules minimum staffing departemen
│   └── leave_requests.csv    # Data 75 request cuti pending
├── solver/
│   ├── optimizer.py          # Formulasi PuLP ILP, solver logic, & explainability engine
│   └── ai_assistant.py       # Engine AI Chatbot (OpenAI/Anthropic API / Smart Fallback)
├── lang.py                   # Dictionary translasi ID/EN terpusat + helper t()
├── app.py                    # Streamlit Dashboard UI & AI Assistant
├── requirements.txt          # Library dependencies
└── README.md                 # Dokumentasi ini
```

---

### 🚀 Panduan Instalasi & Cara Menjalankan

**1. Clone & Setup Environment**
```bash
git clone https://github.com/nurulhasni/smart-leave-optimizer.git
cd smart-leave-optimizer
```

**2. Install Dependencies**
```bash
pip install -r requirements.txt
```

**3. (Opsional) Generate Dataset Sintetis**
```bash
python data/generate_dataset.py
```

**4. Jalankan Dashboard Streamlit**
```bash
python -m streamlit run app.py
```
Aplikasi akan terbuka otomatis di browser pada `http://localhost:8501`.
*(Menggunakan `python -m streamlit` memastikan aplikasi berjalan lancar meskipun executable streamlit belum ditambahkan ke PATH Windows.)*

---

### 🧪 Acceptance Criteria Validation

| Criteria | Status | Hasil Pengujian |
| :--- | :---: | :--- |
| **Dataset Generator** | ✅ PASSED | `generate_dataset.py` berhasil menghasilkan 40 pegawai, 5 departemen, dan 75 request bentrok. |
| **Solver Speed (< 2s)** | ✅ PASSED | Solver PuLP menyelesaikan 75–100 request dalam **1.10 detik** (Status: *Optimal*). |
| **Decision Explainability** | ✅ PASSED | Setiap request `rejected` memiliki pesan alasan rinci (bottleneck tanggal & prioritas pemenang). |
| **Streamlit Dashboard** | ✅ PASSED | Dashboard interaktif dengan Heatmap Before vs After, Filter, & What-If Scenario Simulator. |
| **Dukungan Bilingual** | ✅ PASSED | UI dan seluruh pesan penjelasan/chatbot dinamis berganti penuh antara Indonesia dan Inggris. |
| **Dokumentasi OR** | ✅ PASSED | README menyajikan formulasi matematis, decision variables, constraint, dan alur explainability. |

---

### 🔮 Future Work (Rencana Pengembangan Lanjutan)

Berikut adalah fitur yang sengaja di-skip pada ruang lingkup MVP prototype ini dan diusulkan sebagai pengembangan masa depan:
1. **Integrasi Real-time HRIS / SAP**: Sinkronisasi data karyawan dan saldo cuti riil via REST API / Webhook.
2. **Dukungan Cuti Partial-Day / Half-Day**: Mengakomodasi variabel kontinu untuk cuti setengah hari (4 jam).
3. **Authentication & Multi-Role Access**: Login OAuth SSO untuk Peran Karyawan, Manajer Dept, dan HR Admin.
4. **Fairness Consecutive Rejection Limit**: Constraint tambahan $\sum_{t=1}^k (1 - x_{i,t}) \le \text{max\_consecutive\_rejects}$ untuk menjamin karyawan tidak ditolak secara berturut-turut.