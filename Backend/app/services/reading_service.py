from sqlalchemy.orm import Session

from app.models.sensor_reading import SensorReading
from app.schemas.reading import TelemetryPayload


def save_telemetry(db: Session, device_id: int, payload: TelemetryPayload):
    row = SensorReading(
        device_id=device_id,
        ts=payload.timestamp,
        heart_rate=payload.heart_rate,
        spo2=payload.spo2,
        systolic_bp=payload.systolic_bp,
        diastolic_bp=payload.diastolic_bp,
        body_temp=payload.body_temp,
        ecg_value=payload.ecg_value,
        signal_quality=payload.signal_quality,
        battery_level=payload.battery_level,
        raw_payload=payload.model_dump(mode="json"),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
