"""
Validation and testing utilities for the reconstruction
"""
import numpy as np
import logging
from scipy.spatial.distance import directed_hausdorff

class ValidationUtils:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def compute_coverage(self, points, bbox_min, bbox_max, grid_size=20):
        """
        计算点云的空间覆盖率
        """
        try:
            # 创建体素网格
            x = np.linspace(bbox_min[0], bbox_max[0], grid_size)
            y = np.linspace(bbox_min[1], bbox_max[1], grid_size)
            z = np.linspace(bbox_min[2], bbox_max[2], grid_size)
            
            # 统计每个体素中的点数
            total_voxels = grid_size ** 3
            occupied_voxels = 0
            
            points_array = np.array([[p['x'], p['y'], p['z']] for p in points])
            
            for i in range(grid_size-1):
                for j in range(grid_size-1):
                    for k in range(grid_size-1):
                        # 检查体素中是否有点
                        mask = (points_array[:, 0] >= x[i]) & (points_array[:, 0] < x[i+1]) & \
                               (points_array[:, 1] >= y[j]) & (points_array[:, 1] < y[j+1]) & \
                               (points_array[:, 2] >= z[k]) & (points_array[:, 2] < z[k+1])
                        
                        if np.any(mask):
                            occupied_voxels += 1
            
            coverage = occupied_voxels / total_voxels
            return coverage
            
        except Exception as e:
            self.logger.error(f"Coverage computation failed: {str(e)}")
            return None
    
    def compute_point_cloud_metrics(self, points1, points2):
        """
        计算两个点云之间的相似度指标
        """
        try:
            array1 = np.array([[p['x'], p['y'], p['z']] for p in points1])
            array2 = np.array([[p['x'], p['y'], p['z']] for p in points2])
            
            # 计算Hausdorff距离
            hausdorff_dist = directed_hausdorff(array1, array2)[0]
            
            # 计算平均距离
            tree = KDTree(array2)
            distances, _ = tree.query(array1)
            mean_dist = np.mean(distances)
            
            return {
                'hausdorff_distance': hausdorff_dist,
                'mean_distance': mean_dist
            }
            
        except Exception as e:
            self.logger.error(f"Metrics computation failed: {str(e)}")
            return None
