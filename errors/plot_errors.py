import csv
import numpy as np
import matplotlib.pyplot as plt

def main():
    distances = []
    errors = []
    with open('errors.csv') as errors_file:
        reader = csv.reader(errors_file, delimiter=' ')
        next(reader)
        for row in reader:
            errors.append(float(row[1]))
            distances.append((float(row[0])))

    errors = np.array(errors)
    distances = np.array(distances)
    sorted_indeces = np.argsort(distances)
    distances = distances[sorted_indeces]
    errors = errors[sorted_indeces]

    min_error = 0
    max_error = 40

    fig = plt.figure()
    fig.set_figheight(8)
    fig.set_figwidth(12)
    ax = fig.gca()

    ax.set_xticks(np.arange(distances[0], distances[-1], 5))
    ax.set_yticks(np.arange(min_error, max_error, 5))
    # ax.set_xlim(distances[0]-10, distances[-1])
    ax.set_ylim(min_error, max_error)

    plt.xlabel('Расстояние, мм')
    plt.ylabel('СКО, мм')

    plt.plot(distances, errors, '-o')
    fig.show()
    plt.grid()
    plt.show()


if __name__ == '__main__':
    main()
