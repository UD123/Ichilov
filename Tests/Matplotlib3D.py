""" 
from math import pi, cos, sin
import numpy as np
import matplotlib.colors as mcolors
from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

x_ = np.linspace(0, 314, 50)
y_ = np.linspace(0, 314, 50)
X, Y = np.meshgrid(x_, y_)

t_ = np.linspace(0, 2*pi, 90)

def f(x, y):
  return np.sin(x/50) * np.cos(y/50) * 50 + 50

def g(x, y, t):
  return f(x*cos(t) - y*sin(t), x*sin(t) + y*cos(t))

fig = plt.figure()
ax = fig.add_subplot(projection = "3d")

def animate(n):
    ax.cla()
    Z = g(X, Y, t_[n])
    colorfunction = (X**2+Y**2+Z**2)
    norm = mcolors.Normalize(colorfunction.min(), colorfunction.max())
    ax.plot_surface(
      X, Y, Z, rstride = 1, cstride = 1, facecolors=cm.jet(norm(colorfunction))
    )
    ax.set_zlim(0, 100)
    return fig


anim = FuncAnimation(
  fig = fig, func = animate, frames = len(t_), interval = 1, repeat = False
)
#anim.save("Anim.mp4", fps = 10)
plt.show()

"""
import tkinter

import numpy as np

# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure

root = tkinter.Tk()
root.wm_title("Embedding in Tk")

# 2D
fig   = Figure(figsize=(5, 4), dpi=100)
# t     = np.arange(0, 3, .01)
# ax    = fig.add_subplot()
# line, = ax.plot(t, 2 * np.sin(2 * np.pi * t))
# ax.set_xlabel("time [s]")
# ax.set_ylabel("f(t)")

# 3D Make data
ax = fig.add_subplot(projection='3d')
u = np.linspace(0, 2 * np.pi, 100)
v = np.linspace(0, np.pi, 100)
x = 10 * np.outer(np.cos(u), np.sin(v))
y = 10 * np.outer(np.sin(u), np.sin(v))
z = 10 * np.outer(np.ones(np.size(u)), np.cos(v))
# Plot the surface
s = ax.plot_surface(x, y, z)
# Set an equal aspect ratio
ax.set_aspect('equal')

canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.draw()

# pack_toolbar=False will make it easier to use a layout manager later on.
toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
toolbar.update()

canvas.mpl_connect("key_press_event", lambda event: print(f"you pressed {event.key}"))
canvas.mpl_connect("key_press_event", key_press_handler)

button_quit = tkinter.Button(master=root, text="Quit", command=root.destroy)


def update_frequency(new_val):
    # retrieve frequency
    f = float(new_val)

    # update data
    y = 2 * np.sin(2 * np.pi * f * t)
    line.set_data(t, y)

    # required to update canvas and attached toolbar!
    canvas.draw()

#slider_update = tkinter.Scale(root, from_=1, to=5, orient=tkinter.HORIZONTAL,   command=update_frequency, label="Frequency [Hz]")

def update_ball(new_val):
    # retrieve frequency
    f = float(new_val)
    x = f * np.outer(np.cos(u), np.sin(v))
    y = f * np.outer(np.sin(u), np.sin(v))
    z = f * np.outer(np.ones(np.size(u)), np.cos(v))

    # update data
    # s.set_xdata(x)
    # s.set_ydata(y)
    # s.set_3d_properties(z)
    # s.auto_scale_xyz(x,y,z)
    s = ax.plot_surface(x, y, z)
    
    fig.canvas.flush_events()

    # required to update canvas and attached toolbar!
    canvas.draw()

slider_update = tkinter.Scale(root, from_=1, to=5, orient=tkinter.HORIZONTAL,   command=update_ball, label="Frequency [Hz]")

# Packing order is important. Widgets are processed sequentially and if there
# is no space left, because the window is too small, they are not displayed.
# The canvas is rather flexible in its size, so we pack it last which makes
# sure the UI controls are displayed as long as possible.
button_quit.pack(side=tkinter.BOTTOM)
slider_update.pack(side=tkinter.BOTTOM)
toolbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

tkinter.mainloop()

import matplotlib.pyplot as plt
import numpy as np

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

# Make data
u = np.linspace(0, 2 * np.pi, 100)
v = np.linspace(0, np.pi, 100)
x = 10 * np.outer(np.cos(u), np.sin(v))
y = 10 * np.outer(np.sin(u), np.sin(v))
z = 10 * np.outer(np.ones(np.size(u)), np.cos(v))

# Plot the surface
ax.plot_surface(x, y, z)

# Set an equal aspect ratio
ax.set_aspect('equal')

plt.show()