# modules/module_27/patient_view.py
"""
Streamlit UI for Module 27 — Cardiac ICU Monitoring Database.
6 tabs: Monitoring Dashboard, Scoring Calculator, Stability Analytics,
        ER Diagram, DB Schema, Arrhythmia Alerts.
"""
import streamlit as st
import pandas as pd
import requests
from datetime import datetime

API_BASE = "http://localhost:8000/api/v27"

SEVERITY_ICONS = {
    "Critical": "🔴",
    "High":     "🟠",
    "Medium":   "🟡",
    "Low":      "🟢",
}

ECG_OPTIONS = [
    "Normal Sinus Rhythm",
    "ST-elevation",
    "ST-depression",
    "Atrial Fibrillation",
    "Ventricular Tachycardia",
    "Ventricular Fibrillation",
    "Sinus Tachycardia",
    "Sinus Bradycardia",
    "Right Bundle Branch Block",
    "Left Bundle Branch Block",
]

RISK_FACTOR_OPTIONS = [
    "Diabetes",
    "Hypertension",
    "Smoking",
    "Hyperlipidemia",
    "Obesity",
    "Family History of CAD",
    "Sedentary Lifestyle",
    "Prior MI",
    "Prior PCI/CABG",
]


# ═══════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

def render_patient_module():
    tabs = st.tabs([
        "🫀 Monitoring Dashboard",
        "📊 Scoring Calculator",
        "📈 Stability Analytics",
        "🔗 ER Diagram",
        "📋 DB Schema",
        "🚨 Arrhythmia Alerts",
    ])
    st.divider()
    with tabs[0]: _monitoring_tab()
    with tabs[1]: _scoring_tab()
    with tabs[2]: _stability_tab()
    with tabs[3]: _er_tab()
    with tabs[4]: _schema_tab()
    with tabs[5]: _alerts_tab()
    st.divider()


# ═══════════════════════════════════════════════════════════════════════════
#  TAB 0 — MONITORING DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════

