#include "Arduino.h"
#include "SailOS.h"

Boat::Boat(){
}

void Boat::begin(int baud){
  radio.begin(baud);             //This is of type REYAX, so REYAX functions should be called on it
}
