"""
Sensor initialization and basic control
包含传感器初始化和基本控制功能
"""
from ev3dev2.sensor.lego import UltrasonicSensor, GyroSensor
from ev3dev2.sensor import INPUT_1, INPUT_2
import logging
from config import *

class SensorController:
    def __init__(self):
        try:
            # Initialize sensors
            self.ultrasonic = UltrasonicSensor(ULTRASONIC_PORT)
            self.gyro = GyroSensor(GYRO_PORT)
            
            # Configure ultrasonic sensor
            self.ultrasonic.mode = 'US-DIST-CM'
            
            # Configure gyro sensor
            self.gyro.mode = 'GYRO-ANG'
            self.gyro.reset()
            
            logging.info("Sensors initialized successfully")
            
        except Exception as e:
            logging.error(f"Sensor initialization failed: {str(e)}")
            raise
    
    def get_distance(self):
        """Get distance measurement from ultrasonic sensor"""
        try:
            distance = self.ultrasonic.distance_centimeters
            if MIN_SCAN_DISTANCE <= distance <= MAX_SCAN_DISTANCE:
                return distance
            return None
        except Exception as e:
            logging.error(f"Distance measurement failed: {str(e)}")
            return None
    
    def get_angle(self):
        """Get current angle from gyro sensor"""
        try:
            return self.gyro.angle
        except Exception as e:
            logging.error(f"Angle measurement failed: {str(e)}")
            return None
    
    def reset_gyro(self):
        """Reset gyro sensor"""
        try:
            self.gyro.reset()
            logging.info("Gyro sensor reset successful")
        except Exception as e:
            logging.error(f"Gyro reset failed: {str(e)}")
