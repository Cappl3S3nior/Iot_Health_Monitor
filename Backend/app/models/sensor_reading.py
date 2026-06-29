from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB

from app.db import Base


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(BigInteger, primary_key=True, index=True)
    device_id = Column(
        Integer,
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ts = Column(DateTime(timezone=True), nullable=False, index=True)

    heart_rate = Column(Float)
    spo2 = Column(Float)
    systolic_bp = Column(Float)
    diastolic_bp = Column(Float)
    body_temp = Column(Float)
    ecg_value = Column(Float)
    signal_quality = Column(Float)
    battery_level = Column(Float)

    raw_payload = Column(JSONB)
