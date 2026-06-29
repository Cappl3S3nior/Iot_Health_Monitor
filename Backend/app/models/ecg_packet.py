from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB

from app.db import Base


class ECGPacket(Base):
    __tablename__ = "ecg_packets"

    id = Column(BigInteger, primary_key=True, index=True)
    device_id = Column(
        Integer,
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ts = Column(DateTime(timezone=True), nullable=False, index=True)
    sampling_rate = Column(Integer)
    samples = Column(JSONB)
