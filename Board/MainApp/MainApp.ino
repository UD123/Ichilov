

// 
// Ichilov : Runtime Comm for PC Monitor and connection to Accel

// Compatible : 
//     intended for use with MonitorGUI.py - version 0106

// Usage :
    
// Message Format:
//     '<msgId, type, count, some data - string>'
    
// TODO :

// Accel : 
// Connect SCLK, MISO, MOSI, and CSB of MC3635 to
// SCLK, MISO, MOSI, and DP 10 of Arduino 
// (check http://arduino.cc/en/Reference/SPI for details)
// connection like in : https://www.circuitbasics.com/how-to-set-up-spi-communication-for-arduino/
//

// -----------------------------
//  Ver    Date     Who    Descr
// -----------------------------
// 0201   27.09.24 UD     adopted
// 0107   27.12.22 UD     adding File data write - algo - read
// 0106   11.12.22 UD     adding Max30003 : C:\RobotAI\Customers\Levron\Code\Examples\protocentral_max30003\examples\Example2-ECG-stream-Arduino-Plotter
// 0105   02.12.22 UD     adding Accel. C:\RobotAI\Customers\Levron\Code\Examples\annem-ADXL362-58cfa5b
// 0104   15.11.22 UD     adding A2D
// 0103   12.11.22 UD     Reading versionu
// 0102   11.11.22 UD     Created for Menu
// -----------------------------
#include "MC3635.h"

//=============
// general 
unsigned int VERSION = 201;

const byte numLEDs = 2;
byte ledPin[numLEDs] = {12, 13};
byte ledStatus[numLEDs] = {0, 0};


//=============
// Accel
MC3635 MC3635_acc = MC3635();
int16_t temp;
int16_t XValue, YValue, ZValue, Temperature;


void checkRange()
{
  switch(MC3635_acc.GetRangeCtrl(0))
  {
    case MC3635_RANGE_16G:            Serial.println("Range: +/- 16 g"); break;     
    case MC3635_RANGE_12G:            Serial.println("Range: +/- 12 g"); break;         
    case MC3635_RANGE_8G:             Serial.println("Range: +/- 8 g"); break;
    case MC3635_RANGE_4G:             Serial.println("Range: +/- 4 g"); break;
    case MC3635_RANGE_2G:             Serial.println("Range: +/- 2 g"); break;
    default:                          Serial.println("Range: +/- 8 g"); break;
  }   
}  

void checkResolution()
{
  switch(MC3635_acc.GetResolutionCtrl(0))
  {
    case MC3635_RESOLUTION_6BIT:            Serial.println("Resolution: 6bit"); break;     
    case MC3635_RESOLUTION_7BIT:            Serial.println("Resolution: 7bit"); break;         
    case MC3635_RESOLUTION_8BIT:            Serial.println("Resolution: 8bit"); break;
    case MC3635_RESOLUTION_10BIT:           Serial.println("Resolution: 10bit"); break;
    case MC3635_RESOLUTION_14BIT:           Serial.println("Resolution: 14bit"); break;
    case MC3635_RESOLUTION_12BIT:           Serial.println("Resolution: 12bit"); break;
    default:                                Serial.println("Resolution: 14bit"); break;
  } 
}

void checkSamplingRate()
{
  switch(MC3635_acc.GetCWakeSampleRate(0))
  {
    MC3635_CWAKE_SR_DEFAULT_50Hz:           Serial.println("Output Sampling Rate: 50 Hz"); break;
    MC3635_CWAKE_SR_0p4Hz:                  Serial.println("Output Sampling Rate: 0.4 Hz"); break;
    MC3635_CWAKE_SR_0p8Hz:                  Serial.println("Output Sampling Rate: 0.8 Hz"); break; 
    MC3635_CWAKE_SR_2Hz:                    Serial.println("Output Sampling Rate: 2 Hz"); break; 
    MC3635_CWAKE_SR_6Hz:                    Serial.println("Output Sampling Rate: 6 Hz"); break; 
    MC3635_CWAKE_SR_13Hz:                   Serial.println("Output Sampling Rate: 13 Hz"); break; 
    MC3635_CWAKE_SR_25Hz:                   Serial.println("Output Sampling Rate: 25 Hz"); break; 
    MC3635_CWAKE_SR_50Hz:                   Serial.println("Output Sampling Rate: 50 Hz"); break;
    MC3635_CWAKE_SR_100Hz:                  Serial.println("Output Sampling Rate: 100 Hz"); break; 
    MC3635_CWAKE_SR_200Hz:                  Serial.println("Output Sampling Rate: 200 Hz"); break; 
    default:                                Serial.println("Output Sampling Rate: 50 Hz"); break;
  }   
}  



