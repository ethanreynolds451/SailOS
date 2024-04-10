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
        if(flag.broadcast_data){
            broadcast_data();
        }
    }
    if (two.passed()) {              // Do every two seconds

    }
    if (three.passed()) {            // Do every three seconds
    }
    if (five.passed()) {             // Do every five seconds
    }
    if (ten.passed()) {              // Do every ten seconds
    }
    // Execute on every loop cycle
    command.read();                // Check for new command and execute if recieved
}

void Boat::read_data(){
    radio.dataAdd(Default::data_header);
}

void Boat::broadcast_data(){
    read_data();
    radio.dataSend();
}