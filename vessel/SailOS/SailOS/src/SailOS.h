/*   
 *  Header file for SailOS Arduino Library
 *  Written by: Ethan Reynolds
 *  Sound School 2024
*/

#ifndef SAILOS_h
#define SAILOS_h


#include "definitions.h"


class Boat {
  public:
    Boat();
    void begin();
    void connect();
//    void initiate();
//    void transmit(char* data);
//    void getCommand();
//    void setManualControl();
//    void setAutonomousMode();
//    void sendMode();
  private: 
    char[128] dataIn = "";  //  Create buffer to hold incoming data
    bool autoMode = false;
    struct peripheral_status {
      bool SD_active = false;
      bool MPU_1_active = false;
      bool MPU_2_active = false;
      bool QMC_active = false;
      bool PCF_active = false; 
      bool GPS_active = false;
      bool DTH_active = false;
      bool HCS_active = false;
    };
    peripheral_conditions p_status;  
      
//    void initiatePeripherals(){
//      initiateSD();
//      initiateMPU();
//      initiateQMC();
//      initiatePCF();
//      initiateGPS();
//      initiateDTH();
//      initiateHCS();
//    }
//    
//    //Try to initate 3 times with 1 second rest. Set active to sucess state
//    void initiateSD(){              
//      for(int i = 0; i < 3; i++){
//        if (!SD.begin()) {
//          if(i < 2) {
//            delay(100);
//          } else {
//            pc.SD_active = false;          
//          }
//        } else {
//          pc.SD_active = true;
//          i = 3;
//        }
//      }
//    } 
//    void initiateMPU(){
//      for(int i = 0; i < 3; i++){
//        if (!mpu1.begin(MPU_1_address)) {
//            if(i < 2) {
//              delay(100);
//            } else {
//              pc.MPU_1_active = false; 
//            }
//          } else {
//            pc.MPU_1_active = true; 
//          }
//          if (!mpu2.begin(MPU_2_address)) {
//            if(i < 2) {
//              delay(100);
//            } else {
//              pc.MPU_2_active = false;
//            }
//          } else {
//            pc.MPU_2_active = true;
//          }
//      }
//    }
//    void initiateQMC(){ 
//      compass.init();
//      for(int i = 0; i < 3; i++){
//        if (compass.getX() == -1) {
//            if(i < 2) {
//              compass.init();
//              delay(100);
//            } else {
//              pc.QMC_active = false; 
//            }
//          } else {
//            pc.QMC_active  = true; 
//            compass.setADDR(QMC_address);
//          }
//        }
//    }
//    void initiatePCF(){
//      pcf.begin();
//      for(int i = 0; i < 3; i++){
//        if (!pcf.isConnected()) {
//            if(i < 2) {
//              pcf.begin();
//              delay(100);
//            } else {
//              pc.PCF_active = false; 
//            }
//          } else {
//            pc.PCF_active  = true; 
//         }
//       }
//    }
//    void initiateGPS(){
//      
//    }
//    void initiateDTH(){
//      
//    }
//    void initiateHCS(){
//      
//    }
//
//    void sendStatus(){
//        _transmit("STATUS:SD=");
//        _transmitln(String(pc.SD_active));
//        _transmit("STATUS:MPU1=");
//        _transmitln(String(pc.MPU_1_active));
//        _transmit("STATUS:MPU2=");
//        _transmitln(String(pc.MPU_2_active));
//        _transmit("STATUS:QMC=");
//        _transmitln(String(pc.QMC_active));
//        _transmit("STATUS:PCF=");
//        _transmitln(String(pc.PCF_active)); 
//        _transmit("STATUS:GPS=");
//        _transmitln(String(pc.GPS_active));
//        _transmit("STATUS:DTH=");
//        _transmitln(String(pc.DTH_active));
//        _transmit("STATUS:HCS=");
//        _transmitln(String(pc.HCS_active));
//    }
//
//    void _transmit(String data){
//      Serial.print("AT+SEND=1,");
//      Serial.print(String(data.length())); 
//      Serial.print(",");
//      Serial.println(data);  
//    }
//    
//    String _readCommand(){
//      String data = Serial.readStringUntil("\n");
//      data = data.substring(-1, data.indexOf(',', -1));
//      return data;
//    }
//};

#endif
