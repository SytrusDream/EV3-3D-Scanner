"""
Data fusion and registration for multiple scans
"""
import numpy as np
from sklearn.neighbors import NearestNeighbors
import logging
from config import *

class DataFusion:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def icp_registration(self, source_points, target_points, max_iterations=50, tolerance=0.001):
        """
        使用ICP（迭代最近点）算法进行点云配准
        """
        try:
            # 转换为numpy数组
            source = np.array([[p['x'], p['y'], p['z']] for p in source_points])
            target = np.array([[p['x'], p['y'], p['z']] for p in target_points])
            
            # 初始化转换矩阵
            transformation = np.eye(4)
            
            # 创建最近邻搜索器
            nbrs = NearestNeighbors(n_neighbors=1, algorithm='kd_tree').fit(target)
            
            for iteration in range(max_iterations):
                # 找到最近邻点
                distances, indices = nbrs.kneighbors(source)
                
                # 计算质心
                source_centroid = np.mean(source, axis=0)
                target_centroid = np.mean(target[indices[:, 0]], axis=0)
                
                # 去中心化
                source_centered = source - source_centroid
                target_centered = target[indices[:, 0]] - target_centroid
                
                # 计算最优旋转
                H = np.dot(source_centered.T, target_centered)
                U, S, Vt = np.linalg.svd(H)
                R = np.dot(Vt.T, U.T)
                
                # 确保旋转矩阵是正交的
                if np.linalg.det(R) < 0:
                    Vt[-1, :] *= -1
                    R = np.dot(Vt.T, U.T)
                
                # 计算平移
                t = target_centroid - np.dot(source_centroid, R.T)
                
                # 更新源点云
                source = np.dot(source, R.T) + t
                
                # 检查收敛
                error = np.mean(distances)
                if error < tolerance:
                    break
            
            # 构建最终转换矩阵
            transformation[:3, :3] = R
            transformation[:3, 3] = t
            
            return transformation, error
            
        except Exception as e:
            self.logger.error(f"ICP registration failed: {str(e)}")
            return None, None
    
    def merge_point_clouds(self, point_clouds, transformations):
        """
        合并多个已配准的点云
        """
        try:
            merged_points = []
            
            for i, points in enumerate(point_clouds):
                # 应用转换
                transformed_points = []
                for point in points:
                    p = np.array([point['x'], point['y'], point['z'], 1.0])
                    p_transformed = np.dot(transformations[i], p)
                    transformed_points.append({
                        'x': p_transformed[0],
                        'y': p_transformed[1],
                        'z': p_transformed[2],
                        'timestamp': point['timestamp']
                    })
                
                merged_points.extend(transformed_points)
            
            # 移除重复点
            coords = np.array([[p['x'], p['y'], p['z']] for p in merged_points])
            tree = NearestNeighbors(n_neighbors=2, algorithm='kd_tree').fit(coords)
            distances, indices = tree.kneighbors(coords)
            
            # 使用集合记录要保留的点的索引
            unique_indices = set()
            for i, (dist, idx) in enumerate(zip(distances, indices)):
                if i not in unique_indices and dist[1] > 0.01:  # 距离阈值
                    unique_indices.add(i)
            
            # 返回唯一的点
            return [merged_points[i] for i in unique_indices]
            
        except Exception as e:
            self.logger.error(f"Point cloud merging failed: {str(e)}")
            return None
