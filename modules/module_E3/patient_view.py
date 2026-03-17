# modules/module_E3/patient_view.py
"""
Streamlit UI for Module E3 — Cardiac ICU Monitoring Database.
6 tabs: Monitoring Dashboard, Scoring Calculator, Stability Analytics,
        ER Diagram, DB Schema, Arrhythmia Alerts.
"""
import streamlit as st
import pandas as pd
import requests
from datetime import datetime

API_BASE = "http://localhost:8000/api/v27"

SEVERITY_ICONS = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}

ECG_OPTIONS = [
    "Normal Sinus Rhythm", "ST-elevation", "ST-depression",
    "Atrial Fibrillation", "Ventricular Tachycardia", "Ventricular Fibrillation",
    "Sinus Tachycardia", "Sinus Bradycardia",
    "Right Bundle Branch Block", "Left Bundle Branch Block",
]

RISK_FACTOR_OPTIONS = [
    "Diabetes", "Hypertension", "Smoking", "Hyperlipidemia", "Obesity",
    "Family History of CAD", "Sedentary Lifestyle", "Prior MI", "Prior PCI/CABG",
]


def render_patient_module():
    tabs = st.tabs([
        "🫀 Monitoring Dashboard", "📊 Scoring Calculator",
        "📈 Stability Analytics", "🔗 ER Diagram",
        "📋 DB Schema", "🚨 Arrhythmia Alerts",
    ])
    with tabs[0]: _monitoring_tab()
    with tabs[1]: _scoring_tab()
    with tabs[2]: _stability_tab()
    with tabs[3]: _er_tab()
    with tabs[4]: _schema_tab()
    with tabs[5]: _alerts_tab()


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
            "patient_id": patient_id, "ecg_rhythm": ecg_rhythm,
            "heart_rate": heart_rate, "systolic_bp": systolic_bp,
            "diastolic_bp": diastolic_bp, "troponin_level": troponin,
            "bnp_level": bnp, "creatinine": creatinine,
            "echo_findings": echo or None, "age": age,
            "risk_factors": risk_factors, "aspirin_use": aspirin_use,
            "known_stenosis": known_stenosis, "angina_episodes_24h": angina_24h,
            "cardiac_arrest_on_admission": cardiac_arrest,
            "killip_class": killip_class, "history_notes": history or None,
        }
        try:
            with st.spinner("Running arrhythmia detection & scoring engines..."):
                resp = requests.post(f"{API_BASE}/telemetry", json=payload)
                resp.raise_for_status()
                data = resp.json()

            if data.get("stemi_alert"):
                st.error("🚨 **CRITICAL: STEMI DETECTED** 🚨\n\n"
                         "ST-elevation identified on ECG. **Immediate cardiac catheterization recommended.**\n\n"
                         "Activate CODE STEMI protocol.")
            hemo = data.get("hemodynamic_status", "N/A")
            if hemo == "Critical":
                st.error(f"⚡ Hemodynamic Status: **{hemo}** — Immediate intervention required")
            elif hemo == "Unstable":
                st.warning(f"⚡ Hemodynamic Status: **{hemo}** — Close monitoring needed")
            else:
                st.success(f"⚡ Hemodynamic Status: **{hemo}**")

            scoring = data.get("scoring", {})
            sc1, sc2, sc3, sc4 = st.columns(4)
            sc1.metric("HEART Score", f"{scoring.get('heart_score', 0)} / 10")
            sc2.metric("TIMI Score", f"{scoring.get('timi_score', 0)} / 7")
            sc3.metric("GRACE Score", f"{scoring.get('grace_score', 0)} / 372")
            sc4.metric("Risk Level", scoring.get("risk_level", "N/A"))

            hf = scoring.get("hf_severity", "None")
            if hf != "None":
                st.warning(f"🫀 Heart Failure Severity: **{hf}**")

            alerts = data.get("arrhythmia_alerts", [])
            if alerts:
                st.markdown("### 🚨 Arrhythmia Alerts Triggered")
                for a in alerts:
                    icon = SEVERITY_ICONS.get(a.get("severity", ""), "ℹ️")
                    st.markdown(f"{icon} **{a.get('type')}** — {a.get('severity')}\n\n  _{a.get('detection_rule')}_")
            else:
                st.info("✅ No arrhythmia alerts triggered.")
            st.success(f"Record saved. ID: `{data.get('record_id')}`")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Backend not reachable. Start FastAPI with `uvicorn backend.main:app --reload`\n\n`{e}`")


