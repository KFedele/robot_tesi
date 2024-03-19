#ifndef CustomRobotLibrary_h
#define CustomRobotLibrary_h

#include "Arduino.h"

class CustomRobotLibrary {
  public:
    CustomRobotLibrary(int matrix[4][4]);
    void turn_90_dx();
    void turn_180_dx();
    void turn_90_sx();
    void step_forward();
    void step_back();
    void movimentoADestra();
    void movimentoASinistra();
    void movimentoInBasso();
    void movimentoInAlto();
    void fillMatrix(int matrix[4][4]);
    void findIndex(int matrix[4][4],int num, int& row, int& col);
    int orientamento_corrente = 4;

  private:
    int ROTATION = 850;
    int STEP = 1400;
    
};

#endif
