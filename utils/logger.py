"""
Logging utility for the EV3 3D scanner system
"""
import logging
import os
import datetime
from config import LOG_LEVEL

def setup_logger():
    """Setup and configure logging"""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Generate log filename with timestamp
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f'logs/scanner_{timestamp}.log'
    
    # Configure logging
    logging.basicConfig(
        level=LOG_LEVEL,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logging.info('Logging system initialized')
    return logging.getLogger()
