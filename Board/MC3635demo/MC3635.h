#ifndef MC3635_h
#define MC3635_h

#include "Arduino.h"
#include "Wire.h"
#include "SPI.h"

//#define INTERFACE_I2C
#define INTERFACE_SPI

/*******************************************************************************
 *** CONSTANT / DEFINE
 *******************************************************************************/
#define MC3635_RETCODE_SUCCESS                 (0)
#define MC3635_RETCODE_ERROR_BUS               (-1)
#define MC3635_RETCODE_ERROR_NULL_POINTER      (-2)
#define MC3635_RETCODE_ERROR_STATUS            (-3)
#define MC3635_RETCODE_ERROR_SETUP             (-4)
#define MC3635_RETCODE_ERROR_GET_DATA          (-5)
#define MC3635_RETCODE_ERROR_IDENTIFICATION    (-6)
#define MC3635_RETCODE_ERROR_NO_DATA           (-7)
#define MC3635_RETCODE_ERROR_WRONG_ARGUMENT    (-8)
#define MC3635_FIFO_DEPTH    32
#define MC3635_REG_MAP_SIZE    64



/*******************************************************************************
 *** CONSTANT / DEFINE
 *******************************************************************************/

//=============================================
#define MC3635_INTR_C_IPP_MODE_OPEN_DRAIN    (0x00)
#define MC3635_INTR_C_IPP_MODE_PUSH_PULL     (0x01)

#define MC3635_INTR_C_IAH_ACTIVE_LOW     (0x00)
#define MC3635_INTR_C_IAH_ACTIVE_HIGH    (0x02)


/*******************************************************************************
 *** Register Map
 *******************************************************************************/
//=============================================
#define MC3635_REG_EXT_STAT_1       (0x00)
#define MC3635_REG_EXT_STAT_2       (0x01)
#define MC3635_REG_XOUT_LSB         (0x02)
#define MC3635_REG_XOUT_MSB         (0x03)
#define MC3635_REG_YOUT_LSB         (0x04)
#define MC3635_REG_YOUT_MSB         (0x05)
#define MC3635_REG_ZOUT_LSB         (0x06)
#define MC3635_REG_ZOUT_MSB         (0x07)
#define MC3635_REG_STATUS_1         (0x08)
#define MC3635_REG_STATUS_2         (0x09)
#define MC3635_REG_MODE_C           (0x10)
#define MC3635_REG_WAKE_C           (0x11)
#define MC3635_REG_SNIFF_C          (0x12)
#define MC3635_REG_SNIFFTH_C        (0x13)
#define MC3635_REG_IO_C             (0x14)
#define MC3635_REG_RANGE_C          (0x15)
#define MC3635_REG_FIFO_C           (0x16)
#define MC3635_REG_INTR_C           (0x17)
#define MC3635_REG_PROD             (0x18)
#define MC3635_REG_POWER_MODE       (0x1C)
#define MC3635_REG_DMX              (0x20)
#define MC3635_REG_DMY              (0x21)
#define MC3635_REG_GAIN             (0x21)
#define MC3635_REG_DMZ              (0x22)
#define MC3635_REG_RESET            (0x24)
#define MC3635_REG_XOFFL            (0x2A)
#define MC3635_REG_XOFFH            (0x2B)
#define MC3635_REG_YOFFL            (0x2C)
#define MC3635_REG_YOFFH            (0x2D)
#define MC3635_REG_ZOFFL            (0x2E)
#define MC3635_REG_ZOFFH            (0x2F)
#define MC3635_REG_XGAIN            (0x30)
#define MC3635_REG_YGAIN            (0x31)
#define MC3635_REG_ZGAIN            (0x32)
#define MC3635_REG_OPT              (0x3B)
#define MC3635_REG_LOC_X            (0x3C)
#define MC3635_REG_LOC_Y            (0x3D)
#define MC3635_REG_LOT_dAOFSZ       (0x3E)
#define MC3635_REG_WAF_LOT          (0x3F)

#define MC3635_NULL_ADDR    		(0)

struct MC3635_acc_t
{
	short XAxis;
    short YAxis;
    short ZAxis;      
    float XAxis_g;
	float YAxis_g;
	float ZAxis_g;
} ;

typedef enum
{
    MC3635_GAIN_DEFAULT    = 0b00,
    MC3635_GAIN_4X         = 0b01,
    MC3635_GAIN_1X         = 0b10,
    MC3635_GAIN_NOT_USED   = 0b11,   
}   MC3635_gain_t;

typedef enum
{
    MC3635_MODE_SLEEP 	   = 0b000,
    MC3635_MODE_STANDBY    = 0b001,
    MC3635_MODE_SNIFF      = 0b010,
    MC3635_MODE_CWAKE      = 0b101, 
    MC3635_MODE_TRIG       = 0b111,  
}   MC3635_mode_t;

