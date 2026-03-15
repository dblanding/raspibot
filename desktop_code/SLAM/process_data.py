# process data and save for use by slam program

import numpy as np
import os
import pickle


def load_data(filename="scan_data.pkl"):
    """Loads and deserializes an OGM instance from a binary file."""
    if os.path.exists(filename):
        # Open file in read-binary mode ('rb')
        with open(filename, 'rb') as file:
            data = pickle.load(file)
        print(f"data loaded from {filename}")
        return data
    else:
        print(f"data File {filename} not found.")
        return None

def sync_pose(robot_scan, robot_pose):
    """
    robot_scan: list of {'a': , 'd': , 't': } dictionaries
    robot_pose: {"x": , "y": , "h": , "t": , "xr": , "yr": , "hr": } dict
    Return estimated pose at time of mid-scan
    """
    # Find time difference between mid-scan and pose
    mid_scan_idx = len(robot_scan) // 2
    mid_scan_time = robot_scan[mid_scan_idx]['t']
    pose_time = robot_pose["t"]
    time_diff = mid_scan_time - pose_time

    # Estimate pose value at time of mid-scan
    rx = robot_pose["x"] + robot_pose["xr"] * time_diff
    ry = robot_pose["y"] + robot_pose["yr"] * time_diff
    ryaw = robot_pose["h"] + robot_pose["hr"] * time_diff
    return rx, ry, ryaw


if __name__ == "__main__":
    data = load_data()
    prev_pose = (0, 0, 0)  # Initial value

    # Prepare for saving
    poses = []
    all_angles = []
    all_ranges = []
    scan_lengths = []

    for n in range(0, len(data)):
        print(n)
        print(f"{prev_pose = }")
        robot_scan = (data[n]['scan'])  # in local polar coords
        print(f"{len(robot_scan) = }")
        robot_pose = data[n]['pose']
        print(f"{robot_pose = }")
        synced_pose = sync_pose(robot_scan, robot_pose)  # estimated pose at time of mid-scan
        print(f"{synced_pose = }")
        prev_pose = synced_pose
        print()
        
        # Collect angles and ranges
        scandict = {scan['a']: scan['d']
                    for scan in robot_scan}
        angles = np.array(list(scandict.keys()))
        ranges = np.array(list(scandict.values()))
        poses.append(synced_pose)
        all_angles.extend(angles)
        all_ranges.extend(ranges)
        scan_lengths.append(len(angles))

    # save scan data
    filename = 'scan_data.npz'
    np.savez_compressed(
        filename,
        angles = np.array(all_angles),
        ranges = np.array(all_ranges),
        scan_lengths = np.array(scan_lengths),
        num_scans = len(data)
        )

    # save pose data
    posefilename = 'pose_data.npz'
    np.savez_compressed(
        posefilename,
        poses = np.array(poses),
        num_poses = len(poses)
        )
