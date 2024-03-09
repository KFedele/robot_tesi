#include <Wire.h>
#include <WiFi.h>
#include <MPU6050_tockn.h>
#include <cmath>

MPU6050 mpu6050(Wire);

const char* ssid = "TIM-22909625";
const char* password = "WWDo4Iura2LYq49raLPQlMiE";
const char* serverAddress = "192.168.1.35";
const int serverPort = 12345;

WiFiClient client;
float dt = 0.1;
int c_max=5;
float pos_x = 0;
float pos_y = 0;
float displacement_x = 0;
float displacement_y = 0;
long last_timestamp = 0;
float latest_accel_x=0;
float latest_accel_y=0;
int cont_x=0;
int cont_y=0;

void setup() {
  Serial.begin(9600);
  Wire.begin();
  mpu6050.begin();
  //mpu6050.calcGyroOffsets(true);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print("Connessione WiFi in corso...");
    WiFi.begin(ssid, password);
    delay(5000);
  }

  Serial.println("");
  Serial.println("WiFi connected");

  while (!client.connect(serverAddress, serverPort)) {
    Serial.println("Connection to server failed! Retrying...");
    delay(5000);
  }

  Serial.println("Connected to the server");
}

void loop() {
  mpu6050.update();

  if (millis() - last_timestamp > 100) {
    calcPos();
    last_timestamp = millis();
  }
}

void calcPos() {
  float curr_accel_x = mpu6050.getAccX() * 9.81;
  float curr_accel_y = mpu6050.getAccY() * 9.81;
//filtro 1 (x,y)
  if (-2.0 <= curr_accel_x && curr_accel_x <= 1.0) {
    curr_accel_x = 0;
  }

  if (-1.5 <= curr_accel_y && curr_accel_y <= 1.5) {
    curr_accel_y = 0;
  }
//filtro 2 (rimozione accel extra)
  if(latest_accel_x != 0 && cont_x==0){
      cont_x=cont_x+1;
  }
  if (latest_accel_x != 0 || (1 <= cont_x && cont_x <= c_max)) {
      curr_accel_x = 0;
      cont_x = cont_x + 1;
      if (cont_x == c_max) {
          cont_x = 0;
      }
  }

  if(latest_accel_y != 0 && cont_y==0){
      cont_y=cont_y+1;
  }
  if (latest_accel_y != 0 || (1 <= cont_y && cont_y <= c_max)) {
      curr_accel_y = 0;
      cont_y = cont_y + 1;
      if (cont_y == c_max) {
          cont_y = 0;
      }
  }


  if (fabs(curr_accel_x)>fabs(curr_accel_y)){
    curr_accel_y=0;
  }
  else if (fabs(curr_accel_x)<fabs(curr_accel_y)){
    curr_accel_x=0;
  }
  else{

  } 

  //filtro x
  if (curr_accel_x>0)
  {
    curr_accel_x=2.0;
  }
  else if (curr_accel_x<0){
    curr_accel_x=-2.0;
  }
  else{
    curr_accel_x=0;
  }


  //filtro y
  
  if (curr_accel_y>0)
  {
    curr_accel_y=2.0;
  }
  else if (curr_accel_y<0){
    curr_accel_y=-2.0;
  }
  else {
    curr_accel_y=0;
  }

  
  float curr_vel_x = curr_accel_x * dt;
  float curr_vel_y = curr_accel_y * dt;

  // float disp_x=0.0;
  // float disp_y=0.0;
  // disp_x=curr_vel_x*dt;
  // disp_y=curr_vel_y*dt;


  displacement_x += curr_vel_x * dt;
  displacement_y += curr_vel_y * dt;

  pos_x = displacement_x;
  pos_y = displacement_y;

  String message = "a/g: \t";
  message += pos_x;
  message += "\t";
  message += pos_y;
  message += "\t";
  message += mpu6050.getAccZ() * 9.81;
  message += "\t";
  message += mpu6050.getGyroAngleX();
  message += "\t";
  message += mpu6050.getGyroAngleY();
  message += "\t";
  message += mpu6050.getGyroAngleZ();
  message += "\n";

  client.print("GET / HTTP/1.1\r\n");
  client.print("Host: ");
  client.print(serverAddress);
  client.print("\r\n");
  client.print("Connection: keep-alive\r\n");
  client.print("Content-Length: ");
  client.print(message.length());
  client.print("\r\n\r\n");
  client.print(message);
  Serial.println(message);
  Serial.println(mpu6050.getAccX()*9.81);
  Serial.println("\t");
  Serial.println(mpu6050.getAccY()*9.81);
  Serial.println("\n");
  Serial.println("Dati inviati con successo!");
  latest_accel_x=curr_accel_x;
  latest_accel_y=curr_accel_y;
}
