from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from app.db import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(BigInteger, primary_key=True, index=True)
    device_id = Column(
        Integer,
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ts = Column(DateTime(timezone=True), nullable=False, index=True)
    target_time = Column(DateTime(timezone=True))
    model_name = Column(String(100))
    predicted_hr = Column(Float)
    predicted_spo2 = Column(Float)
    predicted_systolic_bp = Column(Float)
    predicted_diastolic_bp = Column(Float)
    risk_score = Column(Float)
    risk_label = Column(String(50))
    meta = Column(JSONB)
