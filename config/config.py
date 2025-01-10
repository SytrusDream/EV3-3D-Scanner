"""
Configuration file for EV3 3D scanner system
Contains all system constants and parameters
"""
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3

# Hardware Configuration
ULTRASONIC_PORT = INPUT_1
GYRO_PORT = INPUT_2

# Motor Configuration
HORIZONTAL_MOTOR_PORT = OUTPUT_A  # 水平旋转电机
VERTICAL_MOTOR_PORT = OUTPUT_B    # 垂直旋转电机
SCANNER_MOTOR_PORT = OUTPUT_C     # 传感器升降电机

# Scanning Parameters
MAX_SCAN_DISTANCE = 255  # 超声波传感器最大测量距离(mm)
MIN_SCAN_DISTANCE = 30   # 超声波传感器最小测量距离(mm)
HORIZONTAL_STEP = 5      # 水平旋转步进角度
VERTICAL_STEP = 5        # 垂直旋转步进角度
SCAN_SPEED = 50         # 电机转速(度/秒)

# Data Collection Parameters
SAMPLE_RATE = 10        # 数据采样率(Hz)
FILTER_WINDOW = 5       # 数据滤波窗口大小

# System Parameters
DEBUG_MODE = True       # 调试模式开关
LOG_LEVEL = 'INFO'      # 日志级别
