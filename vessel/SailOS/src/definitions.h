#ifndef DEFINITIONS_h
#define DEFINITIONS_h

void(* resetFunc) (void) = 0;       // Create function to perform software reset

#include "libraries.h"

class Pin {
    public:
        static constexpr int radioTx = 2;          //  TX for radio
        static constexpr int radioRx = 3;          //  RX for radio
        static constexpr int gpsTx = 4;            //  TX for radio
        static constexpr int gpsRx = 5;            //  RX for gps
        static constexpr int rudder = 6;           //  Rudder servo pin
        static constexpr int hcsrTrig = 7;         //  Ultrasonic sensor trig pin
        static constexpr int hcsrEcho = 8;         //  Ultrasonic sensor echo pin
        static constexpr int speaker = 9;           //  Speaker pin
        static constexpr int chipSelect = 10;       //  SD card module CS pin
        static constexpr int dth = 13;              //  DTH sensor data
        static constexpr int sailPosition = A0;     //  Sail position potentiometer
        static constexpr int windDirection = A1;    //  Wind direction potentiometer
        static constexpr int waterTemp = A2;        //  Water temperature sensor
        static constexpr int sda = A3;              //  SDA for all I2C interface devices
        static constexpr int scl = A4;              //  SCL for all I2C interface devices
};

class Address {
    public:
        static constexpr int mpu1 = 0x68;     // Default address
        static constexpr int mpu2 = 0x69;     // Pull up to 5V
        static constexpr int qmc = 0x42;      // Default address
        static constexpr int pcf = 0x20;      // Default address
};

class Default {
  public:
    static const int baud = 9600;
};

class Error {
  private:
    struct errorArray {
      uint8_t errorNumber;
      char errorCode[4];
      char errorTone[16];
    };
  public:
    const errorArray error[16] = {
     {0, "NONE", ""},
     {1, "SEND", "d=4,o=6,b=127:f,c#,f,c#"}
    };
};

class commands {
  private:
    struct commandArray {
      byte index;
      char code[4];
    };
  public:
    static const byte numberOfCommands = 2;
    const commandArray command[numberOfCommands] = {
      {0, "RESET"},
      {1, ""}
    };
};

File activeFile;                      //  Create file object for SD read / write
REYAX radio(Pin::radioRx, Pin::radioTx);      //  Create radio object on radio pins
SoftwareSerial gps(Pin::gpsRx, Pin::gpsTx);   //  Create software serial object for GPS
PWMServo rudder;                      //  Create servo object for rudder control
RTTL sound(Pin::speaker);                           //  Create RTTL object for speaker
Adafruit_MPU6050 mpu1;                //  Create MPU object for gyro / accel
Adafruit_MPU6050 mpu2;                //  Create MPU object for gyro / accel
QMC5883LCompass compass;              //  Create compas object
PCF8575 pcf(Address::pcf);             //  Create PCF expansion board object

#endif
