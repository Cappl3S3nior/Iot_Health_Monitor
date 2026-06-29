# Backend Setup Guide

Trước khi chạy backend, hãy đảm bảo máy đã cài đặt:

* Python 3.x
* Mosquitto MQTT Broker
* pip

---

## Step 1: Start MQTT Broker

1. Mở Terminal hoặc Command Prompt.
2. Di chuyển đến thư mục chứa Mosquitto.

```bash
cd mosquittoS
```

3. Khởi động MQTT Broker bằng lệnh:

```bash
mosquitto -c my_mosquitto.conf -v
```

## Step 2: Create and Activate Python Virtual Environment

Mở **một terminal mới** và chuyển đến thư mục **Backend**.

### Tạo môi trường ảo

```bash
python -m venv venv
```

### Kích hoạt môi trường ảo

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### Cài đặt các thư viện cần thiết

```bash
pip install -r requirements.txt
```

---

## Step 3: Run Backend Server

Sau khi cài đặt hoàn tất, chạy backend bằng lệnh:

```bash
uvicorn app.main:app --reload
```

Nếu chạy thành công, server sẽ khởi động tại:

```text
http://127.0.0.1:8000
```

Tài liệu API (Swagger UI):

```text
http://127.0.0.1:8000/docs
```

## Troubleshooting

### ModuleNotFoundError

Nếu gặp lỗi:

```text
ModuleNotFoundError
```

Hãy kiểm tra:

* Đã kích hoạt môi trường ảo (`venv`) chưa.
* Đã chạy:

```bash
pip install -r requirements.txt
```

### MQTT Connection Failed

Kiểm tra:

* MQTT Broker đã được khởi động.
* File `my_mosquitto.conf` đúng cấu hình.
* Địa chỉ Broker trong backend khớp với Broker đang chạy.

---

### Port Already in Use

Nếu cổng `8000` đang được sử dụng:

```bash
uvicorn app.main:app --reload --port 8001
```
