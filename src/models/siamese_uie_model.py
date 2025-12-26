"""
SiameseUIE模型调用模块
使用ModelScope的SiameseUIE模型进行实体抽取
支持命名实体识别、关系抽取、事件抽取、属性情感抽取等多种任务
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks


class SiameseUIEModel:
    """SiameseUIE模型封装类，支持多种信息抽取任务"""
    
    def __init__(self, model_path: str, use_model_id: bool = False):
        """
        初始化SiameseUIE模型
        
        Args:
            model_path: 模型路径，可以是本地路径或ModelScope模型ID
                       模型ID格式: 'damo/nlp_structbert_siamese-uie_chinese-base'
            use_model_id: 是否使用ModelScope模型ID（如果为True，则从ModelScope下载模型）
        """
        self.use_model_id = use_model_id
        
        if use_model_id:
            # 使用ModelScope模型ID
            self.model_path = model_path
            print(f"正在从ModelScope加载模型: {self.model_path}")
        else:
            # 使用本地模型路径
            self.model_path = Path(model_path)
            if not self.model_path.exists():
                raise FileNotFoundError(f"模型路径不存在: {model_path}")
            
            # 转换为绝对路径
            self.model_path = str(self.model_path.absolute())
            print(f"正在加载本地模型: {self.model_path}")
        
        # 初始化pipeline
        try:
            self.pipeline = pipeline(
                Tasks.siamese_uie,
                self.model_path,
                model_revision='master'
            )
            print("模型加载成功！")
        except Exception as e:
            error_msg = f"模型加载失败: {str(e)}"
            print(f"错误详情: {error_msg}")
            import traceback
            traceback.print_exc()
            raise Exception(error_msg)
    
    def extract_entities(self, text: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        从文本中抽取实体（支持多种抽取任务）
        
        支持的schema格式：
        1. 命名实体识别: {"人物": None, "地理位置": None, "组织机构": None}
        2. 关系抽取: {"人物": {"比赛项目(赛事名称)": None, "参赛地点(城市)": None}}
        3. 事件抽取: {"胜负(事件触发词)": {"时间": None, "败者": None, "胜者": None}}
        4. 属性情感抽取: {"属性词": {"情感词": None}}
        
        Args:
            text: 输入文本
            schema: 实体抽取schema，格式参考README示例
            
        Returns:
            抽取结果字典，包含:
            - text: 原始文本
            - entities: 抽取的实体结果
            - error: 错误信息（如果有）
        
        示例:
            # 命名实体识别
            result = model.extract_entities(
                text='1944年毕业于北大的名古屋铁道会长谷口清太郎等人在日本积极筹资。',
                schema={'人物': None, '地理位置': None, '组织机构': None}
            )
            
            # 关系抽取
            result = model.extract_entities(
                text='在北京冬奥会自由式中，中国选手谷爱凌获得金牌。',
                schema={'人物': {'比赛项目(赛事名称)': None, '参赛地点(城市)': None}}
            )
        """
        if not text or not text.strip():
            return {"text": text, "entities": {}}
        
        if not schema:
            return {"text": text, "entities": {}, "error": "schema不能为空"}
        
        try:
            # 按照README示例的方式调用pipeline
            result = self.pipeline(input=text, schema=schema)
            return {
                "text": text,
                "entities": result if result else {}
            }
        except Exception as e:
            error_msg = f"实体抽取出错: {str(e)}"
            print(f"错误详情: {error_msg}")
            import traceback
            traceback.print_exc()
            return {
                "text": text,
                "entities": {},
                "error": error_msg
            }

