#include "MC3635.h"
#include <SPI.h>
#define MC3635_CFG_I2C_ADDR    			(0x4C)
const uint8_t WRITE = 0x40;
const uint8_t READ = 0xC0;
#define MC3635_CFG_MODE_DEFAULT    		MC3635_MODE_STANDBY
#define MC3635_CFG_SAMPLE_RATE_CWAKE_DEFAULT    MC3635_CWAKE_SR_DEFAULT_50Hz
#define MC3635_CFG_SAMPLE_RATE_SNIFF_DEFAULT    MC3635_SNIFF_SR_0p4Hz
#define MC3635_CFG_RANGE_DEFAULT         	MC3635_RANGE_8G
#define MC3635_CFG_RESOLUTION_DEFAULT    	MC3635_RESOLUTION_14BIT
#define MC3635_CFG_ORIENTATION_MAP_DEFAULT    	ORIENTATION_TOP_RIGHT_UP

#define chip_select_delay 500
uint8_t CfgRange, CfgResolution;	
//uint8_t interface = 0; // 0: I2C, 1: SPI
volatile int MY_INT =0 ;
 // Read register bit
bool MC3635::readRegisterBit(uint8_t reg, uint8_t pos,uint8_t idx)
{
    uint8_t value;
    value = readRegister8(reg,idx);
    return ((value >> pos) & 1);
}

// Write register bit
void MC3635::writeRegisterBit(uint8_t reg, uint8_t pos, bool state,uint8_t idx)
{
    uint8_t value;
    value = readRegister8(reg,idx);

    if (state)
        value |= (1 << pos);
    else
        value &= ~(1 << pos);

    writeRegister8(reg, value,idx);
}

// Read 8-bit from register
uint8_t MC3635::readRegister8(uint8_t reg, uint8_t idx)
{
    uint8_t value;
    if (interface == 0)
    {
	    Wire.beginTransmission(MC3635_CFG_I2C_ADDR);
	    Wire.write(reg);
	    Wire.endTransmission(false); //endTransmission but keep the connection active
	    Wire.requestFrom(MC3635_CFG_I2C_ADDR, 1); //Once done, bus is released by default
	    value = Wire.read();
    }
    else
    {
	    uint8_t data = reg | READ;
	    digitalWrite(CSn[idx],LOW);
	    SPI.transfer(data);
	    value = SPI.transfer(0x00);
	    delayMicroseconds(chip_select_delay);
	    digitalWrite(CSn[idx], HIGH);
    }
    return value;
}          

// Write 8-bit to register
void MC3635::writeRegister8(uint8_t reg, uint8_t value, uint8_t idx)
{
    if (interface == 0)
    {
	    Wire.beginTransmission(MC3635_CFG_I2C_ADDR);
	    Wire.write(reg);
	    Wire.write(value);
	    Wire.endTransmission();
    }
    else
    {
	    uint8_t data = reg | WRITE;
	    digitalWrite(CSn[idx],LOW);
	    SPI.transfer(data);
	    SPI.transfer(value);
	    delayMicroseconds(chip_select_delay);
	    digitalWrite(CSn[idx],HIGH);
    }
}

// Read 16-bit from register
int16_t MC3635::readRegister16(uint8_t reg, uint8_t idx)
{
    int16_t value;
    if (interface == 0)
    {
	    Wire.beginTransmission(MC3635_CFG_I2C_ADDR);
	    Wire.write(reg);
	    Wire.endTransmission();
	    Wire.requestFrom(MC3635_CFG_I2C_ADDR, 2);
	    while(!Wire.available()) {};
	    uint8_t vha = Wire.read();
	    uint8_t vla = Wire.read();
	    value = vha << 8 | vla;
    }
    else
    {
	    uint8_t data = reg | READ;
	    uint8_t vha, vla;
	    digitalWrite(CSn[idx],LOW);
	    SPI.transfer(data);
	    vha = SPI.transfer(0x00);
	    vla = SPI.transfer(0x00);
	    delayMicroseconds(chip_select_delay);
	    digitalWrite(CSn[idx], HIGH);
	    value = vha << 8 | vla; 
    }
    return value;
}

