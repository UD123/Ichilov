# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 12:51:44 2022

@author: avita

Levron : Runtime API
Usage :


Install:
	Avita -> env :  C:\RobotAI\Customers\Levron\Code\Envs\Levron

-----------------------------
 Ver    Date     Who    Descr
-----------------------------
0101   22.11.22 UD     created
-----------------------------

"""
# -*- coding: utf-8 -*-
import os
#import tkinter as tk
#import threading
#import json
import random
import time   # just to measure switch time
#import logging

base_path     = os.path.abspath(".")
iconFilePath  = os.path.join(base_path, './logo.ico')



#%%

#from ArduinoComms import *
#from ArduinoObjectComms import MonitorComm
from MonitorComm import MonitorComm
from MonitorMessage import Message, MESSAGE_TYPE
#import atexit

# def exit_handler():
#     print('My application is ending!')
#     closeSerial()
# atexit.register(exit_handler)

# global variables for this module
ledAstatus = 0
ledBstatus = 0
servoPos = 10

import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg , NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.backend_bases import key_press_handler
from matplotlib.animation import FuncAnimation

from threading import Thread

import tkinter as tk
from tkinter import ttk
#import tkinter as tk
#import tkinter.ttk as ttk
#import sys
#import time

style.use("dark_background") # dark_background ggplot

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
        msgRecv = self.new_method()
        msgRecv   = self.com.msgSendRecv(msgSend,msgRecv)
        self.tprint('Board version : %04d' %(msgRecv.Data[0]))

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

    def setupMenu(self):
        # add menu
        menu = tk.Menu(self.win)
        self.win.config(menu=menu)

        # Board
        boardmenu = tk.Menu(menu,tearoff = 0 )
        menu.add_cascade(label='Board',  menu=boardmenu)
        boardmenu.add_command(label='Connect...',               command=lambda:self.radioPress)
        boardmenu.add_command(label='Board Info...',            command= self.getVersion)

        # Sensor
        sensoramenu = tk.Menu(menu,tearoff = 0 )
        menu.add_cascade(label='Sensors',  menu=sensoramenu)
        sensoramenu.add_command(label='Select from List',        command=lambda:self.CameraList())

        # Tests
        sensoramenu = tk.Menu(menu,tearoff = 0 )
        menu.add_cascade(label='Tests',  menu=sensoramenu)
        sensoramenu.add_command(label='Set PWN values',           command=self.setPwmValues)
        sensoramenu.add_separator()
        sensoramenu.add_command(label='Get sensor values',        command=self.getSensorValues)

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
        self.win.title("Levron GUI Demo")
        #self.win.iconbitmap(iconFilePath)

        self.masterframe = tk.Frame(bg = "gray")
        self.masterframe.pack(side='top',fill='both',expand=True)
        self.masterframe.grid_columnconfigure(0, weight=1)
        self.masterframe.grid_rowconfigure(0, weight=1)
        
        # add menu
        self.setupMenu()

        # select port screen
        #self.selectPort()
        #self.autoSelect()
        #self.graphicsScreen()
        #self.createWidgets()
        #self.animatePlotView()
        #self.simplePlotView()
        self.examplePlotView()
        
    def updateFrequency(self, new_val):
        # retrieve frequency
        f = float(new_val)

        # update data
        y = 2 * np.sin(2 * np.pi * f * self.t)
        self.line.set_data(self.t, y)

        # required to update canvas and attached toolbar!
        self.canvas.draw() 
        
    def updateRealTime(self, k=0):
        # Update subplots 
        
        for k in range(100):
            self.tprint('%s' %k)
            # Read temperature
            temperature = random.uniform(1, 10)
            time_now    = k/100 #time.time()

            # # Add x and y to lists
            # self.x_data.append(time_now)
            # self.y_data.append(temperature)

            # # Limit x and y lists to the more recent items
            # size_limit = 30
            # self.x_data = self.x_data[-size_limit:]
            # self.y_data = self.y_data[-size_limit:]        

            # self.line.set_data(np.array(self.x_data), np.array(self.y_data))
            
            # update data
            y = 2 * np.sin(2 * np.pi * 3 * (self.t + time_now))
            self.line.set_data(self.t, y)

            # required to update canvas and attached toolbar!
            self.canvas.draw()                         
            time.sleep(0.1)
        
    def examplePlotView(self):
        # https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html
        
        self.win.wm_title("Embedding in Tk")
        
        fig  = Figure(figsize=(5, 4), dpi=100)
        t    = np.arange(0, 3, .01)
        ax   = fig.add_subplot()
        self.line, = ax.plot(t, 2 * np.sin(2 * np.pi * t))
        self.t = t
        ax.set_xlabel("time [s]")
        ax.set_ylabel("f(t)")
        
        # Create left and right frames
        left_frame  =  tk.Frame(self.masterframe,  width=100,  height=400,  bg='black')
        left_frame.pack(side='left',  fill='both',  padx=10,  pady=5,  expand=True)

        right_frame  =  tk.Frame(self.masterframe,  width=600,  height=400,  bg='black')
        right_frame.pack(side='right',  fill='both',  padx=10,  pady=5,  expand=True)        
        
        self.canvas= FigureCanvasTkAgg(fig, master=right_frame)
        #self.canvas.get_tk_widget().grid(row=1,column=0) #,rowspan = 4, sticky="NSEW") #,columnspan = 4,rowspan = 4)
        self.canvas.draw()
        
        # pack_toolbar=False will make it easier to use a layout manager later on.
        # toolbar = NavigationToolbar2Tk(self.canvas, self.masterframe, pack_toolbar=False)
        # toolbar.update()

        self.canvas.mpl_connect("key_press_event", lambda event: print(f"you pressed {event.key}"))
        self.canvas.mpl_connect("key_press_event", key_press_handler)

        button_quit = tk.Button(master=left_frame, text="Quit", command=self.win.destroy, relief=tk.RAISED)
        slider_update = tk.Scale(left_frame, from_=1, to=5, orient=tk.HORIZONTAL,
                                    command=self.updateFrequency, label="Freq [Hz]")
        self.e  = tk.Entry(master=right_frame)
        # Packing order is important. Widgets are processed sequentially and if there
        # is no space left, because the window is too small, they are not displayed.
        # The canvas is rather flexible in its size, so we pack it last which makes
        # sure the UI controls are displayed as long as possible.
        
        ipadding = {'ipadx': 10, 'ipady': 10}
        #toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        slider_update.pack(**ipadding, side=tk.TOP, fill=tk.BOTH)
        button_quit.pack(**ipadding, side=tk.BOTTOM, fill=tk.BOTH)
        
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)  
        
        self.e.pack(**ipadding, side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.e.delete(0,tk.END)
        self.e.insert(0,'Parameters and Messages')
        
        
        # run multiple
        self.x_data = []
        self.y_data = []
        # for k in range(100):
        #     self.updateRealTime()   
        #     time.sleep(0.1) 
            
        self.ts = Thread(target=self.updateRealTime)
        self.ts.daemon = True
        self.ts.start()  

        self.tprint('Thread is running')
      
        
    def animate(self, frame, xs, ys):
        # runs to extract data
        """Function called periodically by the Matplotlib as an animation.

        It reads a new temperature value, add its to the data series and update the plot.

        :param frame: not used
        :param xs: x data
        :param ys: y data
        """

        # Read temperature
        temperature = random.uniform(10, 30)
        time_now    = time.time()

        # Add x and y to lists
        xs.append(time_now)
        ys.append(temperature)

        # Limit x and y lists to the more recent items
        size_limit = 30
        xs = xs[-size_limit:]
        ys = ys[-size_limit:]

        # Draw x and y lists
        self.ax.clear()
        self.ax.plot(xs, ys)

        # (Re)Format plot
        
        #plt.xticks(rotation=45, ha='right')
        plt.subplots_adjust(bottom=0.30)
        # plt.grid()
        # plt.title('Temperature over time')
        # plt.ylabel('Temperature (°C)')
        # plt.xlabel('Time')        
        
        #self.ax.clear()
        
    def animatePlotView(self):
        # draw a graph
        
        fig  = plt.figure(figsize=(3,3))
        #t = np.arange(0, 3, .01)
        #fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))
        
       
		
        self.ax    = fig.add_subplot(1, 1, 1) #fig.add_axes([0.1,0.1,0.8,0.8],polar=False)
        self.ax.plot([0,1], [0,0])
        plt.title('Temperature over time')
        plt.ylabel('Temperature (°C)')
        plt.xlabel('Time')
        plt.grid()
        
        self.canvas= FigureCanvasTkAgg(fig, master=self.masterframe)
        self.canvas.get_tk_widget().grid(row=1,column=0) #,rowspan = 4, sticky="NSEW") #,columnspan = 4,rowspan = 4)
        self.canvas.draw()
        
          

        self.plotbutton=tk.Button(master=self.masterframe, text="plot", command= self.plot) #lambda: self.plot(canvas,ax))
        self.plotbutton.grid(row=2,column=0)
        label       = tk.Label(self.masterframe, text="Realtime Animated Graphs").grid(column=0, row=0)

        # Create empty data series
        x_data = []
        y_data = []

        # Set up plot to call animate() function periodically
        ani = FuncAnimation(fig, self.animate, fargs=(x_data, y_data), interval=200)
        # NOTE: it is mandatory keep a reference to the animation otherwise it is stopped
        # See: https://matplotlib.org/api/animation_api.html

        # Show
        plt.show()   
        
    def createRealTimeView(self):
        # init for the update

        self.fig  = plt.figure(figsize=(3,3))
        self.ax    = self.fig.add_subplot(1, 1, 1) #fig.add_axes([0.1,0.1,0.8,0.8],polar=False)
        self.gr    = self.ax.plot([0,1], [0,0])[0]
        
        plt.ion()
        plt.title('Temperature over time')
        plt.ylabel('Temperature (°C)')
        plt.xlabel('Time')
        plt.grid()
        plt.show()
        
        self.x_data = []
        self.y_data = []
        
        self.canvas= FigureCanvasTkAgg(self.fig, master=self.masterframe)
        self.canvas.get_tk_widget().grid(row=1,column=0) #,rowspan = 4, sticky="NSEW") #,columnspan = 4,rowspan = 4)
        self.canvas.draw()

    def updateRealTimeView(self):
        # Update subplots 
        
        # Read temperature
        temperature = random.uniform(10, 30)
        time_now    = time.time()

        # Add x and y to lists
        self.x_data.append(time_now)
        self.y_data.append(temperature)

        # Limit x and y lists to the more recent items
        size_limit = 30
        self.x_data = self.x_data[-size_limit:]
        self.y_data = self.y_data[-size_limit:]        

        self.gr.set_xdata(self.x_data)
        self.gr.set_ydata(self.y_data)

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        time.sleep(0.01)

        # Display
        plt.show()

    def simplePlotView(self):
        # draw a graph without animation
        self.createRealTimeView()
        for k in range(100):
            self.updateRealTimeView()
        
        
    def graphView(self):
        # initial view

        self.win.minsize(width=520, height=370)
        self.win.config(bg = 'gray')
        self.win.title("Levron GUI Demo")

        self.masterframe = tk.Frame(bg = "gray")
        self.masterframe.pack()

        # add menu
        self.setupMenu()

        # select port screen
        #self.selectPort()
        self.autoSelect()
        #self.graphicsScreen()
        #self.createWidgets()        

    def runProgram(self):
        self.win.mainloop()

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


    def mainScreen(self):
        #global masterframe
        for child in self.masterframe.winfo_children():
            child.destroy()

        labelA = Label(self.masterframe, width = 5, height = 2, bg = "gray")
        labelB = Label(self.masterframe, width = 5, bg = "gray")
        labelC = Label(self.masterframe, width = 5, bg = "gray")

        self.ledAbutton = Button(self.masterframe, text="LedA", fg="white", bg="black")
        self.ledAbutton.config(command = self.btnA)

        self.ledBbutton = Button(self.masterframe, text="LedB", fg="white", bg="black")
        #self.ledBbutton.config(command = lambda:  self.btnB)
        self.ledBbutton.config(command = self.btnB)

        slider = Scale(self.masterframe, from_=10, to=170, orient=HORIZONTAL)
        slider.config(command = self.slide)
		
        button = Button(master=self.win, text="Quit", command=self.mainQuit)
        button.pack(side=tk.BOTTOM)		

        labelA.grid(row = 0)
        self.ledAbutton.grid(row = 1)
        labelB.grid(row = 1, column = 2)
        self.ledBbutton.grid(row = 1, column = 3)
        labelC.grid(row = 2)
        slider.grid(row = 3, columnspan = 4)
		
    def mainQuit(self):
		# correct way to close
        self.win.quit()     # stops mainloop
        self.win.destroy()  # this is necessary on Windows to prevent
                            # Fatal Python Error: PyEval_RestoreThread: NULL tstate


    def graphicsScreen(self):
        #global masterframe
        for child in self.masterframe.winfo_children():
            child.destroy()
            
        self.masterframe.columnconfigure(0, weight=1)
        self.masterframe.columnconfigure(1, weight=5)
        self.masterframe.columnconfigure(2, weight=1)
        self.masterframe.rowconfigure(0, weight=1)
        #self.masterframe.grid_columnconfigure(0, weight=1)

        #win = self.win
        self.t = tk.Label(self.masterframe, width=35, anchor=tk.W, justify=tk.LEFT,  bg = "gray")
        self.t.configure(text = 'Parameters and Messages:')
        self.e = tk.Entry(self.masterframe, width=35)
        self.e.delete(0,tk.END)
        self.e.insert(0,'Parameters and Messages')


        # from tkinter import scrolledtext
        # scrltxt = scrolledtext.ScrolledText(self.masterframe,width=40,height=4)
        # scrltxt.insert(INSERT,'You text goes here')

        labelA = Label(self.masterframe, width = 5, bg = "gray",text = 'A')
        labelB = Label(self.masterframe, width = 5, bg = "gray",text = 'A')
        labelC = Label(self.masterframe, width = 5, bg = "gray",text = 'Set')

        self.ledAbutton = Button(self.masterframe, text="LedA", fg="white", bg="black")
        self.ledAbutton.config(command = self.btnA)

        self.ledBbutton = Button(self.masterframe, text="LedB", fg="white", bg="black")
        self.ledBbutton.config(command = self.btnB)

        slider = Scale(self.masterframe, from_=10, to=170, orient=HORIZONTAL)
        slider.config(command = self.slide)

        labelA.grid(row = 0, column = 2)
        self.ledAbutton.grid(row = 1, column = 2,sticky="NSEW")
        labelB.grid(row = 2, column = 2)
        self.ledBbutton.grid(row = 3, column = 2, sticky="NSEW")
        labelC.grid(row = 4, column = 2)
        slider.grid(row = 5, column = 2, sticky="NSEW") #, columnspan = 4)
        self.t.grid(row=4,column=1, sticky="NSEW") #,padx=8,pady=4)
        self.e.grid(row=5,column=1, sticky="NSEW") #,padx=8,pady=0,sticky=tk.EW)
        #scrltxt.grid(row=7,columnspan = 4, rowspan = 3)


        #tk.Frame.__init__(self,master)
        self.createWidgets()

    def createWidgets(self):
        fig = plt.figure(figsize=(3,3))
        #t = np.arange(0, 3, .01)
        #fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))
		
        self.ax=fig.add_axes([0.1,0.1,0.8,0.8],polar=False)
        self.canvas=FigureCanvasTkAgg(fig, master=self.masterframe)
        self.canvas.get_tk_widget().grid(row=0,column=1,rowspan = 4, sticky="NSEW") #,columnspan = 4,rowspan = 4)
        self.canvas.draw()

        self.plotbutton=tk.Button(master=self.masterframe, text="plot", command= self.plot) #lambda: self.plot(canvas,ax))
        self.plotbutton.grid(row=6,column=2)

#         data = {
# 			   'Python': 11.27,
# 			      'C': 11.16,
# 				     'Java': 10.46,
# 					    'C++': 7.5,
# 						   'C#': 5.26
# 						   }
#         languages = data.keys()
#         popularity = data.values()
#         figure_canvas = FigureCanvasTkAgg(fig, master=self.masterframe)
#         axes = fig.add_subplot()
#         axes.bar(languages, popularity)
#         axes.set_title('Top 5 Programming Languages')
#         axes.set_ylabel('Popularity')
#         figure_canvas.get_tk_widget().pack(side=self.masterframe, fill=tk.BOTH, expand=1)

        # from tkinter import scrolledtext  
        # win = tk.Tk()  
        # win.title("scroll text")  
        # ttk.Label(win, text="This is Scrolled Text Area").grid(column=0,row=0)  
        # scrolW=30  
        # scrolH=2  
        # scr=scrolledtext.ScrolledText(win, width=scrolW, height=scrolH, wrap=tk.WORD)  
        # scr.grid(column=0, columnspan=3)  

    def plot(self):
        for n in range(5): #infinite loop, reads data of a subprocess
            theta= np.linspace(0,2*np.pi,200)
            r    = np.random.rand(200,1)
            self.ax.plot(theta,r,linestyle="None",marker='o')
            self.canvas.draw()
            self.ax.clear()
            #delay(1)
            time.sleep(0.1)
            #here set axe



 
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
        
    def autoSelect(self,pname = 'COM5'):
        #global radioVar
        self.com.setupSerial(pname)
        #self.mainScreen()
        self.graphicsScreen()        

    def finish(self):
        self.com.closeSerial()
        self.tprint('Done')
        self.mainQuit()
        #self.win.destroy()
        #self.win.quit()

    def tprint(self, txt='',level='I'):

        #self.e.insert(0,txt)
        if level == 'I':
            ptxt = 'I: GUI: %s' % txt
        if level == 'W':
            ptxt = 'W: GUI: %s' % txt
        if level == 'E':
            ptxt = 'E: GUI: %s' % txt

        #self.e.config({"background": bckg})
        print(ptxt)






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
