#include <WiFi.h>
#include "Freenove_4WD_Car_For_ESP32.h"
#define GRID_ROW 4

#include <Wire.h>
#include <RTClib.h>
//nuova libreria

#include <vector>

//libreria personalizzata
#include "CustomRobotLibrary.h"

//Per telecamera
#define CAMERA_MODEL_WROVER_KIT // Has PSRAM
#include "esp_camera.h"
#include "camera_pins.h"

#define MAX_RETRY_ATTEMPTS 100


//Metodi per telecamera
void startCameraServer();
void setupLedFlash(int pin);
void notifyServer();



//Config WiFi
const char* ssid = "TIM-22909625";
const char* password = "WWDo4Iura2LYq49raLPQlMiE";
const char* serverAddress = "192.168.1.52";
const int serverPort = 12345;
WiFiClient client;

//Var nuove per movimenti in fase di pulizia
int matrix[4][4];  // Definisci una matrice 4x4

//Instanzia classe customizzata per i movimenti del robot

CustomRobotLibrary customRobot(matrix);
int current_position=1;
int future_position=0;
std::vector<int> receivedNumbers;  // Utilizzo di std::vector per la dimensione dinamica
//int orientamento_corrente=4; //Sarebbe l'orientamento del robot, la direzione della parte anteriore; 1: su, 2: giù, 3: destra, 4: sinistra
int row_curr=1;
int col_curr=1;
int row_fut=0;
int col_fut=0;



void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

/////////////////////////////////////////////AREA CONFIG TELECAMERA


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


////////////////////////////////////////////////////////////////////////



  Buzzer_Setup();
  customRobot.orientamento_corrente = 4;
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");

  /////////START SERVER TELECAMERA

  startCameraServer();

  Serial.print("Camera Ready! Use 'http://");
  Serial.print(WiFi.localIP());
  Serial.println("' to connect");

///////////////////////


  PCA9685_Setup();
  Serial.println("PCA9685 done!");
  customRobot.fillMatrix(matrix);  // Richiama la funzione per riempire la matrice
}

void loop() {
  int orientamento_corrente = customRobot.orientamento_corrente;
  // put your main code here, to run repeatedly:
  while (!client.connect(serverAddress, serverPort)) {
    Serial.println("Failed to connect to server. Retrying in 0.1 seconds...");
    delay(100);  // Ritardo di 0.5 secondi tra i tentativi
  }


  ////////////////////RICEZIONE MINI-PIANO
  // Leggi i numeri inviati dal server
  receivedNumbers.clear();  // Pulisci il vettore prima di ricevere nuovi numeri

  getVectorFromServer();

  // Fine del ciclo loop, invia un messaggio al server di fine operazione
  //client.stop();  // Chiudi la connessione con il server


/////////////PULIZIA
  while (!client.connect(serverAddress, serverPort)) {
    Serial.println("Failed to connect to server. Retrying in 0.1 seconds...");
    delay(100);  // Ritardo di 0.5 secondi tra i tentativi
  }
  current_position=receivedNumbers[0];
  for (int i=0;i<receivedNumbers.size();i++){
    
    future_position=receivedNumbers[i];
    customRobot.findIndex(matrix,future_position,row_fut,col_fut);
    customRobot.findIndex(matrix,current_position,row_curr,col_curr);
    if(row_curr==row_fut && col_curr==col_fut){
      //fermo
      delay(1000);
      Buzzer_Alert(3,1);
      //notifyServer();
    }
    else if(row_curr==row_fut){ //dx o sx
     if (col_fut==col_curr+1){

      customRobot.movimentoADestra();

      delay(1000);
      Buzzer_Alert(3,1);
      notifyServer();
      delay(1000);
     }
     else{
      customRobot.movimentoASinistra();

      delay(1000);
      Buzzer_Alert(3,1);
      notifyServer();
      delay(1000);
     }

    }
    else {
     if (row_fut==row_curr+1){

      customRobot.movimentoInBasso();
      delay(1000);
      Buzzer_Alert(3,1);
      notifyServer();
      delay(1000);
      
     }
     else{
      customRobot.movimentoInAlto();
      Buzzer_Alert(3,1);
      notifyServer();
      delay(1000);

     }

    }
  current_position=future_position;
  }
  customRobot.step_back();
  notifyServer();

  delay(5000);
  

}

/////////////////////////Per inviare le foto al server

void notifyServer() {
  // Costruisci la richiesta HTTP
  while (!client.connect(serverAddress, serverPort)) {
  Serial.println("Failed to connect to server. Retrying in 0.1 seconds...");
  delay(100);  // Ritardo di 0.5 secondi tra i tentativi
}
  String request = "GET /capture?_cb=" + String(millis()) + " HTTP/1.1\r\n";
  request.concat("Host: " + String(serverAddress) + "\r\n\r\n");

  // Invia la richiesta HTTP
  client.print(request);



  // Aspetta la risposta dal server
  while (client.connected() && !client.available()) {
    delay(10);
  }
  // Aspetta la risposta dal server
  int retryCount = 0;
  while (retryCount < MAX_RETRY_ATTEMPTS && !client.available()) {
    delay(10);
    retryCount++;
  }


  // Leggi la risposta dal server se disponibile
  String response="";
  if (client.available()) {
    response = client.readStringUntil('\r');
    Serial.println("Server response: " + response);
  } else {
    Serial.println("No response from server after " + String(MAX_RETRY_ATTEMPTS) + " attempts");
    // Gestire l'errore o interrompere l'esecuzione
  }
  client.stop();
}



void getVectorFromServer() {
  if (client.connect(serverAddress, serverPort)) {
    Serial.println("Connected to server");
    client.println("GET /get_vector HTTP/1.1");
    client.println("Host: " + String(serverAddress));
    client.println("Connection: close");
    client.println();
  } else {
    Serial.println("Connection to server failed");
    return; // Esci dalla funzione se la connessione fallisce
  }

  // Attendi che la risposta sia disponibile
  while (client.connected() && !client.available()) {
    delay(10);
  }

  // Verifica se la risposta è disponibile
  if (client.available()) {
    String response = client.readString();
    Serial.println("Server response: " + response);

    int vectorStart = response.indexOf("[");
    int vectorEnd = response.indexOf("]", vectorStart);
    if (vectorStart != -1 && vectorEnd != -1) {
      String vectorString = response.substring(vectorStart, vectorEnd + 1);
      Serial.print("Received vector from server: ");
      Serial.println(vectorString);

      int miniPianoNumberStart = response.indexOf("mini_piano_number\": ") + 20;
      int miniPianoNumberEnd = response.indexOf(",", miniPianoNumberStart);
      String miniPianoNumberString = response.substring(miniPianoNumberStart, miniPianoNumberEnd);
      int miniPianoNumber = miniPianoNumberString.toInt();
      Serial.print("Mini-piano number: ");
      Serial.println(miniPianoNumber);

      receivedNumbers.clear();
      String numString = "";
      for (int i = 0; i < vectorString.length(); i++) {
        char c = vectorString.charAt(i);
        if (isdigit(c) || c == '-') { // Considera anche i numeri negativi
          numString += c;
        } else {
          if (numString != "") {
            receivedNumbers.push_back(numString.toInt());
            numString = "";
          }
        }
      }

      if (numString != "") {
        receivedNumbers.push_back(numString.toInt());
      }
    } else {
      Serial.println("Failed to parse vector from server response.");
    }
  } else {
    Serial.println("No response received from server.");
  }
}
