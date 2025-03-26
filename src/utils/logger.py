import os
import sys
from loguru import logger

def setup_logger(config):
    """
    设置日志记录器
    
    Args:
        config: 日志配置字典
    """
    # 获取日志配置
    log_level = config.get('level', 'INFO')
    log_file = config.get('file', 'logs/app.log')
    rotation = config.get('rotation', '10 MB')
    retention = config.get('retention', '1 month')
    
    # 确保日志目录存在
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 移除默认处理器
    logger.remove()
    
    # 添加控制台处理器
    logger.add(sys.stderr, level=log_level)
    
    # 添加文件处理器
    logger.add(
        log_file,
        level=log_level,
        rotation=rotation,
        retention=retention,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        encoding="utf-8"
    )
    
    logger.info("日志系统初始化完成")
    return logger
