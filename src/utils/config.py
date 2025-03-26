import os
import yaml
from loguru import logger

class Config:
    """配置管理类，负责加载和提供配置信息"""
    
    def __init__(self, config_path=None):
        """
        初始化配置
        
        Args:
            config_path: 配置文件路径，默认为项目根目录下的config/config.yaml
        """
        if config_path is None:
            # 获取项目根目录
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_path = os.path.join(root_dir, 'config', 'config.yaml')
        
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"配置文件加载成功: {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise
    
    def get_llm_config(self, provider=None):
        """
        获取LLM配置
        
        Args:
            provider: LLM提供商名称，如果为None则使用默认提供商
            
        Returns:
            LLM配置字典
        """
        if provider is None:
            provider = self.config['llm']['default']
        
        try:
            return self.config['llm']['providers'][provider]
        except KeyError:
            logger.error(f"未找到LLM提供商配置: {provider}")
            raise ValueError(f"未找到LLM提供商配置: {provider}")
    
    def get_video_generator_config(self, provider=None):
        """
        获取视频生成模型配置
        
        Args:
            provider: 视频生成模型提供商名称，如果为None则使用默认提供商
            
        Returns:
            视频生成模型配置字典
        """
        if provider is None:
            provider = self.config['video_generator']['default']
        
        try:
            return self.config['video_generator']['providers'][provider]
        except KeyError:
            logger.error(f"未找到视频生成模型提供商配置: {provider}")
            raise ValueError(f"未找到视频生成模型提供商配置: {provider}")
    
    def get_logging_config(self):
        """获取日志配置"""
        return self.config.get('logging', {})
    
    def get_available_llm_providers(self):
        """获取所有可用的LLM提供商列表"""
        return list(self.config['llm']['providers'].keys())
    
    def get_available_video_generators(self):
        """获取所有可用的视频生成模型提供商列表"""
        return list(self.config['video_generator']['providers'].keys())
