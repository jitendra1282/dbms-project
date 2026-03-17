# modules/module_E3/services.py
"""
Cardiac ICU clinical logic:
  • Arrhythmia Detection (STEMI, Tachycardia, Bradycardia, AFib)
  • HEART / TIMI / GRACE Scoring Engines
  • Hemodynamic Stability Assessment
"""
from typing import Dict, Any, List
from datetime import datetime

from .schemas import CardiacParameterCreate, ArrhythmiaAlert, ScoringResult
from .database import (
    save_telemetry,
    save_arrhythmia_alert,
    save_hemodynamic_log,
)


# ═══════════════════════════════════════════════════════════════════════════
#  ARRHYTHMIA DETECTION
# ═══════════════════════════════════════════════════════════════════════════

def detect_arrhythmias(
    patient_id: str,
    ecg_rhythm: str,
    heart_rate: int,
    troponin: float,
) -> List[ArrhythmiaAlert]:
    """Run rule-based arrhythmia detection and return triggered alerts."""
    alerts: List[ArrhythmiaAlert] = []
    ecg_lower = ecg_rhythm.lower()

    # ── STEMI Recognition (Critical) ──────────────────────────────────
    if "st-elevation" in ecg_lower or "stemi" in ecg_lower:
        alerts.append(ArrhythmiaAlert(
            patient_id=patient_id,
            type="STEMI",
            severity="Critical",
            detection_rule="ECG shows ST-elevation → Immediate catheterization required",
        ))

    # ── Atrial Fibrillation ───────────────────────────────────────────
    if "atrial fibrillation" in ecg_lower or "afib" in ecg_lower:
        alerts.append(ArrhythmiaAlert(
            patient_id=patient_id,
            type="Atrial Fibrillation",
            severity="High",
            detection_rule="ECG rhythm identified as Atrial Fibrillation",
        ))

    # ── Ventricular Tachycardia / Fibrillation ────────────────────────
    if "ventricular tachycardia" in ecg_lower or "v-tach" in ecg_lower:
        alerts.append(ArrhythmiaAlert(
            patient_id=patient_id,
            type="Ventricular Tachycardia",
            severity="Critical",
            detection_rule="V-Tach detected — defibrillation standby",
        ))

    if "ventricular fibrillation" in ecg_lower or "v-fib" in ecg_lower:
        alerts.append(ArrhythmiaAlert(
            patient_id=patient_id,
            type="Ventricular Fibrillation",
            severity="Critical",
            detection_rule="V-Fib detected — immediate defibrillation",
        ))

    # ── Heart Rate anomalies ──────────────────────────────────────────
    if heart_rate > 150:
        alerts.append(ArrhythmiaAlert(
            patient_id=patient_id,
            type="Severe Tachycardia",
            severity="High",
            detection_rule=f"Heart rate {heart_rate} bpm > 150 threshold",
        ))
    elif heart_rate > 100:
        alerts.append(ArrhythmiaAlert(
            patient_id=patient_id,
            type="Tachycardia",
            severity="Medium",
            detection_rule=f"Heart rate {heart_rate} bpm > 100 threshold",
        ))

    if heart_rate < 40:
        alerts.append(ArrhythmiaAlert(
            patient_id=patient_id,
            type="Severe Bradycardia",
            severity="High",
            detection_rule=f"Heart rate {heart_rate} bpm < 40 threshold",
        ))
    elif heart_rate < 60:
        alerts.append(ArrhythmiaAlert(
            patient_id=patient_id,
            type="Bradycardia",
            severity="Medium",
            detection_rule=f"Heart rate {heart_rate} bpm < 60 threshold",
        ))

    # ── Elevated Cardiac Enzymes ──────────────────────────────────────
    if troponin > 0.4:
        alerts.append(ArrhythmiaAlert(
            patient_id=patient_id,
            type="Critical Troponin Elevation",
            severity="Critical",
            detection_rule=f"Troponin {troponin} ng/mL >>> 0.04 (10x normal) — acute MI",
        ))
    elif troponin > 0.04:
        alerts.append(ArrhythmiaAlert(
            patient_id=patient_id,
            type="Elevated Troponin",
            severity="High",
            detection_rule=f"Troponin {troponin} ng/mL > 0.04 normal threshold — High Risk",
        ))

    return alerts


