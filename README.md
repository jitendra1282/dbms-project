


<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
</p>

<h1 align="center">🫀 Module 27 — Cardiac ICU Monitoring Database System</h1>

<p align="center">
  A specialized <strong>Clinical Decision Support System (CDSS)</strong> for real-time cardiac parameter tracking,<br>
  arrhythmia detection, and automated risk scoring in the Intensive Care Unit.
</p>

<p align="center">
  <strong>Live Demo:</strong> 👉 <a href="https://frontend-zxra8c5w4ip3f6k5gvjasp.streamlit.app/">https://frontend-zxra8c5w4ip3f6k5gvjasp.streamlit.app/</a>
</p>

---

## 📑 Table of Contents

- [About the Project](#-about-the-project)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Data Modeling — Why MongoDB?](#-data-modeling--why-mongodb)
- [Key Entities & Collections](#-key-entities--collections)
- [Clinical Scoring Engines](#-clinical-scoring-engines)
- [Arrhythmia Detection Engine](#-arrhythmia-detection-engine)
- [Advanced Features](#-advanced-features)
- [API Endpoints](#-api-endpoints)
- [Streamlit Dashboard](#-streamlit-dashboard)
- [Getting Started](#-getting-started)
- [How It Works — Under the Hood](#-how-it-works--under-the-hood)
- [Database Schema](#-database-schema)
- [Future Scope](#-future-scope)

---

## 🏥 About the Project

This is not a typical CRUD application. The **Cardiac ICU Monitoring Database System** acts as a Clinical Decision Support System (CDSS) — it doesn't just store data, it **interprets** it to help doctors catch heart attacks (STEMI) faster and assess cardiac risk in real time.

### What makes it different?

| Feature | Traditional DBMS Project | This Project |
|---------|--------------------------|--------------|
| Data Handling | Static storage & retrieval | Active interpretation & alerting |
| Risk Assessment | Manual calculation by doctors | Automated HEART, TIMI, GRACE scores |
| STEMI Detection | Doctor reads ECG manually | System auto-flags STEMI in milliseconds |
| Data Model | Rigid SQL tables | Flexible MongoDB documents with embedded scoring |
| Hemodynamics | Separate manual assessment | Real-time Stable / Unstable / Critical classification |

---

## 🏗 System Architecture

The system follows a clean **3-tier architecture** with full separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│                                                             │
│   Streamlit Dashboard (app.py)                              │
│   ├── Login / Signup (auth/)                                │
│   ├── Patient Dashboard (dashboards/patient_dashboard.py)   │
│   ├── Doctor Dashboard  (dashboards/doctor_dashboard.py)    │
│   ├── Admin Dashboard   (dashboards/admin_dashboard.py)     │
│   └── Cardiac ICU View  (modules/module_27/patient_view.py) │
│         ├── 🫀 Monitoring Dashboard                         │
│         ├── 📊 Scoring Calculator                           │
│         ├── 📈 Stability Analytics                          │
│         ├── 🔗 ER Diagram                                   │
│         ├── 📋 DB Schema                                    │
│         └── 🚨 Arrhythmia Alerts                            │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP (REST API)
┌──────────────────────▼──────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                      │
│                                                             │
│   FastAPI Backend (backend/main.py)                         │
│   └── Module 27 Router (modules/module_27/api.py)           │
│       ├── POST /api/v27/telemetry                           │
│       ├── GET  /api/v27/assessment/{patient_id}             │
│       ├── GET  /api/v27/timeseries/{patient_id}             │
│       ├── GET  /api/v27/arrhythmias/alerts                  │
│       └── GET  /api/v27/arrhythmias/patterns                │
│                                                             │
│   Service Layer (modules/module_27/services.py)             │
│   ├── Arrhythmia Detection Engine                           │
│   ├── HEART Score Calculator (0–10)                         │
│   ├── TIMI  Score Calculator (0–7)                          │
│   ├── GRACE Score Calculator (0–372)                        │
│   ├── Heart Failure Severity Indexer                        │
│   └── Hemodynamic Stability Assessor                        │
└──────────────────────┬──────────────────────────────────────┘
                       │ Motor (Async Driver)
┌──────────────────────▼──────────────────────────────────────┐
│                      DATA LAYER                              │
│                                                             │
│   MongoDB Atlas (MedicalCopilotDB)                          │
│   ├── cardiac_telemetry  — Vitals + embedded scoring        │
│   ├── arrhythmias        — Detection alerts                 │
│   └── hemodynamics       — Stability logs                   │
│                                                             │
│   Aggregation Pipelines (modules/module_27/database.py)     │
│   ├── 24h Time-Series: $match → $sort → $project            │
│   └── Pattern Recognition: $match → $group → $sort          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit | Interactive dashboard with forms, charts, alerts |
| **Backend** | FastAPI | Async REST API with Pydantic validation |
| **Database** | MongoDB Atlas | NoSQL document store for semi-structured medical data |
| **Driver** | Motor | Async MongoDB driver for Python |
| **Validation** | Pydantic | Strict input/output data models |
| **Visualization** | Pandas + Streamlit Charts | Time-series line charts for HR, BP, Troponin |
| **Deployment** | Streamlit Cloud | Live hosted frontend |

---

## 📁 Project Structure

```
DBMS-M8/
│
├── app.py                          # Streamlit entry point — role-based routing
├── requirements.txt                # Python dependencies
├── seeddb.py                       # Database seeder script
├── presentation.html               # 10-slide project presentation
├── pyrightconfig.json              # Type checker config
│
├── auth/                           # Authentication
│   ├── login.py                    # Login page (Patient / Doctor / Admin)
│   └── signup.py                   # Signup page
│
├── backend/                        # FastAPI backend
│   └── main.py                     # FastAPI app with router registration
│
├── modules/
│   └── module_27/                  # 🫀 CARDIAC ICU MODULE (Core)
│       ├── __init__.py
│       ├── api.py                  # FastAPI router — REST endpoints
│       ├── schemas.py              # Pydantic models (input/output validation)
│       ├── services.py             # Clinical logic (scoring, detection, assessment)
│       ├── database.py             # MongoDB CRUD + aggregation pipelines
│       └── patient_view.py         # Streamlit UI — 6 tabs
│
├── dashboards/                     # Role-based dashboards
│   ├── patient_dashboard.py        # Patient view with 9 module categories
│   ├── doctor_dashboard.py         # Doctor view
│   └── admin_dashboard.py          # Admin view
│
├── components/                     # Reusable UI components
│   ├── sidebar.py                  # Navigation sidebar
│   ├── charts.py                   # Chart components
│   ├── cards.py                    # Card components
│   └── tabs.py                     # Tab components
│
├── views/                          # View routing
│   ├── category_modules.py         # Category listing view
│   ├── module_detail.py            # Module detail view
│   └── patient_modules.py          # Patient module view
│
└── assets/                         # Static assets
```

---

## 🍃 Data Modeling — Why MongoDB?

Medical data is inherently **semi-structured**. One patient might have detailed ECG rhythm data while another has echocardiogram findings with different fields. MongoDB handles this naturally:

### Key Design Decisions

1. **Flexible Schema** — Different patients produce different clinical data fields. MongoDB's document model stores these without schema migrations.

2. **Embedded Documents** — `ScoringResult` (HEART / TIMI / GRACE scores) is **embedded inside** each `CardiacTelemetry` document. This is a classic NoSQL optimization:

   ```json
   {
     "patient_id": "PT-ICU-001",
     "ecg_rhythm": "ST-elevation",
     "heart_rate": 112,
     "scoring": {           // ← Embedded, not a separate collection
       "heart_score": 8,
       "timi_score": 5,
       "grace_score": 168,
       "risk_level": "High",
       "stemi_flag": true,
       "hf_severity": "Moderate"
     },
     "hemodynamic_status": "Unstable",
     "timestamp": "2026-03-17T16:30:00Z"
   }
   ```

   > When a doctor pulls up a patient's vitals, the risk scores come with them in a **single read** — no SQL JOINs needed.

3. **Aggregation Pipelines** — MongoDB's built-in aggregation framework handles time-series analysis and pattern recognition without external tools.

---

## 🗃 Key Entities & Collections

### Database: `MedicalCopilotDB`

| Collection | Purpose | Key Fields |
|-----------|---------|------------|
| `cardiac_telemetry` | Main telemetry entries with embedded scoring | `patient_id`, `ecg_rhythm`, `heart_rate`, `systolic_bp`, `diastolic_bp`, `troponin_level`, `bnp_level`, `creatinine`, `echo_findings`, `scoring{}`, `hemodynamic_status`, `stemi_alert`, `timestamp` |
| `arrhythmias` | Arrhythmia detection alerts | `patient_id`, `type`, `severity`, `detection_rule`, `timestamp` |
| `hemodynamics` | Hemodynamic stability logs | `patient_id`, `systolic_bp`, `diastolic_bp`, `heart_rate`, `status`, `timestamp` |

### Pydantic Data Models (`schemas.py`)

| Model | Role |
|-------|------|
| `CardiacParameterCreate` | Input validation — enforces HR 20–300 BPM, BP ranges, Killip 1–4, troponin ≥ 0 |
| `ArrhythmiaAlert` | Arrhythmia detection event with type, severity, and detection rule |
| `ScoringResult` | HEART (0–10), TIMI (0–7), GRACE (0–372), risk level, STEMI flag, HF severity |
| `MedicationResponse` | Tracks cardiac drug effects on vital parameters |
| `TelemetryResponse` | Full API response after recording a telemetry entry |
| `AssessmentResponse` | GET response for a patient's latest scoring assessment |

### Entity Relationship (1 : N)

```
  ┌──────────────┐
  │   Patient    │
  │──────────────│
  │ _id (PK)     │
  │ name, age    │
  │ risk_factors │
  └──────┬───────┘
         │ 1 : N
         ▼
  ┌────────────────────┐     ┌─────────────────┐     ┌──────────────────┐
  │ CardiacTelemetry   │────▶│  Arrhythmias    │     │  Hemodynamics    │
  │────────────────────│     │─────────────────│     │──────────────────│
  │ patient_id (FK)    │     │ patient_id (FK) │     │ patient_id (FK)  │
  │ ecg_rhythm, HR, BP │     │ type, severity  │     │ BP, HR, status   │
  │ troponin, BNP      │     │ detection_rule  │     │ timestamp        │
  │ scoring {} (embed) │     │ timestamp       │     └──────────────────┘
  │ hemodynamic_status │     └─────────────────┘
  │ stemi_alert        │
  │ timestamp          │
  └────────────────────┘
```

---

## 📊 Clinical Scoring Engines

Three gold-standard cardiac risk assessment algorithms are computed **automatically** on every telemetry entry.

### HEART Score (0–10)

Each component scored 0–2:

| Component | 0 | 1 | 2 |
|-----------|---|---|---|
| **H**istory | Slightly suspicious | Moderately suspicious | Highly suspicious (chest pain, crushing) |
| **E**CG | Normal | Non-specific changes | ST-deviation |
| **A**ge | < 45 | 45–64 | ≥ 65 |
| **R**isk factors | 0 | 1–2 | ≥ 3 |
| **T**roponin | Normal (< 0.04) | 1–3× normal | > 3× normal (> 0.12) |

**Interpretation:** 0–3 → Low Risk | 4–6 → Moderate | 7–10 → High Risk (admit, early invasive)

### TIMI Score (0–7)

Each criterion = 1 point:

1. Age ≥ 65
2. ≥ 3 CAD risk factors (Diabetes, Hypertension, Smoking, etc.)
3. Known CAD (stenosis ≥ 50%)
4. ASA use in past 7 days
5. ≥ 2 angina events in 24 hours
6. ST deviation on ECG
7. Elevated cardiac markers (troponin > 0.04 ng/mL)

**Interpretation:** 0–2 → Low | 3–4 → Moderate | 5–7 → High Risk

### GRACE Score (0–372)

Weighted risk factors with clinically approximate scoring:

| Factor | Weight Range |
|--------|-------------|
| Age (decades) | 0–91 points |
| Heart Rate | 0–46 points |
| Systolic BP (inverse) | 0–58 points |
| Creatinine | 1–28 points |
| Cardiac arrest | 0 or 39 points |
| ST deviation | 0 or 28 points |
| Elevated troponin | 0 or 14 points |
| Killip class (I–IV) | 0–59 points |

**Interpretation:** < 109 → Low | 109–140 → Moderate | > 140 → High Risk

### Combined Risk Stratification

```python
def determine_risk_level(heart_score, timi_score, grace_score):
    if heart_score >= 7 or timi_score >= 5 or grace_score >= 140:
        return "High"
    elif heart_score >= 4 or timi_score >= 3 or grace_score >= 109:
        return "Moderate"
    return "Low"
```

> If **any** of the three scores crosses its "High" threshold → overall risk = **HIGH**.

---

## 🚨 Arrhythmia Detection Engine

Rule-based detection runs on every incoming telemetry entry:

| Condition | Trigger Rule | Severity |
|-----------|-------------|----------|
| **STEMI** | ECG contains "ST-elevation" or "STEMI" | 🔴 Critical |
| **V-Tach** | ECG contains "Ventricular Tachycardia" | 🔴 Critical |
| **V-Fib** | ECG contains "Ventricular Fibrillation" | 🔴 Critical |
| **Atrial Fibrillation** | ECG contains "AFib" or "Atrial Fibrillation" | 🟠 High |
| **Severe Tachycardia** | Heart Rate > 150 BPM | 🟠 High |
| **Tachycardia** | Heart Rate > 100 BPM | 🟡 Medium |
| **Severe Bradycardia** | Heart Rate < 40 BPM | 🟠 High |
| **Bradycardia** | Heart Rate < 60 BPM | 🟡 Medium |
| **Critical Troponin** | Troponin > 0.4 ng/mL (10× normal) | 🔴 Critical |
| **Elevated Troponin** | Troponin > 0.04 ng/mL | 🟠 High |

---

## ⚡ Advanced Features

### STEMI Recognition (Critical)
```python
if "st-elevation" in ecg_lower or "stemi" in ecg_lower:
    alerts.append(ArrhythmiaAlert(
        type="STEMI",
        severity="Critical",
        detection_rule="ECG shows ST-elevation → Immediate catheterization required"
    ))
```
ST-Elevation Myocardial Infarction is the **#1 time-critical cardiac emergency**. The system auto-detects it by pattern-matching the ECG rhythm field.

### Heart Failure Severity Indexing

```python
def determine_hf_severity(bnp_level, killip_class):
    if killip_class >= 4 or bnp_level > 900:  return "Severe"
    if killip_class >= 3 or bnp_level > 400:  return "Moderate"
    if killip_class >= 2 or bnp_level > 100:  return "Mild"
    return "None"
```

### Hemodynamic Stability Assessment

Evaluates every reading as **Stable**, **Unstable**, or **Critical**:

| Status | Criteria |
|--------|----------|
| **Critical** | SBP < 70, HR < 40, or HR > 150 |
| **Unstable** | SBP < 90, SBP > 180, HR < 50, HR > 120, or DBP > 120 |
| **Stable** | All vitals within acceptable ranges |

### Time-Series Analysis (MongoDB Aggregation)

```javascript
// 24-hour cardiac monitoring pipeline
[
  { $match: { patient_id: "PT-ICU-001", timestamp: { $gte: cutoff_24h } } },
  { $sort:  { timestamp: 1 } },
  { $project: { _id: 0, timestamp: 1, heart_rate: 1, systolic_bp: 1, troponin_level: 1 } }
]
```

### Pattern Recognition

```javascript
// Recurring arrhythmia aggregation
[
  { $match: { severity: { $in: ["Medium", "High", "Critical"] } } },
  { $group: { _id: { type: "$type", severity: "$severity" },
              count: { $sum: 1 }, latest: { $max: "$timestamp" },
              rules: { $addToSet: "$detection_rule" } } },
  { $sort: { count: -1 } }
]
```

---

## 🔌 API Endpoints

Base URL: `http://localhost:8000/api/v27`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/telemetry` | Record cardiac vitals → runs arrhythmia detection + all 3 scoring engines + hemodynamic assessment → saves to MongoDB |
| `GET` | `/assessment/{patient_id}` | Retrieve latest HEART/TIMI/GRACE scores and hemodynamic status |
| `GET` | `/timeseries/{patient_id}` | 24-hour time-series data for HR, BP, ECG, and troponin charting |
| `GET` | `/arrhythmias/alerts` | All High and Critical severity arrhythmia alerts |
| `GET` | `/arrhythmias/patterns` | Aggregation-based pattern recognition for recurring arrhythmias |

---

## 🖥 Streamlit Dashboard

The frontend provides **6 interactive tabs** accessible via the Patient Dashboard → Category E → Module E3:

| Tab | Features |
|-----|----------|
| 🫀 **Monitoring Dashboard** | Full cardiac parameter input form, real-time STEMI alerts, scoring metrics, hemodynamic status, arrhythmia alert display |
| 📊 **Scoring Calculator** | Standalone offline HEART & TIMI score calculator with interactive sliders/checkboxes |
| 📈 **Stability Analytics** | 24h time-series line charts for Heart Rate, Blood Pressure, and Troponin trends |
| 🔗 **ER Diagram** | Entity relationship visualization for Module 27 |
| 📋 **DB Schema** | Collection details, key fields, and sample telemetry document |
| 🚨 **Arrhythmia Alerts** | Live feed of high-severity alerts + pattern analysis with bar charts |

### Role-Based Access

| Role | Dashboard | Capabilities |
|------|-----------|-------------|
| **Patient** | `patient_dashboard.py` | View own records, access 9 module categories (A–I), interact with Cardiac ICU |
| **Doctor** | `doctor_dashboard.py` | Manage patients, view clinical data |
| **Admin** | `admin_dashboard.py` | System administration |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- MongoDB Atlas account (or local MongoDB instance)
- pip

### Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd DBMS-M8

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate          # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

### Running the Application

#### Terminal 1 — Start the FastAPI Backend

```bash
uvicorn backend.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

#### Terminal 2 — Start the Streamlit Frontend

```bash
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`.

### Quick Test

1. Login as **Patient** (any email/password)
2. Navigate to **E – ICU & Real-Time Monitoring** → **E3 – Cardiac ICU Monitoring Database**
3. Fill the Monitoring Dashboard form with sample vitals
4. Click **🔬 Run Cardiac Assessment** to see real-time scoring and alerts

### Seed the Database (Optional)

```bash
python seeddb.py
```

---

## 🧠 How It Works — Under the Hood

### The Processing Pipeline

When a doctor submits cardiac vitals via the dashboard, the following pipeline executes:

```
Patient Vitals → POST /api/v27/telemetry
                    │
                    ▼
            ┌───────────────┐
            │  1. Validate  │  Pydantic: HR 20-300, BP ranges, Killip 1-4
            └───────┬───────┘
                    ▼
            ┌───────────────────────┐
            │  2. Detect            │  STEMI, AFib, V-Tach, V-Fib,
            │     Arrhythmias       │  Tachycardia, Bradycardia, Troponin
            └───────┬───────────────┘
                    ▼
            ┌───────────────────────┐
            │  3. Calculate Scores  │  HEART (0-10) + TIMI (0-7) + GRACE (0-372)
            └───────┬───────────────┘
                    ▼
            ┌───────────────────────┐
            │  4. Assess            │  Stable / Unstable / Critical
            │     Hemodynamics      │
            └───────┬───────────────┘
                    ▼
            ┌───────────────────────┐
            │  5. Determine         │  BNP + Killip → None/Mild/Moderate/Severe
            │     HF Severity       │
            └───────┬───────────────┘
                    ▼
            ┌───────────────────────┐
            │  6. Persist to        │  cardiac_telemetry + arrhythmias
            │     MongoDB           │  + hemodynamics collections
            └───────┬───────────────┘
                    ▼
            Full Assessment Response (JSON)
```

### Why Embedded Documents?

```
❌ SQL Approach (slow):
   SELECT * FROM telemetry t
   JOIN scores s ON t.id = s.telemetry_id
   JOIN alerts a ON t.id = a.telemetry_id
   → Multiple table reads + joins

✅ MongoDB Approach (fast):
   db.cardiac_telemetry.findOne({ patient_id: "PT-001" })
   → Vitals + scores + status in ONE read
```

---

## 🗃 Database Schema

### `cardiac_telemetry` — Sample Document

```json
{
  "_id": "ObjectId('6831...')",
  "patient_id": "PT-ICU-001",
  "ecg_rhythm": "ST-elevation",
  "heart_rate": 112,
  "systolic_bp": 85,
  "diastolic_bp": 55,
  "troponin_level": 0.45,
  "bnp_level": 520.0,
  "creatinine": 1.8,
  "echo_findings": "EF 30%, wall motion abnormality",
  "scoring": {
    "heart_score": 8,
    "timi_score": 5,
    "grace_score": 185,
    "risk_level": "High",
    "stemi_flag": true,
    "hf_severity": "Moderate"
  },
  "hemodynamic_status": "Unstable",
  "stemi_alert": true,
  "timestamp": "2026-03-17T16:30:00Z"
}
```

### `arrhythmias` — Sample Document

```json
{
  "_id": "ObjectId('6831...')",
  "patient_id": "PT-ICU-001",
  "type": "STEMI",
  "severity": "Critical",
  "detection_rule": "ECG shows ST-elevation → Immediate catheterization required",
  "timestamp": "2026-03-17T16:30:00Z"
}
```

### `hemodynamics` — Sample Document

```json
{
  "_id": "ObjectId('6831...')",
  "patient_id": "PT-ICU-001",
  "systolic_bp": 85,
  "diastolic_bp": 55,
  "heart_rate": 112,
  "status": "Unstable",
  "timestamp": "2026-03-17T16:30:00Z"
}
```

---

## 🔮 Future Scope

| Feature | Description |
|---------|-------------|
| ⌚ **Wearable IoT Integration** | Connect Apple Watch, Fitbit, and medical-grade wearables for continuous cardiac monitoring outside the ICU |
| 🤖 **AI-Driven Predictive Analytics** | Machine learning models for early cardiac event prediction — detect STEMI risk 30 minutes before onset |
| 📡 **HL7 FHIR Interoperability** | Standardized health data exchange with Hospital Information Systems and Electronic Health Records |
| 📱 **Mobile Alert System** | Push notifications to on-call cardiologists when critical arrhythmias are detected |
| 📊 **Enhanced Visualization** | 3D cardiac mapping and real-time ECG waveform rendering |
| 🔐 **HIPAA Compliance** | End-to-end encryption and audit logging for patient data privacy |

---

## 📦 Dependencies

```
streamlit                  # Frontend dashboard framework
streamlit-option-menu      # Sidebar navigation component
matplotlib                 # Charting library
fastapi                    # Async REST API framework
uvicorn[standard]          # ASGI server for FastAPI
pydantic                   # Data validation via Python type hints
motor                      # Async MongoDB driver for Python
requests                   # HTTP client (Streamlit → FastAPI calls)
pandas                     # Data manipulation for time-series
```

---

<p align="center">
  <strong>Module 27 — Cardiac ICU Monitoring Database System</strong><br>
  Built with ❤️ for DBMS coursework
</p>
>>>>>>> 0f1e6b7 (Updated Readme.md File)
