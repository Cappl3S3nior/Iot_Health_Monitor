from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.db import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(BigInteger, primary_key=True, index=True)
    device_id = Column(
        Integer,
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ts = Column(DateTime(timezone=True), nullable=False, index=True)
    alert_type = Column(String(50))
    severity = Column(String(20))
    message = Column(Text)
    value = Column(JSONB)
