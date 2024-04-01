#include "Arduino.h"
#include "SailOS.h"

Boat::Boat(){
}

void Boat::begin(int baud){
  radio.begin(baud);             //This is of type REYAX, so REYAX functions should be called on it
}

void Boat::update(){
    // Execute on set interval
    if(one.passed()) {               // Do every second
    }
    if (two.passed()) {              // Do every two seconds
    }
    if (three.passed()) {            // Do every three seconds
        if(flag.waiting_for_start){
            broadcast_start_signal();
        }
    }
    if (five.passed()) {             // Do every five seconds
    }
    if (ten.passed()) {              // Do every ten seconds
    }
    // Execute on every loop cycle
    if(command.read()){                         // If a new command is recieved
        command.execute(command.active);      // Execute the command
    }
}


void Boat::broadcast_start_signal(){
    radio.send(command.start);
    radio.waitSent();
}
