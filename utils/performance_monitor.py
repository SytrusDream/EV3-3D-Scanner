"""
System performance monitoring and analysis
"""
import time
import psutil
import logging
from datetime import datetime
from collections import deque

class PerformanceMonitor:
    def __init__(self, history_size=1000):
        self.logger = logging.getLogger(__name__)
        self.history_size = history_size
        
        # 性能指标历史记录
        self.cpu_history = deque(maxlen=history_size)
        self.memory_history = deque(maxlen=history_size)
        self.scan_time_history = deque(maxlen=history_size)
        self.processing_time_history = deque(maxlen=history_size)
        
        self.start_time = None
        self.is_monitoring = False
    
    def start_monitoring(self):
        """
        开始性能监控
        """
        self.start_time = time.time()
        self.is_monitoring = True
        self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """
        停止性能监控
        """
        self.is_monitoring = False
        self.logger.info("Performance monitoring stopped")
    
    def record_metrics(self, metric_type, value):
        """
        记录性能指标
        """
        if not self.is_monitoring:
            return
            
        timestamp = time.time()
        
        if metric_type == 'cpu':
            self.cpu_history.append((timestamp, value))
        elif metric_type == 'memory':
            self.memory_history.append((timestamp, value))
        elif metric_type == 'scan_time':
            self.scan_time_history.append((timestamp, value))
        elif metric_type == 'processing_time':
            self.processing_time_history.append((timestamp, value))
    
    def get_system_metrics(self):
        """
        获取系统性能指标
        """
        try:
            if not self.is_monitoring:
                return None
                
            metrics = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'timestamp': time.time()
            }
            
            self.record_metrics('cpu', metrics['cpu_percent'])
            self.record_metrics('memory', metrics['memory_percent'])
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {str(e)}")
            return None
    
    def analyze_performance(self):
        """
        分析性能数据
        """
        try:
            if not self.is_monitoring:
                return None
                
            analysis = {
                'duration': time.time() - self.start_time,
                'cpu': {
                    'average': np.mean([x[1] for x in self.cpu_history]),
                    'max': max([x[1] for x in self.cpu_history]),
                    'min': min([x[1] for x in self.cpu_history])
                },
                'memory': {
                    'average': np.mean([x[1] for x in self.memory_history]),
                    'max': max([x[1] for x in self.memory_history]),
                    'min': min([x[1] for x in self.memory_history])
                },
                'scan_time': {
                    'average': np.mean([x[1] for x in self.scan_time_history]),
                    'max': max([x[1] for x in self.scan_time_history]),
                    'min': min([x[1] for x in self.scan_time_history])
                },
                'processing_time': {
                    'average': np.mean([x[1] for x in self.processing_time_history]),
                    'max': max([x[1] for x in self.processing_time_history]),
                    'min': min([x[1] for x in self.processing_time_history])
                }
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Performance analysis failed: {str(e)}")
            return None
    
    def generate_report(self):
        """
        生成性能报告
        """
        try:
            analysis = self.analyze_performance()
            if not analysis:
                return None
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'duration': f"{analysis['duration']:.2f} seconds",
                'performance_metrics': {
                    'cpu_utilization': {
                        'average': f"{analysis['cpu']['average']:.1f}%",
                        'peak': f"{analysis['cpu']['max']:.1f}%"
                    },
                    'memory_usage': {
                        'average': f"{analysis['memory']['average']:.1f}%",
                        'peak': f"{analysis['memory']['max']:.1f}%"
                    },
                    'scanning_performance': {
                        'average_scan_time': f"{analysis['scan_time']['average']:.3f}s",
                        'max_scan_time': f"{analysis['scan_time']['max']:.3f}s"
                    },
                    'processing_performance': {
                        'average_processing_time': f"{analysis['processing_time']['average']:.3f}s",
                        'max_processing_time': f"{analysis['processing_time']['max']:.3f}s"
                    }
                },
                'recommendations': []
            }
            
            # 添加性能建议
            if analysis['cpu']['average'] > 80:
                report['recommendations'].append(
                    "CPU utilization is high. Consider optimizing processing algorithms."
                )
            if analysis['memory']['average'] > 80:
                report['recommendations'].append(
                    "Memory usage is high. Consider implementing data streaming or reducing batch size."
                )
            if analysis['scan_time']['average'] > 2.0:
                report['recommendations'].append(
                    "Scan times are longer than expected. Check sensor and motor performance."
                )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {str(e)}")
            return None
