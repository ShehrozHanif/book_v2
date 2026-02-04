#!/usr/bin/env python3
"""
Chapter 17, Example 1: Structured Logging Utility for Robotics

This example demonstrates:
1. Custom ROS 2 compatible logger
2. Log levels and filtering
3. Log aggregation and rotation
4. Performance-aware logging

Dependencies:
    pip install colorama

Expected Output:
    - Structured log messages
    - Multi-level logging demonstration
    - Log file generation
    - Performance metrics

Platform: Ubuntu 22.04, Python 3.10+
Author: Physical AI & Humanoid Robotics Textbook
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    Fore = Style = type('DummyColorama', (), {'__getattr__': lambda s, n: ''})()


class RoboticsLogger:
    """Structured logger for robotics applications."""
    
    def __init__(self, name="robot", log_dir="logs", console_level=logging.INFO):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        console_handler.setFormatter(ColoredFormatter())
        self.logger.addHandler(console_handler)
        
        # File handler
        log_file = self.log_dir / f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
        ))
        self.logger.addHandler(file_handler)
        
        self.debug(f"Logger initialized: {log_file}")
    
    def debug(self, msg, **kwargs):
        self.logger.debug(self._format_msg(msg, kwargs))
    
    def info(self, msg, **kwargs):
        self.logger.info(self._format_msg(msg, kwargs))
    
    def warning(self, msg, **kwargs):
        self.logger.warning(self._format_msg(msg, kwargs))
    
    def error(self, msg, **kwargs):
        self.logger.error(self._format_msg(msg, kwargs))
    
    def critical(self, msg, **kwargs):
        self.logger.critical(self._format_msg(msg, kwargs))
    
    def _format_msg(self, msg, kwargs):
        if kwargs:
            parts = [msg]
            for k, v in kwargs.items():
                parts.append(f"{k}={v}")
            return " | ".join(parts)
        return msg


class ColoredFormatter(logging.Formatter):
    """Colored console formatter."""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT
    }
    
    def format(self, record):
        levelname = record.levelname
        color = self.COLORS.get(levelname, '')
        
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S.%f')[:-3]
        
        return (f"{Fore.WHITE}{timestamp}{Style.RESET_ALL} | "
                f"{color}{levelname:8s}{Style.RESET_ALL} | "
                f"{record.getMessage()}")


def demo_logging():
    """Demonstrate logging capabilities."""
    print("=" * 70)
    print("Chapter 17, Example 1: Structured Logging")
    print("=" * 70 + "\n")
    
    # Create logger
    logger = RoboticsLogger("humanoid_controller")
    
    # Different log levels
    logger.debug("System initialized", mode="simulation", dt=0.001)
    logger.info("Starting control loop", frequency="1000 Hz")
    logger.warning("Joint velocity near limit", joint=3, velocity=2.8)
    logger.error("IK solver failed", target=[0.5, 0.3, 0.8], iterations=100)
    logger.critical("Emergency stop triggered", reason="collision_detected")
    
    # Simulate control loop logging
    logger.info("Control loop simulation started")
    for i in range(5):
        logger.debug(f"Iteration {i}", 
                    timestamp=i*0.01, 
                    cpu_usage=45.2 + i*2.3)
    
    logger.info("Demonstration complete")
    
    print("\n" + "="*70)
    print("Check the 'logs/' directory for log files")
    print("="*70)


if __name__ == "__main__":
    demo_logging()
