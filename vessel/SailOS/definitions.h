#ifndef DEFINITIONS_h
#define DEFINITIONS_h

void(* resetFunc) (void) = 0;       // Create function to perform software reset

class Pin {
    public:
        static constexpr int radioTx = 2;           //  TX for radio
        static constexpr int radioRx = 3;           //  RX for radio
        static constexpr int gpsTx = 4;             //  TX for radio
        static constexpr int gpsRx = 5;             //  RX for gps
        static constexpr int rudder = 6;            //  Rudder servo pin
        static constexpr int hcsrTrig = 7;          //  Ultrasonic sensor trig pin
        static constexpr int hcsrEcho = 8;          //  Ultrasonic sensor echo pin
        static constexpr int speaker = 9;           //  Speaker pin
        static constexpr int chipSelect = 10;       //  SD card module CS pin
        //  Pins 11 - 13 reserved for SD
        static constexpr int dth = 14;              //  DTH sensor data, pin A0
        static constexpr int sailPosition = A1;     //  Sail position potentiometer
        static constexpr int windDirection = A2;    //  Wind direction potentiometer
        static constexpr int waterTemp = A3;        //  Water temperature sensor
        static constexpr int sda = A4;              //  SDA for all I2C interface devices
        static constexpr int scl = A5;              //  SCL for all I2C interface devices
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

//File activeFile;                                //  Create file object for SD read / write
REYAX radio(Pin::radioRx, Pin::radioTx);        //  Create radio object on radio pins
SoftwareSerial gps(Pin::gpsRx, Pin::gpsTx);     //  Create software serial object for GPS
PWMServo rudder;                                //  Create servo object for rudder control
RTTL sound(Pin::speaker);                       //  Create RTTL object for speaker
Adafruit_MPU6050 mpu1;                          //  Create MPU object for gyro / accel
Adafruit_MPU6050 mpu2;                          //  Create MPU object for gyro / accel
QMC5883LCompass compass;                        //  Create compas object
PCF8575 pcf(Address::pcf);                      //  Create PCF expansion board object


class Error {
  private:
    struct errorArray {
      uint8_t errorNumber;
      char errorCode[4];
      char errorTone[16];
    };
  public:
    const errorArray e[16] = {
     {0, "NONE", ""},
     {1, "SEND", "d=4,o=6,b=127:f,c#,f,c#"}
    };
};

class Command {
    private:
      struct commandArray {
        byte index;
        char code[8];
      };
    public:
      char start[5] = "START";
      static const byte numberOfInCommands = 4;
      char incoming[64] = "";
      int active = NAN;
      const commandArray in[numberOfInCommands] = {
        {0, "NONE"},
        {1, "RECERR"},
        {2, "RESET"},
        {3, "START"}
      };
      byte find(char* com){
        for(int i = 0; i < numberOfInCommands; i++){                // For number of potential commands
            if(strncmp(com, in[i].code, strlen(com)) == 0){     // If strings match
                return i;
            }
         }
        return 1;
      }
      bool read(){
        if(radio.available() > 0){        // Check to see if there is any incoming data
            radio.readData(incoming, 64);
            active = find(incoming);
            return true;
        }
        return false;
      }
      void execute(int index){
        if(in[index].code == "NONE"){
        }
        if(in[index].code == "RESET"){
            resetFunc();
        }
        if(in[index].code == "START"){
            radio.send(start);
        }
      }
};
Command command;

class Sound {
    public:
        const char start = "d=4,o=6,b=127:f,c#,f,c#";
};

class Flag {
    public:
        bool waiting_for_start = true;          // Start up listening for start signal
};
Flag flag;

class Time {
public:
    Time(unsigned long x) : interval(x) {} // Constructor with member initializer list
    bool passed() {
        return wait(interval);
    }
private:
    bool wait(unsigned long time) {
        // return false if we're still "delaying", true if time ms has passed.
        // this should look a lot like "blink without delay"
        unsigned long currentmillis = millis();
        if (currentmillis - previousmillis >= time) {
            previousmillis = currentmillis;
            return true;
        }
        return false;
    }
    unsigned long interval; // Interval for this timer instance
    unsigned long previousmillis = 0; // Previous millis for this timer instance
};
Time one(1000);
Time two (2000);
Time three (3000);
Time five(5000);
Time ten (10000);


#endif
