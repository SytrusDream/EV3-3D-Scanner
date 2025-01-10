"""
Basic data acquisition and processing
包含基础数据采集和处理功能
"""
import time
import logging
import numpy as np
from config import *

class DataAcquisition:
    def __init__(self, sensor_controller, motor_controller):
        self.sensor_ctrl = sensor_controller
        self.motor_ctrl = motor_controller
        self.scan_data = []
        
    def single_point_scan(self):
        """Collect data for a single point"""
        try:
            distance = self.sensor_ctrl.get_distance()
            if distance is not None:
                angle_h = self.motor_ctrl.horizontal_motor.position
                angle_v = self.motor_ctrl.vertical_motor.position
                
                point_data = {
                    'distance': distance,
                    'angle_h': angle_h,
                    'angle_v': angle_v,
                    'timestamp': time.time()
                }
                return point_data
            return None
        except Exception as e:
            logging.error(f"Single point scan failed: {str(e)}")
            return None
    
    def collect_plane_scan(self, start_angle, end_angle, step=HORIZONTAL_STEP):
        """Collect data for a horizontal plane"""
        scan_data = []
        current_angle = start_angle
        
        while current_angle <= end_angle:
            # Move to position
            self.motor_ctrl.rotate_horizontal(current_angle)
            time.sleep(0.1)  # 稳定等待
            
            # Collect data
            point_data = self.single_point_scan()
            if point_data:
                scan_data.append(point_data)
            
            current_angle += step
            
        return scan_data
    
    def filter_data(self, data, window_size=FILTER_WINDOW):
        """Simple moving average filter for distance data"""
        try:
            distances = [d['distance'] for d in data]
            kernel = np.ones(window_size) / window_size
            filtered_distances = np.convolve(distances, kernel, mode='valid')
            
            filtered_data = []
            for i, dist in enumerate(filtered_distances):
                filtered_point = data[i].copy()
                filtered_point['distance'] = dist
                filtered_data.append(filtered_point)
                
            return filtered_data
        except Exception as e:
            logging.error(f"Data filtering failed: {str(e)}")
            return data
