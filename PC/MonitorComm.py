"""

Runtime Comm for PC Monitor

Compatible : 
    MainApp.ino - version 0102

Environment:
    conda Levron

Usage :
    
Message Format:
    '<msgId,type, count, some data - string>'
    
TODO :


-----------------------------
 Ver    Date     Who    Descr
-----------------------------
0201   27.09.24 UD     Created for Menu
-----------------------------

"""

import serial
import time
import sys
import glob

from MonitorMessage import Message, MESSAGE_TYPE

import time
import unittest

# global variables for module
startMarker = 60  # <
endMarker   = 62    # >
ser         = None


#%%
class MonitorComm: 
    
    def __init__(self, cfg = None):  
    
        self.cfg = cfg      
        
    #========================     
    def msgSendRecv(self, msgSend = Message(), msgRecvExpected = Message()):
        # send message and receive result
        self.sendMsg(msgSend)    
        msgRecv = self.recvMsg(msgRecvExpected)
        
        # checks
        if msgRecv.Id != msgRecvExpected.Id:
            self.tprint('Unexpected message Id received : maybe an error','W')
            
        elif msgRecv.Type != msgRecvExpected.Type:
            self.tprint('Unexpected message Type received : maybe an error','W')
            
        elif len(msgRecv.Data) != len(msgRecvExpected.Data):
            self.tprint('Unexpected message Length received : maybe an error','W')            
        
        return msgRecv
        
    #========================     
    def sendMsg(self, msgSend = Message()):
        # send message encoded
        sendStr = msgSend.encodeString()
        self.tprint("SENDSTR %s" %(sendStr))
        self.sendToArduino(sendStr.encode('utf-8'))    
        
    #========================     
    def recvMsg(self, msgRecv = Message()):
        # received message encoded
        msg      = self.recvFromArduino(1)
        recvStr  = msg #.decode('utf-8')
        self.tprint("RECVSTR %s" %(recvStr))
        recvData = msgRecv.decodeString(recvStr)        
        return msgRecv
    
    #========================     
    def valToArduino(self, ledA, ledB, servo):
        dataSend = [ledA, ledB, servo]
        msgSend  = Message(msgId = 1, msgType = MESSAGE_TYPE['ARRAY'],msgData = dataSend)
        self.sendMsg(msgSend)
        
        msgRecv  = Message(msgId = 2, msgType = MESSAGE_TYPE['ARRAY'],msgData = [])
        dataRecv = self.recvMsg(msgRecv)
        
    #========================     
    def valToArduinoOld(self, ledA, ledB, servo):
        sendStr = "%s,%s,%s" %(ledA, ledB, servo)
        self.tprint("SENDSTR %s" %( sendStr))
        self.sendToArduino(sendStr.encode('utf-8'))
    
    #========================     
    def listSerialPorts(self):
           # http://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
           
        """Lists serial ports
    
        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of available serial ports
        """
        if sys.platform.startswith('win'):
            ports = ['COM' + str(i + 1) for i in range(12)]
    
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this is to exclude your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
    
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
    
        else:
            raise EnvironmentError('Unsupported platform')
    
        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException) as e:
                print(e)
                pass
        return result
    
    #========================    
    def setupSerial(self, serPort):
           
        global  ser
        
        # NOTE the user must ensure that the serial port and baudrate are correct
        #~ serPort = "/dev/ttyS81"
        baudRate = 9600
        ser = serial.Serial(serPort, baudRate)
        self.tprint("Serial port " + serPort + " opened  Baudrate " + str(baudRate))

        self.waitForArduino()
    
    #========================    
    def closeSerial(self):
           
        global ser
        if 'ser' in globals():
            ser.close()
            self.tprint("Serial Port Closed")
        else:
            self.tprint("Serial Port Not Opened")
    
    #========================    
    def sendToArduino(self, sendStr):
           
        global startMarker, endMarker, ser
        
        if ser is None:
            self.tprint('Connect serial first')
        return
    
        ser.write(chr(startMarker).encode('utf-8'))
        ser.write(sendStr)
        ser.write(chr(endMarker).encode('utf-8'))
        
    #===========================    
    def recvFromArduino(self, timeOut): # timeout in seconds eg 1.5
           
        global startMarker, endMarker, ser
    
        dataBuf = ""
        x = "z" # any value that is not an end- or startMarker
        byteCount = -1 # to allow for the fact that the last increment will be one too many
        startTime = time.time()
        #~ print "Start %s" %(startTime)
    
        # wait for the start marker
        while  ord(x) != startMarker: 
            if time.time() - startTime >= timeOut:
                return('<<')
            x = ser.read()
    

        # save data until the end marker is found
        while ord(x) != endMarker:
            if time.time() - startTime >= timeOut:
                return('>>')
            if ord(x) != startMarker:
                dataBuf = dataBuf + x.decode("utf-8") 
            x = ser.read()
            
        return(dataBuf)
    
    #============================                    
    def waitForArduino(self):
    
       # wait until the Arduino sends 'Arduino Ready' - allows time for Arduino reset
       # it also ensures that any bytes left over from a previous message are discarded
       
        self.tprint("Waiting for Arduino to reset")
    
        msg = ""
        cnt = 0 
        while msg.find("Arduino is ready") == -1:

            msg = self.recvFromArduino(10)
            self.tprint(msg)
            cnt = cnt + 1
            if cnt > 10000:
                break
            
    def tprint(self, txt='',level='I'):
        
        ptxt = '%s: COM: %s' % (level,txt) 
        print(ptxt)
        
        
#%% --------------------------           
class TestMessage(unittest.TestCase):                
    def test_Create(self):
        d           = Message()
        self.assertEqual(0, d.Id)
        
    def test_CheckIfCreateEvent(self):
        # test params dave a nd load      
        d           = Message()
        isEvent     = d.CheckIfCreateEvent()
        self.assertEqual(False, isEvent)
        time.sleep(d.event_period)
        isEvent     = d.CheckIfCreateEvent()
        self.assertEqual(True, isEvent)
        
    def test_Connection(self):
        # debug interface
        global  ser
        m       = MonitorComm()
        serPort = 'COM12'
        m.setupSerial(serPort)
        msgList = ['1,1,2,3','3,1,2,3','91,1']
        for stxt  in msgList:
            m.sendToPicBoard(stxt)
            rtxt = m.recvFromPicBoard(60)
            print(stxt,' => ',rtxt)
        m.closeSerial()

    def test_BLE(self):
        # debug BLE interface
        global  ser
        m       = MonitorComm()
        serPort = 'COM6'
        m.setupSerial(serPort)
        isOk    = m.configureLocalBLE()
        print(isOk)
        m.closeSerial()

# -------------------------- 
if __name__ == '__main__':
    #print (__doc__)
    
    
    # single view test
    singletest = unittest.TestSuite()
    singletest.addTest(TestMessage("test_Create"))
    #singletest.addTest(TestMessage("test_CheckIfCreateEvent"))
    

    
    unittest.TextTestRunner().run(singletest)
    #unittest.main()