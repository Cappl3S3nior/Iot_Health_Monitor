//#include <WiFi.h>
#include <ArduinoJson.h>
#include <Wire.h>

#include <OneWire.h>
#include <DallasTemperature.h>

#include "MAX30100_PulseOximeter.h"
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

//=====================
// Cấu hình ECG tránh block
//=====================
const int ECG_SAMPLING_RATE = 250;
const unsigned long ECG_SAMPLE_DELAY_US = 1000000UL / ECG_SAMPLING_RATE; // 4000us
const int ECG_SAMPLES_PER_PACKET = 50;

int ecgBuffer[ECG_SAMPLES_PER_PACKET];
int ecgSampleCount = 0;
unsigned long lastEcgSampleUs = 0;

//=====================
//gửi Telemetry và ECG Packet
//=====================
const char* DEVICE_CODE = "esp32_01";

const unsigned long TELEMETRY_INTERVAL_MS = 3000;

//=====================
// Màn OLED
//=====================
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

Adafruit_SSD1306 display(
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    &Wire,
    -1);

//=====================
// DS18B20
//=====================
#define ONE_WIRE_BUS 6

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature tempSensor(&oneWire);

//=====================
// AD8232
//=====================
#define ECG_PIN 4
#define LO_PLUS 15
#define LO_MINUS 16

//=====================
// MAX30100
//=====================
PulseOximeter pox;

// =====================
// Global sensor values
// =====================

float systolicBP = 0;
float diastolicBP = 0;
float heartRate = 0;
float spo2 = 0;
float bodyTemp = 0;

int latestEcgValue = 0;

unsigned long lastTelemetryMs = 0;
unsigned long lastSensorReadMs = 0;
unsigned long lastOledUpdateMs = 0;
unsigned long lastReportMs = 0;

// Khai báo Task chạy ngầm cho MAX30100 trên Core 0
TaskHandle_t TaskMAX30100;
// Khóa Mutex
SemaphoreHandle_t i2cMutex;

// void onBeatDetected()
// {
//     Serial.println("Beat!");
// }

void updateOLED(
    float hr,
    float spo2,
    float temp,
    float sbp,
    float dbp,
    int ecg)
{
    //if (xSemaphoreTake(i2cMutex, pdMS_TO_TICKS(30)) == pdTRUE) {
        display.clearDisplay();

        display.setTextSize(1);
        display.setTextColor(SSD1306_WHITE);

        display.setCursor(0,0);
        display.print("HR:");
        display.print(hr,0);

        display.setCursor(64,0);
        display.print("SpO2:");
        display.print(spo2,0);

        display.setCursor(0,20);
        display.print("Temp:");
        display.print(temp,1);
        display.print("C");

        display.setCursor(0, 32);
        display.print("BP:");
        display.print(sbp, 0);
        display.print("/");
        display.print(dbp, 0);

        display.setCursor(0,40);
        display.print("ECG:");
        display.print(ecg);

        display.display();

    //     //trả khóa
    //     xSemaphoreGive(i2cMutex);
    // }
}

// =====================
// Read one ECG sample
// =====================
int readECGSample() {
  if (digitalRead(LO_PLUS) == HIGH || digitalRead(LO_MINUS) == HIGH) {
    return 0; // electrode off
  }
  return analogRead(ECG_PIN);
}

// =======================
// Gửi telemetry qua Serial
// =======================
void sendTelemetry(){
  StaticJsonDocument<512> doc;

  doc["type"] = "telemetry";
  doc["device_code"] = DEVICE_CODE;
  doc["heart_rate"] = heartRate;
  doc["spo2"] = spo2;
  doc["systolic_bp"] = systolicBP;
  doc["diastolic_bp"] = diastolicBP;
  doc["body_temp"] = bodyTemp;
  doc["ecg_value"] = latestEcgValue;
  doc["signal_quality"] = 0.9; // tạm hardcode
  doc["battery_level"] = 100;  // tạm hardcode

  serializeJson(doc, Serial);
  Serial.println(); // mỗi message 1 dòng
}

// =======================
// Gửi ECG packet qua Serial
// =======================
void sendECGPacket() 
{
  StaticJsonDocument<2048> doc;

  doc["type"] = "ecg";
  doc["device_code"] = DEVICE_CODE;
  doc["sampling_rate"] = ECG_SAMPLING_RATE;

  JsonArray samples = doc.createNestedArray("samples");

  for (int i = 0; i < ECG_SAMPLES_PER_PACKET; i++) {
    samples.add(ecgBuffer[i]);
  }

  serializeJson(doc, Serial);
  Serial.println();
}

