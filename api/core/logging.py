"""
日志配置
"""
import logging
import sys
from pathlib import Path

from tradingagents.utils.logging_manager import get_logger


def setup_logging():
    """设置日志"""
    logger = get_logger('api')
    return logger


logger = setup_logging()

