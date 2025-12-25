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
        """获取模型路径（保留接口兼容性，返回默认值）"""
        return 'model/nlp_structbert_siamese-uie_chinese-base'

