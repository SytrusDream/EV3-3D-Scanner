"""
Main program for EV3 3D scanner system - Automated Version
"""
import logging
import time
from utils.logger import setup_logger
from sensor_init import SensorController
from motor_control import MotorController
from data_acquisition import DataAcquisition
from config import *

class ScannerSystem:
    def __init__(self):
        # Setup logging
        self.logger = setup_logger()
        
        try:
            # Initialize controllers
            self.sensor_ctrl = SensorController()
            self.motor_ctrl = MotorController()
            self.data_acq = DataAcquisition(self.sensor_ctrl, self.motor_ctrl)
            
            logging.info("Scanner system initialized successfully")
            
        except Exception as e:
            logging.error(f"System initialization failed: {str(e)}")
            raise
    
    def perform_test_scan(self):
        """Perform a test scan and process the collected data"""
        try:
            logging.info("Starting test scan...")
            
            # Reset system
            self.motor_ctrl.reset_motors()
            self.sensor_ctrl.reset_gyro()
            
            # Perform a simple horizontal scan
            test_data = self.data_acq.collect_plane_scan(0, 180, HORIZONTAL_STEP)
            
            if test_data:
                logging.info(f"Test scan completed. Collected {len(test_data)} points")
                
                # 初始化数据处理器
                preprocessor = DataPreprocessor()
                reconstructor = StaticReconstructor()
                validator = ValidationUtils()
                
                # 数据预处理
                # 1. 转换坐标系
                cartesian_points = preprocessor.convert_to_cartesian(test_data)
                # 2. 移除异常值
                cleaned_points = preprocessor.remove_outliers(cartesian_points)
                # 3. 应用中值滤波
                filtered_points = preprocessor.apply_median_filter(cleaned_points)
                
                # 重建处理
                reconstructor.set_point_cloud(filtered_points)
                # 1. 估计法向量
                normals = reconstructor.estimate_normals()
                # 2. 计算表面密度
                densities = reconstructor.compute_surface_density()
                # 3. 检测特征点
                features = reconstructor.detect_features()
                
                # 验证结果
                bbox_min = np.min([[p['x'], p['y'], p['z']] for p in filtered_points], axis=0)
                bbox_max = np.max([[p['x'], p['y'], p['z']] for p in filtered_points], axis=0)
                coverage = validator.compute_coverage(filtered_points, bbox_min, bbox_max)
                
                logging.info(f"Processing completed:")
                logging.info(f"- Original points: {len(test_data)}")
                logging.info(f"- Processed points: {len(filtered_points)}")
                logging.info(f"- Coverage: {coverage:.2%}")
                logging.info(f"- Feature points detected: {len(features) if features else 0}")
                
                return {
                    'raw_data': test_data,
                    'processed_points': filtered_points,
                    'normals': normals,
                    'features': features,
                    'coverage': coverage
                }
            else:
                logging.warning("No data collected during test scan")
                return None
                
        except Exception as e:
            logging.error(f"Test scan failed: {str(e)}")
            return None
    
    def shutdown(self):
        """Safely shutdown the system"""
        try:
            # Reset to home position
            self.motor_ctrl.reset_motors()
            logging.info("System shutdown completed")
        except Exception as e:
            logging.error(f"Shutdown failed: {str(e)}")

def main():
    try:
        # 初始化性能监控
        performance_monitor = PerformanceMonitor()
        performance_monitor.start_monitoring()
        
        # 创建所有必要的组件
        sensor_ctrl = SensorController()
        motor_ctrl = MotorController()
        data_acq = DataAcquisition(sensor_ctrl, motor_ctrl)
        preprocessor = DataPreprocessor()
        reconstructor = StaticReconstructor()
        coverage_detector = CoverageDetector()
        path_planner = PathPlanner()
        scan_optimizer = ScanOptimizer(coverage_detector, path_planner)
        data_fusion = DataFusion()
        
        # 创建系统控制器
        system_controller = SystemController(
            sensor_ctrl, motor_ctrl, data_acq,
            preprocessor, reconstructor, coverage_detector,
            path_planner, scan_optimizer, data_fusion
        )
        
        # 运行自动化扫描
        scan_data = system_controller.run_automated_scan()
        
        # 运行系统测试
        system_tester = SystemTester(system_controller)
        test_results = system_tester.run_component_tests()
        stability_results = system_tester.run_stability_test(duration=300)  # 5分钟稳定性测试
        
        # 停止性能监控并生成报告
        performance_monitor.stop_monitoring()
        performance_report = performance_monitor.generate_report()
        
        if scan_data:
            # 保存结果和测试报告
            logging.info("Saving scan results...")
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 保存点云数据
            output_file = f'scans/scan_{timestamp}.txt'
            os.makedirs('scans', exist_ok=True)
            
            with open(output_file, 'w') as f:
                for point in scan_data:
                    f.write(f"{point['x']},{point['y']},{point['z']}\n")
            
            # 保存测试报告
            report_file = f'reports/report_{timestamp}.txt'
            os.makedirs('reports', exist_ok=True)
            
            with open(report_file, 'w') as f:
                f.write(performance_report)
                f.write("\nTest Results:\n")
                f.write(str(test_results))
                f.write("\nStability Results:\n")
                f.write(str(stability_results))
            
            logging.info("Scan results and test reports saved successfully")
        
    except Exception as e:
        logging.error(f"Main program failed: {str(e)}")

if __name__ == "__main__":
    main()
