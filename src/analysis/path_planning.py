"""
Scanning path planning and optimization
"""
import numpy as np
from scipy.optimize import minimize
import logging
from config import *

class PathPlanner:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def calculate_view_score(self, viewpoint, target, normal=None):
        """
        计算视点对目标点的观测分数
        """
        try:
            # 计算视线方向
            view_dir = target - viewpoint
            distance = np.linalg.norm(view_dir)
            view_dir = view_dir / distance
            
            # 基础分数（基于距离）
            score = 1.0 / (1.0 + distance)
            
            # 如果有法向量信息，考虑观测角度
            if normal is not None:
                angle = np.arccos(np.clip(np.dot(view_dir, normal), -1.0, 1.0))
                angle_score = np.cos(angle)
                score *= max(0, angle_score)
            
            return score
            
        except Exception as e:
            self.logger.error(f"View score calculation failed: {str(e)}")
            return 0.0
    
    def optimize_viewpoint(self, target, constraints, normal=None):
        """
        优化单个目标点的观测视点
        """
        try:
            # 定义目标函数（最大化观测分数）
            def objective(x):
                return -self.calculate_view_score(x, target, normal)
            
            # 定义约束（机器人运动范围）
            bounds = [
                (constraints['x_min'], constraints['x_max']),
                (constraints['y_min'], constraints['y_max']),
                (constraints['z_min'], constraints['z_max'])
            ]
            
            # 从多个初始点开始优化
            best_score = float('-inf')
            best_viewpoint = None
            
            for _ in range(5):  # 尝试多个随机初始点
                x0 = np.random.uniform(
                    [b[0] for b in bounds],
                    [b[1] for b in bounds]
                )
                
                result = minimize(
                    objective,
                    x0,
                    bounds=bounds,
                    method='L-BFGS-B'
                )
                
                if result.success and -result.fun > best_score:
                    best_score = -result.fun
                    best_viewpoint = result.x
            
            return best_viewpoint, best_score
            
        except Exception as e:
            self.logger.error(f"Viewpoint optimization failed: {str(e)}")
            return None, None
    
    def plan_scanning_path(self, holes, robot_constraints):
        """
        规划扫描路径以覆盖检测到的空洞区域
        """
        try:
            viewpoints = []
            
            # 对每个空洞区域规划观测点
            for hole in holes:
                target = np.array(hole['center'])
                
                # 优化视点位置
                viewpoint, score = self.optimize_viewpoint(
                    target,
                    robot_constraints
                )
                
                if viewpoint is not None and score > 0.1:  # 设置最小分数阈值
                    viewpoints.append({
                        'position': viewpoint.tolist(),
                        'target': target.tolist(),
                        'score': score
                    })
            
            # 对视点进行排序和优化
            if viewpoints:
                # 按分数排序
                viewpoints.sort(key=lambda x: x['score'], reverse=True)
                
                # 移除冗余视点（如果两个视点太近且观察相同区域）
                filtered_viewpoints = []
                used_targets = set()
                
                for vp in viewpoints:
                    target_key = tuple(map(lambda x: round(x, 3), vp['target']))
                    if target_key not in used_targets:
                        filtered_viewpoints.append(vp)
                        used_targets.add(target_key)
                
                return filtered_viewpoints
            
            return []
            
        except Exception as e:
            self.logger.error(f"Path planning failed: {str(e)}")
            return None

    def generate_scanning_sequence(self, viewpoints):
        """
        生成优化的扫描序列，考虑机器人运动成本
        """
        try:
            if not viewpoints:
                return []
            
            # 使用简单的贪心算法
            sequence = [0]  # 从第一个视点开始
            unvisited = set(range(1, len(viewpoints)))
            current = 0
            
            while unvisited:
                # 找到距离当前位置最近的未访问视点
                current_pos = np.array(viewpoints[current]['position'])
                min_dist = float('inf')
                next_point = None
                
                for i in unvisited:
                    pos = np.array(viewpoints[i]['position'])
                    dist = np.linalg.norm(pos - current_pos)
                    
                    if dist < min_dist:
                        min_dist = dist
                        next_point = i
                
                sequence.append(next_point)
                unvisited.remove(next_point)
                current = next_point
            
            # 返回优化后的视点序列
            return [viewpoints[i] for i in sequence]
            
        except Exception as e:
            self.logger.error(f"Sequence generation failed: {str(e)}")
            return None
