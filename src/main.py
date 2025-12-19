"""
NER Demo主程序
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from .config_manager import ConfigManager
from .file_reader import FileReader
from .ner_model import NERModel


class NERDemo:
    """NER Demo主类"""
    
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
        """初始化NER模型"""
        model_path = self.config_manager.get_model_path()
        print(f"模型路径: {model_path}")
        
        try:
            self.ner_model = NERModel(model_path)
        except Exception as e:
            raise Exception(f"模型初始化失败: {str(e)}")
    
    def _load_entity_config(self):
        """加载实体配置"""
        try:
            self.entity_schema = self.config_manager.load_entity_config()
            print(f"实体配置加载成功: {list(self.entity_schema.keys())}")
        except Exception as e:
            raise Exception(f"实体配置加载失败: {str(e)}")
    
    def process_files(self) -> Dict[str, Any]:
        """
        处理数据目录下的所有文件
        
        Returns:
            处理结果字典
        """
        data_dir = self.config_manager.get_data_dir()
        print(f"\n开始处理数据目录: {data_dir}")
        
        # 读取所有文件
        files_content = self.file_reader.read_all_files_in_dir(data_dir)
        
        if not files_content:
            print("数据目录下没有找到支持的文件")
            return {}
        
        print(f"找到 {len(files_content)} 个文件")
        
        # 进行实体抽取
        results = self.ner_model.extract_from_files(files_content, self.entity_schema)
        
        return results
    
    def save_results(self, results: Dict[str, Any]):
        """
        保存结果到输出目录
        
        Args:
            results: 处理结果字典
        """
        output_dir = Path(self.config_manager.get_output_dir())
        output_dir.mkdir(exist_ok=True)
        
        # 生成输出文件名（带时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"ner_results_{timestamp}.json"
        
        # 构建输出数据结构
        output_data = {
            "timestamp": timestamp,
            "entity_schema": self.entity_schema,
            "files_count": len(results),
            "results": results
        }
        
        # 保存为JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n结果已保存到: {output_file}")
        return str(output_file)


def main():
    """主函数"""
    print("=" * 60)
    print("NER Demo 启动")
    print("=" * 60)
    
    try:
        # 创建NER Demo实例
        demo = NERDemo()
        
        # 处理文件
        results = demo.process_files()
        
        if results:
            # 保存结果
            output_file = demo.save_results(results)
            print(f"\n处理完成！共处理 {len(results)} 个文件")
            print(f"结果文件: {output_file}")
        else:
            print("\n没有文件需要处理")
        
        print("=" * 60)
        print("程序执行完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