# ═══════════════════════════════════════════════════════════════════════════
#  TAB 1 — SCORING CALCULATOR
# ═══════════════════════════════════════════════════════════════════════════

def _scoring_tab():
    st.header("📊 Cardiac Risk Scoring Calculator")
    st.caption("Quick offline calculator — does NOT save to database.")

    with st.expander("❤️ HEART Score (0-10)", expanded=True):
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

    with st.expander("📐 TIMI Score (0-7)"):
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
            st.error(f"TIMI Score: **{timi_total}** — HIGH RISK (14-day mortality ~26%)")
        elif timi_total >= 3:
            st.warning(f"TIMI Score: **{timi_total}** — INTERMEDIATE RISK")
        else:
            st.success(f"TIMI Score: **{timi_total}** — LOW RISK")

    with st.expander("📊 GRACE Score (0-372)"):
        st.markdown("""
        Weighted risk factors for in-hospital & 6-month mortality prediction.

        | Factor | Weight Range |
        |--------|-------------|
        | Age | 0-91 |
        | Heart Rate | 0-46 |
        | Systolic BP (inverse) | 0-58 |
        | Creatinine | 1-28 |
        | Cardiac Arrest | 0-39 |
        | ST Deviation | 0-28 |
        | Elevated Enzymes | 0-14 |
        | Killip Class | 0-59 |
        """)
        g_col1, g_col2 = st.columns(2)
        with g_col1:
            g_age = st.number_input("Age", 18, 130, 55, key="grace_age")
            g_hr = st.number_input("Heart Rate (BPM)", 20, 300, 76, key="grace_hr")
            g_sbp = st.number_input("Systolic BP (mmHg)", 40, 300, 120, key="grace_sbp")
            g_creat = st.number_input("Creatinine (mg/dL)", 0.0, 20.0, 1.0, step=0.1, key="grace_creat")
        with g_col2:
            g_arrest = st.checkbox("Cardiac arrest on admission", key="grace_arrest")
            g_st = st.checkbox("ST deviation on ECG", key="grace_st")
            g_enzymes = st.checkbox("Elevated cardiac enzymes", key="grace_enz")
            g_killip = st.selectbox("Killip Class", [1, 2, 3, 4], key="grace_killip")

        # Calculate GRACE
        grace = 0
        if g_age > 80: grace += 91
        elif g_age > 70: grace += 75
        elif g_age > 60: grace += 58
        elif g_age > 50: grace += 41
        elif g_age > 40: grace += 25

        if g_hr > 200: grace += 46
        elif g_hr > 150: grace += 38
        elif g_hr > 110: grace += 28
        elif g_hr > 90: grace += 15
        elif g_hr > 70: grace += 9

        if g_sbp < 80: grace += 58
        elif g_sbp < 100: grace += 43
        elif g_sbp < 120: grace += 34
        elif g_sbp < 140: grace += 24
        elif g_sbp < 160: grace += 12

        if g_creat > 4.0: grace += 28
        elif g_creat > 2.0: grace += 21
        elif g_creat > 1.5: grace += 14
        elif g_creat > 1.0: grace += 7
        else: grace += 1

        if g_arrest: grace += 39
        if g_st: grace += 28
        if g_enzymes: grace += 14
        killip_scores = {1: 0, 2: 20, 3: 39, 4: 59}
        grace += killip_scores.get(g_killip, 0)
        grace = min(grace, 372)

        if grace >= 140:
            st.error(f"GRACE Score: **{grace}** — HIGH RISK (in-hospital mortality >3%)")
        elif grace >= 109:
            st.warning(f"GRACE Score: **{grace}** — INTERMEDIATE RISK (mortality 1-3%)")
        else:
            st.success(f"GRACE Score: **{grace}** — LOW RISK (mortality <1%)")

    st.divider()

    # ── STEMI RECOGNITION ─────────────────────────────────────────────
    st.subheader("🚨 STEMI Recognition")
    st.caption("Automatic ST-Elevation Myocardial Infarction detection based on ECG rhythm")

    stemi_ecg = st.selectbox("Select ECG Rhythm", ECG_OPTIONS, key="stemi_ecg")
    stemi_trop = st.number_input("Troponin level (ng/mL)", 0.0, 50.0, 0.02, step=0.01, format="%.3f", key="stemi_trop")

    ecg_lower = stemi_ecg.lower()
    is_stemi = "st-elevation" in ecg_lower or "stemi" in ecg_lower
    high_troponin = stemi_trop > 0.04
    critical_troponin = stemi_trop > 0.4

    col_stemi1, col_stemi2 = st.columns(2)
    with col_stemi1:
        if is_stemi:
            st.error("🔴 **STEMI DETECTED**\n\nST-elevation on ECG → **Activate CODE STEMI**\n\n"
                     "→ Immediate cardiac catheterization required\n\n"
                     "→ Target door-to-balloon time: <90 minutes")
        else:
            st.success("🟢 **No STEMI** — ECG does not show ST-elevation")

    with col_stemi2:
        if critical_troponin:
            st.error(f"🔴 **Critical Troponin: {stemi_trop:.3f} ng/mL**\n\n"
                     f">>> 10× normal (0.04) — Acute MI likely")
        elif high_troponin:
            st.warning(f"🟠 **Elevated Troponin: {stemi_trop:.3f} ng/mL**\n\n"
                       f"> Normal threshold (0.04) — High Risk")
        else:
            st.success(f"🟢 **Normal Troponin: {stemi_trop:.3f} ng/mL**")

    st.divider()

    # ── HEART FAILURE SEVERITY ────────────────────────────────────────
    st.subheader("🫀 Heart Failure Severity Index")
    st.caption("Classifies HF severity based on BNP levels and Killip classification")

    hf_col1, hf_col2 = st.columns(2)
    with hf_col1:
        hf_bnp = st.number_input("BNP level (pg/mL)", 0.0, 5000.0, 45.0, step=1.0, key="hf_bnp")
    with hf_col2:
        hf_killip = st.selectbox("Killip Class", [
            "I — No heart failure",
            "II — Rales, S3 gallop",
            "III — Pulmonary edema",
            "IV — Cardiogenic shock"
        ], key="hf_killip_sel")
    killip_map = {"I —": 1, "II —": 2, "III —": 3, "IV —": 4}
    hf_killip_val = next((v for k, v in killip_map.items() if hf_killip.startswith(k)), 1)

    # Determine severity
    if hf_killip_val >= 4 or hf_bnp > 900:
        severity = "Severe"
        st.error(f"🔴 **Heart Failure: SEVERE**\n\n"
                 f"BNP: {hf_bnp:.0f} pg/mL | Killip: {hf_killip}\n\n"
                 f"→ ICU admission, inotropic support, consider mechanical circulatory support")
    elif hf_killip_val >= 3 or hf_bnp > 400:
        severity = "Moderate"
        st.warning(f"🟠 **Heart Failure: MODERATE**\n\n"
                   f"BNP: {hf_bnp:.0f} pg/mL | Killip: {hf_killip}\n\n"
                   f"→ IV diuretics, oxygen therapy, close monitoring")
    elif hf_killip_val >= 2 or hf_bnp > 100:
        severity = "Mild"
        st.info(f"🟡 **Heart Failure: MILD**\n\n"
                f"BNP: {hf_bnp:.0f} pg/mL | Killip: {hf_killip}\n\n"
                f"→ Oral diuretics, lifestyle modifications, follow-up")
    else:
        severity = "None"
        st.success(f"🟢 **No Heart Failure**\n\n"
                   f"BNP: {hf_bnp:.0f} pg/mL | Killip: {hf_killip}")

    st.markdown("""
    **Reference: BNP Thresholds**
    | BNP (pg/mL) | Interpretation |
    |---|---|
    | < 100 | Normal |
    | 100-400 | Mild HF |
    | 400-900 | Moderate HF |
    | > 900 | Severe HF |
    """)




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
                st.info("No telemetry data found in last 24 hours.")
                return
            df = pd.DataFrame(data)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.set_index("timestamp")
            st.success(f"Found **{len(df)}** readings.")

            st.markdown("### 💓 Heart Rate Trend")
            if "heart_rate" in df.columns:
                st.line_chart(df["heart_rate"], color="#ff4b4b")

            st.markdown("### 🩸 Blood Pressure Trend")
            bp_cols = [c for c in ["systolic_bp", "diastolic_bp"] if c in df.columns]
            if bp_cols:
                st.line_chart(df[bp_cols])

            st.markdown("### 🧪 Troponin Level Trend")
            if "troponin_level" in df.columns:
                st.line_chart(df["troponin_level"], color="#ff9800")
                latest_trop = df["troponin_level"].iloc[-1]
                if latest_trop > 0.04:
                    st.warning(f"⚠️ Latest Troponin: **{latest_trop:.3f}** ng/mL (above 0.04 threshold)")

            with st.expander("View Raw Data"):
                st.dataframe(df.reset_index(), use_container_width=True)
        except requests.exceptions.RequestException as e:
            st.error(f"Backend not reachable.\n\n`{e}`")


