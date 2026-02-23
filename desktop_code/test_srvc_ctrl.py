import service_ctrl as sc
import time

sc.restart_scanner()
sc.start_odometer()
time.sleep(10)  # The odometer has to do some initialization
sc.stop_odometer()