def _monitoring_tab():
    st.header("🫀 Cardiac Telemetry Input")
    st.caption("Record new cardiac parameters — arrhythmia detection, scoring, and stability analysis run automatically.")

    with st.form("cardiac_form"):
        st.subheader("Patient & Vitals")
        c1, c2, c3 = st.columns(3)
        with c1:
            patient_id = st.text_input("Patient ID", placeholder="PT-ICU-001")
            age = st.number_input("Age", 0, 130, 55)
        with c2:
            ecg_rhythm = st.selectbox("ECG Rhythm", ECG_OPTIONS)
            heart_rate = st.number_input("Heart Rate (BPM)", 20, 300, 76)
        with c3:
            systolic_bp = st.number_input("Systolic BP (mmHg)", 40, 300, 120)
            diastolic_bp = st.number_input("Diastolic BP (mmHg)", 20, 200, 80)

        st.subheader("Cardiac Enzymes & Labs")
        e1, e2, e3 = st.columns(3)
        with e1:
            troponin = st.number_input("Troponin (ng/mL)", 0.0, 50.0, 0.02, step=0.01, format="%.3f")
        with e2:
            bnp = st.number_input("BNP (pg/mL)", 0.0, 5000.0, 45.0, step=1.0)
        with e3:
            creatinine = st.number_input("Creatinine (mg/dL)", 0.0, 20.0, 1.0, step=0.1)

        st.subheader("Risk Profile")
        r1, r2 = st.columns(2)
        with r1:
            risk_factors = st.multiselect("Risk Factors", RISK_FACTOR_OPTIONS)
            killip_class = st.selectbox("Killip Class", [1, 2, 3, 4])
        with r2:
            aspirin_use = st.checkbox("ASA use in past 7 days")
            known_stenosis = st.checkbox("Known coronary stenosis ≥ 50%")
            cardiac_arrest = st.checkbox("Cardiac arrest on admission")
            angina_24h = st.number_input("Angina episodes (24h)", 0, 50, 0)

        echo = st.text_area("Echo Findings (optional)", placeholder="e.g., EF 35%, wall motion abnormality")
        history = st.text_area("Clinical History Notes", placeholder="e.g., crushing chest pain radiating to left arm")

        submitted = st.form_submit_button("🔬 Run Cardiac Assessment", type="primary", use_container_width=True)

    if submitted:
        if not patient_id:
            st.error("Patient ID is required.")
            return

        payload = {
            "patient_id": patient_id,
            "ecg_rhythm": ecg_rhythm,
            "heart_rate": heart_rate,
            "systolic_bp": systolic_bp,
            "diastolic_bp": diastolic_bp,
            "troponin_level": troponin,
            "bnp_level": bnp,
            "creatinine": creatinine,
            "echo_findings": echo or None,
            "age": age,
            "risk_factors": risk_factors,
            "aspirin_use": aspirin_use,
            "known_stenosis": known_stenosis,
            "angina_episodes_24h": angina_24h,
            "cardiac_arrest_on_admission": cardiac_arrest,
            "killip_class": killip_class,
            "history_notes": history or None,
        }

        try:
            with st.spinner("Running arrhythmia detection & scoring engines..."):
                resp = requests.post(f"{API_BASE}/telemetry", json=payload)
                resp.raise_for_status()
                data = resp.json()

            # ── STEMI Alert (top priority) ────────────────────────────
            if data.get("stemi_alert"):
                st.error("🚨 **CRITICAL: STEMI DETECTED** 🚨\n\n"
                         "ST-elevation identified on ECG. **Immediate cardiac catheterization recommended.**\n\n"
                         "Activate CODE STEMI protocol.")

            # ── Hemodynamic Status ────────────────────────────────────
            hemo = data.get("hemodynamic_status", "N/A")
            if hemo == "Critical":
                st.error(f"⚡ Hemodynamic Status: **{hemo}** — Immediate intervention required")
            elif hemo == "Unstable":
                st.warning(f"⚡ Hemodynamic Status: **{hemo}** — Close monitoring needed")
            else:
                st.success(f"⚡ Hemodynamic Status: **{hemo}**")

            # ── Scoring Metrics ───────────────────────────────────────
            scoring = data.get("scoring", {})
            sc1, sc2, sc3, sc4 = st.columns(4)
            sc1.metric("HEART Score", f"{scoring.get('heart_score', 0)} / 10")
            sc2.metric("TIMI Score", f"{scoring.get('timi_score', 0)} / 7")
            sc3.metric("GRACE Score", f"{scoring.get('grace_score', 0)} / 372")
            sc4.metric("Risk Level", scoring.get("risk_level", "N/A"))

            hf = scoring.get("hf_severity", "None")
            if hf != "None":
                st.warning(f"🫀 Heart Failure Severity: **{hf}**")

            # ── Arrhythmia Alerts ─────────────────────────────────────
            alerts = data.get("arrhythmia_alerts", [])
            if alerts:
                st.markdown("### 🚨 Arrhythmia Alerts Triggered")
                for a in alerts:
                    icon = SEVERITY_ICONS.get(a.get("severity", ""), "ℹ️")
                    st.markdown(
                        f"{icon} **{a.get('type')}** — {a.get('severity')}\n\n"
                        f"  _{a.get('detection_rule')}_"
                    )
            else:
                st.info("✅ No arrhythmia alerts triggered.")

            st.success(f"Record saved. ID: `{data.get('record_id')}`")

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Backend not reachable. Start FastAPI with `uvicorn backend.main:app --reload`\n\n`{e}`")


# ═══════════════════════════════════════════════════════════════════════════
#  TAB 1 — SCORING CALCULATOR (standalone — no DB write)
# ═══════════════════════════════════════════════════════════════════════════

