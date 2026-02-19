import numpy as np
import math


class Build_OGM:
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

    def update_map(self, robot_pose, scan_data):
        """
        Updates the map using an inverse sensor model.
        robot_pose: {"x_m": 0.0, "y_m": 0.0, "hdg_rad": 0.0} dict
        scan_data: list of {'a': 6.24, 'd': 4.07} dictionaries
        """
        rx = robot_pose["x_m"]
        ry = robot_pose["y_m"]
        ryaw = robot_pose["hdg_rad"]
        
        ix_src, iy_src = self.pos_to_index(rx, ry)

        for meas in scan_data:
            angle = meas['a']
            dist = meas['d']
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


# --- Example Usage ---
if __name__ == '__main__':
    # Initialize OGM (10m x 10m, 0.1m resolution)
    ogm = BuildOGM(width=3, height=3, resolution=0.04)

    # Simulated Robot Poses: [x, y, yaw]
    pose = [0, 0, 0]
    
    for i in range(1, 11, 1):  # 1 through 10, inclusive
        filename = f"../arena_scan_data/scan{i}.csv"
        scn = file_read(filename)
        ogm.update_map(pose, scn)

    # Save ogm
    np.save('my_map.npy', ogm.data)
    print("Map saved to my_map.npy")
