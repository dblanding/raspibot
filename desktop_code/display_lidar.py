import os
from math import cos, sin, pi
import matplotlib.pyplot as plt
import numpy as np
import pickle

file_name = "data.pkl"
with open(file_name, 'rb') as file:
    scans = pickle.load(file)

def run_lidar_mapping():
    try:
        # Setup matplotlib plot
        plt.ion() # Turn on interactive mode
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, polar=True)
        scatter = ax.scatter([0, 0], [0, 0], s=5) # Initialize scatter plot
        ax.set_ylim(0, 1500) # Set max distance for the plot (in mm)

        for scan in scans:
            if len(scan) > 0:
                # Extract angles and distances
                # Convert to radians, filter invalid data
                angles = [-measurement[1] * pi / 180 for measurement in scan if measurement[2] > 0]
                distances = [measurement[2] for measurement in scan if measurement[2] > 0]

                # Update the scatter plot data
                scatter.set_offsets(list(zip(angles, distances)))
                fig.canvas.draw_idle()
                plt.pause(1.0) # Pause to allow plot to update
                
    except KeyboardInterrupt:
        print('Stopping...')
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        plt.ioff() # Turn off interactive mode
        plt.show()

if __name__ == '__main__':
    run_lidar_mapping()