// Write 8-bit from register
void MC3635::writeRegister16(uint8_t reg, int16_t value,uint8_t idx)
{
    if (interface ==0)
    {
	    Wire.beginTransmission(MC3635_CFG_I2C_ADDR);
	    Wire.write(reg);
	    Wire.write((uint8_t)(value >> 8));
	    Wire.write((uint8_t)value);
	    Wire.endTransmission();
    }
    else
    {
	    uint8_t data = reg | WRITE;
	    digitalWrite(CSn[idx],LOW);
	    SPI.transfer(data);
	    SPI.transfer((uint8_t)value>>8);
	    SPI.transfer((uint8_t)value);
	    delayMicroseconds(chip_select_delay);
	    digitalWrite(CSn[idx],HIGH);
    }
}

// Repeated Read Byte(s) from register
void MC3635::readRegisters(uint8_t reg, byte *buffer, uint8_t len, uint8_t idx)
{
    if (interface == 0)
    {
	    Wire.beginTransmission(MC3635_CFG_I2C_ADDR);
	    Wire.write(reg);
	    Wire.endTransmission(false); //endTransmission but keep the connection active
	    Wire.requestFrom(MC3635_CFG_I2C_ADDR, len); //Ask for bytes, once done, bus is released by default

	    while(Wire.available() < len); //Hang out until we get the # of bytes we expect
	    for(int x = 0 ; x < len ; x++)
		buffer[x] = Wire.read();
    }
    else
    {
	    uint8_t data = reg | READ;
	    digitalWrite(CSn[idx],LOW);
	    SPI.transfer(data);
	    for (int x = 0 ; x < len ; x++)
		buffer[x] = SPI.transfer(0x00);
	    delayMicroseconds(chip_select_delay);
	    digitalWrite(CSn[idx], HIGH);
    }
}
//Set interface  
void MC3635::SetInterface(uint8_t _interface)
{
	interface = _interface;

}
//Set the operation mode  
void MC3635::SetMode(MC3635_mode_t mode, uint8_t idx)
{
    uint8_t value;
    value = readRegister8(MC3635_REG_MODE_C, idx);
    value &= 0b11110000;
    value |= mode;
    writeRegister8(MC3635_REG_MODE_C, value,idx);

}

//Set the range control
void MC3635::SetRangeCtrl(MC3635_range_t range,uint8_t idx)
{
    uint8_t value;    
    CfgRange = range;
    SetMode(MC3635_MODE_STANDBY,idx);
    value = readRegister8(MC3635_REG_RANGE_C,idx);
    value &= 0b00000111;
    value |= (range << 4)&0x70 ;
    writeRegister8(MC3635_REG_RANGE_C, value,idx);
    Serial.print(MC3635_REG_RANGE_C);
    Serial.print('\t');
    Serial.print(value);
    Serial.print('\n');
    
}

