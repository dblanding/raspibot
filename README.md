# Command Summary for Raspibot
* Check Batteries:
    * From `ssh doug@raspibot.local`
        * `sudo python3 ~/UPS/INA219.py`
        * ctrl c to exit
* Run lidar test (10 scans):
    * From `ssh doug@raspibot.local`
        * `uv run python robot/tests/rplidar_test.py`
    * From *raspibot/desktop_code/* folder on laptop
        * Copy data `scp doug@raspibot.local:data.pkl .`
        * Display the scan `python display_lidar.py`
* Run OTOS test:
    * From `ssh doug@raspibot.local`
        * `uv run python robot/tests/otos_test.py`
        * ctrl c to exit
