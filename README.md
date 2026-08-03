# 🗓️ Smart Leave Approval Optimizer

> **OrionHackathon 2026 Project Submission**  
> **Track**: Operations Research (ILP Optimization & Decision Intelligence)

---

## 📌 Problem Context & Executive Summary

Persetujuan cuti karyawan secara manual sering kali menimbulkan kemacetan operasional (*operational bottleneck*):
1. **Bentrokan Cuti (Overlapping Leave Peak)**: Beberapa karyawan di departemen yang sama mengajukan cuti pada tanggal yang bersamaan (seperti mid-month atau libur panjang), yang menyebabkan jumlah staf bertugas di bawah batas minimum operasional (*under-staffing*).
2. **Kurangnya Objektivitas**: Keputusan persetujuan tanpa acuan matematis yang jelas berisiko menimbulkan rasa ketidakadilan (favoritisme).
3. **Kurangnya Transparansi (Explainability)**: Cuti yang ditolak sering kali tidak disertai alasan konkret yang spesifik dan rasional.

**Smart Leave Approval Optimizer** menyelesaikan tantangan ini dengan memformulasikan persetujuan cuti sebagai **Integer Linear Programming (ILP)** menggunakan library `PuLP`. Sistem mengotomatisasi persetujuan secara instan (< 2 detik untuk 100 request), menjamin *minimum staffing* per departemen, serta menyajikan alasan penolakan yang rinci dan transparan melalui dashboard interaktif Streamlit.

---

## ⚙️ Formulasi Matematis Operations Research (ILP)

### 1. Decision Variable
$$\forall i \in \text{Requests}, \quad x_i \in \{0, 1\}$$
- $x_i = 1$: Request cuti ke-$i$ **disetujui (Approved)**.
- $x_i = 0$: Request cuti ke-$i$ **ditolak (Rejected)**.

### 2. Objective Function (Maximize Total Priority Score)
$$\max \sum_{i \in \text{Requests}} w_i \cdot x_i$$

Di mana bobot prioritas $w_i$ dihitung sebagai kombinasi linear dari lama menunggu keputusan dan tingkat senioritas karyawan:
$$w_i = \alpha \cdot \text{waiting\_days}_i + \beta \cdot \text{seniority}_i$$
- $\text{waiting\_days}_i$: Jumlah hari sejak request diajukan hingga tanggal evaluasi.
- $\text{seniority}_i$: Level senioritas karyawan (skala 1 - 10).
- $\alpha, \beta$: Parameter bobot fleksibel yang dapat disesuaikan pada dashboard.

---

### 3. Constraints (Batas Kendala)

#### A. Daily Departmental Staffing Constraint
Untuk setiap departemen $d$ dan setiap tanggal $t$ dalam periode perencanaan:
$$\sum_{i \in \text{Dept}(d), \, t \in [\text{start}_i, \text{end}_i]} x_i \le \text{total\_staff}_d - \text{min\_staff}_d$$
*Artinya: Jumlah karyawan di departemen $d$ yang diizinkan cuti bersamaan pada tanggal $t$ tidak boleh melebihi batas maksimum cuti ($\text{max\_on\_leave}_d = \text{total\_staff}_d - \text{min\_staff}_d$).*

#### B. Employee Quota Constraint
Untuk setiap karyawan $e$:
$$\sum_{i \in \text{Reqs}(e)} \text{duration\_days}_i \cdot x_i \le \text{sisa\_quota\_cuti}_e$$
*Artinya: Total durasi hari cuti yang disetujui untuk karyawan $e$ tidak boleh melebihi sisa jatah kuota cuti tahunan.*

---

## 🔍 Explainability Engine (Mengapa Heuristic Data-Driven?)

### Tantangan MIP vs Dual Values / Shadow Prices
Pada Linear Programming (LP) murni, *shadow price* (`constraint.pi`) digunakan untuk mengukur sensitivitas constraint. Namun, karena model ini menggunakan variabel **Integer/Binary ($x_i \in \{0, 1\}$)**, model ini termasuk **Mixed Integer Programming (MIP)**. Solver CBC default PuLP **tidak menghasilkan dual value (`.pi`) yang valid** untuk kendala integer.

### Pendekatan Solusi: Post-Solve Heuristic Attribution
Untuk memberikan penjelasan yang instan tanpa perlunya re-solve berulang kali, kami menerapkan algoritma atribusi data-driven:

1. **Pengecekan Kuota Individual**: Cek apakah total durasi request approved milik karyawan + request yang ditolak melebihi kuota karyawan.
   - *Output Alasan*: `Quota tidak cukup: sisa quota X hari, request ini butuh Y hari.`