//=============
// comm related
unsigned int msgId   = 0;
unsigned int msgType = 0;
unsigned int msgCount = 0;
int inputData[10] = {0};

const byte buffSize = 40;
char inputBuffer[buffSize];
const char startMarker = '<';
const char endMarker = '>';
byte bytesRecvd = 0;
boolean readInProgress = false;
boolean newDataFromPC = false;
char * strtokIndx; // this is used by strtok() as an index

//char messageFromPC[buffSize] = {0};

//=============
// Algorithm
unsigned int algoState       = 0;  //0-init, 1-received, 2-send
int16_t algoResult      = 0;
int16_t algoFileLV      = 0;
int16_t algoFileSurf    = 0;
int16_t algoFilePress   = 0; 

//=============
// Timer
unsigned long prevReplyToPCmillis = 0;
unsigned long replyToPCinterval = 1000;

//=============
void PrintFileNameDateTime()
{ // needs a Serial.begin(baudrate) before calling this function
  Serial.print("Code running comes from file ");
  Serial.println(__FILE__);
  Serial.print("compiled ");
  Serial.print(__DATE__);
  Serial.print(" ");
  Serial.println(__TIME__);
}
//=============
// Generally, you should use "unsigned long" for variables that hold time
// The value will quickly become too large for an int to store
unsigned long previousMillis = 0;  // will store last time LED was updated
unsigned long curMillis;
// constants won't change:
unsigned long interval = 1000;  // interval at which to blink (milliseconds)
boolean isTimeout = false;

//=============
// Analog In
// These constants won't change. They're used to give names to the pins used:
const int analogInPin = A0;  // Analog input pin that the potentiometer is attached to
int sensorValue = 0;  // value read from the pot

//=============
void setup() {
  Serial.begin(9600);
  //while (!Serial); // wait for

  // tell the version
  Serial.print("Main - Version: "); Serial.println(VERSION);

  PrintFileNameDateTime();
  
  // flash LEDs so we know we are alive
  for (byte n = 0; n < numLEDs; n++) {
     pinMode(ledPin[n], OUTPUT);
     digitalWrite(ledPin[n], HIGH);
  }
  delay(1000); // delay() is OK in setup as it only happens once
  
  for (byte n = 0; n < numLEDs; n++) {
     digitalWrite(ledPin[n], LOW);
  }

  // Accel
  pinMode(8 , OUTPUT);
  digitalWrite(8, HIGH);
  delay(10);

  MC3635_acc.SetNumOfDevice(1);
  MC3635_acc.SetCSPin(0, 10);
  MC3635_acc.SetInterface(1);
  MC3635_acc.start(1); // SPI interface
  
  Serial.println("mCube Accelerometer MC3635:");
  checkRange();
  checkResolution();
  checkSamplingRate();

  // init algo
  algoState = 0;

  // tell the PC we are ready
  Serial.println("<Arduino is ready>");

}

//=============
// main loop
void loop() {
  curMillis = millis();
  getMsgFromPC();

  // debug
  //msgId = 41;
  //newDataFromPC = true;
  //delay(1000);

  checkTimeout();
  //switchLEDs();
  writeOutputs();
  //moveServo();
  readAccel();
  //readRawECG();
  //readSensors();
  algoRun();
  sendMsgToPC();
  
}

