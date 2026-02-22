# Summary of Commands for Raspibot
* First, connect via ssh: `ssh doug@raspibot.local`

* Check Batteries:
    * `sudo python3 ~/UPS/INA219.py`
    * *ctrl c* to exit
* Scanner service (lidar):
    * Check status: `systemctl status scanner`
    * For more information, and to see its full log, use `journalctl -u scanner.service`
    * Restart service: `sudo service scanner restart`
* Odometer (OTOS)
    * Start: `uv run python robot/odometer.py`
    * *ctrl c* to Stop

## Commands run on laptop:
* Update code on robot: `pyinfra inventory.py deploy/update_code.py`
* Mapper:
    * Start mapping: `uv run python mapper.py`
    * *ctrl c* to Stop (saves map to file)
    * Display map by running *display_saved_map.py*
* MQTTUI:
    * Start: `mqttui -b mqtt://raspibot.local -u robot --password robot`
    * *q* to Quit

