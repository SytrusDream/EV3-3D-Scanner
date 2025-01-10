"""
Basic 3D reconstruction from processed point cloud data
"""
import numpy as np
from sklearn.neighbors import KDTree
import logging

class StaticReconstructor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.point_cloud = None
        self.kdtree = None
    
    def set_point_cloud(self, points):
        """
        设置点云数据并构建KD树用于近邻搜索
        """
        try:
            self.point_cloud = np.array([[p['x'], p['y'], p['z']] for p in points])
            self.kdtree = KDTree(self.point_cloud)
            return True
        except Exception as e:
            self.logger.error(f"Point cloud initialization failed: {str(e)}")
            return False
    
    def estimate_normals(self, k_neighbors=10):
        """
        估计每个点的法向量
        """
        try:
            if self.point_cloud is None or self.kdtree is None:
                raise ValueError("Point cloud not initialized")
            
            normals = []
            for point in self.point_cloud:
                # 找到临近点
                distances, indices = self.kdtree.query([point], k=k_neighbors)
                neighbors = self.point_cloud[indices[0]]
                
                # 计算协方差矩阵
                centered = neighbors - np.mean(neighbors, axis=0)
                cov = np.dot(centered.T, centered)
                
                # 使用SVD求法向量
                _, _, vh = np.linalg.svd(cov)
                normal = vh[2]
                normals.append(normal)
            
            return np.array(normals)
            
        except Exception as e:
            self.logger.error(f"Normal estimation failed: {str(e)}")
            return None
    
    def compute_surface_density(self, radius=0.1):
        """
        计算点云的表面密度
        """
        try:
            if self.point_cloud is None or self.kdtree is None:
                raise ValueError("Point cloud not initialized")
            
            densities = []
            for point in self.point_cloud:
                # 统计给定半径内的点数
                count = len(self.kdtree.query_radius([point], r=radius)[0])
                density = count / (4/3 * np.pi * radius**3)
                densities.append(density)
            
            return np.array(densities)
            
        except Exception as e:
            self.logger.error(f"Density computation failed: {str(e)}")
            return None

    def detect_features(self, min_neighbors=5, radius=0.1):
        """
        检测点云中的特征点（如边缘或角点）
        """
        try:
            if self.point_cloud is None or self.kdtree is None:
                raise ValueError("Point cloud not initialized")
            
            features = []
            for i, point in enumerate(self.point_cloud):
                # 获取邻域点
                indices = self.kdtree.query_radius([point], r=radius)[0]
                
                if len(indices) < min_neighbors:
                    continue
                
                neighbors = self.point_cloud[indices]
                
                # 计算主曲率
                centered = neighbors - np.mean(neighbors, axis=0)
                cov = np.dot(centered.T, centered)
                eigenvalues = np.linalg.eigvals(cov)
                eigenvalues.sort()
                
                # 使用特征值比例判断是否为特征点
                if eigenvalues[0] / eigenvalues[2] < 0.1:
                    features.append({
                        'index': i,
                        'position': point,
                        'type': 'edge' if eigenvalues[1] / eigenvalues[2] < 0.1 else 'corner'
                    })
            
            return features
            
        except Exception as e:
            self.logger.error(f"Feature detection failed: {str(e)}")
            return None
