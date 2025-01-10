"""
Comprehensive system testing framework
"""
import time
import logging
import numpy as np
from datetime import datetime
from config import *

class SystemTester:
    def __init__(self, system_controller):
        self.logger = logging.getLogger(__name__)
        self.system_ctrl = system_controller
        self.test_results = {}
        
    def run_component_tests(self):
        """
        测试各个组件的功能
        """
        test_results = {
            'sensor_tests': self.test_sensors(),
            'motor_tests': self.test_motors(),
            'scan_tests': self.test_scanning(),
            'processing_tests': self.test_processing()
        }
        
        return test_results
    
    def test_sensors(self):
        """
        测试传感器功能
        """
        try:
            results = {'status': 'passed', 'details': []}
            
            # 测试超声波传感器
            distance = self.system_ctrl.sensor_ctrl.get_distance()
            if distance is None:
                results['details'].append("Ultrasonic sensor test failed")
                results['status'] = 'failed'
            
            # 测试陀螺仪
            angle = self.system_ctrl.sensor_ctrl.get_angle()
            if angle is None:
                results['details'].append("Gyro sensor test failed")
                results['status'] = 'failed'
                
            return results
            
        except Exception as e:
            self.logger.error(f"Sensor testing failed: {str(e)}")
            return {'status': 'error', 'details': [str(e)]}
    
    def test_motors(self):
        """
        测试电机功能
        """
        try:
            results = {'status': 'passed', 'details': []}
            
            # 测试水平旋转
            if not self.system_ctrl.motor_ctrl.rotate_horizontal(90):
                results['details'].append("Horizontal rotation test failed")
                results['status'] = 'failed'
            
            # 测试垂直旋转
            if not self.system_ctrl.motor_ctrl.rotate_vertical(45):
                results['details'].append("Vertical rotation test failed")
                results['status'] = 'failed'
                
            # 重置位置
            self.system_ctrl.motor_ctrl.reset_motors()
            
            return results
            
        except Exception as e:
            self.logger.error(f"Motor testing failed: {str(e)}")
            return {'status': 'error', 'details': [str(e)]}
    
    def test_scanning(self):
        """
        测试扫描功能
        """
        try:
            results = {'status': 'passed', 'details': []}
            
            # 执行简单扫描
            scan_data = self.system_ctrl.data_acq.single_point_scan()
            if not scan_data:
                results['details'].append("Single point scan test failed")
                results['status'] = 'failed'
            
            return results
            
        except Exception as e:
            self.logger.error(f"Scanning testing failed: {str(e)}")
            return {'status': 'error', 'details': [str(e)]}
    
    def test_processing(self):
        """
        测试数据处理功能
        """
        try:
            results = {'status': 'passed', 'details': []}
            
            # 生成测试数据
            test_data = [
                {'distance': 100, 'angle_h': 0, 'angle_v': 0, 'timestamp': time.time()},
                {'distance': 110, 'angle_h': 10, 'angle_v': 0, 'timestamp': time.time()},
                {'distance': 90, 'angle_h': 20, 'angle_v': 0, 'timestamp': time.time()}
            ]
            
            # 测试数据处理
            processed_data = self.system_ctrl.process_scan_data(test_data)
            if not processed_data:
                results['details'].append("Data processing test failed")
                results['status'] = 'failed'
            
            return results
            
        except Exception as e:
            self.logger.error(f"Processing testing failed: {str(e)}")
            return {'status': 'error', 'details': [str(e)]}
    
    def run_stability_test(self, duration=300):  # 5分钟测试
        """
        运行系统稳定性测试
        """
        try:
            start_time = time.time()
            results = {
                'start_time': datetime.now().isoformat(),
                'duration': duration,
                'scans_completed': 0,
                'errors_occurred': 0,
                'events': []
            }
            
            while (time.time() - start_time) < duration:
                try:
                    # 执行扫描
                    scan_data = self.system_ctrl.data_acq.single_point_scan()
                    if scan_data:
                        results['scans_completed'] += 1
                    else:
                        results['errors_occurred'] += 1
                        results['events'].append({
                            'time': datetime.now().isoformat(),
                            'type': 'error',
                            'message': 'Scan failed'
                        })
                    
                    # 移动电机
                    self.system_ctrl.motor_ctrl.rotate_horizontal(10)
                    time.sleep(0.5)
                    
                except Exception as e:
                    results['errors_occurred'] += 1
                    results['events'].append({
                        'time': datetime.now().isoformat(),
                        'type': 'error',
                        'message': str(e)
                    })
            
            results['end_time'] = datetime.now().isoformat()
            return results
            
        except Exception as e:
            self.logger.error(f"Stability testing failed: {str(e)}")
            return None