//=============
void checkTimeout()
{ // needs a Serial.begin(baudrate)
  unsigned long currentMillis = millis();
  isTimeout      = false;
  if (currentMillis - previousMillis >= interval) {
    // save the last time you blinked the LED
    previousMillis = currentMillis;
    isTimeout      = true;
    //Serial.print("T : "); Serial.println(previousMillis);
  }
}

//=============
void switchLEDs() {
  for (byte n = 1; n < numLEDs; n++) {
    digitalWrite( ledPin[n], ledStatus[n]);
  }
}


//=============
void readAccel(){

  MC3635_acc_t rawAccel = MC3635_acc.readRawAccel(0);
  delay(10);

  // read all three axis in burst to ensure all measurements correspond to same sample time
  XValue = rawAccel.XAxis;
  YValue = rawAccel.YAxis;
  ZValue = rawAccel.ZAxis;
  
  // Display the results (acceleration is measured in m/s^2)
  Serial.print("X: \t"); Serial.print(XValue); Serial.print("\t");
  Serial.print("Y: \t"); Serial.print(YValue); Serial.print("\t");
  Serial.print("Z: \t"); Serial.print(ZValue); Serial.print("\t");
  Serial.println("m/s^2");

}


//=============
// read version
void readVersion() {
    // tell the version
  //Serial.print("   Test - Version: "); Serial.println(VERSION);
  PrintFileNameDateTime();
}

//=============
void writeOutputs() {

    // if the LED is off turn it on and vice-versa:
    if (isTimeout) {
      if (ledStatus[1] == LOW) {
        ledStatus[1] = HIGH;
        //digitalWrite(LED_BUILTIN, HIGH);
        //Serial.print("U : "); Serial.println(curMillis);
        //digitalWrite(ledPin[0], ledStatus[0]);
      } else {
        ledStatus[1] = LOW;
        //digitalWrite(LED_BUILTIN, LOW);
        //Serial.print("D : "); Serial.println(curMillis);
        //digitalWrite(ledPin[0], ledStatus[0]);
      }

      // set the LED with the ledState of the variable:
      digitalWrite(ledPin[1], ledStatus[1]);
      //Serial.print("T : "); Serial.println(previousMillis);
    }

}

//=============
void algoRun(){
  switch (algoState) {
    case 0: // do nothing
      algoState = 1; 
      break;
    case 1: // process
      algoState = 1; 
      algoResult = algoFileLV *100 + algoFileSurf * 10 + algoFilePress;
      break;      
    default: //Serial.println("ERROR : Unrecognized command");
      algoState = 0;
  }

}


//============= COMM ====================
void getMsgFromPC() {

    // receive data from PC and save it into inputBuffer
    
  if(Serial.available() > 0) {

    char x = Serial.read();

    // the order of these IF clauses is significant
      
    if (x == endMarker) {
      readInProgress = false;
      newDataFromPC = true;
      inputBuffer[bytesRecvd] = 0;
      parseRecvMsg();
    }
    
    if(readInProgress) {
      inputBuffer[bytesRecvd] = x;
      bytesRecvd ++;
      if (bytesRecvd == buffSize) {
        bytesRecvd = buffSize - 1;
      }
    }

    if (x == startMarker) { 
      bytesRecvd = 0; 
      readInProgress = true;
    }
  }
}

//=============
void parseRecvMsg() {

    // split the data into its parts
    // assumes the data will be received as (eg) msgId,msgType,msgCount,0,1,35
    
  //char * strtokIndx; // this is used by strtok() as an index
  
  strtokIndx = strtok(inputBuffer,","); // msgId
  msgId      = atoi(strtokIndx); //  convert to an integer

  strtokIndx = strtok(NULL,","); // msgId
  msgType    = atoi(strtokIndx); //  convert to an integer

  strtokIndx = strtok(NULL,","); // msgCount
  msgCount   = atoi(strtokIndx); //  convert to an integer

  parseRecvCommand();

/*
  strtokIndx = strtok(NULL,","); // get the first part
  ledStatus[0] = atoi(strtokIndx); //  convert to an integer
  
  strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
  ledStatus[1] = atoi(strtokIndx);
  
  strtokIndx = strtok(NULL, ","); 
  newServoPos = atoi(strtokIndx); 
*/
}

