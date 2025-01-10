"""
Data preprocessing and cleaning for scanned point data
"""
import numpy as np
from scipy.signal import medfilt
import logging
from config import *

class DataPreprocessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def convert_to_cartesian(self, scan_data):
        """
        将极坐标数据转换为笛卡尔坐标系
        scan_data: 包含distance, angle_h, angle_v的点数据列表
        """
        try:
            points = []
            for point in scan_data:
                # 获取球坐标系参数
                r = point['distance']
                theta = np.radians(point['angle_h'])  # 水平角度
                phi = np.radians(point['angle_v'])    # 垂直角度
                
                # 转换为笛卡尔坐标
                x = r * np.sin(phi) * np.cos(theta)
                y = r * np.sin(phi) * np.sin(theta)
                z = r * np.cos(phi)
                
                points.append({
                    'x': x,
                    'y': y,
                    'z': z,
                    'timestamp': point['timestamp']
                })
            
            return points
        except Exception as e:
            self.logger.error(f"Coordinate conversion failed: {str(e)}")
            return None

    def remove_outliers(self, points, std_dev_threshold=2.0):
        """
        使用统计方法移除异常点
        """
        try:
            # 转换为numpy数组以便计算
            coords = np.array([[p['x'], p['y'], p['z']] for p in points])
            
            # 计算每个点到质心的距离
            centroid = np.mean(coords, axis=0)
            distances = np.sqrt(np.sum((coords - centroid) ** 2, axis=1))
            
            # 计算距离的标准差
            mean_dist = np.mean(distances)
            std_dist = np.std(distances)
            
            # 移除异常点
            mask = distances <= (mean_dist + std_dev_threshold * std_dist)
            filtered_points = [p for i, p in enumerate(points) if mask[i]]
            
            self.logger.info(f"Removed {len(points) - len(filtered_points)} outlier points")
            return filtered_points
            
        except Exception as e:
            self.logger.error(f"Outlier removal failed: {str(e)}")
            return points

    def apply_median_filter(self, points, window_size=5):
        """
        对点云数据应用中值滤波
        """
        try:
            coords = np.array([[p['x'], p['y'], p['z']] for p in points])
            
            # 对每个维度分别进行中值滤波
            filtered_coords = np.zeros_like(coords)
            for i in range(3):
                filtered_coords[:, i] = medfilt(coords[:, i], window_size)
            
            # 重建点列表
            filtered_points = []
            for i, coord in enumerate(filtered_coords):
                filtered_points.append({
                    'x': coord[0],
                    'y': coord[1],
                    'z': coord[2],
                    'timestamp': points[i]['timestamp']
                })
            
            return filtered_points
            
        except Exception as e:
            self.logger.error(f"Median filtering failed: {str(e)}")
            return points
