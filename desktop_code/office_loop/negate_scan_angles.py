# read scans and poses from file
# negate angle values in all scans
# save to file

import os
import pickle
from pprint import pprint


def load_data(filename="scan_data.pkl"):
    """Loads and deserializes data from a binary file."""
    if os.path.exists(filename):
        # Open file in read-binary mode ('rb')
        with open(filename, 'rb') as file:
            data = pickle.load(file)
        print(f"data loaded from {filename}")
        return data
    else:
        print(f"data File {filename} not found.")
        return None

# --- Save data ---
def save_data(data, filename="scan_data.pkl"):
    """Serializes and saves data to a binary file."""
    # Open file in write-binary mode ('wb')
    with open(filename, 'wb') as file:
        pickle.dump(data, file)
    print(f"data saved to {filename}")



data = load_data()
print(f"{len(data)=}")
print()
for n, d in enumerate(data):
    pose = d['pose']
    scan = d['scan']  # list of scan dicts {'a': 6.1446, 'd': 2.0495, 't': 116.71034}
    for scandict in scan:
        scandict['a'] *= -1

save_data(data)


pprint(scan)  # the last scan