def _scoring_tab():
    st.header("📊 Cardiac Risk Scoring Calculator")
    st.caption("Quick offline calculator — does NOT save to database. Submit via Monitoring Dashboard to persist.")

    st.markdown("---")

    # ── HEART Score ───────────────────────────────────────────────────
    with st.expander("❤️ HEART Score", expanded=True):
        st.markdown("""
        | Component | 0 | 1 | 2 |
        |-----------|---|---|---|
        | **H**istory | Slightly suspicious | Moderately suspicious | Highly suspicious |
        | **E**CG | Normal | Non-specific changes | ST deviation |
        | **A**ge | < 45 | 45-64 | ≥ 65 |
        | **R**isk factors | 0 | 1-2 | ≥ 3 |
        | **T**roponin | Normal | 1-3× normal | > 3× normal |
        """)
        h_h = st.slider("History (H)", 0, 2, 0, key="heart_h")
        h_e = st.slider("ECG (E)", 0, 2, 0, key="heart_e")
        h_a = st.slider("Age (A)", 0, 2, 0, key="heart_a")
        h_r = st.slider("Risk Factors (R)", 0, 2, 0, key="heart_r")
        h_t = st.slider("Troponin (T)", 0, 2, 0, key="heart_t")
        heart_total = h_h + h_e + h_a + h_r + h_t
        if heart_total >= 7:
            st.error(f"HEART Score: **{heart_total}** — HIGH RISK (admit, early invasive strategy)")
        elif heart_total >= 4:
            st.warning(f"HEART Score: **{heart_total}** — MODERATE RISK (observation, further workup)")
        else:
            st.success(f"HEART Score: **{heart_total}** — LOW RISK (consider discharge with follow-up)")

    # ── TIMI Score ────────────────────────────────────────────────────
    with st.expander("📐 TIMI Score"):
        st.markdown("Each criterion = 1 point (0-7 total)")
        t1 = st.checkbox("Age ≥ 65", key="timi_1")
        t2 = st.checkbox("≥ 3 CAD risk factors", key="timi_2")
        t3 = st.checkbox("Known CAD (stenosis ≥ 50%)", key="timi_3")
        t4 = st.checkbox("ASA use in past 7 days", key="timi_4")
        t5 = st.checkbox("≥ 2 angina events in 24h", key="timi_5")
        t6 = st.checkbox("ST deviation on ECG", key="timi_6")
        t7 = st.checkbox("Elevated cardiac markers", key="timi_7")
        timi_total = sum([t1, t2, t3, t4, t5, t6, t7])
        if timi_total >= 5:
            st.error(f"TIMI Score: **{timi_total}** — HIGH RISK")
        elif timi_total >= 3:
            st.warning(f"TIMI Score: **{timi_total}** — INTERMEDIATE RISK")
        else:
            st.success(f"TIMI Score: **{timi_total}** — LOW RISK")


# ═══════════════════════════════════════════════════════════════════════════
#  TAB 2 — STABILITY ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════

def _stability_tab():
    st.header("📈 Hemodynamic Trend Analysis")
    st.caption("Time-series visualization of cardiac parameters from the last 24 hours.")

    patient_id = st.text_input("Patient ID for time-series", placeholder="PT-ICU-001", key="ts_pid")

    if st.button("📡 Load 24h Telemetry", use_container_width=True):
        if not patient_id:
            st.warning("Enter a Patient ID.")
            return

        try:
            resp = requests.get(f"{API_BASE}/timeseries/{patient_id}")
            resp.raise_for_status()
            data = resp.json()

            if not data:
                st.info("No telemetry data found in last 24 hours for this patient.")
                return

            df = pd.DataFrame(data)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.set_index("timestamp")

            st.success(f"Found **{len(df)}** readings in the last 24 hours.")

            # ── Heart Rate Chart ──────────────────────────────────────
            st.markdown("### 💓 Heart Rate Trend")
            if "heart_rate" in df.columns:
                st.line_chart(df["heart_rate"], color="#ff4b4b")
            else:
                st.info("No heart rate data.")

            # ── Blood Pressure Chart ──────────────────────────────────
            st.markdown("### 🩸 Blood Pressure Trend")
            bp_cols = [c for c in ["systolic_bp", "diastolic_bp"] if c in df.columns]
            if bp_cols:
                st.line_chart(df[bp_cols])
            else:
                st.info("No BP data.")

            # ── Troponin Trend ────────────────────────────────────────
            st.markdown("### 🧪 Troponin Level Trend")
            if "troponin_level" in df.columns:
                st.line_chart(df["troponin_level"], color="#ff9800")
                latest_trop = df["troponin_level"].iloc[-1]
                if latest_trop > 0.04:
                    st.warning(f"⚠️ Latest Troponin: **{latest_trop:.3f}** ng/mL (above 0.04 threshold)")
            else:
                st.info("No troponin data.")

            # ── Raw Data Table ────────────────────────────────────────
            with st.expander("View Raw Data"):
                st.dataframe(df.reset_index(), use_container_width=True)

        except requests.exceptions.RequestException as e:
            st.error(f"Backend not reachable. Ensure FastAPI is running.\n\n`{e}`")


# ═══════════════════════════════════════════════════════════════════════════
#  TAB 3 — ER DIAGRAM
# ═══════════════════════════════════════════════════════════════════════════

