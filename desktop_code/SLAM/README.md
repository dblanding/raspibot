# Implementing SLAM, a work in progress
* Drive Kitchen loop with reflective surfaces masked.
* Run *scan_grabber.py* during loop to collect scan & pose data @ 1/s, saved in file *scan_data.pkl*
    * Scan data includes timestamps
    * Pose data includes timestamps, and rate of change of x, y, h
* File *process_data.py* loads the saved data from *scan_data.pkl* and synchronizes pose to scan, then saves (without timestamps and rates) in .npz format
* File *load_data.py* demonstrates loading of processed scan and pose data from .npz format.
