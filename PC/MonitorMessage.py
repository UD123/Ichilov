"""

Levron : Runtime Comm Message for PC Monitor
Usage :
    
Message Format:
    '<msgId,count, some data - string>'
    
TODO :


-----------------------------
 Ver    Date     Who    Descr
-----------------------------
0102   18.11.22 UD     Created 
-----------------------------

"""


import time
import unittest


#%% Message
MESSAGE_TYPE                     = {'VALUE':0, 'TEXT':1, 'ARRAY':2}
class Message:
    
    def __init__(self, msgId = 1, msgType = MESSAGE_TYPE['ARRAY'], msgCount = 0, msgData = []):

        self.Id             = int(msgId)
        self.Type           = int(msgType)
        self.Count          = int(msgCount)      # time in sec
        self.Data           = msgData
        
        self.Error          = int(0)
        
    def dataToString(self):
        # convert data to string
        if  self.Type == MESSAGE_TYPE['VALUE']:
            txt = str(self.Data)
            
        elif self.Type == MESSAGE_TYPE['TEXT']:
            txt = str(self.Data)

        elif self.Type == MESSAGE_TYPE['ARRAY']:
            txt = str(self.Data)
            txt = txt[1:-1]  # remove brackets
            
        else:
            raise ValueError 
            
        return txt   

    def stringToData(self, txt):
        # convert data to string
        dout = []
        if  self.Type == MESSAGE_TYPE['VALUE']:
            dout = float(txt)
            
        elif self.Type == MESSAGE_TYPE['TEXT']:
            dout = str(txt)

        elif self.Type == MESSAGE_TYPE['ARRAY']:
            if isinstance(txt,str):
                data = txt.split(',')
            else:
                data = txt
                
            dout = [float(x) for x in data]
            
        else:
            raise ValueError             
  
        return dout        
        
    def encodeString(self):
        # convert message to string
        dtxt = self.dataToString()
        mtxt = '%d,%d,%d,%s' %(self.Id,self.Type,self.Count,dtxt)
        return mtxt
    
    def decodeString(self, txt):
        data = txt.split(',')
        if len(data) < 3:
            self.Error = 1
            print('Decode error')
            return
        #print(txt)
        expectedId          = self.Id
                
        try:
            self.Id         = int(data[0])
            self.Type       = int(data[1])
            self.Count      = int(data[2])
            self.Data       = self.stringToData(data[3:])

        except Exception as e:
            self.Id         = int(0)
            self.Count      = int(0)
            self.Data       = []
            self.tprint('ERROR : String Decode')
            print(e)
            
        # check
        if self.Id != expectedId:
            self.Error = 2
            self.tprint('ERROR : Unexpected message')
  
        return self.Data
        
    def tprint(self, txt='',level='I'):
        
        ptxt = '%s: MSG: %s' % (level,txt) 
        print(ptxt)        
        
#%% --------------------------           
class TestMessage(unittest.TestCase):                
    def test_Create(self):
        d           = Message(0,1,2)
        self.assertEqual(0, d.Id)
        self.assertEqual(1, d.Type)
        
    def test_DataToStringAndBack_Value(self):
        # test params dave a nd load 
        dataIn      = 120
        m           = Message(1,MESSAGE_TYPE['VALUE'],1,dataIn)
        txt         = m.dataToString()
        dataOut     = m.stringToData(txt)
        self.assertEqual(dataIn, dataOut)
        
    def test_DataToStringAndBack_Text(self):
        # test params dave a nd load 
        dataIn      = 'Kukuriku - 120'
        m           = Message(1,MESSAGE_TYPE['TEXT'],1,dataIn)
        txt         = m.dataToString()
        dataOut     = m.stringToData(txt)
        self.assertEqual(dataIn, dataOut)
        
    def test_DataToStringAndBack_Array(self):
        # test params dave a nd load 
        dataIn      = [2,1.3,-2355,128,0.0005,3.14]
        m           = Message(1,MESSAGE_TYPE['ARRAY'],1,dataIn)
        txt         = m.dataToString()
        dataOut     = m.stringToData(txt)
        self.assertEqual(dataIn, dataOut)  
        
    def test_MsgToStringAndBack_Array(self):
        # test params dave a nd load 
        dataIn      = [2,1.3,-2355,128,0.0005,3.14]
        m           = Message(1,MESSAGE_TYPE['ARRAY'],1,dataIn)
        txt         = m.encodeString()
        dataOut     = m.decodeString(txt)
        self.assertEqual(dataIn, dataOut)         
        
# -------------------------- 
if __name__ == '__main__':
    #print (__doc__)
    
    
    # single view test
    singletest = unittest.TestSuite()
    #singletest.addTest(TestMessage("test_Create"))
    #singletest.addTest(TestMessage("test_DataToStringAndBack_Value"))
    #singletest.addTest(TestMessage("test_DataToStringAndBack_Text"))
    singletest.addTest(TestMessage("test_DataToStringAndBack_Array"))
    singletest.addTest(TestMessage("test_MsgToStringAndBack_Array"))
    
    unittest.TextTestRunner().run(singletest)
    #unittest.main()