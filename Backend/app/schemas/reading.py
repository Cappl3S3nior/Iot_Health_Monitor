from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class TelemetryPayload(BaseModel):
    device_code: str
    timestamp: datetime
    heart_rate: Optional[float] = None
    spo2: Optional[float] = None
    systolic_bp: Optional[float] = None
    diastolic_bp: Optional[float] = None
    body_temp: Optional[float] = None
    ecg_value: Optional[float] = None
    signal_quality: Optional[float] = None
    battery_level: Optional[float] = None


class ECGPayload(BaseModel):
    device_code: str
    timestamp: datetime
    sampling_rate: int
    samples: List[float]
