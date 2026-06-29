from datetime import datetime, timezone

from fastapi import APIRouter

from app.schemas.control import TestECGPayload, TestTelemetryPayload
from app.websocket_manager import manager

router = APIRouter(prefix="/control", tags=["control"])


@router.post("/test/telemetry")
async def push_test_telemetry(payload: TestTelemetryPayload):
    ws_data = {
        "type": "telemetry",
        "device_code": payload.device_code,
        "data": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "heart_rate": payload.heart_rate,
            "spo2": payload.spo2,
            "systolic_bp": payload.systolic_bp,
            "diastolic_bp": payload.diastolic_bp,
            "body_temp": payload.body_temp,
            "ecg_value": payload.ecg_value,
            "signal_quality": payload.signal_quality,
            "battery_level": payload.battery_level,
        },
    }

    await manager.broadcast_json(ws_data)
    return {"status": "ok", "message": "test telemetry broadcasted"}


@router.post("/test/ecg")
async def push_test_ecg(payload: TestECGPayload):
    ws_data = {
        "type": "ecg",
        "device_code": payload.device_code,
        "data": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sampling_rate": payload.sampling_rate,
            "samples": payload.samples,
        },
    }

    await manager.broadcast_json(ws_data)
    return {"status": "ok", "message": "test ecg broadcasted"}
