from sqlalchemy.orm import Session

from app.models.ecg_packet import ECGPacket
from app.schemas.reading import ECGPayload


def save_ecg_packet(db: Session, device_id: int, payload: ECGPayload):
    row = ECGPacket(
        device_id=device_id,
        ts=payload.timestamp,
        sampling_rate=payload.sampling_rate,
        samples=payload.samples,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
