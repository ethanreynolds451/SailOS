char in[64];
char out[64];
static const char header[] = "CM:";

static const char separator = ';';          // Use semicolon to spearate data sets
static const char designator = ':';          // Use semicolon to spearate data sets
static const char rudder = 'S';             // 0 : 180
static const char thruster = 'M';           // -90 : 90
static const char trim = 'T';               // 0, 1, 2
static const char sail_position = 'T';       // 0, 1, 2

void setup() {
  Serial.begin(115200);
}

void loop() {
  if (readData(in)) {
    parseCommands(in, out);
    sendResponse(out);
  }
  delay(100);
}

bool readData(char* buffer) {
  if (Serial.available() > 0) {
    byte index = 0;
    while (Serial.available() > 0) {
      buffer[index] = Serial.read();
      index++;
    }
    buffer[index] = '\0';
    return true;
  }
  return false;
}

void parseCommands(char* inBuffer, char* outBuffer) {
  size_t index = index_of(header, inBuffer);
  if (index != -1) {
    char* data = readData(rudder, inBuffer);
    if (data != nullptr) {
      strcat(outBuffer, data);
      delete[] data; // Liberar la memoria asignada
    } else {
      strcat(outBuffer, "No data found!");
    }
  } else {
    strcpy(outBuffer, inBuffer);
  }
}

void sendResponse(char* buffer) {
  Serial.println(buffer);
  for (int i = 0; i < 64; i++) {
    buffer[i] = '\0';
  }
}

char* readData(char* parameter, char* buf) {
  size_t dataIndex = searchData(parameter, buf);
  if (dataIndex != -1) {
    size_t len = (strchr(&buf[dataIndex], separator) - &buf[dataIndex]) - headerLength(parameter);
    char* output = new char[len + 1]; // Asignar memoria para el resultado
    strncpy(output, &buf[dataIndex + headerLength(parameter)], len);
    output[len] = '\0'; // Asegurarse de terminar la cadena
    return output;
  }
  return nullptr;
}

size_t searchData(char* search, char* buf) {
  char headers[3];
  sprintf(headers, "%c%c", search, designator);
  if (size_t index = index_of(headers, buf); index != -1) {
    return index;
  }  
  return -1;
}

size_t headerLength(char* head) {
  char headers[3];
  sprintf(headers, "%c%c", head, designator);
  return strlen(headers);
}

size_t index_of(char* header, char* data) { 
  char* found = strstr(data, header);
  if (found != nullptr) {
    return found - data;
  }
  return -1;
}
