import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.alerts import router as alerts_router
from app.api.control import router as control_router
from app.api.ecg import router as ecg_router
from app.api.predictions import router as predictions_router
from app.api.readings import router as readings_router
from app.config import settings
from app.db import Base, engine
from app.mqtt_client import set_event_loop, start_mqtt
from app.websocket_manager import manager

mqtt_client_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global mqtt_client_instance

    Base.metadata.create_all(bind=engine)

    loop = asyncio.get_running_loop()
    set_event_loop(loop)

    mqtt_client_instance = start_mqtt()
    print("MQTT started")

    yield

    if mqtt_client_instance:
        mqtt_client_instance.loop_stop()
        mqtt_client_instance.disconnect()
        print("MQTT stopped")


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(readings_router)
app.include_router(ecg_router)
app.include_router(alerts_router)
app.include_router(predictions_router)
app.include_router(control_router)


@app.get("/")
def root():
    return {"message": "IoT Health Monitor Backend is running"}


@app.websocket("/ws/live")
async def websocket_live(websocket: WebSocket):
    await manager.connect(websocket)
    print("WS CONNECTED:", websocket.client)

    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("WS DISCONNECTED:", websocket.client)
        manager.disconnect(websocket)
    except Exception as e:
        print("WS ERROR:", e)
        manager.disconnect(websocket)
