import matplotlib.pyplot as plt
import numpy as np
import random

def main():
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    x = [0]
    y = [0]
    z = [0]
    while True:
        ax.plot(xs = x, ys = y, zs = z, marker='o')
        # x = random.randint(0, 10)
        plt.pause(0.01)
        y[0] += 0.1
        ax.cla()

if __name__ == '__main__':
    main()