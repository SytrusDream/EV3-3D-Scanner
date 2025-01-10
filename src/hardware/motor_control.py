"""
Basic motor control for the scanning system
包含电机控制的基本功能
"""
from ev3dev2.motor import LargeMotor, MediumMotor, SpeedPercent
import logging
from config import *

class MotorController:
    def __init__(self):
        try:
            # Initialize motors
            self.horizontal_motor = LargeMotor(HORIZONTAL_MOTOR_PORT)
            self.vertical_motor = LargeMotor(VERTICAL_MOTOR_PORT)
            self.scanner_motor = MediumMotor(SCANNER_MOTOR_PORT)
            
            # Reset motors
            self.reset_motors()
            
            logging.info("Motors initialized successfully")
            
        except Exception as e:
            logging.error(f"Motor initialization failed: {str(e)}")
            raise
    
    def reset_motors(self):
        """Reset all motors to home position"""
        try:
            self.horizontal_motor.reset()
            self.vertical_motor.reset()
            self.scanner_motor.reset()
            logging.info("Motors reset successful")
        except Exception as e:
            logging.error(f"Motor reset failed: {str(e)}")
    
    def rotate_horizontal(self, angle, speed=SCAN_SPEED):
        """Rotate horizontal motor by specified angle"""
        try:
            self.horizontal_motor.on_for_degrees(
                SpeedPercent(speed),
                angle
            )
            return True
        except Exception as e:
            logging.error(f"Horizontal rotation failed: {str(e)}")
            return False
    
    def rotate_vertical(self, angle, speed=SCAN_SPEED):
        """Rotate vertical motor by specified angle"""
        try:
            self.vertical_motor.on_for_degrees(
                SpeedPercent(speed),
                angle
            )
            return True
        except Exception as e:
            logging.error(f"Vertical rotation failed: {str(e)}")
            return False
            
    def move_scanner(self, position, speed=SCAN_SPEED):
        """Move scanner to specified position"""
        try:
            self.scanner_motor.on_to_position(
                SpeedPercent(speed),
                position
            )
            return True
        except Exception as e:
            logging.error(f"Scanner movement failed: {str(e)}")
            return False
