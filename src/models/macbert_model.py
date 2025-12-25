"""
MacBERT模型调用模块
使用chinese-macbert-base模型进行实体抽取
支持命名实体识别任务（基于规则方法）
"""
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple
import torch
from transformers import AutoTokenizer, AutoModel
import re


class MacBERTModel:
    """MacBERT模型封装类，支持命名实体识别任务"""
    
    def __init__(self, model_path: str):
        """
        初始化MacBERT模型
        
        Args:
            model_path: 模型路径（本地路径）
        """
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"模型路径不存在: {model_path}")
        
        self.model_path = str(self.model_path.absolute())
        print(f"正在加载MacBERT模型: {self.model_path}")
        
        try:
            # 加载tokenizer和model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModel.from_pretrained(self.model_path)
            self.model.eval()  # 设置为评估模式
            
            # 检查是否有GPU
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            
            print(f"MacBERT模型加载成功！使用设备: {self.device}")
        except Exception as e:
            error_msg = f"MacBERT模型加载失败: {str(e)}"
            print(f"错误详情: {error_msg}")
            import traceback
            traceback.print_exc()
            raise Exception(error_msg)
    
    def extract_entities(self, text: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        从文本中抽取实体
        
        注意：由于chinese-macbert-base是基础BERT模型，未经过NER任务微调，
        这里使用基于特征提取和规则的方法进行实体抽取。
        
        Args:
            text: 输入文本
            schema: 实体抽取schema，格式: {"实体类型": None}
            
        Returns:
            抽取结果字典，格式与SiameseUIE保持一致
        """
        if not text or not text.strip():
            return {"text": text, "entities": {}}
        
        if not schema:
            return {"text": text, "entities": {}, "error": "schema不能为空"}
        
        try:
            # 获取实体类型列表
            entity_types = [key for key in schema.keys() if schema[key] is None]
            
            if not entity_types:
                # 如果schema是关系抽取格式，返回空结果
                return {
                    "text": text,
                    "entities": {"output": []}
                }
            
            # 使用基于规则和特征的方法进行实体抽取
            results = self._extract_entities_with_rules(text, entity_types)
            
            # 转换为与SiameseUIE一致的格式
            output = []
            for entity_type, entities in results.items():
                for entity_text, start, end in entities:
                    output.append([{
                        "type": entity_type,
                        "span": entity_text,
                        "offset": [start, end]
                    }])
            
            return {
                "text": text,
                "entities": {"output": output}
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
    
    def _extract_entities_with_rules(self, text: str, entity_types: List[str]) -> Dict[str, List[Tuple[str, int, int]]]:
        """
        使用规则和特征提取方法进行实体抽取
        
        Args:
            text: 输入文本
            entity_types: 实体类型列表
            
        Returns:
            字典，key为实体类型，value为(实体文本, 起始位置, 结束位置)的列表
        """
        results = {}
        
            # 定义一些常见的实体识别规则（可以根据需要扩展）
        entity_patterns = {
            "人物": [
                r'[A-Za-z\u4e00-\u9fa5]{2,6}(?:先生|女士|老师|教授|博士|主任|经理|总|长|主任|部长|局长|市长|省长|主席|总理|总统|委员|代表|委员长)',
                r'[A-Za-z\u4e00-\u9fa5]{2,6}(?:等|等人)',
                r'[A-Za-z\u4e00-\u9fa5]{2,6}(?:选手|运动员|队员|成员)',
            ],
            "地理位置": [
                r'[A-Za-z\u4e00-\u9fa5]+(?:省|市|县|区|镇|村|街道|路|街|大道|广场|公园|山|河|湖|海|岛|港|湾|江|河)',
                r'[A-Za-z\u4e00-\u9fa5]+(?:国|州|邦|地区)',
                r'[A-Za-z\u4e00-\u9fa5]+(?:城|市|县|区)',
            ],
            "组织机构": [
                r'[A-Za-z\u4e00-\u9fa5]+(?:公司|集团|企业|银行|学校|大学|学院|医院|研究所|研究院|中心|协会|组织|政府|部门|委员会|局|部|处|科|办|署)',
                r'[A-Za-z\u4e00-\u9fa5]+(?:有限公司|股份有限公司|有限责任公司|集团)',
                r'[A-Za-z\u4e00-\u9fa5]+(?:铁道|铁路|航空|航空|运输|通信|科技|技术|工程)',
            ],
            "时间": [
                r'\d{4}年\d{1,2}月\d{1,2}日',
                r'\d{4}年\d{1,2}月',
                r'\d{4}年',
                r'\d{1,2}月\d{1,2}日',
                r'今天|明天|昨天|前天|后天',
                r'上午|下午|晚上|凌晨|中午',
                r'[上中下]午\d{1,2}点',
            ],
            "事件": [
                r'[A-Za-z\u4e00-\u9fa5]+(?:会议|比赛|活动|事件|事故|战争|冲突|谈判|协议|合作|项目|计划|方案)',
                r'[A-Za-z\u4e00-\u9fa5]+(?:会|赛|节|展|演)',
            ],
        }
        
        # 为每个实体类型查找匹配
        for entity_type in entity_types:
            entities = []
            
            # 使用预定义规则
            if entity_type in entity_patterns:
                for pattern in entity_patterns[entity_type]:
                    matches = re.finditer(pattern, text)
                    for match in matches:
                        entity_text = match.group(0)
                        start = match.start()
                        end = match.end()
                        entities.append((entity_text, start, end))
            
            # 去重（保留最长的匹配）
            if entities:
                # 按位置排序
                entities.sort(key=lambda x: (x[1], -len(x[0])))
                unique_entities = []
                seen_positions = set()
                
                for entity_text, start, end in entities:
                    # 检查是否与已有实体重叠
                    overlap = False
                    for seen_start, seen_end in seen_positions:
                        if not (end <= seen_start or start >= seen_end):
                            overlap = True
                            break
                    
                    if not overlap:
                        unique_entities.append((entity_text, start, end))
                        seen_positions.add((start, end))
                
                results[entity_type] = unique_entities
            else:
                results[entity_type] = []
        
        return results
    
    def _extract_with_model_features(self, text: str, entity_types: List[str]) -> Dict[str, List[Tuple[str, int, int]]]:
        """
        使用模型特征提取进行实体抽取（可选的高级方法）
        
        注意：这是一个示例方法，实际效果取决于模型是否经过NER微调
        如果模型未经过NER微调，效果可能不理想
        
        Args:
            text: 输入文本
            entity_types: 实体类型列表
            
        Returns:
            字典，key为实体类型，value为(实体文本, 起始位置, 结束位置)的列表
        """
        # 这里可以实现基于模型特征提取的方法
        # 例如：使用模型的隐藏层输出进行序列标注
        # 由于chinese-macbert-base未经过NER微调，这里暂时返回空结果
        # 如果需要，可以后续添加基于模型特征的抽取逻辑
        
        results = {}
        for entity_type in entity_types:
            results[entity_type] = []
        
        return results
    
    def extract_from_files(self, files_content: Dict[str, str], schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        从多个文件内容中抽取实体
        
        Args:
            files_content: 文件内容字典，key为文件名，value为文件内容
            schema: 实体抽取schema
            
        Returns:
            抽取结果字典，key为文件名，value为抽取结果
        """
        results = {}
        for filename, content in files_content.items():
            print(f"正在处理文件: {filename}")
            results[filename] = self.extract_entities(content, schema)
        return results

