from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.alert import Alert
from app.models.device import Device

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/{device_code}")
def get_alerts(device_code: str, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.device_code == device_code).first()
    if not device:
        return {"error": "device not found"}

    rows = (
        db.query(Alert)
        .filter(Alert.device_id == device.id)
        .order_by(Alert.ts.desc())
        .limit(100)
        .all()
    )
    return rows
