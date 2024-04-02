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
        static constexpr int ultraTrig = 7;          //  Ultrasonic sensor trig pin
        static constexpr int ultraEcho = 8;          //  Ultrasonic sensor echo pin
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

// Stores any parameters that are subject to change based on hardware or software configuration
class Default {
  public:
    static constexpr int baud = 9600;
    static constexpr char data_header[4] = "DT:";
};

static constexpr char command_header[4] = "CM:";
static constexpr char control_header[4] = "CX";

//File activeFile;                                //  Create file object for SD read / write
REYAX radio(Pin::radioTx, Pin::radioRx);        //  Create radio object on radio pins
SoftwareSerial gps(Pin::gpsTx, Pin::gpsRx);     //  Create software serial object for GPS
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

// This class manages everything related to outgoing transmissions
class Data {
    private:
    public:
        char start[6] = "START";

};
Data data;

// This class manages everything related to incoming transmissions
class Command {
    public:
      int active;
      void read(){
        if(radio.available() > 0){        // Check to see if there is any incoming data
            radio.readData(incoming, incoming_buffer_length);
            Serial.print("Recieved Transmission: ");
            if (is_control(incoming)){
                strip_header(incoming, control_header);
                Serial.println("Control Data");
            } else if (is_command(incoming)){
                Serial.print("Command: ");
                strip_header(incoming, command_header);
                execute(incoming);
            } else {
                Serial.println("Unrecognized");
            }
        }
      }
      void parse_control_data (){
      }
      void execute(char* code){
        if(strcmp(code, none) == 0){

        } else if(strcmp(code, reset) == 0){
            resetFunc();
        } else if(strcmp(code, start) == 0){
            Serial.println("Start Command");
            radio.send(data.start);
        } else {
            Serial.println("Command Not Recognized");
        }
      }
    private:
      char none[8] = "NONE";
      char recieve_error[8] = "RECERR";
      char reset[8] = "RESET";
      char start[8] = "START";
      static const int incoming_buffer_length = 64;
      char incoming[incoming_buffer_length] = "";
      bool is_command(char* msg){
        return strncmp(msg, command_header, strlen(command_header)) == 0;
      }
      bool is_control(char* msg){
        return strncmp(msg, control_header, strlen(control_header)) == 0;
      }
      // From ChatGPT
      void strip_header(char* message, const char* header) {
          size_t headerLength = strlen(header);
          size_t messageLength = strlen(message);
          // Find the position of the header sequence in the message
          char* headerPosition = strstr(message, header);
          // If the header sequence is found
          if (headerPosition != NULL) {
              // Calculate the number of characters to shift
              size_t charactersToShift = messageLength - (headerPosition - message) - headerLength + 1;
              // Shift the characters to remove the header sequence
              memmove(headerPosition, headerPosition + headerLength, charactersToShift);
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
        bool broadcast_data = false;          // Start up listening for start signal
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
