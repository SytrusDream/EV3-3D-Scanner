"""
Detection of missing areas in scanned point cloud
"""
import numpy as np
from sklearn.neighbors import KDTree
import logging
from config import *

class CoverageDetector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def create_visibility_map(self, points, resolution=0.05):
        """
        创建扫描区域的可见性地图
        """
        try:
            # 计算边界框
            coords = np.array([[p['x'], p['y'], p['z']] for p in points])
            min_bounds = np.min(coords, axis=0)
            max_bounds = np.max(coords, axis=0)
            
            # 创建体素网格
            x_range = np.arange(min_bounds[0], max_bounds[0], resolution)
            y_range = np.arange(min_bounds[1], max_bounds[1], resolution)
            z_range = np.arange(min_bounds[2], max_bounds[2], resolution)
            
            # 构建KD树用于快速邻域搜索
            tree = KDTree(coords)
            
            visibility_map = {}
            for x in x_range:
                for y in y_range:
                    for z in z_range:
                        point = np.array([x, y, z])
                        # 检查邻域内的点数
                        indices = tree.query_radius([point], r=resolution*2)[0]
                        visibility_map[(x,y,z)] = len(indices)
            
            return visibility_map
            
        except Exception as e:
            self.logger.error(f"Visibility map creation failed: {str(e)}")
            return None
    
    def detect_holes(self, visibility_map, threshold=3):
        """
        检测点云中的空洞区域
        """
        try:
            holes = []
            for pos, count in visibility_map.items():
                if count < threshold:
                    holes.append({
                        'position': pos,
                        'density': count
                    })
            
            # 对空洞区域进行聚类
            if holes:
                positions = np.array([h['position'] for h in holes])
                tree = KDTree(positions)
                
                # 使用基于密度的聚类
                clusters = []
                processed = set()
                
                for i, pos in enumerate(positions):
                    if i in processed:
                        continue
                        
                    # 获取临近的空洞点
                    indices = tree.query_radius([pos], r=threshold*0.1)[0]
                    if len(indices) >= 3:  # 最小聚类大小
                        clusters.append({
                            'center': np.mean(positions[indices], axis=0),
                            'size': len(indices),
                            'points': positions[indices].tolist()
                        })
                        processed.update(indices)
            
            return clusters
            
        except Exception as e:
            self.logger.error(f"Hole detection failed: {str(e)}")
            return None
