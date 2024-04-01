/*   
 *  Header file for SailOS Arduino Library
 *  Written by: Ethan Reynolds
 *  Sound School 2024
*/

#ifndef SAILOS_h
#define SAILOS_h

#include "libraries.h"
#include "definitions.h"

class Boat {
  public:
    Boat();
    void begin(int baud = Default::baud);
    void update();
  private:
    void broadcast_start_signal();
};

#endif
