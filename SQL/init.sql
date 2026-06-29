CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    device_code VARCHAR(50) UNIQUE NOT NULL,
    patient_name VARCHAR(100),
    location VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sensor_readings (
    id BIGSERIAL PRIMARY KEY,
    device_id INT NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    ts TIMESTAMPTZ NOT NULL,
    heart_rate FLOAT,
    spo2 FLOAT,
    systolic_bp FLOAT,
    diastolic_bp FLOAT,
    body_temp FLOAT,
    ecg_value FLOAT,
    signal_quality FLOAT,
    battery_level FLOAT,
    raw_payload JSONB
);

CREATE TABLE IF NOT EXISTS ecg_packets (
    id BIGSERIAL PRIMARY KEY,
    device_id INT NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    ts TIMESTAMPTZ NOT NULL,
    sampling_rate INT,
    samples JSONB
);

CREATE TABLE IF NOT EXISTS alerts (
    id BIGSERIAL PRIMARY KEY,
    device_id INT NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    ts TIMESTAMPTZ NOT NULL,
    alert_type VARCHAR(50),
    severity VARCHAR(20),
    message TEXT,
    value JSONB
);

CREATE TABLE IF NOT EXISTS predictions (
    id BIGSERIAL PRIMARY KEY,
    device_id INT NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    ts TIMESTAMPTZ NOT NULL,
    target_time TIMESTAMPTZ,
    model_name VARCHAR(100),
    predicted_hr FLOAT,
    predicted_spo2 FLOAT,
    predicted_systolic_bp FLOAT,
    predicted_diastolic_bp FLOAT,
    risk_score FLOAT,
    risk_label VARCHAR(50),
    meta JSONB
);
