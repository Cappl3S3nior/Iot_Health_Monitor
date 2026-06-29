# Dashboard Setup Guide

Trước khi chạy Dashboard, hãy đảm bảo:

* Backend Server đang hoạt động.
* MQTT Broker đã được khởi động.
* Python 3.x đã được cài đặt.

---

## Run Dashboard

Mở **một terminal mới** và chuyển đến thư mục Dashboard:

```bash
cd Iot_Health_Monitor\Dashboard
```

Khởi động HTTP Server:

```bash
python -m http.server 5500
```

---

## Open Dashboard

Sau khi server khởi động thành công, mở trình duyệt và truy cập:

```text
http://localhost:5500
```

## Troubleshooting

### Cannot access `http://localhost:5500`

Kiểm tra:

* Đã chạy lệnh:

```bash
python -m http.server 5500
```

* Đang đứng đúng thư mục `Dashboard`?
* Cổng `5500` chưa bị ứng dụng khác sử dụng?

---

### Dashboard does not display data

Kiểm tra:

* Backend Server đang chạy?
* MQTT Broker đang hoạt động?
* ESP32 đã kết nối WiFi thành công?
* ESP32 đang publish dữ liệu lên đúng MQTT Topic?
* Dashboard đã kết nối thành công tới Backend/WebSocket?

---

## Default Address

| Service     | URL                          |
| ----------- | ---------------------------- |
| Dashboard   | `http://localhost:5500`      |
| Backend API | `http://127.0.0.1:8000`      |
| Swagger UI  | `http://127.0.0.1:8000/docs` |
