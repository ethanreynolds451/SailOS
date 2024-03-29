#ifndef COMMANDS_h
#define COMMANDS_h

#include "definitions.h"

class commands {
  private:
    struct commandArray {
      byte index;
      char code[4];
    }
  public:
    byte numberOfCommands = 2;
    const command command[numberOfCommands] = {
      {0, "RESET", 0},
      {1, "", 0}
    };
    byte read(char* input){
      while(int i = 0; i < numberOfCommands){
        for(int i = 0; i < numberOfCommands; i++){  // For number of potential commands
         if(strncmp(input, command[i].code, strlen(input)) == 0){  // If strings match
            return command[i].index;   // Set active command to current index
         }
      }
     return -1;
    }
    void execute(index){
      
    }
};

commands c;   // Create instance of commands class as c


#endif
