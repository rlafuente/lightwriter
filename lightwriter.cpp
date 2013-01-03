#include <WProgram.h> 


/*
 * Lightwriter -- Arduino program
 *
 * copyleft 2007-2009 ricardo lafuente
 * 
 * This application should be uploaded to the Arduino board through the
 * following command:
 *
 *   make && make upload
 * 
 */

// Output assignments

// pin numbers for each LED; change according to your layout
int ledPin[] = {12,11,10,9,8};
// max amount of pixel rows in the text buffer

char data[] = "01010101010101010101"; // dummy data, this var will hold the string


int BUFFERLENGTH = 600; // maximum length of the string (rows)
int charLength = BUFFERLENGTH; 
boolean textBuffer[600];

int zeroCount = 0; // count the zeroes to find if we're at the end of the string
int wait = 25; // number of consecutive zeroes found that will make the string
// be truncated

int position = 0; // what's the row to be printed
int RESOLUTION = 5; // vertical resolution (futureproof) = number of LED's
int currentRow[5]; // holds the value of the row to be printed

// this needs to be volatile since it's going to be modified in an interrupt
// function
volatile boolean draw = false;

// SERIAL STUFF
int incoming = 0;
int serialPosition = 0;

// replaceable by 
// boolean textBuffer[BUFFERLENGTH];

// interrupt function
void boing() { draw = !draw; }

void loadRow();
void setPens();
void doSerial();

void setup()
{
  // INTERRUPT: switch control
  // TODO: refine switch (check for RISING and FALLING events)
  attachInterrupt(0, boing, CHANGE);
  // startup LED pins
  for (int i=0; i < RESOLUTION; i++) { pinMode(ledPin[i], OUTPUT); }
  // load the first row
  loadRow(); 
  // init serial connection
  Serial.begin(9600);
  // init the buffer
  for (int i=0; i < BUFFERLENGTH; i++) { textBuffer[i] = 0; }
  // show pretty lights at the beginning
  // FIXME: this is not working, nothing comes up after turning on
  for (int i=0; i<10; i++) { textBuffer[i] = data[i]; }

}

void loop() {
  if (draw) {
    setPens(); 
    delay(wait);
  }
  else {
    for (int i=0; i < RESOLUTION; i++) {
    	digitalWrite(ledPin[i], LOW);
  	} 
  	doSerial();
  }
}

void ledOn (int pinnumber) {
  digitalWrite(ledPin[pinnumber], HIGH);
}

void ledOff (int pinnumber) {
  digitalWrite(ledPin[pinnumber], LOW);
}  
  
void loadRow() {
  if (position >= charLength) {
    position = 0;
  }
  // load a new row of bits
  for (int i = 0; i < RESOLUTION; i++) {
    int pixelValue = position*RESOLUTION + i;
    currentRow[i] = textBuffer[pixelValue];
  }
  // and shift to the next row
  position++; 
}

void setPens() {
  // check row data and set each LED on/off accordingly
  for (int i=0; i < RESOLUTION; i++) {
    if (currentRow[i] == true) { 
      ledOn(i); 
      zeroCount = 0;
    }
    else { 
      ledOff(i); 
      zeroCount++; 
      // we keep track of off-pixels, since having a few of them
      // signals the string is over
    }
  }
  // if we have too many empty spaces, the string is over
  if (zeroCount++ > 35) { position = 0; }
  // load the next row
  loadRow();
}

void doSerial()
{
	if (Serial.available() > 0) {
		incoming = Serial.read();
		Serial.flush();
		if (incoming == 50) { // received 2: python is asking to send stuff
			Serial.println(2, DEC); // acknowledge
		}
		else if (incoming == 48) { // received 0
			textBuffer[serialPosition] = 0;
			Serial.println(0, DEC);
			serialPosition++;
		}
		else if (incoming == 49) { // received 1
			textBuffer[serialPosition] = 1;
			Serial.println(1, DEC);
			serialPosition++;
		}
		else if (incoming == 51) { // received 3: string is over
			Serial.println(3, DEC);
			// zero the rest of the buffer
			for (int i=serialPosition; i < BUFFERLENGTH; i++) {
				textBuffer[i] = 0; 
			}
			// reset variables
			position = 0;
			serialPosition = 0;
			Serial.flush();
			// load first row
			loadRow();
		}
		else {
			Serial.println(4,DEC);
		}
		delay(10); // tweak value?
	}
}


