#ifndef RTTL_h
#define RTTL_h

//Include the tone library 
#include "Tone-1.0.0/tone.h"

#define isdigit(n) (n >= '0' && n <= '9')
#define OCTAVE_OFFSET 0

char *song = "";

class RTTL {
  public:
    RTTL(int pin);
    void begin();
    void play(char* p);
  private:
    int tonePin; 
    int notes[50] = {0, 262, 277, 294, 311, 330, 349, 370, 392, 415, 440, 466, 494, 523, 554, 587, 622, 659, 698, 740, 784, 831, 880, 932, 988, 1047, 1109, 1175, 1245, 1319, 1397, 1480, 1568, 1661, 1760, 1865, 1976, 2093, 2217, 2349, 2489, 2637, 2794, 2960, 3136, 3322, 3520, 3729, 3951};
    byte default_dur = 4;
    byte default_oct = 6;
    int bpm = 63;
    int num;
    long wholenote;
    long duration;
    byte note;
    byte scale;
};

#endif
