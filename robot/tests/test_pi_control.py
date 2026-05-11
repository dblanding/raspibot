# test_pi_control.py (run on Raspberry Pi)
import serial
import time

class RobotCommander:
    def __init__(self, port='/dev/serial0', baudrate=115200):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(0.1)  # Let serial initialize
        print(f"Connected to {port}")
    
    def set_mode(self, mode):
        """Set mode: AUTO or TELEOP"""
        cmd = f"M,{mode}\n"
        print(f"Sending: {cmd.strip()}")
        self.ser.write(cmd.encode())
    
    def set_velocity(self, linear, angular):
        """
        Set velocity command.
        linear: m/s (positive = forward)
        angular: rad/s (positive = counter-clockwise)
        """
        cmd = f"V,{linear:.3f},{angular:.3f}\n"
        print(f"Sending: {cmd.strip()}")
        self.ser.write(cmd.encode())
    
    def stop(self):
        """Emergency stop"""
        cmd = "S\n"
        print(f"Sending: {cmd.strip()}")
        self.ser.write(cmd.encode())
    
    def test_basic_motion(self):
        """Run basic motion tests"""
        print("\n=== Basic Motion Test ===")
        
        print("\n1. Setting mode to AUTO")
        self.set_mode("AUTO")
        time.sleep(0.5)
        
        print("\n2. Drive forward at 0.2 m/s")
        self.set_velocity(0.2, 0.0)
        time.sleep(2)
        
        print("\n3. Stop")
        self.set_velocity(0.0, 0.0)
        time.sleep(1)
        
        print("\n4. Drive backward at 0.2 m/s")
        self.set_velocity(-0.2, 0.0)
        time.sleep(2)
        
        print("\n5. Stop")
        self.set_velocity(0.0, 0.0)
        time.sleep(1)
        
        print("\n6. Rotate in place (counter-clockwise)")
        self.set_velocity(0.0, 2.1)  # 360 degrees
        time.sleep(3)
        
        print("\n7. Stop")
        self.set_velocity(0.0, 0.0)
        time.sleep(1)
        
        print("\n8. Drive in arc (forward + turn)")
        self.set_velocity(0.2, 0.3)
        time.sleep(3)
        
        print("\n9. Final stop")
        self.stop()
        
        print("\n=== Test Complete ===")

if __name__ == '__main__':
    robot = RobotCommander()
    
    try:
        robot.test_basic_motion()
    except KeyboardInterrupt:
        print("\nInterrupted - stopping robot")
        robot.stop()