2. **Pengecekan Bottleneck Staffing Departemen**: Jika kuota cukup, periksa tanggal-tanggal dalam rentang request di mana jumlah cuti disetujui telah mencapai kapasitas maksimum ($\text{max\_on\_leave}_d$).
   - *Output Alasan*: `Kapasitas cuti Dept Product penuh pada tanggal 2026-08-11 (maksimum 2 orang cuti bersamaan agar min staff 6 terpenuhi). Slot terisi oleh 2 request berprioritas lebih tinggi (REQ003, REQ037).`
3. **Priority Trade-off Attribution**: Jika kedua pengecekan di atas lolos, penolakan disebabkan trade-off prioritas global pada objective function.

---

### 🛠️ Project Structure & Tech Stack

### Tech Stack
- **Python 3.11+**
- **PuLP**: Solver Integer Linear Programming (ILP) CBC
- **Streamlit**: Web Dashboard & Interface (Warm Cream Theme)
- **Anthropic API (Opsional)**: AI Natural-Language Query Chatbot untuk menjawab pertanyaan *"Aman gak kalau saya approve cuti Andi 10-15 Agustus?"* (dengan fallback *Built-in Smart Reasoning Engine*).
- **Pandas & NumPy**: Data processing & Matrix calculations
- **Plotly Express**: Staffing capacity heatmaps & bar charts

### Struktur Folder
```
smart-leave-optimizer/
├── data/
│   ├── generate_dataset.py   # Script generator data sintetis karyawan, dept, & request
│   ├── employees.csv         # Data karyawan (40 orang)
│   ├── departments.csv       # Rules minimum staffing departemen
│   └── leave_requests.csv    # Data 75 request cuti pending
├── solver/
│   ├── optimizer.py          # Formulasi PuLP ILP, solver logic, & explainability engine
│   └── ai_assistant.py       # Engine AI Chatbot (Anthropic API / Smart Fallback)
├── app.py                    # Streamlit Dashboard UI, Warm Cream Theme, & AI Assistant
├── requirements.txt          # Library dependencies
└── README.md                 # Dokumentasi spesifikasi & formulasi OR
```

---

## 🚀 Panduan Instalasi & Cara Menjalankan

### 1. Clone & Setup Environment
```bash
git clone https://github.com/user/smart-leave-optimizer.git
cd smart-leave-optimizer
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. (Opsional) Generate Dataset Sintetis
```bash
python data/generate_dataset.py
```

### 4. Jalankan Dashboard Streamlit
```bash
python -m streamlit run app.py
```
Aplikasi akan terbuka otomatis di browser pada `http://localhost:8501`.
*(Menggunakan `python -m streamlit` memastikan aplikasi berjalan lancar meskipun executable streamlit belum ditambahkan ke PATH Windows).*

---

## 🧪 Acceptance Criteria Validation

| Criteria | Status | Hasil Pengujian |
| :--- | :---: | :--- |
| **Dataset Generator** | ✅ PASSED | `generate_dataset.py` berhasil menghasilkan 40 pegawai, 5 departemen, dan 75 request bentrok. |
| **Solver Speed (< 2s)** | ✅ PASSED | Solver PuLP menyelesaikan 75-100 request dalam **1.10 detik** (Status: *Optimal*). |
| **Decision Explainability** | ✅ PASSED | Setiap request `rejected` memiliki pesan alasan rinci (bottleneck tanggal & prioritas pemenang). |
| **Streamlit Dashboard** | ✅ PASSED | Dashboard interaktif dengan Heatmap Before vs After, Filter, & What-If Scenario Simulator. |
| **Dokumentasi OR** | ✅ PASSED | README menyajikan formulasi matematis, decision variables, constraint, dan alur explainability. |

---

## 🔮 Future Work (Rencana Pengembangan Lanjutan)

Berikut adalah fitur yang sengaja di-skip pada ruang lingkup MVP prototype ini dan diusulkan sebagai pengembangan masa depan:
1. **Integrasi Real-time HRIS / SAP**: Sinkronisasi data karyawan dan saldo cuti riil via REST API / Webhook.
2. **Dukungan Cuti Partial-Day / Half-Day**: Mengakomodasi variabel kontinu untuk cuti setengah hari (4 jam).
3. **Authentication & Multi-Role Access**: Login OAuth SSO untuk Peran Karyawan, Manajer Dept, dan HR Admin.
4. **Fairness Consecutive Rejection Limit**: Constraint tambahan $\sum_{t=1}^k (1 - x_{i,t}) \le \text{max\_consecutive\_rejects}$ untuk menjamin karyawan tidak ditolak secara berturut-turut.
