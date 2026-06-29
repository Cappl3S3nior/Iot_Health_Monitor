CÁCH CHẠY BACKEND

Bước 1: Mở MQTT Broker
- Mở terminal, cd C:\Program Files\mosquitto
- Chạy lệnh: mosquitto -c my_mosquitto.conf -v
- Giữ nguyên terminal, không tắt

Bước 2: Tạo môi trường ảo (venv)
- Mở terminal thứ 2, D:\UIT\Bai_tap\DoAn1\Iot_Health_Monitor\Backend
- Chạy lệnh: python -m venv venv (tạo môi trường ảo)
- Kích hoạt môi trường ảo: venv\Scripts\activate
- Cài đặt các gói cần thiết: pip install -r requirements.txt

Bước 3: Chạy Backend
- cd Iot_Health_Monitor\Backend
- Chạy lệnh: uvicorn app.main:app --reload

Bước 4: Chạy Dashboard
- Mở thêm terminal thứ 3, cd Iot_Health_Monitor\Dashboard
- Chạy lệnh: python -m http.server 5500
- Truy cập dashboard tại: http://localhost:5500

Bước 5: Truyền dữ liệu từ ESP32
- Cắm ESP32 vào máy tính
- Mở terminal thứ 4, cd Backend\tools
- Chạy lệnh: python serial_to_mqtt_bridge.py