# ═══════════════════════════════════════════════════════════════════════════
#  TAB 3 — ER DIAGRAM
# ═══════════════════════════════════════════════════════════════════════════

def _er_tab():
    st.header("🔗 Entity Relationship Diagram")
    st.caption("Module E3 — Cardiac ICU Monitoring database relationships")

    import os
    img_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "e3_er_diagram.png")
    if os.path.exists(img_path):
        st.image(img_path, caption="Cardiac ICU ER Diagram — 6 entities with relationships", use_container_width=True)
    else:
        st.warning("ER diagram image not found at `assets/e3_er_diagram.png`")

    st.markdown("""
    **Key Relationships:**

    | Relationship | Type | Description |
    |---|---|---|
    | Patient → CardiacTelemetry | 1:N | A patient generates many telemetry records |
    | CardiacTelemetry → ScoringResult | 1:1 | Each telemetry record embeds one scoring result (HEART/TIMI/GRACE) |
    | CardiacTelemetry → ArrhythmiaAlert | 1:N | Each telemetry record produces zero or more arrhythmia alerts |
    | Patient → ArrhythmiaAlert | 1:N | A patient triggers multiple arrhythmia alerts over time |
    | Patient → Hemodynamics | 1:N | Stability logs logged for each patient |
    | Patient → MedicationResponse | 1:N | A patient receives multiple drug response records |

    > **Note:** `ScoringResult` is an **embedded document** inside `CardiacTelemetry`, not a separate collection.
    """)