//=============
// identifies which command to execute 
void parseRecvCommand() {

  switch (msgId) {
    case 1:  // control leds
      readIntBuffer(3);
      ledStatus[0] = inputData[0];
      ledStatus[1] = inputData[1];
      //newServoPos  = inputData[2];
      break;
    case 31: // write PWM delay
      readIntBuffer(1); 
      interval = inputData[0];
      break;      
    case 33: // read sensor
      readIntBuffer(0); 
      break;
    case 35: // read accel
      readIntBuffer(0); 
      break;    
    case 41: // read raw ecg
      readIntBuffer(0); 
      break;    
    case 51: // read raw data from file
      readIntBuffer(3); 
      algoFileLV      = inputData[0];
      algoFileSurf    = inputData[1];
      algoFilePress   = inputData[2];      
      break;           
    case 91: // version
      readIntBuffer(0); 
      break;
    default: //Serial.println("ERROR : Unrecognized command");
      msgId = 101;
  }
}

//=============
// identifies which result to send 
void parseSendCommand() {

  switch (msgId) {
    case 2:  // reply with led status     
      inputData[0] = ledStatus[0];
      inputData[1] = ledStatus[1];
      inputData[2] = 123;
      writeIntBuffer(3);
      break;

    case 32:  // send ok on PWM delay      
      inputData[0] = interval;
      writeIntBuffer(1);
      break;

    case 34:  // return sensor value      
      inputData[0] = sensorValue;
      writeIntBuffer(1);
      break; 

    case 36: // read accel data XValue, YValue, ZValue, Temperature
      inputData[0] = XValue;
      inputData[1] = YValue;
      inputData[2] = ZValue;
      inputData[3] = Temperature;
      writeIntBuffer(4); 
      break;

    case 42: // read ECG raw data ecgdata - signed long
      inputData[0] = (int)(101);
      inputData[1] = (int)(102);
      //Serial.print(inputData[1]);
      //Serial.print(",");
      //Serial.println(inputData[0]);
      //inputData[1] = (int)(max30003.ecgdata >> 6); // 6 bit are controls Table 32. FIFO Memory Access and Data Structure Summary
      writeIntBuffer(2); 
      break; 

    case 52: // write algo data back
      inputData[0] = (int16_t)(algoResult);
      writeIntBuffer(1); 
      break;                       

    case 92: 
      inputData[0] = VERSION;
      writeIntBuffer(1);
      break;

    default: //Serial.println("ERROR : Unrecognized command");
      msgId = 101;
  }
}

//=============
void sendMsgToPC() {

  if (newDataFromPC) {
    msgId         = msgId+1;  // reply
    newDataFromPC = false;
    Serial.print("<");
    Serial.print(msgId);
    Serial.print(",");
    Serial.print(msgType);
    Serial.print(",");    
    Serial.print(msgCount+1);
    //Serial.print(",");  

    parseSendCommand();

    Serial.println(">");
  }
}

//=============
// read a number of variables into a buffer
void readIntBuffer(int wNum) {

  for(int cnt = 0;cnt < wNum;cnt++) {
    strtokIndx = strtok(NULL,","); // get the first part
    inputData[cnt] = atoi(strtokIndx); //  convert to an integer
  }
}
//=============
// write a buffer to the port
void writeIntBuffer(int wNum) {

  for(int cnt = 0;cnt < wNum;cnt++) {
    Serial.print(",");
    Serial.print(inputData[cnt]);
    
  }
}

// void replyToPC() {

//   if (newDataFromPC) {
//     newDataFromPC = false;
//     Serial.print("<LedA ");
//     Serial.print(ledStatus[0]);
//     Serial.print(" LedB ");
//     Serial.print(ledStatus[1]);
//     Serial.print(" SrvPos ");
//     Serial.print(newServoPos);
//     Serial.print(" Time ");
//     Serial.print(curMillis >> 9); // divide by 512 is approx = half-seconds
//     Serial.println(">");
//   }
// }

