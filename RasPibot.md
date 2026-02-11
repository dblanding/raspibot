# Notes on building the RaspiBot
* Use a Raspberry Pi SBC configured with pyinfra, using the services/MQTT paradigm from LRP3
* *Repurpose* the chassis and RasPi from my old ROS robot
* Will do (roughly) what the picobot aimed to do:
    * Explore and map the house
    * Discover *canyons* wide enough to fit through
    * Find and follow a loop to return home.
* Will have these features:
    * 2 wheel differential drive
    * Slamtec RPLidar A1 distance sensing (connected via Raspi USB)
    * [Sparkfun Optical Tracking Odometry Sensor](https://www.sparkfun.com/products/24904) (connected to Raspi I2C)
        * [YouTube video](https://www.youtube.com/watch?v=WcCNC8wExUc&t=120s) discusses calibration process
    * DC power provided by [Waveshare UPS Module 3S](https://www.amazon.com/waveshare-Uninterruptible-UPS-Module-3S/dp/B0BQC2WNR8/ref=ast_sto_dp_puis) (3x 18650 batts)
        * 3.7 * 3 = 11.1V supplied to [Waveshare motor driver board](https://www.amazon.com/Waveshare-Driver-Raspberry-Driving-Suitable/dp/B09D7MDL2C/ref=ast_sto_dp_puis) (which powers the onboard Pico)
        * 5V power for Raspberry Pi
        * I2C battery monitoring using [INA219.py](https://drive.google.com/file/d/1rSbdvlRwfYJuLa_MSni0Q6e7lDZz0r6w/view)
    * Wheel motors controlled by Raspberry Pi Pico directly.
    * Teleop control via BLE between 2 Picos as described in this [BLE Joystick Controlled Mecanum Car](https://github.com/dblanding/BLE-Joystick-Controlled-Mecanum-Car) project.
        * The driver station is the BLE server.
        * The Pico on board the raspibot is the BLE client (using ony 2 axes).
    * [Raspi Shutdown](https://forums.raspberrypi.com/viewtopic.php?t=334857) via:
        1. Physical button switch
        2. Clickable button on webserver

## Preparing the SD card (as in LRP3 ch3)
1. Prepare a Headless Raspberry Pi for a Robot
    * Raspberry Pi 3B+
    * SD card: 32 GB 
    * Raspberry Pi OS Lite (32-bit)
        * I had a lot of trouble with this using the Raspi-imager on my linux laptop
        * I ended up succeeding by using the imager (v2.03) under windows
        * Also, I noticed that although I selected the 64-bit version, the summary showed me that the 32-bit version was going to be installed.
    * Host Name: raspibot
    * User Name: doug
    * pswd: robot
    * ssh enabled
2. Once the SD card was finished, I inserted it into the Rapberry Pi 3B+
    * `ping raspibot.local`
    * `ssh doug@raspibot.local`
        * Update and upgrade: `sudo apt update -y && sudo apt upgrade -y`
        * `sudo poweroff`
3. Set up SSH Key Authentication
    * During the Raspberry Pi Imager setup, I enabled only password authentication
    * So now I need to enable SSH Key Authentication
        * On my laptop, I already have SSH keys in `~/.ssh/`
        * So I just need to run `ssh-copy-id doug@raspibot.local` to send over the public key.

## Set up pushbutton shutdown on Raspberry Pi
* Pin 5 (GPIO3) is the default for shutdown and wake-up, but I plan to use that pin for I2C.
* To implement a safe shutdown on a Raspberry Pi 3B+ using a GPIO pin other than Pin 5, connect a momentary button between your chosen GPIO pin (e.g., GPIO 26) and Ground (GND), then add `dtoverlay=gpio-shutdown,gpio_pin=26,active_low=1,debounce=200` to /boot/config.txt, changing 26 to your pin's GPIO number to trigger a graceful shutdown when the button is pressed for about 3 seconds. This leverages the built-in gpio-shutdown overlay for simple hardware-based power management. 

#### Hardware Setup 
1. Choose Your Pin: Select any available GPIO pin (e.g. GPIO 26, which is physical pin 37). 
2. Connect the Button: Wire a momentary push button between your chosen GPIO pin and any Ground (GND) pin on the Raspberry Pi header. 

#### Software Configuration 

1. Edit file `config.txt`: Open the configuration file with `sudo nano /boot/firmware/config.txt`. 
2. Add the Overlay: Add the following line to the end of the file, replacing `26` with your chosen GPIO number (e.g., `gpio_pin=21` for GPIO 21): 

`dtoverlay=gpio-shutdown,gpio_pin=26,active_low=1,debounce=200`

* `gpio_pin=26`: Specifies your chosen GPIO. 
* `active_low=1`: Assumes the button connects the pin to ground (pull-up is default). 
* `debounce=200`: Waits 200ms (0.2 seconds) to prevent accidental triggers from button bounce. 

3. Save and Reboot: Save the file (Ctrl+X, then Y, then Enter) and reboot your Raspberry Pi (`sudo reboot`).

Now, pressing the button for about 0.2 seconds will initiate a graceful shutdown.

## Set up program to monitor UPS
* Hook up SDA and SCL pins on UPS to SDA & SCL pins on Raspberry Pi
* `ssh doug@raspibot.local`
* Follow instructions in [Waveshare primer](https://www.youtube.com/watch?v=9xOhMiyDwow)
    * Add file `~/UPS/INA219.py`
    * Enable I2C in raspi-conifg `sudo raspi-config`
    * Run `i2cdetect -y -r 1`
        * Device address is 41
    * Run python file `sudo python3 ~/UPS/INA219.py`
    * Output (typ):
    ```
    Load Voltage:  12.492 V
    Current:        0.081991 A
    Power:          1.024 W
    Percent:       97.0%
    ```

## Install Rplidar s/w
* Follow instructions at RPLidar A1 Python module GitHub repo: [Skoltech Robotics RPLidar](https://github.com/SkoltechRobotics/rplidar)
    * `ssh doug@raspibot.local`
        * `sudo pip3 install rplidar`
            * got the error: externally-managed-environment, This environment is externally managed
            * When I got this error on my laptop, I installed uv, so I will do that here.
        * Install uv with: `curl -LsSf https://astral.sh/uv/install.sh | sh`
        * Install rplidar with: `uv add rplidar-roboticia`
        * Set `~` as the uv project directory: `uv init`
            * This will add a bunch of *uv* related files to *~*.
* Maybe now is a good time to use `pyinfra` to install the following simple example:
``` Python
from rplidar import RPLidar
lidar = RPLidar('/dev/ttyUSB0')

info = lidar.get_info()
print(info)

health = lidar.get_health()
print(health)

for i, scan in enumerate(lidar.iter_scans()):
    print('%d: Got %d measurments' % (i, len(scan)))
    if i > 10:
        break

lidar.stop()
lidar.stop_motor()
lidar.disconnect()
```
        
## Using `pyinfra` to manage the code on the (remote) raspibot
In chapter 4 of Danny Staple's book *Learn Robotics Programming (Version 3)*, he shows how `pyinfra` can be used to keep all the code and configuration up-to-date on remote computers from the laptop. (Just to be clear, since I have elected to install `uv` and set up my `~` directory as a *uv project*, I will continue to manage the *uv* environment directly via ssh, and will use *pyinfra* to maintain the code and the *apt* configuration on the raspibot.)

#### Referring to *LRP3 chapter 4* as a guide:
* **On my laptop**, create a *raspibot* folder. This will contain all the files for the project that are located on the laptop.
* Run the command `uv init` from a terminal inside the *raspibot* folder.
    * This initializes the folder as a *uv-managed Python project*, enabling the use of the `pyinfra` command, which has already been added system-wide as a *uv tool*.
    * It also sets up the folder as a git repository
* Create a file named `inventory.py` in the *raspibot* folder, listing the robot’s details.
* Create a sub-folder named *robot* under *raspibot*. This will contain all the robot's python files.
* Create another folder named *tests* under *robot*.
* Create a file named *rplidar_test.py* under *tests* and copy the above example code into it.
* From a terminal in the *raspibot* folder, run the command: `pyinfra inventory.py files.sync src=robot dest=robot -y`. This will create *robot/tests/rplidar_test.py* on the raspibot.
* Now ssh to the robot `ssh doug@raspibot.local`
    * Run the command `uv run python robot/tests/rplidar_test.py`
    * Produced the following output
```
doug@raspibot:~/robot $ uv run python robot/tests/rplidar_test.py
{'model': 24, 'firmware': (1, 29), 'hardware': 7, 'serialnumber': '92D5EE8BC8E792D6B1E39BF01B034C6C'}
('Good', 0)
0: Got 24 measurments
1: Got 103 measurments
2: Got 103 measurments
3: Got 100 measurments
4: Got 101 measurments
5: Got 100 measurments
6: Got 105 measurments
7: Got 103 measurments
8: Got 103 measurments
9: Got 103 measurments
10: Got 107 measurments
11: Got 105 measurments
```
* Next, edit *rplidar_test.py* code on laptop to save the 10 scans to a pickle file *~/data.pkl*.
* Run `pyinfra inventory.py files.sync src=robot dest=robot -y` again to transfer the changes to raspibot.
* With the robot placed inside the arena, run the rplidar_test script again (from ssh) to generate the file *~/data.pkl* containing the scan data.
* From the laptop, run `scp doug@raspibot.local:data.pkl .` to retrieve the scans.
* On the laptop, run the file *display_lidar.py*, which loads the data and displays it.
    * The image below is *just the last of the 10 scans*.
![Arena lidar map](desktop_code/arena_lidar_map.png)

## Set up Odometry Sensor
* Run `i2cdetect -y -r 1`
    * Device address is 17
* Test it
    * Add test code to robot/tests folder
        * *otos_test.py*
        * *qwiic_otos.py*
    * sync with `pyinfra inventory.py files.sync src=robot dest=robot -y`
    * ssh to raspibot
        * Add the *sparkfun-qwiic-i2c* library: `uv add sparkfun-qwiic-i2c`
        * run `uv run python robot/tests/otos_test.py`
    * It works!
* To do: Calibrate the OTOS per instructions on [Adafruit video](https://www.youtube.com/watch?v=WSELKAIJeFk&t=4s).

## Additional steps to setting up *pyinfra*
#### Create a file for updating code, which we can keep for later.
* Add a *deploy* directory, and create the file *deploy/update_code.py*
``` python
from pyinfra.operations import files

files.sync(src="robot", dest="robot", delete=True, exclude=("*.pyc", "__pycache__"))
```
* This script will perform the sync, and also ensure certain files are excluded from it. This sends over any changed files in the robot folder, storing them in a robot folder on the Raspberry Pi. With *delete=True*, it will also handle files being renamed or removed.
* Can now use the command `pyinfra inventory.py deploy/update_code.py` to update the code on the raspibot with any changes made to the code in the *robot* folder on the laptop.

#### Updating *apt* packages on the raspibot
* When you’ve installed Raspberry Pi OS on an SD card, the packages and package index can be out of date. It’s common to update them before installing other packages.
* Create the file *deploy/update_packages.py* with the following:
```
from pyinfra.operations import apt

apt.update(
    name="Update apt cache",
    _sudo=True,
)

apt.upgrade(
    name="Upgrade all packages",
    _sudo=True,
)
```
* Can now use the command `pyinfra inventory.py deploy/update_packages.py` keep all the packages on the raspibot up to date.
* Tested it. Took several minutes, but it seemed to work.

#### Update both packages and code
* Create the file *deploy/deploy_all.py*
* By running the `pyinfra inventory.py deploy/deploy_all.py -y`, both the packages and the code on the raspibot will be updated.

#### Updating uv packages on the raspibot
* Because I have chosen to use *uv* to manage the virtual environment on the raspibot, keeping the libraries in that environment up to date would require an additional script.
* I created the file *deploy/update_uv_pkgs.py* on the laptop to do this. (I got this code from Google AI and it isn't guaranteed to work)
* Unfortunately, I couldn't get it to work.
```
doug@HP-Laptop:~/Desktop/raspibot$ pyinfra inventory.py deploy/update_uv_pkgs.py
--> Loading config...
--> Loading inventory...
--> Connecting to hosts...
    [raspibot.local] Connected

--> Preparing operation files...
    Loading: deploy/update_uv_pkgs.py
    [raspibot.local] Ready: deploy/update_uv_pkgs.py

--> Detected changes:
    Operation                                         Change               Conditional Change   
    Upgrade all packages in the project environment   1 (raspibot.local)   -                    

    Detected changes may not include every change pyinfra will execute.
    Hidden side effects of operations may alter behaviour of future operations,
    this will be shown in the results. The remote state will always be updated
    to reflect the state defined by the input operations.

    Detected changes displayed above, skip this step with -y
                             
--> Beginning operation run...
--> Starting operation: Upgrade all packages in the project environment 
    [raspibot.local] sh: 1: uv: not found
    [raspibot.local] Error: executed 0 commands
```
* So I decided I would just continue to manage the uv package environment manually via ssh, as I have been doing.
* Here is a summary of the *uv* environment so far:
    * `ssh doug@raspibot.local`
        * `uv add rplidar-roboticia`
        * `uv add sparkfun-qwiic-i2c`

## Proposed idea for how to do mapping
Here's the idea: When the raspibot powers up, 2 services will start:
1. Scanner service
    * This will start out in **sleep mode** with the scan motor off.
    * It will respond to a trigger (a gpio pin pulled LOW) which will set it into **scan mode**
2. Webserver service
    * This will serve up a webpage with a **Start Mapping** button that arouses the scanner and starts the OTOS, and a **Stop Mapping** button that ends the program and returns the scanner to sleep mode.
    * While scanning, the robot will build an OGM as it is driven around in Tele-op mode. The OGM can then be downloaded and displayed on the laptop.

* Create file *robot/tests/gpio_test.py* to test the use of gpio as trigger.
    * Hook up a switch between pin 11 (gpio 17) and adjacent pin 9 (ground)
    * Test: `ssh doug@raspibot.local` then run `python robot/tests/gpio_test.py`

## Add the systemD scanner service
Chapter 7 of LRP3 shows how to create the services that will enable building the mapping behavior described above.

* Create the file *deploy/service_template.j2* (minus the *After=mosquitto.service* line since I am not planning to use MQTT.)
* Create the file *deploy/deploy_services.py*
* Create the file *robot/scanner.py*
    * Interestingly, whereas *gpio_test.py* was able to *import RPi.GPIO*, *scanner.py* (running under uv) was not.
    * Had to add another uv library: `uv add RPi.GPIO` to get it to run.
* Deploy the *scanner service* by running `pyinfra inventory.py deploy/deploy_services.py -y`
