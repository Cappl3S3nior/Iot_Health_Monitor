# 🫀 IoT Health Monitor

Hệ thống giám sát sức khỏe từ xa sử dụng **ESP32**, **MQTT** và **Python**. Dữ liệu từ cảm biến được gửi từ ESP32 đến Backend thông qua MQTT và hiển thị theo thời gian thực trên Dashboard.

---

# Cấu trúc Project

```text
IoT_Health_Monitor
│
├── Backend
│   └── README.md
│
├── Dashboard
│   └── README.md
│
├── Firmware
│
├── mosquittoS
│
└── README.md
```

---

# Yêu cầu

Trước khi chạy project, hãy đảm bảo máy tính đã cài đặt:

* Python 3.x
* Mosquitto MQTT Broker

---

# Hướng dẫn chạy hệ thống

## Bước 1. Khởi động MQTT Broker

## Bước 2. Chạy Backend

## Bước 3. Chạy Dashboard

## Bước 4. Truyền dữ liệu từ ESP32

# Thứ tự khởi động

Để hệ thống hoạt động chính xác, hãy chạy theo đúng thứ tự sau:

1. MQTT Broker
2. Backend
3. Dashboard
4. ESP32 (Serial to MQTT Bridge)

---

# Tài liệu

| Thư mục               | Nội dung                          |
| --------------------- | --------------------------------- |
| `Backend/README.md`   | Hướng dẫn cài đặt và chạy Backend |
| `Dashboard/README.md` | Hướng dẫn chạy Dashboard          |
| `Firmware/`           | Mã nguồn chương trình ESP32       |

---

# Luồng hoạt động của hệ thống

```text
ESP32
   │
USB Serial
   │
serial_to_mqtt_bridge.py
   │
MQTT Broker
   │
Backend
   │
Dashboard
```

---

# Ghi chú

* Chỉ cần cài đặt thư viện Python (`pip install -r requirements.txt`) ở lần chạy đầu tiên.
* Nếu Dashboard không hiển thị dữ liệu, hãy kiểm tra Backend, MQTT Broker và ESP32 đã được khởi động theo đúng thứ tự.
