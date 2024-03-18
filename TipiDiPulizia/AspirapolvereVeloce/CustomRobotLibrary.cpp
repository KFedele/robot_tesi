#include "Arduino.h"
#include "CustomRobotLibrary.h"
#include "Freenove_4WD_Car_For_ESP32.h"

CustomRobotLibrary::CustomRobotLibrary(int matrix[4][4]) {
    // Inizializza le variabili di classe se necessario
    orientamento_corrente = 4; // Inizializza orientamento_corrente a un valore di default
    fillMatrix(matrix); // Chiamata alla funzione per riempire la matrice all'avvio
}


void CustomRobotLibrary::turn_90_dx() {
  Motor_Move(-ROTATION, -ROTATION, ROTATION, ROTATION);
  delay(1000);
  Motor_Move(0, 0, 0, 0);
}

void CustomRobotLibrary::turn_180_dx() {
  Motor_Move(-ROTATION*2, -ROTATION*1.5, ROTATION*1.5, ROTATION*1.5);
  delay(1000);
  Motor_Move(0, 0, 0, 0);
}

void CustomRobotLibrary::turn_90_sx() {
  Motor_Move(ROTATION, ROTATION, -ROTATION, -ROTATION);
  delay(1000);
  Motor_Move(0, 0, 0, 0);
}

void CustomRobotLibrary::step_forward() {
  Motor_Move(-STEP, -STEP, -STEP, -STEP);
  delay(400);
  Motor_Move(0, 0, 0, 0);
}

void CustomRobotLibrary::step_back() {
  Motor_Move(STEP, STEP, STEP, STEP);
  delay(400);
  Motor_Move(0, 0, 0, 0);
}

void CustomRobotLibrary::movimentoADestra(){
  switch (orientamento_corrente) {
    case 1:
      turn_90_sx();
      delay(1000);
      step_back();
      orientamento_corrente=4;
      break;

    case 2:
      turn_90_dx();
      delay(1000);
      step_back();
      orientamento_corrente=4;
      break;

    case 3:
      //step_forward();
      turn_180_dx();
      step_back();
      orientamento_corrente=4;
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

void CustomRobotLibrary::movimentoASinistra(){
  switch (orientamento_corrente) {
    case 1:
      turn_90_dx();
      delay(1000);
      step_back();
      orientamento_corrente=3;
      break;

    case 2:
      turn_90_sx();
      delay(1000);
      step_back();
      orientamento_corrente=3;
      break;

    case 3:
      step_back();
      orientamento_corrente=3;
      break;

    case 4:
     // step_forward();
      turn_180_dx();
      step_back();
      orientamento_corrente=3;
      break;

    default:
      // Codice da eseguire se il numero non corrisponde a nessun caso
      Serial.println("Error mov sinistra");
      break;
  }  
}

void CustomRobotLibrary::movimentoInBasso(){
  switch (orientamento_corrente) {
    case 1:
      // Rivolto verso l'alto
      step_back();
      orientamento_corrente=1;
      break;

    case 2:
      // Rivolto verso il basso
      turn_180_dx();
      step_back();
      //step_forward();
      orientamento_corrente=1;
      break;

    case 3:
      // Rivolto a destra
      turn_90_sx();
      delay(1000);
      step_back();
      orientamento_corrente=1;
      break;

    case 4:
      // Rivolto a sinistra
      turn_90_dx();
      delay(1000);
      step_back();
      orientamento_corrente=1;
      break;

    default:
      // Codice da eseguire se il numero non corrisponde a nessun caso
      Serial.println("Error mov basso");
      break;
  }  
}

void CustomRobotLibrary::movimentoInAlto(){
  switch (orientamento_corrente) {
    case 1:
      // Codice da eseguire se il numero è 1
      turn_180_dx();
      step_back();
     // step_forward();
      orientamento_corrente=2;
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
      step_back();
      orientamento_corrente=2;
      break;

    case 4:
      // Codice da eseguire se il numero è 3
      turn_90_dx();
      delay(1000);
      step_back();
      orientamento_corrente=2;
      break;

    default:
      // Codice da eseguire se il numero non corrisponde a nessun caso
      Serial.println("Error mov in alto");
      break;
  }
}

void CustomRobotLibrary::fillMatrix(int matrix[4][4]) {
  int count = 1;

  // Riempi la matrice con i numeri da 1 a 16
  for (int i = 0; i < 4; i++) {
    for (int j = 0; j < 4; j++) {
      matrix[i][j] = count++;
    }
  }
}

void CustomRobotLibrary::findIndex(int matrix[4][4],int num, int& row, int& col) {
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
