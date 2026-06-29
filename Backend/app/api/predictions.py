from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.device import Device
from app.models.prediction import Prediction

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/{device_code}")
def get_predictions(device_code: str, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.device_code == device_code).first()
    if not device:
        return {"error": "device not found"}

    rows = (
        db.query(Prediction)
        .filter(Prediction.device_id == device.id)
        .order_by(Prediction.ts.desc())
        .limit(100)
        .all()
    )
    return rows
