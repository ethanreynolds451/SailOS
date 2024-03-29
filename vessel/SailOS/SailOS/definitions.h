#ifndef DEFINITIONS_h
#define DEFINITIONS_h

void(* resetFunc) (void) = 0; // Create function to perform software reset

#include "libraries.h"

#define Radio_TX 2          //  TX for radio
#define Radio_RX 3          //  RX for radio
#define GPS_TX 4            //  TX for radio
#define GPS_RX 5            //  RX for gps
#define DTH11 6             //  DTH sensor data
#define HCSR04_Trig 7       //  Ultrasonic sensor trig pin
#define HCSR04_Echo 8       //  Ultrasonic sensor echo pin
#define Speaker 9           //  Speaker pin
#define chipSelect 10       //  SD card module CS pin
#define SailPosition A0     //  Sail position potentiometer
#define WindDirection A1    //  Wind direction potentiometer
#define WaterTemp A2        //  Water temperature sensor
#define I2C_SDA A3          //  SDA for all I2C interface devices
#define I2C_SCL A4          //  SCL for all I2C interface devices

#define MPU_1_address 0x68      // Default address
#define MPU_2_address 0x69      // Pull up to 5V to change
#define QMC_address 0x42        // Default address
#define PCF_address 0x20        // Default address

File activeFile;                      //  Create file object for SD read / write
REYAX radio(Radio_RX, Radio_TX);      //  Create radio object on radio pins
SoftwareSerial gps(GPS_RX, GPS_TX);   //  Create software serial object for GPS
PWMServo rudder;                      //  Create servo object for rudder control
Tone sound;                           //  Create tone object for speaker
Adafruit_MPU6050 mpu1;                //  Create MPU object for gyro / accel
Adafruit_MPU6050 mpu2;                //  Create MPU object for gyro / accel
QMC5883LCompass compass;              //  Create compas object
PCF8575 pcf(PCF_address);             //  Create PCF expansion board object

#endif
