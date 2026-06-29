from typing import List, Optional

from pydantic import BaseModel


class TestTelemetryPayload(BaseModel):
    device_code: str
    heart_rate: Optional[float] = None
    spo2: Optional[float] = None
    systolic_bp: Optional[float] = None
    diastolic_bp: Optional[float] = None
    body_temp: Optional[float] = None
    ecg_value: Optional[float] = None
    signal_quality: Optional[float] = None
    battery_level: Optional[float] = None


class TestECGPayload(BaseModel):
    device_code: str
    sampling_rate: int
    samples: List[int]