def _er_tab():
    st.header("🔗 Entity Relationship Diagram")
    st.caption("Module 27 — Cardiac ICU Monitoring database relationships")
    st.image(
        "https://via.placeholder.com/900x500.png?text=Module+27+ER+Diagram+-+Cardiac+ICU",
        caption="Entities: CardiacTelemetry, Arrhythmia, Hemodynamics, ScoringResult, Patient",
    )
    st.markdown("""
    **Key Relationships:**
    - A **Patient** generates many **CardiacTelemetry** entries (time-series)
    - Each **Telemetry** record produces zero or more **Arrhythmia** alerts
    - Each **Telemetry** record generates one **Hemodynamics** log
    - **ScoringResult** (HEART/TIMI/GRACE) is embedded within each telemetry document
    - **MedicationResponse** tracks drug effects linked to a patient
    """)


# ═══════════════════════════════════════════════════════════════════════════
#  TAB 4 — DB SCHEMA
# ═══════════════════════════════════════════════════════════════════════════

def _schema_tab():
    st.header("📋 Database Collections")
    st.write("Module 27 interacts with the following MongoDB collections inside `MedicalCopilotDB`:")

    schema = {
        "Collection": ["cardiac_telemetry", "arrhythmias", "hemodynamics"],
        "Role": [
            "Main collection: stores ECG, vitals, enzymes, embedded HEART/TIMI/GRACE scores, and STEMI flags.",
            "Arrhythmia detection alerts with type, severity, and detection rule that fired.",
            "Hemodynamic stability logs: BP, HR, and Stable/Unstable/Critical status per reading.",
        ],
        "Key Fields": [
            "patient_id, ecg_rhythm, heart_rate, systolic_bp, diastolic_bp, troponin_level, bnp_level, scoring{}, hemodynamic_status, stemi_alert, timestamp",
            "patient_id, type, severity, detection_rule, timestamp",
            "patient_id, systolic_bp, diastolic_bp, heart_rate, status, timestamp",
        ]
    }
    st.table(pd.DataFrame(schema))

    st.subheader("Sample Telemetry Document")
    st.code("""{
  "_id": "ObjectId('...')",
  "patient_id": "PT-ICU-001",
  "ecg_rhythm": "ST-elevation",
  "heart_rate": 112,
  "systolic_bp": 85,
  "diastolic_bp": 55,
  "troponin_level": 0.45,
  "bnp_level": 520.0,
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
}""", language="json")


# ═══════════════════════════════════════════════════════════════════════════
#  TAB 5 — ARRHYTHMIA ALERTS
# ═══════════════════════════════════════════════════════════════════════════

def _alerts_tab():
    st.header("🚨 High-Severity Arrhythmia Alerts")
    st.caption("Live feed of High and Critical severity detection events from the `arrhythmias` collection.")

    col_refresh, col_patterns = st.columns(2)

    with col_refresh:
        if st.button("🔄 Refresh Alerts", use_container_width=True):
            try:
                resp = requests.get(f"{API_BASE}/arrhythmias/alerts")
                resp.raise_for_status()
                alerts = resp.json()

                if not alerts:
                    st.info("No high-severity alerts recorded yet.")
                else:
                    st.success(f"Found **{len(alerts)}** alert(s).")
                    for a in alerts:
                        icon = SEVERITY_ICONS.get(a.get("severity", ""), "ℹ️")
                        ts = a.get("timestamp", "")[:19].replace("T", " ") if a.get("timestamp") else "N/A"
                        with st.expander(f"{icon} {a.get('type')} — {a.get('severity')} | {ts}"):
                            st.write(f"**Patient:** `{a.get('patient_id')}`")
                            st.write(f"**Rule:** _{a.get('detection_rule')}_")
                            st.write(f"**Alert ID:** `{a.get('_id', 'N/A')}`")

            except requests.exceptions.RequestException as e:
                st.error(f"Backend not reachable.\n\n`{e}`")

    with col_patterns:
        if st.button("📊 Analyse Patterns", use_container_width=True):
            try:
                resp = requests.get(f"{API_BASE}/arrhythmias/patterns")
                resp.raise_for_status()
                patterns = resp.json()

                if not patterns:
                    st.info("Not enough data for pattern analysis.")
                else:
                    df = pd.DataFrame(patterns)
                    st.markdown("### Recurring Arrhythmia Patterns")
                    st.bar_chart(df.set_index("type")["count"], color="#e91e63")
                    st.dataframe(df, use_container_width=True, hide_index=True)

            except requests.exceptions.RequestException as e:
                st.error(f"Backend not reachable.\n\n`{e}`")
