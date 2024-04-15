#include "SailOS/SailOS.h"
#include "SailOS/SailOS.cpp"

Boat boat;

void setup(){
  boat.begin(28800);
}

void loop(){
  boat.update();
}