typedef enum
{
    MC3635_RANGE_2G   = 0b000,
    MC3635_RANGE_4G   = 0b001,
    MC3635_RANGE_8G   = 0b010,
    MC3635_RANGE_16G  = 0b011,
    MC3635_RANGE_12G  = 0b100,
    MC3635_RANGE_END,	
}   MC3635_range_t;

typedef enum
{
    MC3635_RESOLUTION_6BIT    = 0b000, 
    MC3635_RESOLUTION_7BIT    = 0b001, 
    MC3635_RESOLUTION_8BIT    = 0b010, 
    MC3635_RESOLUTION_10BIT   = 0b011, 
    MC3635_RESOLUTION_12BIT   = 0b100, 
    MC3635_RESOLUTION_14BIT   = 0b101,  //(Do not select if FIFO enabled)
    MC3635_RESOLUTION_END,
}   MC3635_resolution_t;

typedef enum
{
    // Table match to low power
    MC3635_CWAKE_ULP_DEFAULT_50Hz = 0b0000,
    MC3635_CWAKE_ULP_0p4Hz        = 0b0001,
    MC3635_CWAKE_ULP_0p8Hz        = 0b0010,
    MC3635_CWAKE_ULP_2Hz          = 0b0011,
    MC3635_CWAKE_ULP_6Hz          = 0b0100,
    MC3635_CWAKE_ULP_RESER0       = 0b0101,
    MC3635_CWAKE_ULP_25Hz         = 0b0110,
    MC3635_CWAKE_ULP_50Hz         = 0b0111,
    MC3635_CWAKE_ULP_100Hz        = 0b1000,
    MC3635_CWAKE_ULP_190Hz        = 0b1001,
    MC3635_CWAKE_ULP_380Hz        = 0b1010,
    MC3635_CWAKE_ULP_750Hz        = 0b1011,
    MC3635_CWAKE_ULP_1100Hz       = 0b1100,
    MC3635_CWAKE_ULP_RESER1       = 0b1101,
    MC3635_CWAKE_ULP_RESER2       = 0b1110,
    MC3635_CWAKE_ULP_1300Hz       = 0b1111,
    MC3635_CWAKE_ULP_END,
}   MC3635_cwake_ulp_t;
typedef enum
{
    // Table match to low power
    MC3635_CWAKE_LP_DEFAULT_50Hz = 0b0000,
    MC3635_CWAKE_LP_0p4Hz        = 0b0001,
    MC3635_CWAKE_LP_0p8Hz        = 0b0010,
    MC3635_CWAKE_LP_2Hz          = 0b0011,
    MC3635_CWAKE_LP_6Hz          = 0b0100,
    MC3635_CWAKE_LP_14Hz         = 0b0101,
    MC3635_CWAKE_LP_28Hz         = 0b0110,
    MC3635_CWAKE_LP_54Hz         = 0b0111,
    MC3635_CWAKE_LP_100Hz        = 0b1000,
    MC3635_CWAKE_LP_210Hz        = 0b1001,
    MC3635_CWAKE_LP_400Hz        = 0b1010,
    MC3635_CWAKE_LP_600Hz        = 0b1011,
    MC3635_CWAKE_LP_RESER0       = 0b1100,
    MC3635_CWAKE_LP_RESER1       = 0b1101,
    MC3635_CWAKE_LP_RESER2       = 0b1110,
    MC3635_CWAKE_LP_750Hz        = 0b1111,
    MC3635_CWAKE_LP_END,
}   MC3635_cwake_lp_t;
typedef enum
{
    // Table match to precision power
    MC3635_CWAKE_PP_DEFAULT_50Hz = 0b0000,
    MC3635_CWAKE_PP_0p4Hz        = 0b0001,
    MC3635_CWAKE_PP_0p8Hz        = 0b0010,
    MC3635_CWAKE_PP_2Hz          = 0b0011,
    MC3635_CWAKE_PP_6Hz          = 0b0100,
    MC3635_CWAKE_PP_14Hz         = 0b0101,
    MC3635_CWAKE_PP_28Hz         = 0b0110,
    MC3635_CWAKE_PP_55Hz         = 0b0111,
    MC3635_CWAKE_PP_80Hz         = 0b1000,
    MC3635_CWAKE_PP_RESER0       = 0b1001,
    MC3635_CWAKE_PP_RESER1       = 0b1010,
    MC3635_CWAKE_PP_RESER2       = 0b1011,
    MC3635_CWAKE_PP_RESER3       = 0b1100,
    MC3635_CWAKE_PP_RESER4       = 0b1101,
    MC3635_CWAKE_PP_RESER5       = 0b1110,
    MC3635_CWAKE_PP_100Hz        = 0b1111,
    MC3635_CWAKE_PP_END,
}   MC3635_cwake_pp_t;

