from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.alert import Alert


def create_alert(
    db: Session,
    device_id: int,
    alert_type: str,
    severity: str,
    message: str,
    value: dict,
):
    row = Alert(
        device_id=device_id,
        ts=datetime.now(timezone.utc),
        alert_type=alert_type,
        severity=severity,
        message=message,
        value=value,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def check_and_create_alerts(db: Session, device_id: int, payload):
    created = []

    if payload.heart_rate is not None and payload.heart_rate > 120:
        created.append(
            create_alert(
                db,
                device_id,
                "high_hr",
                "high",
                "Heart rate too high",
                {"heart_rate": payload.heart_rate},
            )
        )

    if payload.spo2 is not None and payload.spo2 < 92:
        created.append(
            create_alert(
                db,
                device_id,
                "low_spo2",
                "high",
                "SpO2 too low",
                {"spo2": payload.spo2},
            )
        )

    return created
