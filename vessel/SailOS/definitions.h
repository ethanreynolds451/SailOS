#ifndef DEFINITIONS_h
#define DEFINITIONS_h

void(* resetFunc) (void) = 0;       // Create function to perform software reset

class Pin {
    public:
        static constexpr uint8_t radioTx = 2;           //  TX for radio
        static constexpr uint8_t radioRx = 3;           //  RX for radio
        static constexpr uint8_t gpsTx = 4;             //  TX for radio
        static constexpr uint8_t gpsRx = 5;             //  RX for gps
        static constexpr uint8_t rudder = 6;            //  Rudder servo pin
        static constexpr uint8_t ultraTrig = 7;          //  Ultrasonic sensor trig pin
        static constexpr uint8_t ultraEcho = 8;          //  Ultrasonic sensor echo pin
        static constexpr uint8_t speaker = 9;           //  Speaker pin
        static constexpr uint8_t chipSelect = 10;       //  SD card module CS pin
        //  Pins 11 - 13 reserved for SD
        static constexpr uint8_t dth = 14;              //  DTH sensor data, pin A0
        static constexpr uint8_t sailPosition = A1;     //  Sail position potentiometer
        static constexpr uint8_t windDirection = A2;    //  Wind direction potentiometer
        static constexpr uint8_t waterTemp = A3;        //  Water temperature sensor
        static constexpr uint8_t sda = A4;              //  SDA for all I2C interface devices
        static constexpr uint8_t scl = A5;              //  SCL for all I2C interface devices
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
    static constexpr int baud = 115200;
    static constexpr byte rudder_center = 90;
    static const char header_separator = '=';
    static const char data_separator = ';';
    static constexpr const char* command_header = "CM:";
    static constexpr const char* control_header = "CX:";
};


//File activeFile;                                //  Create file object for SD read / write
REYAX radio(Pin::radioTx, Pin::radioRx);        //  Create radio object on radio pins
SoftwareSerial gps(Pin::gpsTx, Pin::gpsRx);     //  Create software serial object for GPS
Servo rudder;                                //  Create servo object for rudder control
RTTL sound(Pin::speaker);                       //  Create RTTL object for speaker
Adafruit_MPU6050 mpu1;                          //  Create MPU object for gyro / accel
Adafruit_MPU6050 mpu2;                          //  Create MPU object for gyro / accel
QMC5883LCompass compass;                        //  Create compas object
PCF8575 pcf(Address::pcf);                      //  Create PCF expansion board object

class Flag {
    public:
        bool broadcast_data = true;          // Start up listening for start signal
};
Flag flag;

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

// This class manages everything related to OUTGOING transmissions
class Data {
    private:
    public:
        static constexpr const char* start = "START";
        static constexpr const char* response = "RESP";

        static constexpr const char* header = "DT:";
        //static char* header_separator = &Default::header_separator;
        static const char designator = ':';
        static const char separator = ';';          // Use semicolon to spearate data sets
        static const char rudder = 'S';             // 0 : 180
        static const char thruster = 'M';           // -90 : 90
        static const char trim = 'T';               // 0, 1, 2
        static const char sail_position = 'T';       // 0, 1, 2
};


// data.find(substring) returnst index of first ocurrence
// data.substr(start, length);

class Sound {
    public:
        static constexpr char* start = "d=4,o=6,b=127:f,c#,f,c#";
};

class Control {
    public:
      void set (char* data) {
        char dataBuffer[8];

        // Set rudder
        readData(Data::rudder, dataBuffer, data);
        if(dataBuffer != nullptr){
           rudder = atoi(dataBuffer);
        } else {
           rudder = Default::rudder_center;
        }

        // Set thruster
        readData(Data::thruster, dataBuffer, data);
        if(dataBuffer != nullptr){
           int thruster_state = atoi(dataBuffer);
           if(thruster_state == 0){
                thruster_active = false;
                thruster_reverse = false;
           } else if(thruster_state == 1){
                thruster_active = true;
                thruster_reverse = false;
           } else if(thruster_state == 2){
                thruster_active = true;
                thruster_reverse = true;
           }
        } else {
           thruster_active = false;
           thruster_reverse = false;
        }
      }
      int rudder = Default::rudder_center;
      bool thruster_active = false;
      bool thruster_reverse = false;
      bool trim_active = false;
      bool trim_reversed = false;
      bool engage_active = false;
      bool engage_reverse = false;
    private:
      void readData(char* parameter, char* output, char* buf) {
          for (int i = 0; i < 7; i++) {
               output[i] = '\0';
          }
          size_t dataIndex = searchData(parameter, buf);
          if (dataIndex != -1) {
            size_t len = (strchr(&buf[dataIndex], Data::separator) - &buf[dataIndex]) - headerLength(parameter);
            strncpy(output, &buf[dataIndex + headerLength(parameter)], len);
            output[len] = '\0'; // Asegurarse de terminar la cadena
          }
          return nullptr;
        }
        size_t searchData(char* search, char* buf) {
          char headers[3];
          sprintf(headers, "%c%c", search, Data::designator);
          if (size_t index = index_of(headers, buf); index != -1) {
            return index;
          }
          return -1;
        }
        size_t headerLength(char* head) {
          char headers[3];
          sprintf(headers, "%c%c", head, Data::designator);
          return strlen(headers);
        }
      size_t index_of (char* header, char* data){
        char* found = strstr(data, header);
        if(found){
            return found - data;
        }
        return -1;
      }
      class Header {
        public:
            //static char* header_separator = &Default::header_separator;
            //static char* data_separator = &Default::data_separator;
            static const char data_separator = Default::data_separator;
            static const char rudder = 'S';     // 0 - 180
            static const char thruster = 'M';   // F, R, X
            static const char trim = 'T';       // I, O, D, X
      };
};
Control control;

// This class manages everything related to incoming transmissions
class Command {
    public:
      int active;
      void read(){
        if(radio.available() > 0){        // Check to see if there is any incoming data
            radio.readData(incoming, incoming_buffer_length);
            if (is_control(incoming)){
                strip_header(incoming, Default::control_header);
                control.set(incoming);
            } else if (is_command(incoming)){
                strip_header(incoming, Default::command_header);
                execute(incoming);
            } else {

            }
        }
      }
      void execute(char* code){
        if(strcmp(code, none) == 0){

        } else if(strcmp(code, reset) == 0){
            resetFunc();
        } else if(strcmp(code, get_response) == 0){
            radio.send(Data::response);
        } else if(strcmp(code, start) == 0){
            flag.broadcast_data = true;
            radio.send(Data::start);
        } else {

        }
      }
    private:
      const char none[5] = "NONE";
      const char reset[4] = "RST";
      const char get_response[4] = "GTR";
      char* start = Data::start;
      static const int incoming_buffer_length = 64;
      char incoming[incoming_buffer_length] = "";
      bool is_command(char* msg){
        size_t len = strlen(Default::command_header);
        return strncmp(msg, Default::command_header, len) == 0;
      }
      bool is_control(char* msg){
        size_t len = strlen(Default::control_header);
        return strncmp(msg, Default::control_header, len) == 0;
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