//Hàm thực thi riêng của Core 0: Độc quyền xử lý cập nhật dữ liệu MAX30100
void Core0TaskCode( void * pvParameters ){
  for(;;){
    pox.update();
    vTaskDelay(1); // Trả lại 1ms cho hệ điều hành tránh lỗi Watchdog trì trệ
  }
}

void setup()
{
    Serial.begin(115200);

    //KHỞI TẠO KHÓA MUTEX TRƯỚC KHI CHẠY I2C
    i2cMutex = xSemaphoreCreateMutex();

    // Cấu hình DS18B20 chạy không chặn (ASYNC)
    tempSensor.begin();
    tempSensor.setWaitForConversion(false);

    // ECG
    pinMode(LO_PLUS, INPUT);
    pinMode(LO_MINUS, INPUT);

    // MAX30100
    Wire.begin(18,17);
    Wire.setClock(400000);


    pox.setIRLedCurrent(MAX30100_LED_CURR_4_4MA);


    // OLED 128x64
    if(!display.begin(
        SSD1306_SWITCHCAPVCC,
        0x3C))
    {
        while(1);
    }

    display.clearDisplay();

    display.setTextSize(2);
    display.setTextColor(SSD1306_WHITE);

    display.setCursor(0,0);
    display.println("Hello");

    display.display();
    delay(1000);

    if (!pox.begin())
    {
        while (1);
    }

    // ESP32-S3 ADC 12-bit
    analogReadResolution(12);   // giá trị 0 -> 4095

    // Kích hoạt lệnh đo nhiệt độ đầu tiên để sẵn sàng cho vòng loop
    tempSensor.requestTemperatures();

    //TẠO LUỒNG CHẠY RIÊNG CHO MAX30100 TRÊN CORE 0
    xTaskCreatePinnedToCore(
      Core0TaskCode,      /* Tên hàm thực thi task */
      "TaskMAX30100",     /* Tên định danh của task */
      4096,               /* Dung lượng bộ nhớ Stack cấp cho task (bytes) */
      NULL,               /* Tham số truyền vào */
      2,                  /* Độ ưu tiên của task (Càng cao càng ưu tiên) */
      &TaskMAX30100,      /* Biến quản lý task */
      0                   /* Chỉ định chạy trên Core 0 */
    );
}

void loop()
{ 
    // Lấy mẫu ECG bằng Micros() - Hoàn toàn không gây nghẽn dữ liệu
    if (micros() - lastEcgSampleUs >= ECG_SAMPLE_DELAY_US) {
        lastEcgSampleUs = micros();
        
        latestEcgValue = readECGSample();
        ecgBuffer[ecgSampleCount] = latestEcgValue;
        ecgSampleCount++;

        // Khi gom đủ 50 mẫu (đủ 1 gói), tiến hành gửi dữ liệu
        if (ecgSampleCount >= ECG_SAMPLES_PER_PACKET) {
            sendECGPacket();
            ecgSampleCount = 0; // reset bộ đếm mẫu
        }
    }

    // Mỗi 1 giây đọc dữ liệu
    if (millis() - lastSensorReadMs > 1000)
    {
        // HR + SpO2
        if (xSemaphoreTake(i2cMutex, pdMS_TO_TICKS(10)) == pdTRUE) {
            heartRate = pox.getHeartRate();
            spo2 = pox.getSpO2();
            xSemaphoreGive(i2cMutex);
        }
        //DS18B20
        bodyTemp = tempSensor.getTempCByIndex(0);
        tempSensor.requestTemperatures();
        

        lastSensorReadMs = millis();

    }

    //Cập nhật 1.2 giây
    if (millis() - lastOledUpdateMs > 1200) {
        lastOledUpdateMs = millis();
        updateOLED(heartRate, spo2, bodyTemp, systolicBP, diastolicBP, latestEcgValue);
    }

    // gửi telemetry mỗi 3 giây
    if (millis() - lastTelemetryMs >= TELEMETRY_INTERVAL_MS) {
        lastTelemetryMs = millis();
        sendTelemetry();
    }
}