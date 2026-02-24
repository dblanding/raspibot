import RPi.GPIO as GPIO
import time

# Pin Definition. Connect to pin 17 (motor control) by jumper.
GPIO_PIN = 27 

# Suppress warnings about potential GPIO conflicts
GPIO.setwarnings(False)

# Pin Setup
# Use the Broadcom (BCM) pin-numbering scheme
GPIO.setmode(GPIO.BCM) 

# Set the desired pin as an output
# We can also set the initial state here to LOW
GPIO.setup(GPIO_PIN, GPIO.OUT, initial=GPIO.LOW)

print(f"GPIO pin {GPIO_PIN} (BCM numbering) is set to LOW. Press CTRL+C to exit.")
try:
    # Keep the program running indefinitely to hold the pin state
    while True:
        # Keep the pin low as long as program is running
        GPIO.output(GPIO_PIN, GPIO.LOW)
        time.sleep(1) # Sleep to reduce CPU usage

except KeyboardInterrupt:
    # This block is executed when the user presses CTRL+C
    print("\nExiting program and cleaning up GPIO pins.")

finally:
    # Good practice: clean up all GPIO resources on exit
    GPIO.cleanup()

