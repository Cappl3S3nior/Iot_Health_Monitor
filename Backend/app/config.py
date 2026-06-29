from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "IoT Health Monitor Backend"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    MQTT_BROKER: str
    MQTT_PORT: int = 1883
    MQTT_USERNAME: str = ""
    MQTT_PASSWORD: str = ""
    MQTT_TOPIC_TELEMETRY: str = "healthcare/+/telemetry"
    MQTT_TOPIC_ECG: str = "healthcare/+/ecg"

    class Config:
        env_file = ".env"


settings = Settings()
