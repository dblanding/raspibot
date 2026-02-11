import RPi.GPIO as GPIO
import time

# Pin Definitions
# Use BCM numbering; you can also use GPIO.BOARD for physical pin numbers
INPUT_PIN = 17 # GPIO pin 17 (Physical pin 11)

# Configure the system
GPIO.setmode(GPIO.BCM) 

# Set up the pin as an input with an internal pull-up resistor
# The input will read HIGH by default (3.3V)
# When a button is pressed or the pin is grounded, it will read LOW (0V)
GPIO.setup(INPUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print(f"Monitoring GPIO pin {INPUT_PIN}...")
print("Press Ctrl+C to exit.")

try:
    while True:
        # Check the state of the pin
        # GPIO.LOW means the pin has been pulled to ground (0V)
        if GPIO.input(INPUT_PIN) == GPIO.LOW:
            print("Pin pulled low! Button pressed.")
            # Debounce delay to prevent multiple detections for one press
            time.sleep(0.3)
        
        # A small delay to keep the loop from running too fast
        time.sleep(0.01)

except KeyboardInterrupt:
    # Clean up GPIO settings when the program is interrupted
    print("\nProgram exited by user.")
    GPIO.cleanup()
