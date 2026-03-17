# modules/module_27/database.py
import motor.motor_asyncio
from typing import List, Dict, Any
from datetime import datetime, timedelta

MONGO_DETAILS = "mongodb+srv://24je0608_db_user:Dakshta%401234@cluster0.n7xgc4b.mongodb.net/?appName=Cluster0"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

db = client["MedicalCopilotDB"]

# ─── Collections ──────────────────────────────────────────────────────────
cardiac_telemetry = db.cardiac_telemetry      # Main telemetry entries
arrhythmias_col   = db.arrhythmias            # Arrhythmia detection alerts
hemodynamics_col  = db.hemodynamics           # Hemodynamic stability logs


# ─── CRUD ─────────────────────────────────────────────────────────────────

async def save_telemetry(doc: Dict[str, Any]) -> str:
    """Insert a new cardiac telemetry record."""
    doc["timestamp"] = datetime.utcnow()
    result = await cardiac_telemetry.insert_one(doc)
    return str(result.inserted_id)


async def fetch_patient_telemetry(patient_id: str) -> List[Dict[str, Any]]:
    """Fetch all telemetry records for a patient, newest first."""
    cursor = cardiac_telemetry.find({"patient_id": patient_id}).sort("timestamp", -1)
    records = await cursor.to_list(length=100)
    for r in records:
        r["_id"] = str(r["_id"])
        if isinstance(r.get("timestamp"), datetime):
            r["timestamp"] = r["timestamp"].isoformat()
    return records


async def save_arrhythmia_alert(alert: Dict[str, Any]) -> str:
    """Insert an arrhythmia detection alert."""
    alert["timestamp"] = datetime.utcnow()
    result = await arrhythmias_col.insert_one(alert)
    return str(result.inserted_id)


async def fetch_high_severity_alerts() -> List[Dict[str, Any]]:
    """Fetch all High and Critical severity arrhythmia alerts."""
    cursor = arrhythmias_col.find(
        {"severity": {"$in": ["High", "Critical"]}}
    ).sort("timestamp", -1).limit(50)
    alerts = await cursor.to_list(length=50)
    for a in alerts:
        a["_id"] = str(a["_id"])
        if isinstance(a.get("timestamp"), datetime):
            a["timestamp"] = a["timestamp"].isoformat()
    return alerts


# ─── Time-Series Aggregation (last 24h) ──────────────────────────────────

async def fetch_24h_timeseries(patient_id: str) -> List[Dict[str, Any]]:
    """
    MongoDB aggregation pipeline: fetch last 24 hours of heart rate, BP,
    and ECG data sorted by timestamp — simulates real-time cardiac monitoring.
    """
    cutoff = datetime.utcnow() - timedelta(hours=24)
    pipeline = [
        {"$match": {
            "patient_id": patient_id,
            "timestamp": {"$gte": cutoff}
        }},
        {"$sort": {"timestamp": 1}},
        {"$project": {
            "_id": 0,
            "timestamp": 1,
            "heart_rate": 1,
            "systolic_bp": 1,
            "diastolic_bp": 1,
            "ecg_rhythm": 1,
            "troponin_level": 1
        }}
    ]
    cursor = cardiac_telemetry.aggregate(pipeline)
    results = await cursor.to_list(length=500)
    for r in results:
        if isinstance(r.get("timestamp"), datetime):
            r["timestamp"] = r["timestamp"].isoformat()
    return results


# ─── Pattern Recognition — recurring arrhythmia types ────────────────────

async def fetch_arrhythmia_patterns() -> List[Dict[str, Any]]:
    """
    Aggregation: group arrhythmia alerts by type and severity,
    count occurrences, identify recurring patterns.
    Uses $match + $group for pattern recognition across telemetry logs.
    """
    pipeline = [
        {"$match": {"severity": {"$in": ["Medium", "High", "Critical"]}}},
        {"$group": {
            "_id": {"type": "$type", "severity": "$severity"},
            "count": {"$sum": 1},
            "latest": {"$max": "$timestamp"},
            "detection_rules": {"$addToSet": "$detection_rule"}
        }},
        {"$sort": {"count": -1}}
    ]
    cursor = arrhythmias_col.aggregate(pipeline)
    results = await cursor.to_list(length=50)
    return [
        {
            "type": r["_id"]["type"],
            "severity": r["_id"]["severity"],
            "count": r["count"],
            "latest": r["latest"].isoformat() if isinstance(r.get("latest"), datetime) else str(r.get("latest", "")),
            "detection_rules": r.get("detection_rules", [])
        }
        for r in results
    ]


async def save_hemodynamic_log(doc: Dict[str, Any]) -> str:
    """Log a hemodynamic stability assessment."""
    doc["timestamp"] = datetime.utcnow()
    result = await hemodynamics_col.insert_one(doc)
    return str(result.inserted_id)
