from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.device import Device
from app.models.ecg_packet import ECGPacket

router = APIRouter(prefix="/ecg", tags=["ecg"])


@router.get("/latest/{device_code}")
def get_latest_ecg(device_code: str, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.device_code == device_code).first()
    if not device:
        return {"error": "device not found"}

    row = (
        db.query(ECGPacket)
        .filter(ECGPacket.device_id == device.id)
        .order_by(ECGPacket.ts.desc())
        .first()
    )
    return row
