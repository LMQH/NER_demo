"""
NER Demo核心业务逻辑模块

本模块提供NERDemo类，包含实体抽取的核心业务逻辑。
现在项目使用FastAPI服务模式（app.py），不再使用命令行脚本模式。
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from .config_manager import ConfigManager
from .file_reader import FileReader
from .siamese_uie_model import SiameseUIEModel


class NERDemo:
    """
    NER Demo核心业务类
    
    提供文件处理和实体抽取的核心功能。
    注意：现在推荐使用FastAPI服务（app.py）进行API调用，而不是直接使用此类。
    """
    
    def __init__(self):
        """初始化NER Demo"""
        self.config_manager = ConfigManager()
        self.file_reader = FileReader()
        self.ner_model = None
        self.entity_schema = None
        
        # 初始化模型
        self._init_model()
        
        # 加载实体配置
        self._load_entity_config()
    
    def _init_model(self):
        """初始化SiameseUIE模型"""
        model_path = self.config_manager.get_model_path()
        print(f"模型路径: {model_path}")
        
        try:
            self.ner_model = SiameseUIEModel(model_path)
        except Exception as e:
            raise Exception(f"模型初始化失败: {str(e)}")
    
    def _load_entity_config(self):
        """加载实体配置"""
        try:
            self.entity_schema = self.config_manager.load_entity_config()
            print(f"实体配置加载成功: {list(self.entity_schema.keys())}")
        except Exception as e:
            raise Exception(f"实体配置加载失败: {str(e)}")
    
    def process_files(self, files_content: Dict[str, str]) -> Dict[str, Any]:
        """
        处理文件内容字典
        
        Args:
            files_content: 文件内容字典，key为文件名，value为文件内容
        
        Returns:
            处理结果字典
        """
        if not files_content:
            print("没有文件需要处理")
            return {}
        
        print(f"开始处理 {len(files_content)} 个文件")
        
        # 进行实体抽取
        results = self.ner_model.extract_from_files(files_content, self.entity_schema)
        
        return results
    
    def save_results(self, results: Dict[str, Any], output_path: str = None) -> str:
        """
        保存结果到指定路径或返回JSON字符串
        
        Args:
            results: 处理结果字典
            output_path: 输出文件路径，如果为None则返回JSON字符串
            
        Returns:
            输出文件路径或JSON字符串
        """
        # 生成输出数据结构
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_data = {
            "timestamp": timestamp,
            "entity_schema": self.entity_schema,
            "files_count": len(results),
            "results": results
        }
        
        if output_path:
            # 保存到文件
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n结果已保存到: {output_file}")
            return str(output_file)
        else:
            # 返回JSON字符串
            return json.dumps(output_data, ensure_ascii=False, indent=2)
