"""
配置管理模块
处理环境配置和实体配置
"""
import os
import json
from pathlib import Path
from typing import Dict, Any
from .env_loader import load_config as load_env_config


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, env_file: str = None):
        """
        初始化配置管理器
        
        Args:
            env_file: 环境配置文件路径（已废弃，现在根据域名自动加载）
        """
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """根据域名加载配置文件"""
        # 使用新的环境加载器根据域名加载配置
        env_config = load_env_config()
        
        # 将配置加载到环境变量中
        for key, value in env_config.items():
            if value is not None:
                os.environ[key] = value
        
        # 获取环境类型
        env_type = env_config.get('ENV_TYPE', 'dev_env')
        
        # 加载配置
        self.config = {
            'env_type': env_type,
            'model_path': env_config.get('MODEL_PATH', 'model/nlp_structbert_siamese-uie_chinese-base'),
            'data_dir': env_config.get('DATA_DIR', 'data'),
            'output_dir': env_config.get('OUTPUT_DIR', 'output'),
            'entity_config_path': env_config.get('ENTITY_CONFIG_PATH', 'entity_config.json'),
            'model_downloaded': env_config.get('MODEL_DOWNLOADED', 'true').lower() == 'true'
        }
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self.config.get(key, default)
    
    def load_entity_config(self) -> Dict[str, Any]:
        """
        加载实体配置文件
        
        Returns:
            实体配置字典
        """
        config_path = Path(self.config['entity_config_path'])
        if not config_path.exists():
            raise FileNotFoundError(f"实体配置文件不存在: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            entity_config = json.load(f)
        
        return entity_config.get('entities', {})
    
    def get_model_path(self) -> str:
        """获取模型路径"""
        return self.config['model_path']
    
    def get_data_dir(self) -> str:
        """获取数据目录"""
        return self.config['data_dir']
    
    def get_output_dir(self) -> str:
        """获取输出目录"""
        return self.config['output_dir']

