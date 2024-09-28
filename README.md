# Arduino
Basic implementation of the Accelerometer MC3565 interface
and python GUI that can receive and display the data in real time

# Arduino Uno and mCube (MC3635) SPI Connection
Make sure to connect evaluation board of MC3635 in the following way
Name           |  Arduino Uno  | MC3635 
:------------: |  :----------: | :-------------: 
               |  SCLK 13      | SCL 6
-              |  MISO 12      | SDO 1
-              |  MOSI 11      | SDA 7
-              |  SS   10      | SCS 10
               |  3.3V         | DVDD 9
               | GND           | GND 8

# Folder structure

# Special thanks
The code is based on the library provided by:
https://github.com/cphuangf/Accelerometer_MC3635
https://github.com/mcubemems/mCube_mc36xx_mcu_driver/tree/master

# Python installation
# Install Anaconda
conda create --prefix C:\RobotAI\Customers\Levron\Code\Envs\Levron python=3.9
conda activate C:\RobotAI\Customers\Levron\Code\Envs\Levron

# assume Spyder is installed as your EDT
pip install spyder-kernels==2.3.*
conda install pyserial


# Versions

 Ver  | Date         | Who   | Descr
:---: | :----------: | :---: |:-------------: 
0105  | 01.12.22     | UD    | Addign Accel

