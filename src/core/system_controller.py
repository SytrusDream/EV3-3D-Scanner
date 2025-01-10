"""
System controller for automated scanning process
"""
import time
import logging
from config import *

class SystemController:
    def __init__(self, sensor_ctrl, motor_ctrl, data_acq, 
                 preprocessor, reconstructor, coverage_detector,
                 path_planner, scan_optimizer, data_fusion):
        self.logger = logging.getLogger(__name__)
        
        # 组件初始化
        self.sensor_ctrl = sensor_ctrl
        self.motor_ctrl = motor_ctrl
        self.data_acq = data_acq
        self.preprocessor = preprocessor
        self.reconstructor = reconstructor
        self.coverage_detector = coverage_detector
        self.path_planner = path_planner
        self.scan_optimizer = scan_optimizer
        self.data_fusion = data_fusion
        
        # 系统状态
        self.is_scanning = False
        self.current_scan_data = []
        self.all_scans = []
        self.transformations = []
    
    def initialize_system(self):
        """
        初始化系统，包括所有传感器和电机的校准
        """
        try:
            self.logger.info("Initializing system...")
            
            # 重置电机位置
            self.motor_ctrl.reset_motors()
            
            # 校准传感器
            self.sensor_ctrl.reset_gyro()
            
            # 等待系统稳定
            time.sleep(1)
            
            self.logger.info("System initialization completed")
            return True
            
        except Exception as e:
            self.logger.error(f"System initialization failed: {str(e)}")
            return False
    
    def execute_scanning_sequence(self, scan_sequence):
        """
        执行扫描序列
        """
        try:
            scan_data = []
            
            for viewpoint in scan_sequence:
                # 移动到视点位置
                position = viewpoint['position']
                target = viewpoint['target']
                
                # 计算电机角度
                h_angle = np.arctan2(target[1] - position[1], target[0] - position[0])
                v_angle = np.arctan2(target[2] - position[2], 
                                   np.sqrt((target[0] - position[0])**2 + 
                                         (target[1] - position[1])**2))
                
                # 控制电机运动
                self.motor_ctrl.rotate_horizontal(np.degrees(h_angle))
                self.motor_ctrl.rotate_vertical(np.degrees(v_angle))
                
                # 等待运动完成
                time.sleep(0.5)
                
                # 采集数据
                point_data = self.data_acq.single_point_scan()
                if point_data:
                    scan_data.append(point_data)
            
            return scan_data
            
        except Exception as e:
            self.logger.error(f"Scanning sequence execution failed: {str(e)}")
            return None
    
    def run_automated_scan(self, completion_threshold=0.9, max_iterations=5):
        """
        运行自动化扫描过程
        """
        try:
            self.logger.info("Starting automated scanning process...")
            
            # 初始化系统
            if not self.initialize_system():
                return False
            
            iteration = 0
            while iteration < max_iterations:
                self.logger.info(f"Starting scan iteration {iteration + 1}")
                
                # 获取当前扫描计划
                robot_constraints = {
                    'x_min': -500, 'x_max': 500,
                    'y_min': -500, 'y_max': 500,
                    'z_min': 0, 'z_max': 500
                }
                
                scan_plan = self.scan_optimizer.generate_next_scan(
                    self.current_scan_data,
                    robot_constraints
                )
                
                if not scan_plan:
                    self.logger.info("No more scanning required")
                    break
                
                # 执行扫描
                new_scan_data = self.execute_scanning_sequence(scan_plan['viewpoints'])
                
                if not new_scan_data:
                    self.logger.error("Failed to collect scan data")
                    break
                
                # 处理新数据
                processed_data = self.process_scan_data(new_scan_data)
                
                # 注册和合并点云
                if self.current_scan_data:
                    transform, error = self.data_fusion.icp_registration(
                        processed_data,
                        self.current_scan_data
                    )
                    
                    if transform is not None:
                        self.transformations.append(transform)
                        self.all_scans.append(processed_data)
                        
                        # 合并点云
                        self.current_scan_data = self.data_fusion.merge_point_clouds(
                            self.all_scans,
                            self.transformations
                        )
                else:
                    self.current_scan_data = processed_data
                    self.all_scans.append(processed_data)
                    self.transformations.append(np.eye(4))
                
                # 检查完成度
                completion = self.scan_optimizer.estimate_completion(
                    self.current_scan_data,
                    threshold=completion_threshold
                )
                
                if completion and completion['is_complete']:
                    self.logger.info("Scanning completed successfully")
                    break
                
                iteration += 1
            
            return self.current_scan_data
            
        except Exception as e:
            self.logger.error(f"Automated scanning failed: {str(e)}")
            return None
    
    def process_scan_data(self, raw_data):
        """
        处理扫描数据
        """
        try:
            # 坐标转换
            cartesian_points = self.preprocessor.convert_to_cartesian(raw_data)
            
            # 移除异常值
            cleaned_points = self.preprocessor.remove_outliers(cartesian_points)
            
            # 应用滤波
            filtered_points = self.preprocessor.apply_median_filter(cleaned_points)
            
            return filtered_points
            
        except Exception as e:
            self.logger.error(f"Data processing failed: {str(e)}")
            return None
    
    def shutdown_system(self):
        """
        安全关闭系统
        """
        try:
            self.logger.info("Shutting down system...")
            
            # 停止所有进行中的操作
            self.is_scanning = False
            
            # 重置到安全位置
            self.motor_ctrl.reset_motors()
            
            # 等待电机停止
            time.sleep(1)
            
            self.logger.info("System shutdown completed")
            return True
            
        except Exception as e:
            self.logger.error(f"System shutdown failed: {str(e)}")
            return False
