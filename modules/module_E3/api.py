# modules/module_E3/api.py
from fastapi import APIRouter, HTTPException, status
from typing import List

from .schemas import CardiacParameterCreate, TelemetryResponse, AssessmentResponse, ArrhythmiaAlert
from .services import process_cardiac_telemetry
from .database import fetch_patient_telemetry, fetch_high_severity_alerts, fetch_24h_timeseries, fetch_arrhythmia_patterns

router = APIRouter(prefix="/api/v27", tags=["Module E3 - Cardiac ICU Monitoring"])


@router.post("/telemetry", response_model=TelemetryResponse, status_code=status.HTTP_201_CREATED,
             summary="Record new cardiac parameters & run all scoring engines")
async def create_telemetry(payload: CardiacParameterCreate):
    try:
        return await process_cardiac_telemetry(payload)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assessment/{patient_id}", summary="Get latest TIMI/GRACE/HEART scores & hemodynamic status")
async def get_assessment(patient_id: str):
    try:
        records = await fetch_patient_telemetry(patient_id)
        if not records:
            raise HTTPException(status_code=404, detail=f"No records for {patient_id}")
        return records[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/arrhythmias/alerts", summary="Fetch high-severity arrhythmia alerts")
async def get_arrhythmia_alerts():
    try:
        return await fetch_high_severity_alerts()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not fetch alerts.")


@router.get("/timeseries/{patient_id}", summary="24-hour cardiac time-series data")
async def get_timeseries(patient_id: str):
    try:
        return await fetch_24h_timeseries(patient_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/arrhythmias/patterns", summary="Pattern recognition: recurring arrhythmia types")
async def get_arrhythmia_patterns():
    try:
        return await fetch_arrhythmia_patterns()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not analyse patterns.")
