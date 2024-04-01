#include "SailOS/SailOS.h"
#include "SailOS/SailOS.cpp"

Boat boat;

void setup(){
  boat.begin();
}

void loop(){
  boat.update();
}
