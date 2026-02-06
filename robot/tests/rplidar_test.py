from mysave import save_data
from rplidar import RPLidar
import os


lidar = RPLidar('/dev/ttyUSB0')

info = lidar.get_info()
print(f"info: {info}")

health = lidar.get_health()
print(f"health: {health}")
scans = []
for i, scan in enumerate(lidar.iter_scans()):
    print('%d: Got %d measurments' % (i, len(scan)))
    scans.append(scan)
    if i > 10:
        break
print("CWD: ", os.getcwd())
save_data(scans)
lidar.stop()
lidar.stop_motor()

lidar.disconnect()
