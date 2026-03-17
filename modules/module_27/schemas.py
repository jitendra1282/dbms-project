# modules/module_27/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class _DatetimeMixin(BaseModel):
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# ─── Input Models ────────────────────────────────────────────────────────

class CardiacParameterCreate(BaseModel):
    """Input payload to record a new cardiac telemetry entry."""
    patient_id: str
    ecg_rhythm: str = Field(..., description="e.g. Normal Sinus, ST-elevation, Atrial Fibrillation")
    heart_rate: int = Field(..., ge=20, le=300, description="BPM")
    systolic_bp: int = Field(..., ge=40, le=300, description="mmHg")
    diastolic_bp: int = Field(..., ge=20, le=200, description="mmHg")
    troponin_level: float = Field(0.0, ge=0, description="ng/mL — normal < 0.04")
    bnp_level: float = Field(0.0, ge=0, description="pg/mL — normal < 100")
    creatinine: float = Field(1.0, ge=0, description="mg/dL")
    echo_findings: Optional[str] = None
    age: int = Field(50, ge=0, le=130)
    risk_factors: List[str] = Field(default_factory=list, description="e.g. Diabetes, Hypertension, Smoking")
    aspirin_use: bool = False
    known_stenosis: bool = False
    angina_episodes_24h: int = Field(0, ge=0)
    cardiac_arrest_on_admission: bool = False
    killip_class: int = Field(1, ge=1, le=4, description="Killip I-IV heart failure class")
    history_notes: Optional[str] = None


class ArrhythmiaAlert(_DatetimeMixin):
    """An arrhythmia detection event."""
    alert_id: Optional[str] = None
    patient_id: str
    type: str               # e.g. STEMI, Atrial Fibrillation, Tachycardia, Bradycardia
    severity: str            # Low | Medium | High | Critical
    detection_rule: str      # Human-readable rule that fired
    timestamp: Optional[datetime] = None


class MedicationResponse(BaseModel):
    """Track how a cardiac drug affects vital parameters."""
    patient_id: str
    drug_name: str
    pre_hr: int
    post_hr: int
    pre_bp_systolic: int
    post_bp_systolic: int
    response_status: str     # Improved | No Change | Worsened


# ─── Scoring Models ─────────────────────────────────────────────────────

class ScoringResult(BaseModel):
    heart_score: int = Field(0, ge=0, le=10, description="HEART Score 0-10")
    timi_score: int = Field(0, ge=0, le=7, description="TIMI Score 0-7")
    grace_score: int = Field(0, ge=0, le=372, description="GRACE Score 0-372")
    risk_level: str          # Low | Moderate | High
    stemi_flag: bool = False
    hf_severity: str = "None"   # None | Mild | Moderate | Severe


# ─── Combined API Responses ─────────────────────────────────────────────

class TelemetryResponse(_DatetimeMixin):
    """Full response after recording a telemetry entry."""
    record_id: str
    patient_id: str
    ecg_rhythm: str
    heart_rate: int
    systolic_bp: int
    diastolic_bp: int
    troponin_level: float
    bnp_level: float
    scoring: ScoringResult
    hemodynamic_status: str   # Stable | Unstable | Critical
    arrhythmia_alerts: List[ArrhythmiaAlert] = []
    stemi_alert: bool = False
    timestamp: Optional[datetime] = None


class AssessmentResponse(_DatetimeMixin):
    """GET response for a patient's latest assessment."""
    patient_id: str
    scoring: ScoringResult
    hemodynamic_status: str
    arrhythmia_alerts: List[ArrhythmiaAlert] = []
    stemi_alert: bool = False
    timestamp: Optional[datetime] = None
