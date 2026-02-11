import RPi.GPIO as GPIO
import rplidar
import time

INPUT_PIN = 17 # GPIO pin 17 (Physical pin 11)
GPIO.setmode(GPIO.BCM)
GPIO.setup(INPUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Create a Lidar object
lidar = rplidar.RPLidar('/dev/ttyUSB0')

info = lidar.get_info()
print(f"info: {info}")

health = lidar.get_health()
print(f"health: {health}")

def run():
    print('Starting scan...')
    # Iterate over scans (motor runs automatically when scanning starts)
    for i, scan in enumerate(lidar.iter_scans()):
        print('%d: Got %d measurements' % (i, len(scan)))
        if not GPIO.input(INPUT_PIN) == GPIO.LOW:
            break

    # Stop the motor and disconnect cleanly
    print('Stopping motor and disconnecting...')
    lidar.stop()           # Stops the scanning/data acquisition
    lidar.stop_motor()     # Explicitly stops the motor
    print('RPLidar stopped.')

def stop():
    lidar.stop()
    lidar.stop_motor()

if __name__ == '__main__':
    try:
        while True:
            while GPIO.input(INPUT_PIN) == GPIO.LOW:
                run()
            stop()
            time.sleep(1)

    except KeyboardInterrupt:
        print('Interrupted by user, stopping...')

    finally:
        # Stop the motor and disconnect cleanly
        print('Stopping motor and disconnecting...')
        lidar.stop()           # Stops the scanning/data acquisition
        lidar.stop_motor()     # Explicitly stops the motor
        lidar.disconnect()     # Disconnects from the serial port
        print('RPLidar stopped and disconnected.')
