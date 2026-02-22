import numpy as np
import matplotlib.pyplot as plt
import math
import parameters

def p_from_log_odds(l):
    return 1.0 - (1.0 / (1.0 + np.exp(l)))

def plot_map(np_map, width=parameters.width, height=parameters.height):
    # Convert log-odds back to probability for visualization
    prob_map = p_from_log_odds(saved_map)
    plt.imshow(prob_map.T, cmap="Greys", origin="lower",
               extent=[-width*parameters.orig_x_pos,
                       width*(1-parameters.orig_x_pos),
                       -height*parameters.orig_y_pos,
                       height*(1-parameters.orig_y_pos)])
    plt.colorbar(label="Occupancy Probability")
    plt.xlabel("X [m]")
    plt.ylabel("Y [m]")
    plt.pause(0.01)
    plt.show()


# Load map from file and display it
saved_map = np.load('my_map.npy')
plot_map(saved_map)
