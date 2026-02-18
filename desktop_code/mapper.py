import json
import numpy as np
import matplotlib.pyplot as plt
import math
import paho.mqtt.client as mqtt
import time


MQTT_BROKER_IP = "192.168.1.85"
pose = None
scan = None

# Define Callback for Client A
def on_message_a(client, userdata, message):
    global scan
    scan = json.loads(message.payload.decode())
    print("New lidar scan received")

# Define Callback for Client B
def on_message_b(client, userdata, message):
    global pose
    pose = json.loads(message.payload.decode())
    print("Robot pose updated")


class OccupancyGridMap:
    def __init__(self, width, height, resolution, p_occ=0.7, p_free=0.3, p_prior=0.5):
        self.resolution = resolution
        self.width = width
        self.height = height
        
        # Initialize grid dimensions
        self.nx = int(round(width / resolution))
        self.ny = int(round(height / resolution))
        
        # Log-odds values for updates
        self.l_occ = self._log_odds(p_occ)
        self.l_free = self._log_odds(p_free)
        self.l_prior = self._log_odds(p_prior)
        
        # Initialize map with prior log-odds
        self.data = np.full((self.nx, self.ny), self.l_prior)

    def _log_odds(self, p):
        return math.log(p / (1 - p))

    def _p_from_log_odds(self, l):
        return 1.0 - (1.0 / (1.0 + np.exp(l)))

    def pos_to_index(self, x, y):
        ix = int(round((x + self.width / 2) / self.resolution))
        iy = int(round((y + self.height / 2) / self.resolution))
        return ix, iy

    def update_map(self, pose, scan_data):
        """
        Updates the map using an inverse sensor model.
        pose: {"x_m": 0.0, "y_m": 0.0, "hdg_rad": 0.0}
        scan_data: list of {"a": 6.23, "d": 4.04} measurements
        distances are in meters, angles are in radians
        """
        rx, ry, ryaw = pose["x_m"], pose["y_m"], pose["hdg_rad"]
        ix_src, iy_src = self.pos_to_index(rx, ry)

        for meas_dict in scan_data:
            dist = meas_dict["d"]
            angle = meas_dict["a"]
            # Calculate absolute position of the detection
            tx = rx + dist * math.cos(ryaw - angle)
            ty = ry + dist * math.sin(ryaw - angle)
            ix_tar, iy_tar = self.pos_to_index(tx, ty)

            # Bresenham's line algorithm to find all cells between robot and target
            line = self._get_line(ix_src, iy_src, ix_tar, iy_tar)
            
            # Update cells along the ray as 'free'
            for (x, y) in line[:-1]:
                if 0 <= x < self.nx and 0 <= y < self.ny:
                    self.data[x, y] += self.l_free - self.l_prior
            
            # Update the endpoint cell as 'occupied'
            if 0 <= ix_tar < self.nx and 0 <= iy_tar < self.ny:
                self.data[ix_tar, iy_tar] += self.l_occ - self.l_prior

    def _get_line(self, x1, y1, x2, y2):
        """Standard Bresenham's line algorithm."""
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x, y = x1, y1
        sx = -1 if x1 > x2 else 1
        sy = -1 if y1 > y2 else 1

        if dx > dy:
            err = dx / 2.0
            while x != x2:
                points.append((x, y))
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y2:
                points.append((x, y))
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
        points.append((x, y))
        return points

    def plot_map(self):
        # Convert log-odds back to probability for visualization
        prob_map = self._p_from_log_odds(self.data)
        plt.imshow(prob_map.T, cmap="Greys", origin="lower",
                   extent=[-self.width/2, self.width/2, -self.height/2, self.height/2])
        plt.colorbar(label="Occupancy Probability")
        plt.xlabel("X [m]")
        plt.ylabel("Y [m]")
        plt.pause(0.01)


if __name__ == '__main__':
    # Initialize OGM (10m x 10m, 0.1m resolution)
    ogm = OccupancyGridMap(width=3, height=3, resolution=0.04)

    # Setup Client A
    client_a = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client_a.on_message = on_message_a
    client_a.connect(MQTT_BROKER_IP, 1883)
    client_a.subscribe("lidar/data")

    # Setup Client B
    client_b = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client_b.on_message = on_message_b
    client_b.connect(MQTT_BROKER_IP, 1883)
    client_b.subscribe("odom/pose")

    # Start non-blocking loops
    client_a.loop_start()
    client_b.loop_start()

    print("Listening for messages... Press Ctrl+C to stop.")

    try:
        while True:
            if pose and scan:
                ogm.update_map(pose, scan)
            time.sleep(0.1)
    except KeyboardInterrupt:
        client_a.loop_stop()
        client_b.loop_stop()
    finally:
        plt.figure(figsize=(8, 6))
        ogm.plot_map()
        plt.show()
