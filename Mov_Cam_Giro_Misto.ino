#include "esp_camera.h"
#include <WiFi.h>
#include "Freenove_4WD_Car_For_ESP32.h"
#define GRID_ROW 4
#define ROTATION 850
#define STEP 700
#include <Wire.h>
#include <RTClib.h>

#define CAMERA_MODEL_WROVER_KIT // Has PSRAM
#include "camera_pins.h"

RTC_DS3231 rtc;

const char* ssid = "TIM-22909625";
const char* password = "WWDo4Iura2LYq49raLPQlMiE";
const char* serverAddress = "192.168.1.35";
const int serverPort = 12345;

void startCameraServer();
void setupLedFlash(int pin);
void notifyServer();

WiFiClient client;
void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_UXGA;
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  if (config.pixel_format == PIXFORMAT_JPEG) {
    if (psramFound()) {
      config.jpeg_quality = 1;
      config.fb_count = 2;
      config.grab_mode = CAMERA_GRAB_LATEST;
    } else {
      config.frame_size = FRAMESIZE_SVGA;
      config.fb_location = CAMERA_FB_IN_DRAM;
    }
  } else {
    config.frame_size = FRAMESIZE_240X240;
#if CONFIG_IDF_TARGET_ESP32S3
    config.fb_count = 2;
#endif
  }

#if defined(CAMERA_MODEL_ESP_EYE)
  pinMode(13, INPUT_PULLUP);
  pinMode(14, INPUT_PULLUP);
#endif

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  sensor_t * s = esp_camera_sensor_get();
  if (s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1);
    s->set_brightness(s, 1);
    s->set_saturation(s, -2);
  }
  if (config.pixel_format == PIXFORMAT_JPEG) {
    s->set_framesize(s, FRAMESIZE_QVGA);
  }

#if defined(CAMERA_MODEL_M5STACK_WIDE) || defined(CAMERA_MODEL_M5STACK_ESP32CAM)
  s->set_vflip(s, 1);
  s->set_hmirror(s, 1);
#endif

#if defined(CAMERA_MODEL_ESP32S3_EYE)
  s->set_vflip(s, 1);
#endif

#if defined(LED_GPIO_NUM)
  setupLedFlash(LED_GPIO_NUM);
#endif
  
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");

  startCameraServer();

  Serial.print("Camera Ready! Use 'http://");
  Serial.print(WiFi.localIP());
  Serial.println("' to connect");

   PCA9685_Setup();
  Serial.println("PCA9685 done!");
}

void loop() {
  while (!client.connect(serverAddress, serverPort)) {
    Serial.println("Failed to connect to server. Retrying in 0.1 seconds...");
    delay(100);  // Ritardo di 0.5 secondi tra i tentativi
  }

  Serial.println("Connected to server");

  notifyServer();
  step_forward();
  notifyServer();
  delay(1000);
  for (int i = 0; i < GRID_ROW; i++) {
    for (int j = 0; j < GRID_ROW - 1; j++) {
      step_forward();
      notifyServer();
      delay(1000);
    }

    turn_90_dx();
    notifyServer();
    delay(1000);

    step_forward();
    notifyServer();
    delay(1000);

    turn_90_dx();
    notifyServer();
    delay(1000);
    for (int j = 0; j < GRID_ROW - 1; j++) {
      step_forward();
      notifyServer();
      delay(1000);
    }

    turn_90_sx();
    notifyServer();
    delay(1000);

    step_forward();
    notifyServer();
    delay(1000);

    turn_90_sx();
    notifyServer();
    delay(1000);
  }
  // Chiudi la connessione
  client.stop();
  delay(5000);
}

void notifyServer() {


  // Costruisci la richiesta HTTP
  String request = "GET /capture?_cb=" + String(millis()) + " HTTP/1.1\r\n";
  request.concat("Host: " + String(serverAddress) + "\r\n\r\n");

  // Invia la richiesta HTTP
  client.print(request);

  Serial.println("Control request sent");

  // Aspetta la risposta dal server
  while (client.connected() && !client.available()) {
    delay(10);
  }

  // Leggi la risposta dal server
  String response = client.readStringUntil('\r');
  Serial.println("Server response: " + response);

}


void turn_90_dx() {
  Motor_Move(-ROTATION, -ROTATION, ROTATION, ROTATION);
  delay(1000);
  Motor_Move(0, 0, 0, 0);
}

void turn_90_sx() {
  Motor_Move(ROTATION, ROTATION, -ROTATION, -ROTATION);
  delay(1000);
  Motor_Move(0, 0, 0, 0);
}

void step_forward() {
  Motor_Move(-STEP, -STEP, -STEP, -STEP);
  delay(1000);
  Motor_Move(0, 0, 0, 0);
}
