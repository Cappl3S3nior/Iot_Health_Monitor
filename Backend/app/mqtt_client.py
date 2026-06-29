import asyncio
import json
import traceback

import paho.mqtt.client as mqtt

from app.config import settings
from app.db import SessionLocal
from app.schemas.reading import ECGPayload, TelemetryPayload
from app.services.alert_service import check_and_create_alerts
from app.services.device_service import get_or_create_device
from app.services.ecg_service import save_ecg_packet
from app.services.reading_service import save_telemetry
from app.websocket_manager import manager

loop_ref = None


def set_event_loop(loop):
    global loop_ref
    loop_ref = loop


def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code:", rc)
    client.subscribe(settings.MQTT_TOPIC_TELEMETRY)
    client.subscribe(settings.MQTT_TOPIC_ECG)


def on_message(client, userdata, msg):
    topic = msg.topic
    payload_str = msg.payload.decode("utf-8")
    print("MQTT message received:", topic, payload_str)

    try:
        data = json.loads(payload_str)
    except Exception as e:
        print("Invalid JSON:", e)
        return

    db = SessionLocal()
    try:
        if topic.endswith("/telemetry"):
            payload = TelemetryPayload(**data)
            device = get_or_create_device(db, payload.device_code)
            row = save_telemetry(db, device.id, payload)
            alerts = check_and_create_alerts(db, device.id, payload)

            print("[MQTT] telemetry received:", payload.device_code)
            ws_data = {
                "type": "telemetry",
                "device_code": payload.device_code,
                "data": {
                    "timestamp": str(row.ts),
                    "heart_rate": row.heart_rate,
                    "spo2": row.spo2,
                    "systolic_bp": row.systolic_bp,
                    "diastolic_bp": row.diastolic_bp,
                    "body_temp": row.body_temp,
                    "ecg_value": row.ecg_value,
                    "signal_quality": row.signal_quality,
                    "battery_level": row.battery_level,
                },
            }

            if loop_ref:
                print("[MQTT] broadcasting telemetry...")
                asyncio.run_coroutine_threadsafe(
                    manager.broadcast_json(ws_data), loop_ref
                )

        elif topic.endswith("/ecg"):
            payload = ECGPayload(**data)
            device = get_or_create_device(db, payload.device_code)
            row = save_ecg_packet(db, device.id, payload)

            print("[MQTT] ecg received:", payload.device_code)
            ws_data = {
                "type": "ecg",
                "device_code": payload.device_code,
                "data": {
                    "timestamp": str(row.ts),
                    "sampling_rate": row.sampling_rate,
                    "samples": row.samples,
                },
            }
            if loop_ref:
                print("[MQTT] broadcasting ecg...")
                asyncio.run_coroutine_threadsafe(
                    manager.broadcast_json(ws_data), loop_ref
                )

    except Exception as e:
        print("MQTT processing error:", e)
        traceback.print_exc()
    finally:
        db.close()


def start_mqtt():
    client = mqtt.Client()
    if settings.MQTT_USERNAME:
        client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 60)
    client.loop_start()
    return client