void MC3635::reset(uint8_t idx)
{
    writeRegister8(0x10, 0x01, idx);
	writeRegister8(0x24, 0x40, idx);
    writeRegister8(0x1b, 0x00, idx);
	if (interface == 0)
		writeRegister8(0x0D, 0x40, idx);
	else
		writeRegister8(0x0D, 0x80, idx);
}
void MC3635::SetSniffAGAIN(MC3635_gain_t gain,uint8_t idx)
{
	writeRegister8(0x20, 0x00,idx);
	uint8_t value;
    value = readRegister8(MC3635_REG_GAIN,idx);
    value &= 0b00111111;
    value |= (gain << 6);
    writeRegister8(MC3635_REG_GAIN, value, idx);
    /*Serial.print(MC3635_REG_GAIN);
    Serial.print('\t');
    Serial.print(value);
    Serial.print('\n');
    */
}
void MC3635::SetWakeAGAIN(MC3635_gain_t gain,uint8_t idx)
{
	writeRegister8(0x20, 0x01, idx);
	uint8_t value;
    value = readRegister8(MC3635_REG_GAIN, idx);
    value &= 0b00111111;
    value |= (gain << 6);
    writeRegister8(MC3635_REG_GAIN, value, idx);
    /*Serial.print(MC3635_REG_GAIN);
    Serial.print('\t');
    Serial.print(value);
    Serial.print('\n');
    */
}
//Set the resolution control
void MC3635::SetResolutionCtrl(MC3635_resolution_t resolution, uint8_t idx)
{
     uint8_t value;
     CfgResolution = resolution;
     SetMode(MC3635_MODE_STANDBY, idx);
     value = readRegister8(MC3635_REG_RANGE_C, idx);
     value &= 0b01110000;
     value |= resolution;
     writeRegister8(MC3635_REG_RANGE_C, value, idx);
    Serial.print(MC3635_REG_RANGE_C);
    Serial.print('\t');
    Serial.print(value);
    Serial.print('\n');
    
}

//Set the sampling rate
void MC3635::SetCWakeLPSampleRate(MC3635_cwake_lp_t sample_rate, uint8_t idx)
{
     uint8_t value;
     SetMode(MC3635_MODE_STANDBY, idx);
     value = readRegister8(MC3635_REG_WAKE_C, idx);
     value &= 0b00000000;
     value |= sample_rate;
     writeRegister8(MC3635_REG_WAKE_C, value, idx);
}

void MC3635::SetCWakeULPSampleRate(MC3635_cwake_ulp_t sample_rate, uint8_t idx)
{
     uint8_t value;
     SetMode(MC3635_MODE_STANDBY, idx);
     value = readRegister8(MC3635_REG_WAKE_C, idx);
     value &= 0b00000000;
     value |= sample_rate;
     writeRegister8(MC3635_REG_WAKE_C, value, idx);
}
void MC3635::SetCWakePRESampleRate(MC3635_cwake_pp_t sample_rate, uint8_t idx) 
{
     uint8_t value;     
     SetMode(MC3635_MODE_STANDBY, idx);
     value = readRegister8(MC3635_REG_WAKE_C, idx);
     value &= 0b00000000;
     value |= sample_rate;
     writeRegister8(MC3635_REG_WAKE_C, value, idx);
    /*Serial.print(MC3635_REG_WAKE_C);
    Serial.print('\t');
    Serial.print(value);
    Serial.print('\n');
    */
}	
void MC3635::SetPowerMode(MC3635_power_t pm, uint8_t idx)
{
     uint8_t value;
     SetMode(MC3635_MODE_STANDBY, idx);
     value = readRegister8(MC3635_REG_POWER_MODE, idx);
     value &= 0b00000000;
     value |= pm;
     writeRegister8(MC3635_REG_POWER_MODE, value, idx);
    /*Serial.print(MC3635_REG_POWER_MODE);
    Serial.print('\t');
    Serial.print(value);
    Serial.print('\n');
    */
}
//Get the output sampling rate
MC3635_cwake_lp_t MC3635::GetCWakeSampleRate(uint8_t idx)
{
/* Read the data format register to preserve bits */
     uint8_t value;
     value = readRegister8(MC3635_REG_WAKE_C, idx);
     value &= 0b00000111;
     return (MC3635_cwake_lp_t) (value);
}

//Get the range control
MC3635_range_t MC3635::GetRangeCtrl(uint8_t idx)
{
  	/* Read the data format register to preserve bits */
     uint8_t value;
     value = readRegister8(MC3635_REG_RANGE_C, idx);
     value &= 0x70;
     return (MC3635_range_t) (value >> 4);
}

