#include "Arduino.h"
#include "SailOS.h"

Boat::Boat(){
}

void Boat::begin(int baud){
  rudder.attach(Pin::rudder);
  //pcf.begin();
  pinMode(Pin::gpsTx, OUTPUT);
  pinMode(Pin::gpsRx, OUTPUT);
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
    update_vehicle();
}

void Boat::update_vehicle(){
    rudder.write(control.rudder);
    if (control.thruster_active) {
        if (control.thruster_reverse){
            digitalWrite(Pin::gpsTx, LOW);
            digitalWrite(Pin::gpsRx, HIGH);
            //pcf.write(2, LOW);
            //pcf.write(3, HIGH);
        } else {
            digitalWrite(Pin::gpsTx, HIGH);
            digitalWrite(Pin::gpsRx, LOW);
            //pcf.write(2, HIGH);
            //pcf.write(3, LOW);
        }
    } else {
        digitalWrite(Pin::gpsTx, LOW);
        digitalWrite(Pin::gpsRx, LOW);
        //pcf.write(2, LOW);
        //pcf.write(3, LOW);
    }
}

void Boat::read_data(){
    radio.dataAdd(Data::header);
    char rDat[4];
    itoa(control.rudder,rDat , 10);
    radio.dataAdd(rDat);
    if(control.thruster_active) {
        if(control.thruster_reverse){
            radio.dataAdd(",R");
        } else {
            radio.dataAdd(",F");
        }
    } else {
        radio.dataAdd(",X");
    }
}

void Boat::broadcast_data(){
    read_data();
    radio.dataSend();
}
