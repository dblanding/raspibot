import numpy as np
import matplotlib.pyplot as plt
import math

def p_from_log_odds(l):
    return 1.0 - (1.0 / (1.0 + np.exp(l)))

def plot_map(np_map, width=3, height=3):
    # Convert log-odds back to probability for visualization
    prob_map = p_from_log_odds(saved_map)
    plt.imshow(prob_map.T, cmap="Greys", origin="lower",
               extent=[-width/2, width/2, -height/2, height/2])
    plt.colorbar(label="Occupancy Probability")
    plt.xlabel("X [m]")
    plt.ylabel("Y [m]")
    plt.pause(0.01)
    plt.show()


# Load map from file and display it
saved_map = np.load('my_map.npy')
plot_map(saved_map)