typedef enum
{
    MC3635_SNIFF_SR_DEFAULT_6Hz = 0b0000,
    MC3635_SNIFF_SR_0p4Hz      = 0b0001,
    MC3635_SNIFF_SR_0p8Hz      = 0b0010,
    MC3635_SNIFF_SR_2Hz        = 0b0011,
    MC3635_SNIFF_SR_6Hz        = 0b0100,
    MC3635_SNIFF_SR_13Hz       = 0b0101,
    MC3635_SNIFF_SR_25Hz       = 0b0110,
    MC3635_SNIFF_SR_50Hz       = 0b0111,
    MC3635_SNIFF_SR_100Hz      = 0b1000,
    MC3635_SNIFF_SR_200Hz      = 0b1001,
    MC3635_SNIFF_SR_400Hz      = 0b1010,// only for OSR = 32
    MC3635_SNIFF_SR_END,
}   MC3635_sniff_sr_t;

typedef enum
{
    MC3635_FIFO_CONTROL_DISABLE = 0,
    MC3635_FIFO_CONTROL_ENABLE,
    MC3635_FIFO_CONTROL_END,
}   MC3635_fifo_control_t;

typedef enum
{
    MC3635_FIFO_MODE_NORMAL = 0,
    MC3635_FIFO_MODE_WATERMARK,
    MC3635_FIFO_MODE_END,
}   MC3635_fifo_mode_t;

typedef struct
{
    unsigned char    bWAKE;              // Sensor wakes from sniff mode.
    unsigned char    bACQ;               // New sample is ready and acquired.
    unsigned char    bFIFO_EMPTY;        // FIFO is empty.
    unsigned char    bFIFO_FULL;         // FIFO is full.
    unsigned char    bFIFO_THRESHOLD;    // FIFO sample count is equal to or greater than the threshold count.
    unsigned char    bRESV;
    unsigned char    baPadding[2];
}   MC3635_InterruptEvent;

typedef enum 
{
	MC3635_LOW_POWER =0,
	MC3635_RESERVED_1,
	MC3635_RESERVED_2,
	MC3635_ULOW_POWER,
	MC3635_PRE_POWER,
}MC3635_power_t;
#define NUM_OF_DEVICE 10

class MC3635{
 public:
    float ODRlookup(float requestODR);

	uint8_t interface;
	uint8_t numOfDevice;
  	bool start(uint8_t _interface);      // begin measurements
  	void stop();       // end measurments
	void reset(uint8_t idx);
	void SetInterface(uint8_t _interface);
	void SetNumOfDevice(uint8_t num);
	void SetCSPin(uint8_t idx, uint8_t pin);
  	void SetMode(MC3635_mode_t, uint8_t idx);
	void SetRangeCtrl(MC3635_range_t, uint8_t idx);   
	void SetResolutionCtrl(MC3635_resolution_t, uint8_t idx); 
	void SetCWakeLPSampleRate(MC3635_cwake_lp_t, uint8_t idx);  
	void SetCWakeULPSampleRate(MC3635_cwake_ulp_t, uint8_t idx);  
	void SetCWakePRESampleRate(MC3635_cwake_pp_t, uint8_t idx);  
	void SetSniffAGAIN(MC3635_gain_t, uint8_t idx);
	void SetWakeAGAIN(MC3635_gain_t, uint8_t idx);
	void SetPowerMode(MC3635_power_t, uint8_t idx);
	MC3635_sniff_sr_t GetSniffSampleRate(MC3635_sniff_sr_t, uint8_t idx);
	MC3635_resolution_t GetResolutionCtrl(uint8_t idx);	
	MC3635_range_t GetRangeCtrl(uint8_t idx);
	MC3635_cwake_lp_t GetCWakeSampleRate(uint8_t idx);   
	MC3635_acc_t readRawAccel(uint8_t idx);
	uint8_t readRegister(uint8_t addr, uint8_t idx);
	void writeRegister(uint8_t addr, uint8_t value, uint8_t idx);
        void readRegisters(uint8_t reg, byte *buffer, uint8_t len, uint8_t idx);  
        void knock();

    //double ODRLookup(int requestODR);
	
 private:
 	short x, y, z;
	uint8_t CSn[NUM_OF_DEVICE]; //P10,P9,... for Chip select
	MC3635_acc_t AccRaw; // Raw Accelerometer data
	uint8_t readRegister8(uint8_t reg, uint8_t idx);
	int16_t readRegister16(uint8_t reg, uint8_t idx);
	//void readRegisters(uint8_t reg, byte *buffer, uint8_t len, uint8_t idx);  
	bool readRegisterBit(uint8_t reg, uint8_t pos, uint8_t idx);
	void writeRegisterBit(uint8_t reg, uint8_t pos, bool state, uint8_t idx);
	void writeRegister16(uint8_t reg, int16_t value, uint8_t idx);
	void writeRegister8(uint8_t reg, uint8_t value, uint8_t idx);       
    //double ODRLookup(int requestODR);

};
#endif
