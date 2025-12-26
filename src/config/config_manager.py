"""
配置管理模块
处理实体配置
"""
import os
import json
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, entity_config_path: str = None):
        """
        初始化配置管理器
        
        Args:
            entity_config_path: 实体配置文件路径，如果为None则使用默认路径
        """
        # 默认实体配置文件路径
        default_config_path = Path(__file__).parent.parent / 'entity_config.json'
        self.entity_config_path = Path(entity_config_path) if entity_config_path else default_config_path
        self.config = {}
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置项（保留接口兼容性）"""
        return self.config.get(key, default)
    
    def load_entity_config(self) -> Dict[str, Any]:
        """
        加载实体配置文件
        
        Returns:
            实体配置字典
        """
        if not self.entity_config_path.exists():
            # 如果配置文件不存在，返回空配置
            return {}
        
        try:
            with open(self.entity_config_path, 'r', encoding='utf-8') as f:
                entity_config = json.load(f)
            
            return entity_config.get('entities', {})
        except Exception as e:
            # 如果加载失败，返回空配置
            return {}
    
    def get_model_path(self) -> str:
        """
        获取模型基础路径
        
        从环境变量 MODEL_PATH 读取，如果未设置则返回默认值 'model/'
        注意：此方法返回的是模型存储的基础目录，具体模型选择由接口参数控制
        
        Returns:
            模型基础路径（相对于项目根目录）
        """
        # 从环境变量读取 MODEL_PATH
        model_path = os.getenv('MODEL_PATH')
        
        if model_path:
            # 确保路径以 / 结尾（如果路径不为空）
            model_path = model_path.strip()
            if model_path and not model_path.endswith('/') and not model_path.endswith('\\'):
                model_path = model_path + '/'
            return model_path
        
        # 返回默认基础路径
        return 'model/'

