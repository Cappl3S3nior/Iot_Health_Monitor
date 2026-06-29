from sqlalchemy.orm import Session

from app.models.device import Device


def get_or_create_device(db: Session, device_code: str) -> Device:
    device = db.query(Device).filter(Device.device_code == device_code).first()
    if device:
        return device

    device = Device(device_code=device_code)
    db.add(device)
    db.commit()
    db.refresh(device)
    return device
