# topics.py
"""
Central topic definitions for robot MQTT communication.
Single Point Of Truth (S.P.O.T.) for all topic names.
Noy all of these topics are actually in use.
Dom't use hard-coded topics.
"""

class Topics:
    """MQTT topic names for robot system"""
    
    # Sensors
    LIDAR_SCAN = 'robot/sensor/lidar/scan'  # in use
    LIDAR_STATUS = 'robot/sensor/lidar/status'  # in use
    CAMERA_IMAGE = 'robot/sensor/camera/image'
    CAMERA_COMPRESSED = 'robot/sensor/camera/compressed'
    IMU_DATA = 'robot/sensor/imu/data'
    
    # Odometry
    ODOM_POSE = 'robot/odometry/pose'   # Raw odometry pose (odom frame)
    INITIAL_POSE = "robot/initialpose"  # Set initial pose
    ODOM_VELOCITY = 'robot/odometry/velocity'
    ODOM_OPTICAL = 'robot/odometry/optical'
    
    # Motor Control
    MOTOR_CMD = 'robot/motor/cmd'  # in use
    MOTOR_STATUS = 'robot/motor/status'
    MOTOR_LEFT_ENCODER = 'robot/motor/left/encoder'
    MOTOR_RIGHT_ENCODER = 'robot/motor/right/encoder'

    # Localization
    CORRECTION = "robot/localization/correction"  # odom correction transform
    POSE = "robot/localization/pose"    # Localized pose (map frame)
    
    # Mapping
    MAP_GRID = 'robot/map/grid'
    MAP_OCCUPANCY = 'robot/map/occupancy'
    MAP_UPDATE = 'robot/map/update'
    MAP_METADATA = 'robot/map/metadata'
    
    # Navigation
    NAV_GOAL = 'robot/navigation/goal'
    NAV_PATH = 'robot/navigation/path'
    NAV_STATUS = 'robot/navigation/status'
    NAV_CMD_VEL = 'robot/navigation/cmd_vel'
    NAV_SHUTDOWN = 'robot/navigation/shutdown'  # signals obstacle_avoidance to exit
    EXPLORE_GOAL = 'robot/navigation/explore_goal'  # frontier_explorer → path_follower
    
    # System
    SYSTEM_HEALTH = 'robot/system/health'
    SYSTEM_BATTERY = 'robot/system/battery'
    SYSTEM_CPU = 'robot/system/cpu'
    SYSTEM_STATUS = 'robot/system/status'
    SYSTEM_DIAGNOSTICS = 'robot/system/diagnostics'
    
    # Debug
    DEBUG_STATE = 'robot/debug/state'
    DEBUG_TIMING = 'robot/debug/timing'
    DEBUG_LOG = 'robot/debug/log'
    
    @classmethod
    def all_topics(cls):
        """Return list of all topics (useful for logging/monitoring)"""
        return [v for k, v in vars(cls).items() if not k.startswith('_') and isinstance(v, str)]
    
    @classmethod
    def sensor_topics(cls):
        """Return all sensor-related topics"""
        return [v for k, v in vars(cls).items() if 'LIDAR' in k or 'CAMERA' in k or 'IMU' in k]