# ═══════════════════════════════════════════════════════════════════════════
#  TAB 4 — DB SCHEMA
# ═══════════════════════════════════════════════════════════════════════════

def _schema_tab():
    st.header("📋 Database Collections")
    schema = {
        "Collection": ["cardiac_telemetry", "arrhythmias", "hemodynamics"],
        "Role": [
            "Main: ECG, vitals, enzymes, embedded HEART/TIMI/GRACE scores, STEMI flags.",
            "Arrhythmia detection alerts with type, severity, and detection rule.",
            "Hemodynamic stability logs: BP, HR, Stable/Unstable/Critical status.",
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
  "patient_id": "PT-ICU-001",
  "ecg_rhythm": "ST-elevation",
  "heart_rate": 112,
  "systolic_bp": 85,
  "troponin_level": 0.45,
  "scoring": {
    "heart_score": 8, "timi_score": 5, "grace_score": 185,
    "risk_level": "High", "stemi_flag": true, "hf_severity": "Moderate"
  },
  "hemodynamic_status": "Unstable",
  "stemi_alert": true
}""", language="json")


# ═══════════════════════════════════════════════════════════════════════════
#  TAB 5 — ARRHYTHMIA ALERTS
# ═══════════════════════════════════════════════════════════════════════════

def _alerts_tab():
    st.header("🚨 High-Severity Arrhythmia Alerts")
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
