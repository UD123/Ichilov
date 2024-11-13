import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk

# Replace with your webcam streaming URL
url = 'http://192.168.1.60:4747/video'

def capture_video():
    ret, frame = cap.read()
    if ret:
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)
        lmain.after(10, capture_video)

# Create a window
window = tk.Tk()
window.title("Webcam Stream")

# Create a label to display video frames
lmain = ttk.Label(window)
lmain.grid(row=0, column=0, padx=10, pady=10)

# Initialize video capture
cap = cv2.VideoCapture(url)
capture_video()

# Run the tkinter event loop
window.mainloop()