# ═══════════════════════════════════════════════════════════════════════════
#  SCORING ENGINES
# ═══════════════════════════════════════════════════════════════════════════

def calculate_heart_score(
    history_notes: str, ecg_rhythm: str, age: int,
    risk_factors: List[str], troponin: float,
) -> int:
    """HEART Score (0-10). Each component scored 0-2."""
    score = 0
    if history_notes:
        h_lower = history_notes.lower()
        if any(w in h_lower for w in ["chest pain", "angina", "pressure", "crushing"]):
            score += 2
        elif any(w in h_lower for w in ["discomfort", "shortness", "dyspnea"]):
            score += 1
    ecg_lower = ecg_rhythm.lower()
    if "st-elevation" in ecg_lower or "st-depression" in ecg_lower or "stemi" in ecg_lower:
        score += 2
    elif "normal" not in ecg_lower:
        score += 1
    if age >= 65:
        score += 2
    elif age >= 45:
        score += 1
    rf_count = len(risk_factors)
    if rf_count >= 3:
        score += 2
    elif rf_count >= 1:
        score += 1
    if troponin > 0.12:
        score += 2
    elif troponin > 0.04:
        score += 1
    return min(score, 10)


def calculate_timi_score(
    age: int, risk_factors: List[str], ecg_rhythm: str,
    troponin: float, aspirin_use: bool, known_stenosis: bool,
    angina_episodes_24h: int,
) -> int:
    """TIMI Risk Score for UA/NSTEMI (0-7)."""
    score = 0
    if age >= 65: score += 1
    if len(risk_factors) >= 3: score += 1
    if known_stenosis: score += 1
    if aspirin_use: score += 1
    if angina_episodes_24h >= 2: score += 1
    ecg_lower = ecg_rhythm.lower()
    if "st-elevation" in ecg_lower or "st-depression" in ecg_lower: score += 1
    if troponin > 0.04: score += 1
    return min(score, 7)


def calculate_grace_score(
    age: int, heart_rate: int, systolic_bp: int, creatinine: float,
    cardiac_arrest: bool, ecg_rhythm: str, troponin: float, killip_class: int,
) -> int:
    """Simplified GRACE Score (0-372)."""
    score = 0
    if age > 80: score += 91
    elif age > 70: score += 75
    elif age > 60: score += 58
    elif age > 50: score += 41
    elif age > 40: score += 25

    if heart_rate > 200: score += 46
    elif heart_rate > 150: score += 38
    elif heart_rate > 110: score += 28
    elif heart_rate > 90: score += 15
    elif heart_rate > 70: score += 9

    if systolic_bp < 80: score += 58
    elif systolic_bp < 100: score += 43
    elif systolic_bp < 120: score += 34
    elif systolic_bp < 140: score += 24
    elif systolic_bp < 160: score += 12

    if creatinine > 4.0: score += 28
    elif creatinine > 2.0: score += 21
    elif creatinine > 1.5: score += 14
    elif creatinine > 1.0: score += 7
    else: score += 1

    if cardiac_arrest: score += 39
    ecg_lower = ecg_rhythm.lower()
    if "st-elevation" in ecg_lower or "st-depression" in ecg_lower: score += 28
    if troponin > 0.04: score += 14
    killip_scores = {1: 0, 2: 20, 3: 39, 4: 59}
    score += killip_scores.get(killip_class, 0)
    return min(score, 372)


def determine_risk_level(heart_score: int, timi_score: int, grace_score: int) -> str:
    if heart_score >= 7 or timi_score >= 5 or grace_score >= 140: return "High"
    elif heart_score >= 4 or timi_score >= 3 or grace_score >= 109: return "Moderate"
    return "Low"


