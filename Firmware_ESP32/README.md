# ESP32 Data Transmission Guide

Trước khi truyền dữ liệu từ ESP32, hãy đảm bảo:

* MQTT Broker đang chạy.
* Backend Server đang hoạt động.
* Đã cài đặt đầy đủ các thư viện Python trong Backend.

---

## Connect ESP32

1. Cắm bo mạch **ESP32** vào máy tính bằng cáp USB.
2. Chờ hệ điều hành nhận cổng Serial (COM).

---

## Run Serial to MQTT Bridge

Mở **một terminal mới** và chuyển đến thư mục `Backend/tools`:

```bash
cd Backend\tools
```

Chạy chương trình chuyển tiếp dữ liệu

```bash
python serial_to_mqtt_bridge.py
```

## Troubleshooting

### ESP32 Not Detected

Kiểm tra:

* ESP32 đã được cắm đúng cáp USB?
* Cáp USB hỗ trợ truyền dữ liệu (không chỉ sạc)?
* Driver USB-to-Serial đã được cài đặt?
* Cổng COM xuất hiện trong Device Manager?

---

### Cannot Open Serial Port

Nếu chương trình báo lỗi không mở được cổng Serial:

* Đóng Arduino IDE hoặc Serial Monitor nếu đang mở.
* Kiểm tra đúng cổng COM trong file `serial_to_mqtt_bridge.py`.
* Rút và cắm lại ESP32.

---

### No Data on Dashboard

Kiểm tra:

* ESP32 đang gửi dữ liệu qua Serial?
* `serial_to_mqtt_bridge.py` đang chạy?
* MQTT Broker đang hoạt động?
* Backend đã kết nối tới MQTT Broker?
* Dashboard đã kết nối tới Backend/WebSocket?
