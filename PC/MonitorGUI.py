# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 12:51:44 2022

@author: avita

Main application GUI

Usage :


Install:
	Avita -> env :  C:\RobotAI\Customers\Levron\Code\Envs\Levron

-----------------------------
 Ver    Date     Who    Descr
-----------------------------
0301   30.09.24 UD     3D view is added
0201   27.09.24 UD     adopted Levron
-----------------------------

"""
# -*- coding: utf-8 -*-
import os
#import tkinter as tk
#import threading
#import json

import time   # just to measure switch time
import logging

base_path     = os.path.abspath(".")
iconFilePath  = os.path.join(base_path, './logo.ico')


#%%
import tkinter as tk
import tkinter.ttk as ttk
#from tkinter import *
from MonitorComm import MonitorComm
from MonitorMessage import Message, MESSAGE_TYPE
#import atexit
COMM_PORT = 'COM4'

# def exit_handler():
#     print('My application is ending!')
#     closeSerial()
# atexit.register(exit_handler)

# global variables for this module
ledAstatus = 0
ledBstatus = 0
servoPos = 10
stopThread = False

import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg #, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib.backend_bases import key_press_handler

from threading import Thread
#import tkinter as tk

def FromUnsignedToSigned16(n):
    return n - 0x10000 if n & 0x8000 else n
def FromSignedToUnsigned16(n):
    return 0x10000 + n if n < 0 else n

style.use("dark_background")

class MonitorGUI:

    def __init__(self, win, cfg = None):

        self.win = win
        self.cfg = cfg
        self.com = MonitorComm(cfg)
		
		# ugly but simple
        self.pwm_value = 1000 # msec

    def getVersion(self):
        # 91 : read version
        msgSend   = Message(91,MESSAGE_TYPE['ARRAY'],1,[0])
        msgRecv   = self.new_method()
        msgRecv   = self.com.msgSendRecv(msgSend,msgRecv)
        self.tprint('Board version : %04d' %(msgRecv.Data[0]))

    def getSatus(self):
        # 93 : read status
        msgSend   = Message(93,[0])
        msgRecv   = self.new_method()
        msgRecv   = self.com.msgSendRecv(msgSend,msgRecv)
        self.tprint('Board stats : %04d' %(msgRecv.Data[0])) 
    def new_method(self):
        msgRecv   = Message(92,MESSAGE_TYPE['ARRAY'],1,[0])
        return msgRecv
		
		
    def setPwmValues(self):
        # 31 : read version
        msgSend   = Message(31,MESSAGE_TYPE['ARRAY'],1,[self.pwm_value])
        msgRecv   = Message(32,MESSAGE_TYPE['ARRAY'],1,[self.pwm_value])
        msgRecv   = self.com.msgSendRecv(msgSend,msgRecv)
        self.tprint('Set PWM value : %04d' %(msgRecv.Data[0]))	
        self.pwm_value = self.pwm_value + 500
		
    def getSensorValues(self):
        # 33 : read version
        msgSend   = Message(33,MESSAGE_TYPE['ARRAY'],1,[0])
        msgRecv   = Message(34,MESSAGE_TYPE['ARRAY'],1,[0])
        msgRecv   = self.com.msgSendRecv(msgSend,msgRecv)
        self.tprint('Sensor value : %04d' %(msgRecv.Data[0]))
        return msgRecv.Data[0]		
    
    def getAccelValues(self):
        # 33 : read version
        msgSend   = Message(35,MESSAGE_TYPE['ARRAY'],1,[0])
        msgRecv   = Message(36,MESSAGE_TYPE['ARRAY'],1,[0])
        msgRecv   = self.com.msgSendRecv(msgSend,msgRecv)
        self.tprint('Sensor values X: %04d,Y: %04d,Z: %04d,T: %04d' %(msgRecv.Data[0],msgRecv.Data[1],msgRecv.Data[2],msgRecv.Data[3]))
        return msgRecv.Data[0:3]	
    
    def getEcgRawValues(self):
        # 41 : read raw data
        msgSend   = Message(41,MESSAGE_TYPE['ARRAY'],1,[0])
        msgRecv   = Message(42,MESSAGE_TYPE['ARRAY'],1,[0,0])
        msgRecv   = self.com.msgSendRecv(msgSend,msgRecv)
        self.tprint('Raw values 0: %04d,1: %04d' %(msgRecv.Data[0],msgRecv.Data[1]))
        # convert 2 intergers to signed long
        #ecgData   = msgRecv.Data[1]*(2**16) + FromSignedToUnsigned16(msgRecv.Data[0])
        ecgData   = msgRecv.Data[1]
        self.tprint('Ecg value : %04f' %(ecgData))
        return ecgData
    
    def setFileData(self, valLV = 0, valSurf = 1, valPress = 2):
        # 51 : write, process and read file data
        msgSend   = Message(51,MESSAGE_TYPE['ARRAY'],1,[valLV,valSurf,valPress])
        msgRecv   = Message(52,MESSAGE_TYPE['ARRAY'],1,[0])
        msgRecv   = self.com.msgSendRecv(msgSend,msgRecv)
        self.tprint('Raw values LV: %04d, Surf: %04d, Press: %04d' %(msgSend.Data[0],msgSend.Data[1],msgSend.Data[2]))
        algData = msgRecv.Data[0]
        self.tprint('Alg value : %04f' %(algData))
        return algData
    
    
    # -------------------------
    def setupMenu(self):
        # add menu
        menu = tk.Menu(self.win)
        self.win.config(menu=menu)

        # Board
        boardmenu = tk.Menu(menu,tearoff = 0 )
        menu.add_cascade(label='Board',  menu=boardmenu)
        boardmenu.add_command(label='Connect...',                   command= self.commConnect)
        boardmenu.add_separator()    
        boardmenu.add_command(label='Serial List ports...',         command= self.listPorts)
        boardmenu.add_command(label='Serial Connect...',            command= self.commConnect)       
        boardmenu.add_command(label='Serial Close...',              command= self.commClose)  
        boardmenu.add_separator() 
        boardmenu.add_command(label='Board Version...',             command= self.getVersion)  
        boardmenu.add_command(label='Board Status...',              command= self.getSatus)

        # Sensor
        sensoramenu = tk.Menu(menu,tearoff = 0 )
        menu.add_cascade(label='Sensors',  menu=sensoramenu)
        sensoramenu.add_command(label='Select from List',           command=self.listPorts)

        # Tests
        sensoramenu = tk.Menu(menu,tearoff = 0 )
        menu.add_cascade(label='Tests',  menu=sensoramenu)
        sensoramenu.add_command(label='Set PWN values',             command=self.setPwmValues)
        sensoramenu.add_separator()
        sensoramenu.add_command(label='Get sensor values',          command=self.getSensorValues)
        sensoramenu.add_command(label='Get accel data',             command=self.getAccelValues)
        sensoramenu.add_command(label='Get ECG data',               command=self.getEcgRawValues)
        sensoramenu.add_separator()
        sensoramenu.add_command(label='Send Recv File',             command=self.setFileData)
        
        # Help
        helpmenu = tk.Menu(menu, tearoff = 0)
        menu.add_cascade(label='Help',        menu=helpmenu)
        helpmenu.add_command(label='User Manual',               command=lambda:self.HelpUserManual())
        helpmenu.add_command(label='About/Version',             command=lambda:self.getVersion)
        helpmenu.add_separator()
        helpmenu.add_command(label='Exit',                      command=self.finish)

    def setupView(self):
        # initial view

        self.win.minsize(width=520, height=370)
        self.win.config(bg = 'gray')
        self.win.title("ICHILOV GUI Demo")
        #self.win.iconbitmap(iconFilePath)

        self.masterframe = tk.Frame(bg = "gray")
        self.masterframe.pack(side='top',fill='both',expand=True)
        self.masterframe.grid_columnconfigure(0, weight=1)
        self.masterframe.grid_rowconfigure(0, weight=1)

        # add menu
        self.setupMenu()

        # which plot type
        #self.setupPlot2D()
        self.setupPlot3D()
         
        # select view
        self.setupScreen()
        
        # connection to board
        #self.selectPort()
        self.autoSelect()        
        
    def setupScreen(self):
        # https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html

        # self.fig  = Figure(figsize=(8, 6), dpi=100)
        # self.t    = np.arange(0, 3, .01)
        # self.y    = 2 * np.sin(2 * np.pi * self.t)
        # self.ax   = self.fig.add_subplot()
        # self.line, = self.ax.plot(self.t, self.y)
        # self.ax.set_xlabel("time [s]")
        # self.ax.set_ylabel("f(t)")
       
        
        # Create left and right frames
        left_frame  =  tk.Frame(self.masterframe,  width=60,  height=400,  bg='black')
        left_frame.pack(side='left',  fill='both',  padx=10,  pady=5,  expand=True)

        right_frame  =  tk.Frame(self.masterframe,  width=720,  height=400,  bg='black')
        right_frame.pack(side='right',  fill='both',  padx=10,  pady=5,  expand=True)        
        
        self.canvas= FigureCanvasTkAgg(self.fig, master=right_frame)
        #self.canvas.get_tk_widget().grid(row=1,column=0) #,rowspan = 4, sticky="NSEW") #,columnspan = 4,rowspan = 4)
        self.canvas.draw()
        self.right_frame = right_frame
        
        # pack_toolbar=False will make it easier to use a layout manager later on.
        # toolbar = NavigationToolbar2Tk(self.canvas, self.masterframe, pack_toolbar=False)
        # toolbar.update()

        self.canvas.mpl_connect("key_press_event", lambda event: print(f"you pressed {event.key}"))
        self.canvas.mpl_connect("key_press_event", key_press_handler)

        #button_quit = tk.Button(master=left_frame, text="Quit", command=self.win.destroy, relief=tk.RAISED)
        button_quit         = tk.Button(master=left_frame, text="Quit", command=self.finish, relief=tk.RAISED)
        slider_update       = tk.Scale(left_frame, from_=1, to=5, orient=tk.HORIZONTAL, command=self.slide, label="Freq [Hz]")
        self.btnAcquire     = tk.Button(master=left_frame, text="Acquire", command=self.btnAcquirePress, relief=tk.RAISED)
        self.btnAccel       = tk.Button(master=left_frame, text="Get Accel", command=self.btnAccelPress, relief=tk.RAISED)
        self.btnEcgRaw      = tk.Button(master=left_frame, text="Get Dir", command=self.btnEcgRawPress, relief=tk.RAISED)
        self.btnFileOffLine = tk.Button(master=left_frame, text="File Offline", command=self.btnFileOffLinePress, relief=tk.RAISED)
        self.btnFileOnLine  = tk.Button(master=left_frame, text="File on Board", command=self.btnFileOnLinePress, relief=tk.RAISED)
        self.e              = tk.Entry(master=right_frame)
        
                
        self.ledAbutton = tk.Button(master=left_frame, text="LedA", fg="white", bg="black", command = self.btnA)
        self.ledBbutton =  tk.Button(master=left_frame, text="LedB", fg="white", bg="black", command = self.btnB)

        
        # Packing order is important. Widgets are processed sequentially and if there
        # is no space left, because the window is too small, they are not displayed.
        # The canvas is rather flexible in its size, so we pack it last which makes
        # sure the UI controls are displayed as long as possible.
        
        ipadding = {'ipadx': 10, 'ipady': 10, 'padx': 5, 'pady': 5}
        #toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.btnAcquire.pack(**ipadding, side=tk.TOP, fill=tk.BOTH)
        self.btnAccel.pack(**ipadding, side=tk.TOP, fill=tk.BOTH)
        self.btnEcgRaw.pack(**ipadding, side=tk.TOP, fill=tk.BOTH)
        self.btnFileOffLine.pack(**ipadding, side=tk.TOP, fill=tk.BOTH)
        self.btnFileOnLine.pack(**ipadding, side=tk.TOP, fill=tk.BOTH)
        slider_update.pack(**ipadding, side=tk.TOP, fill=tk.BOTH)
  
        self.ledAbutton.pack(**ipadding, side=tk.TOP, fill=tk.BOTH)
        self.ledBbutton.pack(**ipadding, side=tk.TOP, fill=tk.BOTH)
        button_quit.pack(**ipadding, side=tk.BOTTOM, fill=tk.BOTH)
        
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)  
        
        self.e.pack(**ipadding, side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.e.delete(0,tk.END)
        self.e.insert(0,'Parameters and Messages')
        
        # run multiple
        self.x_data = []
        self.y_data = []
        self.btnAcquireStatus = False

    def setupPlot2D(self):
        # https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html

        self.fig  = Figure(figsize=(8, 6), dpi=100)
        self.t    = np.arange(0, 3, .01)
        self.y    = 2 * np.sin(2 * np.pi * self.t)
        self.ax   = self.fig.add_subplot()
        self.line, = self.ax.plot(self.t, self.y)
        self.ax.set_xlabel("time [s]")
        self.ax.set_ylabel("f(t)")

    def setupPlot3D(self):
        # https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html

        self.fig        = Figure(figsize=(10, 6), dpi=100)
        #self.fig.canvas.set_window_title('3D Scene')
        self.z_data     = np.arange(0, 10, 1)
        self.y_data     = np.sin(self.z_data)*2 
        self.x_data     = np.cos(self.z_data)*2 
        
#        self.ax         = self.fig.subplots() #
#        self.line       = self.ax.plot(self.x_data, self.y_data, self.z_data)
#        
#        self.ax         = self.fig.add_subplot()
#        self.line       = self.ax.plot(self.x_data, self.y_data, self.z_data)
        
        # matplotlib 3.5.3
        #self.ax         = self.fig.gca(projection='3d') #self.fig.add_subplot(111) # #self.fig.add_subplot(111)
        self.ax         = self.fig.add_subplot(projection='3d')
        self.line,      = self.ax.plot(self.x_data, self.y_data, self.z_data)
        self.ax.set_xlabel("X [mm]")
        self.ax.set_ylabel("Y [mm]")
        self.ax.set_zlabel("Z [mm]")
        #Axes3D.mouse_init(self.ax)
        #self.fig.tight_layout()
        self.ax.xaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        self.ax.yaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        self.ax.zaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        #self.ax.axis('equal')
        #self.ax.axis("off")
        #self.ax.view_init(elev=90, azim=0)
                
        # run multiple
        self.x_data = []
        self.y_data = []    
        self.z_data = []

    def runProgram(self):
        self.win.mainloop()

    # -- COMM ---
    def selectPort(self):
        global radioVar
        for child in self.masterframe.winfo_children():
            child.destroy()
        radioVar = tk.StringVar()

        lst = self.com.listSerialPorts()

        l1= tk.Label(self.masterframe, width = 5, height = 2, bg = "gray")
        l1.pack()

        if len(lst) > 0:
            for n in lst:
                r1 = tk.Radiobutton(self.masterframe, text=n, variable=radioVar, value=n, bg = "gray")
                r1.config(command = self.radioPress)
                r1.pack(anchor=W)
        else:
            l2 = tk.Label(self.masterframe, text = "No Serial Port Found")
            l2.pack()
            
    # ---------------------------------
    # -- Task --
    def acquireRealTime(self, k=0):
        # Update subplots 
        self.time_start = time.time()
        while self.btnAcquireStatus:
            #self.tprint('%s' %k)
            # Read temperature
            sens_val    = self.getSensorValues()
            time_now    = time.time() - self.time_start

            # # Add x and y to lists
            # self.x_data.append(time_now)
            # self.y_data.append(temperature)

            # # Limit x and y lists to the more recent items
            # size_limit = 30
            # self.x_data = self.x_data[-size_limit:]
            # self.y_data = self.y_data[-size_limit:]        

            # self.line.set_data(np.array(self.x_data), np.array(self.y_data))
            
            # update data
            y = sens_val/1000 * np.sin(2 * np.pi * 5 * (self.t + time_now))
            self.line.set_data(self.t, y)

            # required to update canvas and attached toolbar!
            self.canvas.draw()                         
            time.sleep(0.01)  
            
    # -- Control --            
    def btnAcquirePress(self):
        # when pressed starts or stops thread
        if self.btnAcquireStatus == False:
            self.btnAcquireStatus = True
            self.btnAcquire.config(bg="red", fg="white", text="Stop")
            
            self.ts = Thread(target=self.acquireRealTime)
            #self.ts.daemon = True
            self.ts.start()  
            self.tprint('Thread is running')   
            
        else:
            self.btnAcquireStatus = False
            self.btnAcquire.config(bg="gray", fg="black", text="Acquire")
            self.ts.join()
            self.tprint('Thread is stopped')             
       
    # ---------------------------------         
    # -- Accel 2D Show Config --
    def setupAccelDataView(self):
        # reconfigure the right pannel for data show
        #for child in self.right_frame.winfo_children():
        #    child.destroy()        
        
        #self.fig       = Figure(figsize=(5, 4), dpi=100)
        self.ax.clear()
        self.x_data    = np.arange(0, 3, .1)
        self.y_data    = np.zeros((len(self.x_data),3))
        #self.ax        = self.fig.add_subplot()
        self.ax.plot(self.x_data, self.y_data)
        self.ax.set_xlabel("time [s]")
        self.ax.set_ylabel("Accel(t)")
        self.ax.set_ylim(-1500, 1500)
        self.ax.legend(['X', 'Y', 'Z'])

        #self.canvas= FigureCanvasTkAgg(self.fig, master=self.right_frame)
        #self.canvas.get_tk_widget().grid(row=1,column=0) #,rowspan = 4, sticky="NSEW") #,columnspan = 4,rowspan = 4)
        #self.canvas.draw()
            
    # -- Task --            
    def acquireAccelRealTime(self, k=0):
        # Update subplots 
        self.time_start = time.time()
        while self.btnAcquireStatus:
            #self.tprint('%s' %k)
            # Read temperature
            sens_val    = self.getAccelValues()
            time_now    = time.time() - self.time_start

            # # Add x and y to lists
            # self.x_data.append(time_now)
            # self.y_data.append(sens_val[0:3]) # drop temperature
            #xdata       = self.line.get_xdata()
            

            # Limit x and y lists to the more recent items
            size_limit = 30
            # self.x_data = self.x_data[-size_limit:]
            # self.y_data = self.y_data[-size_limit:]  
            xdata       = self.ax.lines[0].get_xdata()
            xdata[0:-1] = xdata[1:]
            xdata[-1]   = time_now           
            
            for k in range(3):

                ydata       = self.ax.lines[k].get_ydata()
                ydata[0:-1] = ydata[1:]
                ydata[-1]   = np.array(sens_val[k])
                self.ax.lines[k].set_ydata(ydata)
                self.ax.lines[k].set_xdata(xdata)
                  
            # scale plot in x values
            self.ax.set_xlim([xdata[0],xdata[-1]])
            
            #self.line.set_data(np.array(self.x_data), np.array(self.y_data))
            #self.line.set_data(xdata, ydata)

            # required to update canvas and attached toolbar!
            self.canvas.draw()                         
            time.sleep(0.01)  
      
    # -- Control --      
    def btnAccelPress(self):
        # when pressed starts or stops thread
        global stopThread
        if self.btnAcquireStatus == False:
            self.setupAccelDataView()
            stopThread = False
            self.btnAcquireStatus = True
            self.btnAccel.config(bg="red", fg="white", text="Stop")
            
            self.ts = Thread(target=self.acquireAccelRealTime)
            #self.ts.daemon = True
            self.ts.start()  
            self.tprint('Thread is running')   
            
        else:
            self.btnAcquireStatus = False
            stopThread = True
            self.btnAccel.config(bg="gray", fg="black", text="Get Accel")
            #self.ts.join()
            self.tprint('Thread is stopped')  
            
    # ---------------------------------   
    # --  Accel 3D Show Configure -- 
    def setupEcgRawDataView(self):
        # reconfigure the right pannel for data show
        #for child in self.right_frame.winfo_children():
        #    child.destroy()        
        
        #self.fig       = Figure(figsize=(5, 4), dpi=100)
        self.ax.clear()
        self.x_data    = np.array([0,0])
        self.y_data    = np.array([0,0])
        self.z_data    = np.array([0,1])
        #self.ax        = self.fig.add_subplot()
        self.line,      = self.ax.plot(self.x_data, self.y_data,self.z_data)
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")
        self.ax.set_xlim(-1.2, 1.2)
        self.ax.set_ylim(-1.2, 1.2)
        self.ax.set_zlim(-1.2, 1.2)
        self.ax.legend(['Gravity'])

        #self.canvas= FigureCanvasTkAgg(self.fig, master=self.right_frame)
        #self.canvas.get_tk_widget().grid(row=1,column=0) #,rowspan = 4, sticky="NSEW") #,columnspan = 4,rowspan = 4)
        #self.canvas.draw()
                                 
    # -- Task --
    def acquireEcgRawRealTime(self, k=0):
        # Update subplots 
        self.time_start = time.time()
        while self.btnAcquireStatus:
            #self.tprint('%s' %k)
            # Read temperature
            sens_val    = self.getAccelValues()
            time_now    = time.time() - self.time_start
            
            sens_val    = np.array(sens_val)
            sens_val    = sens_val/np.linalg.norm(sens_val)

            # Limit x and y lists to the more recent items 
            xdata       = np.array([0,sens_val[0]])  
            ydata       = np.array([0,sens_val[1]])  
            zdata       = np.array([0,sens_val[2]])   
                  
            self.line.set_data(xdata, ydata)
            self.line.set_3d_properties(zdata)
            #self.line.set_data(np.array(self.x_data), np.array(self.y_data))
            #self.line.set_data(xdata, ydata)

            # required to update canvas and attached toolbar!
            self.canvas.draw()                         
            time.sleep(0.01) 
            
    # -- Control --
    def btnEcgRawPress(self):
        # when pressed starts or stops thread
        global stopThread
        if self.btnAcquireStatus == False:
            self.setupEcgRawDataView()
            self.btnAcquireStatus = True
            stopThread = False
            self.btnEcgRaw.config(bg="red", fg="white", text="Stop")
            
            self.ts = Thread(target=self.acquireEcgRawRealTime)
            #self.ts.daemon = True
            self.ts.start()  
            self.tprint('Thread is running')   
            
        else:
            self.btnAcquireStatus = False
            stopThread = True
            self.btnEcgRaw.config(bg="gray", fg="black", text="Get ECG")
            #self.ts.join()
            self.tprint('Thread is stopped')             

   # ---READ DATA FROM FILE ---------------------------------------
   # -- Setup  --
    def setupFileOffLine(self):
        # read csv file raw by raw
        import csv

        csv_path = r'C:\RobotAI\Customers\Levron\Data\2022-12-10\Event_20_2022_11_15_15_18_00.642.csv';
        try:
            csvfile = open(csv_path)
        except Exception as e:
            print(e)
            return
        self.reader = csv.DictReader(csvfile)
        # with open(csv_path, newline='') as csvfile:
        #     self.reader = csv.DictReader(csvfile)       
        
        self.ax.clear()
        self.x_data    = np.arange(0, 5, .01)
        self.y_data    = np.zeros((len(self.x_data),3))
        #self.ax        = self.fig.add_subplot()
        self.ax.plot(self.x_data, self.y_data)
        self.ax.set_xlabel("time [s]")
        self.ax.set_ylabel("f(t)")
        self.ax.set_ylim(-150, 250)
        self.ax.legend(['LV','Surface','PleuralPressure'])     

    # -- Task --
    def processFileOffLine(self, k=0):
        # Update subplots 
        global stopThread
        self.time_start = time.time()
        cnt = 0
        for row in self.reader:
            
            cnt = cnt + 1
            
            # decimate
            if np.mod(cnt,10) != 0:
                continue
            
            #time_s = time.time()
            # user stop
            if stopThread: #not self.btnAcquireStatus:
                self.tprint('Stop is detected')
                break
            
            # Read time and values
            time_now = float(row['Time'].split()[0])
            lv_value = float(row['LV'])
            surf_value = float(row['Surface'])
            press_value = float(row['PleuralPressure'])
            
            #self.tprint('Time decode %f' %(time.time()-time_s))

            # Limit x and y lists to the more recent items
            #size_limit = 300
            # self.x_data = self.x_data[-size_limit:]
            # self.y_data = self.y_data[-size_limit:]  
            xdata       = self.ax.lines[0].get_xdata()
            xdata[0:-1] = xdata[1:]
            xdata[-1]   = time_now           

            sens_val   = [lv_value,surf_value, press_value]
            for k in range(3):

                ydata       = self.ax.lines[k].get_ydata()
                ydata[0:-1] = ydata[1:]
                ydata[-1]   = np.array(sens_val[k])
                self.ax.lines[k].set_ydata(ydata)
                self.ax.lines[k].set_xdata(xdata)

           # scale plot in x values
            self.ax.set_xlim([xdata[0],xdata[-1]])
            
            #self.tprint('Time set lines %f' %(time.time()-time_s))
            
            # required to update canvas and attached toolbar!
            self.canvas.draw()                         
            #time.sleep(0.01) 
            #self.tprint('Total cycle %f' %(time.time()-time_s))

    # -- Control --        
    def btnFileOffLinePress(self):
        # when pressed starts or stops thread
        global stopThread
        if self.btnAcquireStatus == False:
            self.setupFileOffLine()
            self.btnAcquireStatus = True
            stopThread = False
            self.btnFileOffLine.config(bg="red", fg="white", text="Stop")
            
            self.ts = Thread(target=self.processFileOffLine)
            #self.ts.daemon = True
            self.ts.start()  
            self.tprint('Thread is running')   
            
        else:
            self.btnAcquireStatus = False
            stopThread = True
            self.btnFileOffLine.config(bg="white", fg="black", text="Process File")
            #self.tprint('Thread is sopping')
            #self.ts.join()
            self.tprint('Thread is stopped')                         

   # ---READ DATA FROM FILE AND PROCESS in ARDUINO----------
   # -- Setup --
    def setupFileOnLine(self):
        # read csv file raw by raw
        import csv

        csv_path = r'C:\RobotAI\Customers\Levron\Data\2022-12-10\Event_20_2022_11_15_15_18_00.642.csv';
        try:
            csvfile = open(csv_path)
        except Exception as e:
            print(e)
            return
        self.reader = csv.DictReader(csvfile)
        # with open(csv_path, newline='') as csvfile:
        #     self.reader = csv.DictReader(csvfile)       
        
        self.ax.clear()
        self.x_data    = np.arange(0, 5, .01)
        self.y_data    = np.zeros((len(self.x_data),4))
        #self.ax        = self.fig.add_subplot()
        self.ax.plot(self.x_data, self.y_data)
        self.ax.set_xlabel("time [s]")
        self.ax.set_ylabel("f(t)")
        self.ax.set_ylim(-50, 50)
        self.ax.legend(['LV','Surface','PleuralPressure','Algo'])     

    # -- Task --
    def processFileOnLine(self, k=0):
        # Update subplots 
        global stopThread
        self.time_start = time.time()
        cnt = 0
        for row in self.reader:
            
            if stopThread: #not self.btnAcquireStatus:
                self.tprint('Stop is detected')
                break            

            # decimate
            cnt = cnt + 1
            if np.mod(cnt,10) != 0:
                continue
            
            # Read time and values
            time_now = float(row['Time'].split()[0])
            lv_value = float(row['LV'])
            surf_value = float(row['Surface'])
            press_value = float(row['PleuralPressure'])
            
            # send receive
            alg_value = self.setFileData(valLV = lv_value, valSurf = surf_value, valPress = press_value)
            
            #self.tprint('Time decode %f' %(time.time()-time_s))

            # Limit x and y lists to the more recent items
            #size_limit = 300
            # self.x_data = self.x_data[-size_limit:]
            # self.y_data = self.y_data[-size_limit:]  
            xdata       = self.ax.lines[0].get_xdata()
            xdata[0:-1] = xdata[1:]
            xdata[-1]   = time_now           

            sens_val   = [lv_value,surf_value, press_value, alg_value]
            for k in range(4):

                ydata       = self.ax.lines[k].get_ydata()
                ydata[0:-1] = ydata[1:]
                ydata[-1]   = np.array(sens_val[k])
                self.ax.lines[k].set_ydata(ydata)
                self.ax.lines[k].set_xdata(xdata)

           # scale plot in x values
            self.ax.set_xlim([xdata[0],xdata[-1]])
            
            #self.tprint('Time set lines %f' %(time.time()-time_s))
            
            # required to update canvas and attached toolbar!
            self.canvas.draw()                         
            #time.sleep(0.01) 
            #self.tprint('Total cycle %f' %(time.time()-time_s))

    # -- Control --        
    def btnFileOnLinePress(self):
        # when pressed starts or stops thread
        global stopThread
        if self.btnAcquireStatus == False:
            self.setupFileOnLine()
            #self.btnAcquireStatus = True
            stopThread = False
            self.btnFileOnLine.config(bg="red", fg="white", text="Stop")
            
            self.ts = Thread(target=self.processFileOnLine)
            #self.ts.daemon = True
            self.ts.start()  
            self.tprint('Thread is running')   
            
        else:
            self.btnAcquireStatus = False
            stopThread = True
            self.btnFileOnLine.config(bg="white", fg="black", text="File on Board")
            #self.tprint('Thread is sopping')
            #self.ts.join()
            self.tprint('Thread is stopped')                         

            
    # ------------------------------------------

    def btnA(self):
        global ledAstatus, ledBstatus, servoPos

        if ledAstatus == 0:
            ledAstatus = 1
            self.ledAbutton.config(bg="white", fg="black")
        else:
            ledAstatus = 0
            self.ledAbutton.config(fg="white", bg="black")

        self.com.valToArduino(ledAstatus, ledBstatus, servoPos)

    def btnB(self):
        global ledAstatus, ledBstatus, servoPos

        if ledBstatus == 0:
            ledBstatus = 1
            self.ledBbutton.config(bg="white", fg="black")
        else:
            ledBstatus = 0
            self.ledBbutton.config(fg="white", bg="black")
        #self.com.valToArduino(ledAstatus, ledBstatus, servoPos)

        msgSend   = Message(1,MESSAGE_TYPE['ARRAY'],1,[ledAstatus, ledBstatus, servoPos])
        msgRecv   = Message(2,MESSAGE_TYPE['ARRAY'],1,[0, 0, 0])
        self.com.msgSendRecv(msgSend,msgRecv)
        
    def slide(self,sval):
        global ledAstatus, ledBstatus, servoPos

        servoPos = int(sval)
        #self.com.valToArduino(ledAstatus, ledBstatus, servoPos)

        msgSend   = Message(1,MESSAGE_TYPE['ARRAY'],1,[ledAstatus, ledBstatus, servoPos])
        msgRecv   = Message(2,MESSAGE_TYPE['ARRAY'],1,[0, 0, 0])
        self.com.msgSendRecv(msgSend,msgRecv)

    def radioPress(self):
        global radioVar
        self.com.setupSerial(radioVar.get())
        #self.mainScreen()
        self.graphicsScreen()
        
   # ---COMM IF----------
    def listPorts(self):
        # list ports
        res = self.com.listSerialPorts()
        #self.mainScreen()
        #self.graphicsScreen()
        if len(res) > 0:
            self.autoSelect(res[0])

    def commConnect(self):
        # Check if the connection exists
        ret = self.autoSelect(COMM_PORT)
        #ret = self.com.setupSerial()
        
        if ret: #self.checkAlive():
            self.tprint('Board connection is found ...')
            return
        else:
            self.tprint('Board software is not running or BLE problem ...','E')
            return
            
        #self.graphicsScreen()
        self.tprint('Waiting to PIC board connection ...')
        isOk = self.com.waitForPicBoard()
        if isOk:
            self.tprint('Connected')
        else: 
            self.tprint('PIC Board connection problem. Try reset.','W')
        
    def autoSelect(self,pname = 'COM5'):
        #global radioVar
        
        try:
            self.com.setupSerial(pname)
            ret = True
        except :
            self.tprint('Did you connect the Arduino board?')
            ret = False
        #self.mainScreen()

        return ret
        
    def commClose(self):
        # close port
        self.com.closeSerial()
        
    def mainQuit(self):
		# correct way to close
        self.win.quit()     # stops mainloop
        self.win.destroy()  # this is necessary on Windows to prevent
                            # Fatal Python Error: PyEval_RestoreThread: NULL tstate

    def finish(self):
        self.com.closeSerial()
        self.tprint('Done')
        self.mainQuit()
        #self.win.destroy()
        #self.win.quit()

    def tprint(self, txt='',level='I', showInCmdLine = True):
        try:
            self.e.delete(0,tk.END)
        except:
            print('Main window is destroyed')
            return

        if level == 'I':
            ptxt = 'I: GUI: %s' % txt
            bckg = "White"
        if level == 'W':
            ptxt = 'W: GUI: %s' % txt
            bckg = "Yellow"
        if level == 'E':
            ptxt = 'E: GUI: %s' % txt
            bckg = "Red"
            
        print(ptxt)    

        if showInCmdLine:
            self.e.insert(0,txt)
            self.e.config({"background": bckg})




#%% Main Code


def AppGUI(version = '0000', module_dict = {}):
    #%
    # #__version__ = version
    # logging.basicConfig(handlers=[RotatingFileHandler('./robotai.log', maxBytes=50000000, backupCount=10)],
    #                     level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    # # log a message
    # logging.info('====== Starting up the program %s =======' % version)
    # do not show the logging on the console
    #logging.propagate = False

    # # key board short cuts
    # def keyPressedCallback(event):
    #     #win.focus_set()
    #     # The obvious information
    #     c = event.keysym
    #     s = event.state
    #     shift = (s & 0x1) != 0
    #     # protect
    #     if not shift:
    #         return
    #     if event.char == 'a':
    #         app.CameraImageSave()
    #     if event.char == 'r':
    #         app.RobotCameraImageSave()
    #     if event.char == 'q':
    #         app.stop = True
    #     #print("pressed", repr(event.char))




    # cfg         = module_dict['cfg']
    # prj         = module_dict['prj'] # load session
    # cam         = module_dict['cam']
    # obj         = module_dict['obj']
    # rob         = module_dict['rob']
    # lbl         = module_dict['lbl']


#    prj    = ProjectManager(config = cfg) # load session
#    cam    = CameraManager(config = cfg)
#    obj    = ObjectManager(config = cfg)
#    rob    = RobotManager(config = cfg)
#    lbl    = LabelManager(config = cfg)




    #app         = RobotAIGUI(version, win, cam, prj, obj, rob, lbl) # object instantiated
    # check if requested
    #app.AutoStart()


    #win.mainloop()
    #app.Finish()


    win = tk.Tk()
    #win.iconbitmap(iconFilePath)


    gui = MonitorGUI(win)
    gui.setupView()
    #win.bind("<Key>", gui.KeyPressedCallback)
    #atexit.register(gui.finish())
    win.mainloop()
    #gui.finish()
    #logging.shutdown()
# --------------------------
if __name__ == '__main__':
    AppGUI()
