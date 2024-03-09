#include <WiFi.h>
#include "Freenove_4WD_Car_For_ESP32.h"
#define GRID_ROW 4
#define ROTATION 850
#define STEP 1400
#include <Wire.h>

//nuova libreria

#include <vector>


const char* ssid = "TIM-22909625";
const char* password = "WWDo4Iura2LYq49raLPQlMiE";
const char* serverAddress = "192.168.1.35";
const int serverPort = 12345;
WiFiClient client;

//var nuove
int matrix[4][4];  // Definisci una matrice 4x4
int current_position=1;
int future_position=0;
std::vector<int> receivedNumbers;  // Utilizzo di std::vector per la dimensione dinamica
int orientamento_corrente=3; //Sarebbe l'orientamento del robot, la direzione della parte anteriore; 1: su, 2: giù, 3: destra, 4: sinistra
int row_curr=1;
int col_curr=1;
int row_fut=0;
int col_fut=0;



void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();
  Buzzer_Setup();
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  PCA9685_Setup();
  Serial.println("PCA9685 done!");
  fillMatrix();  // Richiama la funzione per riempire la matrice
}

void loop() {
  // put your main code here, to run repeatedly:
  while (!client.connect(serverAddress, serverPort)) {
    Serial.println("Failed to connect to server. Retrying in 0.1 seconds...");
    delay(100);  // Ritardo di 0.5 secondi tra i tentativi
  }
  // Leggi i numeri inviati dal server
  receivedNumbers.clear();  // Pulisci il vettore prima di ricevere nuovi numeri
  while (client.available()) {
      String line = client.readStringUntil('\n');
      // Verifica se il messaggio di "fine trasmissione" è stato ricevuto
      if (line == "END") {
          break;
      }
      receivedNumbers.push_back(line.toInt());
  }
  client.stop();
  for (int i=0;i<receivedNumbers.size();i++){
    future_position=receivedNumbers[i];
    findIndex(future_position,row_fut,col_fut);
    findIndex(current_position,row_curr,col_curr);
    if(row_curr==row_fut && col_curr==col_fut){
      //fermo
      delay(1000);
      Buzzer_Alert(3,1);
    }
    else if(row_curr==row_fut){ //dx o sx
     if (col_fut==col_curr+1){

      movimentoADestra();
      delay(1000);
      Buzzer_Alert(3,1);
     }
     else{
      movimentoASinistra();
      delay(1000);
      Buzzer_Alert(3,1);
     }

    }
    else {
     if (row_fut==row_curr+1){

      movimentoInBasso();
      delay(1000);
      Buzzer_Alert(3,1);
     }
     else{
      movimentoInAlto();
      delay(1000);
      Buzzer_Alert(3,1);
     }

    }
  current_position=future_position;
  }


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
  delay(400);
  Motor_Move(0, 0, 0, 0);
}

void step_back() {
  Motor_Move(STEP, STEP, STEP, STEP);
  delay(400);
  Motor_Move(0, 0, 0, 0);
}

void movimentoADestra(){
switch (orientamento_corrente) {
  case 1:
 
    turn_90_dx();
    delay(1000);
    step_forward();
    orientamento_corrente=3;
    break;

  case 2:

    turn_90_sx();
    delay(1000);
    step_forward();
    orientamento_corrente=3;
    break;

  case 3:

    step_forward();
    orientamento_corrente=3;
    break;

  case 4:

    step_back();
    orientamento_corrente=4;
    break;

  default:
    // Codice da eseguire se il numero non corrisponde a nessun caso
    Serial.println("Error mov destra");
    break;
}  



}

void movimentoASinistra(){
  switch (orientamento_corrente) {
  case 1:
 
    turn_90_sx();
    delay(1000);
    step_forward();
    orientamento_corrente=4;
    break;

  case 2:

    turn_90_dx();
    delay(1000);
    step_forward();
    orientamento_corrente=4;
    break;

  case 3:

    step_back();
    orientamento_corrente=3;
    break;

  case 4:

    step_forward();
    orientamento_corrente=4;
    break;

  default:
    // Codice da eseguire se il numero non corrisponde a nessun caso
    Serial.println("Error mov sinistra");
    break;
}  

}

void movimentoInBasso(){

switch (orientamento_corrente) {
  case 1:
    // Rivolto verso l'alto
    step_back();
    orientamento_corrente=1;
    break;

  case 2:
    // Rivolto verso il basso
    step_forward();
    orientamento_corrente=2;
    break;

  case 3:
    // Rivolto a destra
    turn_90_dx();
    delay(1000);
    step_forward();
    orientamento_corrente=2;
    break;
  case 4:
    // Rivolto a sinistra
    turn_90_sx();
    delay(1000);
    step_forward();
    orientamento_corrente=2;
    break;
  // Aggiungi altri casi se necessario

  default:
    // Codice da eseguire se il numero non corrisponde a nessun caso
    Serial.println("Error mov basso");
    break;
}  



}

void movimentoInAlto(){

  switch (orientamento_corrente) {
  case 1:
    // Codice da eseguire se il numero è 1
    step_forward();
    orientamento_corrente=1;
    break;

  case 2:
    // Codice da eseguire se il numero è 2
    step_back();
    orientamento_corrente=2;
    break;

  case 3:
    // Codice da eseguire se il numero è 3
    turn_90_sx();
    delay(1000);
    step_forward();
    orientamento_corrente=1;
    break;
  case 4:
    // Codice da eseguire se il numero è 3
    turn_90_dx();
    delay(1000);
    step_forward();
    orientamento_corrente=1;
    break;
  // Aggiungi altri casi se necessario

  default:
    // Codice da eseguire se il numero non corrisponde a nessun caso
    Serial.println("Error mov in alto");
    break;
}

  
}


void fillMatrix() {
  int count = 1;

  // Riempi la matrice con i numeri da 1 a 16
  for (int i = 0; i < 4; i++) {
    for (int j = 0; j < 4; j++) {
      matrix[i][j] = count++;
    }
  }
}
void findIndex(int num, int& row, int& col) {
  // Trova l'indice di riga e di colonna del numero nella matrice
  for (int i = 0; i < 4; i++) {
    for (int j = 0; j < 4; j++) {
      if (matrix[i][j] == num) {
        row = i + 1;  // Incrementa l'indice di riga di 1
        col = j + 1;  // Incrementa l'indice di colonna di 1
        return;  // Termina la funzione una volta trovato il numero
      }
    }
  }
}

