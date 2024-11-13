import datetime
import random

import matplotlib.animation as animation
import matplotlib.pyplot as plt


def read_temperature():
    """Read temperature (stub here of course)

    :return: the temperature
    """
    return random.uniform(10, 30)


def animate(frame, xs, ys):
    """Function called periodically by the Matplotlib as an animation.

    It reads a new temperature value, add its to the data series and update the plot.

    :param frame: not used
    :param xs: x data
    :param ys: y data
    """

    # Read temperature
    temperature = read_temperature()

    # Add x and y to lists
    xs.append(datetime.datetime.now().strftime('%H:%M:%S %f'))
    ys.append(temperature)

    # Limit x and y lists to the more recent items
    size_limit = 30
    xs = xs[-size_limit:]
    ys = ys[-size_limit:]

    # Draw x and y lists
    ax.clear()
    ax.plot(xs, ys)

    # (Re)Format plot
    plt.grid()
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)

    plt.title('Temperature over time')
    plt.ylabel('Temperature (°C)')
    plt.xlabel('Time')


if __name__ == '__main__':
    # Create figure
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    # Create empty data series
    x_data = []
    y_data = []

    # Set up plot to call animate() function periodically
    ani = animation.FuncAnimation(fig, animate, fargs=(x_data, y_data), interval=200)
    # NOTE: it is mandatory keep a reference to the animation otherwise it is stopped
    # See: https://matplotlib.org/api/animation_api.html

    # Show
    plt.show()