def determine_hf_severity(bnp_level: float, killip_class: int) -> str:
    if killip_class >= 4 or bnp_level > 900: return "Severe"
    elif killip_class >= 3 or bnp_level > 400: return "Moderate"
    elif killip_class >= 2 or bnp_level > 100: return "Mild"
    return "None"


# ═══════════════════════════════════════════════════════════════════════════
#  HEMODYNAMIC STABILITY ASSESSMENT
# ═══════════════════════════════════════════════════════════════════════════

def assess_hemodynamics(systolic_bp: int, diastolic_bp: int, heart_rate: int) -> str:
    if systolic_bp < 70 or heart_rate < 40 or heart_rate > 150: return "Critical"
    if systolic_bp < 90 or systolic_bp > 180 or heart_rate < 50 or heart_rate > 120: return "Unstable"
    if diastolic_bp > 120: return "Unstable"
    return "Stable"


# ═══════════════════════════════════════════════════════════════════════════
#  ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════

async def process_cardiac_telemetry(payload: CardiacParameterCreate) -> Dict[str, Any]:
    alerts = detect_arrhythmias(payload.patient_id, payload.ecg_rhythm, payload.heart_rate, payload.troponin_level)
    stemi_alert = any(a.type == "STEMI" for a in alerts)

    heart = calculate_heart_score(payload.history_notes or "", payload.ecg_rhythm, payload.age, payload.risk_factors, payload.troponin_level)
    timi = calculate_timi_score(payload.age, payload.risk_factors, payload.ecg_rhythm, payload.troponin_level, payload.aspirin_use, payload.known_stenosis, payload.angina_episodes_24h)
    grace = calculate_grace_score(payload.age, payload.heart_rate, payload.systolic_bp, payload.creatinine, payload.cardiac_arrest_on_admission, payload.ecg_rhythm, payload.troponin_level, payload.killip_class)
    risk_level = determine_risk_level(heart, timi, grace)
    hf_severity = determine_hf_severity(payload.bnp_level, payload.killip_class)
    scoring = ScoringResult(heart_score=heart, timi_score=timi, grace_score=grace, risk_level=risk_level, stemi_flag=stemi_alert, hf_severity=hf_severity)

    hemo_status = assess_hemodynamics(payload.systolic_bp, payload.diastolic_bp, payload.heart_rate)

    now = datetime.utcnow()
    telemetry_doc = {
        "patient_id": payload.patient_id, "ecg_rhythm": payload.ecg_rhythm,
        "heart_rate": payload.heart_rate, "systolic_bp": payload.systolic_bp,
        "diastolic_bp": payload.diastolic_bp, "troponin_level": payload.troponin_level,
        "bnp_level": payload.bnp_level, "creatinine": payload.creatinine,
        "echo_findings": payload.echo_findings, "scoring": scoring.dict(),
        "hemodynamic_status": hemo_status, "stemi_alert": stemi_alert, "timestamp": now,
    }
    record_id = await save_telemetry(telemetry_doc)

    alert_dicts = []
    for a in alerts:
        aid = await save_arrhythmia_alert({"patient_id": a.patient_id, "type": a.type, "severity": a.severity, "detection_rule": a.detection_rule})
        a.alert_id = aid
        alert_dicts.append(a)

    await save_hemodynamic_log({"patient_id": payload.patient_id, "systolic_bp": payload.systolic_bp, "diastolic_bp": payload.diastolic_bp, "heart_rate": payload.heart_rate, "status": hemo_status})

    return {
        "record_id": record_id, "patient_id": payload.patient_id,
        "ecg_rhythm": payload.ecg_rhythm, "heart_rate": payload.heart_rate,
        "systolic_bp": payload.systolic_bp, "diastolic_bp": payload.diastolic_bp,
        "troponin_level": payload.troponin_level, "bnp_level": payload.bnp_level,
        "scoring": scoring.dict(), "hemodynamic_status": hemo_status,
        "arrhythmia_alerts": [a.dict() for a in alert_dicts],
        "stemi_alert": stemi_alert, "timestamp": now,
    }
