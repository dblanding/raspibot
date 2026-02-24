# Summary of Commands for Raspibot
* First, connect via ssh: `ssh doug@raspibot.local`

* Check Batteries:
    * `sudo python3 ~/UPS/INA219.py`
    * *CTRL+C* to exit
* Scanner service (lidar):
    * Check status: `systemctl status scanner`
    * For more information, and to see its full log, use `journalctl -u scanner.service`
    * Restart service: `sudo service scanner restart`
* Odometer (OTOS):
    * Check status: `systemctl status odometer`
    * For more information, and to see its full log, use `journalctl -u odometer.service`
    * Start: `sudo systemctl start odometer.service`
    * Stop: `sudo systemctl stop odometer.service`

* Run_scan_mtr (lidar):
    * Check status: `systemctl status run_scan_mtr`
    * For more information, and to see its full log, use `journalctl -u run_scan_mtr.service`
    * Start motor running: `sudo systemctl start run_scan_mtr.service`
    * Stop motor: `sudo systemctl stop run_scan_mtr.service`

## Commands run on laptop:
* Update code on robot: `pyinfra inventory.py deploy/update_code.py`
* Mapper:
    * Start mapping: `uv run python mapper.py`
    * *CTRL+C* to Stop (saves map to file)
    * Display map by running *display_saved_map.py*
* MQTTUI:
    * Start: `mqttui -b mqtt://raspibot.local -u robot --password robot`
    * *q* to Quit

