from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.device import Device
from app.models.sensor_reading import SensorReading

router = APIRouter(prefix="/readings", tags=["readings"])


@router.get("/latest/{device_code}")
def get_latest_reading(device_code: str, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.device_code == device_code).first()
    if not device:
        return {"error": "device not found"}

    row = (
        db.query(SensorReading)
        .filter(SensorReading.device_id == device.id)
        .order_by(SensorReading.ts.desc())
        .first()
    )
    return row


@router.get("/{device_code}")
def get_readings(
    device_code: str,
    from_ts: datetime | None = Query(None),
    to_ts: datetime | None = Query(None),
    limit: int = 100,
    db: Session = Depends(get_db),
):
    device = db.query(Device).filter(Device.device_code == device_code).first()
    if not device:
        return {"error": "device not found"}

    q = db.query(SensorReading).filter(SensorReading.device_id == device.id)

    if from_ts:
        q = q.filter(SensorReading.ts >= from_ts)
    if to_ts:
        q = q.filter(SensorReading.ts <= to_ts)

    rows = q.order_by(SensorReading.ts.desc()).limit(limit).all()
    return rows