//Get the range control
MC3635_resolution_t MC3635::GetResolutionCtrl(uint8_t idx)
{
  	/* Read the data format register to preserve bits */
     uint8_t value;
     value = readRegister8(MC3635_REG_RANGE_C, idx);
     value &= 0x07;
     return (MC3635_resolution_t) (value);
}
void MC3635::SetNumOfDevice(uint8_t num)
{
	numOfDevice = num;
}
void MC3635::SetCSPin(uint8_t idx,uint8_t pin)
{
	if (idx > NUM_OF_DEVICE)
		return;
	CSn[idx] = pin;
}
void MC3635::writeRegister(uint8_t addr, uint8_t value, uint8_t idx)
{
  writeRegister8(addr, value,idx);
}
uint8_t MC3635::readRegister(uint8_t addr, uint8_t idx)
{
  return readRegister8(addr, idx);
}



bool MC3635::start(uint8_t _interface)
{
     SetInterface(_interface);
     if (interface == 0)
     {
	     Wire.begin(); // Initialize I2C
     }
     else
     {
	     // Initialize SPI
	     SPI.begin();
	     SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE3));
	     for (int x = 0; x < numOfDevice; x++)
	     {
		     pinMode(CSn[x] , OUTPUT);
		     digitalWrite(CSn[x], HIGH);
	     }
     }
     for (uint8_t idx=0; idx < numOfDevice; idx++)
     {
	//Reset
    writeRegister(0x1B, 0xFF, idx);
	reset(idx);
    writeRegister(0x1B, 0xFF, idx);

	SetMode(MC3635_MODE_STANDBY, idx);
        writeRegister(0x1B, 0xFF, idx);


	//SetWakeAGAIN
	SetWakeAGAIN(MC3635_GAIN_1X, idx);
	//SetSniffAGAIN
	SetSniffAGAIN(MC3635_GAIN_1X, idx);
	SetPowerMode(MC3635_PRE_POWER, idx);
	SetRangeCtrl(MC3635_RANGE_2G, idx); //Range: 8g
	SetResolutionCtrl(MC3635_RESOLUTION_12BIT, idx); //Resolution: 14bit
	

    SetMode(MC3635_MODE_CWAKE, idx); //Mode: Active
}
    return true;

}

void MC3635::stop()
{
     for (uint8_t idx=0; idx < numOfDevice; idx++){
      SetMode(MC3635_MODE_SLEEP, idx); //Mode: Sleep
  }
}

//Read the raw counts and SI units mearsurement data
MC3635_acc_t MC3635::readRawAccel(uint8_t idx)
{
      float faRange[5] = { 19.614f, 39.228f, 78.456f, 156.912f, 117.684f}; //{2g, 4g, 8g, 16g, 12g}
      float faResolution[6] = { 32.0f, 64.0f, 128.0f, 512.0f, 2048.0f, 8192.0f}; //{6bit, 7bit, 8bit, 10bit, 12bit, 14bit}

      byte rawData[6];
      readRegisters(MC3635_REG_XOUT_LSB, rawData, 6, idx);  // Read the six raw data registers into data array
      x = (short)((((unsigned short)rawData[1]) << 8) | rawData[0]);
      y = (short)((((unsigned short)rawData[3]) << 8) | rawData[2]);
      z = (short)((((unsigned short)rawData[5]) << 8) | rawData[4]);

      AccRaw.XAxis = (short) (x);
      AccRaw.YAxis = (short) (y);
      AccRaw.ZAxis = (short) (z);
      AccRaw.XAxis_g = (float) (x) / faResolution[CfgResolution]*faRange[CfgRange];
      AccRaw.YAxis_g = (float) (y) / faResolution[CfgResolution]*faRange[CfgRange];
      AccRaw.ZAxis_g = (float) (z) / faResolution[CfgResolution]*faRange[CfgRange];
      return AccRaw;

}
