#include "Arduino.h"
#include "SailOS.h"

Boat::Boat(){
}

void Boat::begin(){
  radio.begin(9600);  //This is of type REYAX, so REYAX functions should be called on it
  initiatePeripherals();
}

// Check for connection signal every one second
void Boat::connect(){   
  while(true){                    // Repeat until command recieved                        
    if(radio.available() > 0){    // Check if the radio has recieved a transmission
      if(strncmp(radio.readData, "START", 5) == false)   // If there is data, check if it the start command
        radio.send("START");      // If so, send a start response
        if(! radio.waitSent()){   // Wait for radio to send
                                  // If there is an error, sound error tone
      }
    }
    delay(1000);
  }
}



//void Boat::transmit(String data){
//  _transmit(data);
//}
//
//
//String Boat::getCommand(){
//  String command = _readCommand();
//  return command;
//}
//
//void Boat::connect(){
//  monitorPrintln("Waiting...");
//  while(true){
//      if(_readCommand() == "READY"){
//        _transmit("READY");
//        monitorPrintln("Recieved Signal");
//        for(int i = 0; i < 10; i++){
//          if(_readCommand() == "START"){
//            _transmit("ACTIVE");
//            break;
//          }
//          delay(500);
//        }
//      }
//   }
//}
//
//void Boat::setManualControl(){
//  autoMode = false;
//}
//
//void Boat::setAutonomousMode(){
//  autoMode = true;
//}
//
//void Boat::sendMode(){
//  Serial.print("MODE=");
//  Serial.println(autoMode);
//}
