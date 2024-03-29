#ifndef ERRORS_h
#define ERRORS_h

class error {
  private:
    struct errorArray {
      uint8_t errorNumber;
      char errorCode[4];
      char errorTone[16];
    };
  public:
    const errorArray error[16] = {
     {0, "NONE", ""},
     {1, "SEND", ""}
    };
};

error e;

// Elements can be acessed as error.error[index].errorNumber

#endif
