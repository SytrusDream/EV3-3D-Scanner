以下是 scan_optimizer.py 文件的原内容：
Python复制
"""
Optimization of scanning process
"""
import numpy as np
import logging
from config import *

class ScanOptimizer:
    def __init__(self, coverage_detector, path_planner):
        self.logger = logging.getLogger(__name__)
        self.coverage_detector = coverage_detector
        self.path_planner = path_planner
        
    def analyze_coverage(self, points):
        """
        分析当前扫描的覆盖情况
        """
        try:
            # 创建可见性地图
            visibility_map = self.coverage_detector.create_visibility_map(points)
            
            # 检测空洞
            holes = self.coverage_detector.detect_holes(visibility_map)
            
            return {
                'visibility_map': visibility_map,
                'holes': holes
            }
            
        except Exception as e:
            self.logger.error(f"Coverage analysis failed: {str(e)}")
            return None
    
    def generate_next_scan(self, current_points, robot_constraints):
        """
        生成下一次扫描的计划
        """
        try:
            # 分析当前覆盖情况
            coverage_info = self.analyze_coverage(current_points)
            
            if not coverage_info or not coverage_info['holes']:
                return None
            
            # 规划扫描路径
            viewpoints = self.path_planner.plan_scanning_path(
                coverage_info['holes'],
                robot_constraints
            )
            
            if not viewpoints:
                return None
            
            # 生成扫描序列
            scan_sequence = self.path_planner.generate_scanning_sequence(viewpoints)
            
            return {
                'viewpoints': scan_sequence,
                'holes': coverage_info['holes']
            }
            
        except Exception as e:
            self.logger.error(f"Scan generation failed: {str(e)}")
            return None
    
    def estimate_completion(self, points, threshold=0.9):
        """
        估计扫描完成度
        """
        try:
            # 分析覆盖情况
            coverage_info = self.analyze_coverage(points)
            
            if not coverage_info:
                return None
            
            # 计算完成度
            total_voxels = len(coverage_info['visibility_map'])
            covered_voxels = sum(1 for count in coverage_info['visibility_map'].values() 
                               if count > 0)
            
            completion = covered_voxels / total_voxels
            
            return {
                'completion_rate': completion,
                'is_complete': completion >= threshold,
                'uncovered_regions': len(coverage_info['holes']) if coverage_info['holes'] else 0
            }
            
        except Exception as e:
            self.logger.error(f"Completion estimation failed: {str(e)}")
            return None
