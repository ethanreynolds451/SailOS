#include "RTTL/RTTL.h"
#include "RTTL/RTTL.cpp"

RTTL sound(8);
 
void setup(){
  sound.begin();
}

void loop(){
  sound.play("Error:d=4,o=6,b=127:f,c#,f,c#");
  delay(5000);
}
