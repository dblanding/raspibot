# test_speed.py
"""
Report vehicle speed while driving.
"""
import qwiic_otos
import sys
import time

# --- OTOS Configuration ---
# Initialize the SparkFun OTOS
otos = qwiic_otos.QwiicOTOS()
if not otos.is_connected():
    print("The OTOS is not connected. Check wiring.")
    client.loop_stop()
    sys.exit(1)
otos.begin()

# Calibrate the IMU, which removes the accelerometer and gyroscope offsets
print("Ensure the OTOS is flat and stationary during calibration!")
for i in range(5, 0, -1):
    print("Calibrating in %d seconds..." % i)
    time.sleep(1)
print("Calibrating IMU...")
otos.calibrateImu()
otos.setLinearScalar(1.0)
otos.setAngularScalar(0.9976)

# Account for OTOS location w/r/t robot center
offset = qwiic_otos.Pose2D(0.295, 0, 0)
otos.setOffset(offset)

# Set units for linear and angular measurements.
# If not set, the default is inches and degrees.
# Note that this setting is not stored in the sensor.
# it's part of the library, so you need to set it.
otos.setLinearUnit(otos.kLinearUnitMeters)
otos.setAngularUnit(otos.kAngularUnitRadians)

# Reset the tracking algorithm - this resets the position to the origin,
# but can also be used to recover from some rare tracking errors
otos.resetTracking()
print("OTOS initialized")

class Odom():
    """Keep track of previous reading to calculate change rates"""

    def __init__(self):
        self.t = time.monotonic()  # (prev) timestamp (seconds)
        self.x = 0.0  # (prev) x value of pose (meters)
        self.y = 0.0  # (prev) y value of pose (meters)
        self.h = 0.0  # (prev) heading value of pose (radians)

    def get_pose(self):
        ts = time.monotonic()
        dt = ts - self.t
        pose = otos.getPosition()
        dx = pose.x - self.x  # change of x
        dy = pose.y - self.y  # change of y
        dh = pose.h - self.h  # change of h
        xr = dx / dt  # rate of change of x
        yr = dy / dt  # rate of change of y
        hr = dh / dt  # rate of change of h
        self.x = pose.x
        self.y = pose.y
        self.h = pose.h
        self.t = ts
        pose_data = {
                "x": pose.x,
                "y": pose.y,
                "h": pose.h,
                "t": ts,
                "xr": xr,
                "yr": yr,
                "hr": hr
                }
        return pose_data

def spd_test():
    odom = Odom()
    # Main loop to read and print speed data
    while True:
        new_pose = odom.get_pose()
        speed = new_pose['xr']
        print(speed, " mps")
        time.sleep(0.1)

if __name__ == "__main__":
    spd_test()
