import json
from datetime import datetime, timedelta, timezone

import paho.mqtt.client as mqtt
import serial

# =========================
# CONFIG
# =========================
SERIAL_PORT = "COM10"  # đổi theo máy mày
BAUDRATE = 115200

MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
MQTT_USER = None
MQTT_PASS = None

VN_TZ = timezone(timedelta(hours=7))

# =========================
# MQTT SETUP
# =========================
mqtt_client = mqtt.Client()

if MQTT_USER:
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)

mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

# =========================
# SERIAL SETUP
# =========================
ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)

print(f"Listening Serial on {SERIAL_PORT} @ {BAUDRATE}")
print("Publishing to MQTT broker:", MQTT_BROKER, MQTT_PORT)

while True:
    try:
        line = ser.readline().decode("utf-8", errors="ignore").strip()
        if not line:
            continue

        print("SERIAL:", line)

        data = json.loads(line)

        msg_type = data.get("type")
        device_code = data.get("device_code", "unknown_device")

        # gắn timestamp tại PC
        data["timestamp"] = datetime.now(VN_TZ).isoformat()

        if msg_type == "telemetry":
            topic = f"healthcare/{device_code}/telemetry"
        elif msg_type == "ecg":
            topic = f"healthcare/{device_code}/ecg"
        else:
            print("Unknown message type:", msg_type)
            continue

        # bỏ field type trước khi publish vào backend nếu muốn
        publish_data = dict(data)
        publish_data.pop("type", None)

        mqtt_client.publish(topic, json.dumps(publish_data))
        print("MQTT PUB ->", topic)

    except json.JSONDecodeError as e:
        print("JSON parse error:", e)

    except Exception as e:
        print("Bridge error:", e)
