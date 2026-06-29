from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.db import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_code = Column(String(50), unique=True, nullable=False, index=True)
    patient_name = Column(String(100))
    location = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
