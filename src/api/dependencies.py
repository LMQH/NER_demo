"""
API 依赖项
用于依赖注入
"""
from fastapi import Depends
from src.model_manager import ModelManager
from src.file_reader import FileReader
from src.config_manager import ConfigManager
from pathlib import Path

# 这些将在 app.py 中初始化
_model_manager: ModelManager = None
_file_reader: FileReader = None
_config_manager: ConfigManager = None
_project_root: Path = None


def init_dependencies(model_manager: ModelManager, file_reader: FileReader, 
                     config_manager: ConfigManager, project_root: Path):
    """初始化依赖项"""
    global _model_manager, _file_reader, _config_manager, _project_root
    _model_manager = model_manager
    _file_reader = file_reader
    _config_manager = config_manager
    _project_root = project_root


def get_model_manager() -> ModelManager:
    """获取模型管理器"""
    return _model_manager


def get_file_reader() -> FileReader:
    """获取文件读取器"""
    return _file_reader


def get_config_manager() -> ConfigManager:
    """获取配置管理器"""
    return _config_manager


def get_project_root() -> Path:
    """获取项目根目录"""
    return _project_root

