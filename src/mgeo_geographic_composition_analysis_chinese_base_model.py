"""
MGeo地理组成分析模型调用模块
使用ModelScope的MGeo地理组成分析模型进行地理实体抽取和分析
支持地理组成分析、地理实体识别等任务
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks


class MGeoGeographicCompositionAnalysisModel:
    """MGeo地理组成分析模型封装类，支持地理组成分析任务"""
    
    def __init__(self, model_path: str, use_model_id: bool = False):
        """
        初始化MGeo地理组成分析模型
        
        Args:
            model_path: 模型路径，可以是本地路径或ModelScope模型ID
                       模型ID格式: 'damo/mgeo_geographic_composition_analysis_chinese_base'
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
            # MGeo模型使用token-classification任务
            # 根据README: task = Tasks.token_classification
            task_type = Tasks.token_classification
            
            # 检查transformers版本兼容性
            try:
                import transformers
                transformers_version = transformers.__version__
                print(f"当前transformers版本: {transformers_version}")
                
                # MGeo模型可能需要较老的transformers版本（根据README推荐）
                # 如果版本过新，给出警告
                major, minor = map(int, transformers_version.split('.')[:2])
                if major > 4 or (major == 4 and minor > 20):
                    print("警告: MGeo模型可能需要transformers 4.20.x或更早版本")
                    print("如果遇到导入错误，请尝试降级transformers:")
                    print("  pip install transformers==4.20.1")
            except Exception:
                pass
            
            # 优先使用ModelScope模型ID（让ModelScope处理版本兼容性）
            model_id = 'damo/mgeo_geographic_composition_analysis_chinese_base'
            
            if self.use_model_id:
                # 直接使用ModelScope模型ID
                print(f"使用ModelScope模型ID加载: {model_id}")
                self.pipeline = pipeline(
                    task_type,
                    model_id,
                    model_revision='master'
                )
                print("模型加载成功！")
            else:
                # 使用本地路径，但先尝试ModelScope模型ID作为备选
                try:
                    print(f"尝试使用ModelScope模型ID加载: {model_id}")
                    self.pipeline = pipeline(
                        task_type,
                        model_id,
                        model_revision='master'
                    )
                    print("使用ModelScope模型ID加载成功！")
                except Exception as e1:
                    # 如果ModelScope模型ID失败，尝试使用本地路径
                    print(f"ModelScope模型ID加载失败: {str(e1)}")
                    print(f"尝试使用本地路径加载: {self.model_path}")
                    self.pipeline = pipeline(
                        task_type,
                        self.model_path,
                        model_revision='master'
                    )
                    print("使用本地路径加载成功！")
        except Exception as e:
            error_msg = f"模型加载失败: {str(e)}"
            print(f"\n错误详情: {error_msg}")
            
            # 检查是否是transformers版本兼容性问题
            if "configuration_bert" in str(e) or "No module named" in str(e):
                print("\n" + "="*60)
                print("检测到transformers版本兼容性问题！")
                print("="*60)
                print("\n解决方案:")
                print("1. 降级transformers到兼容版本:")
                print("   pip install transformers==4.20.1")
                print("\n2. 或者使用ModelScope模型ID（设置use_model_id=True）")
                print("   让ModelScope自动处理版本兼容性")
                print("\n3. 参考模型README中的版本要求:")
                print("   model/mgeo_geographic_composition_analysis_chinese_base/README.md")
                print("="*60)
            
            import traceback
            traceback.print_exc()
            raise Exception(error_msg)
    
    def extract_entities(self, text: str, schema: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        从文本中抽取地理实体（支持地理组成分析任务）
        
        注意：MGeo模型是token-classification任务，不需要schema参数。
        schema参数保留是为了接口兼容性，但会被忽略。
        
        Args:
            text: 输入文本（地址query，如"浙江省杭州市余杭区阿里巴巴西溪园区"）
            schema: 实体抽取schema（可选，MGeo模型不使用此参数，保留仅为接口兼容）
            
        Returns:
            抽取结果字典，包含:
            - text: 原始文本
            - entities: 抽取的实体结果，格式为:
              {
                "output": [
                  {"type": "PB", "start": 0, "end": 3, "span": "浙江省"},
                  {"type": "PC", "start": 3, "end": 6, "span": "杭州市"},
                  ...
                ]
              }
            - error: 错误信息（如果有）
        
        示例:
            # 地理组成分析（地址成分分析）
            result = model.extract_entities(
                text='浙江省杭州市余杭区阿里巴巴西溪园区'
            )
            
            # 输出示例:
            # {
            #   "text": "浙江省杭州市余杭区阿里巴巴西溪园区",
            #   "entities": {
            #     "output": [
            #       {"type": "PB", "start": 0, "end": 3, "span": "浙江省"},
            #       {"type": "PC", "start": 3, "end": 6, "span": "杭州市"},
            #       {"type": "PD", "start": 6, "end": 9, "span": "余杭区"},
            #       {"type": "Entity", "start": 9, "end": 17, "span": "阿里巴巴西溪园区"}
            #     ]
            #   }
            # }
        """
        if not text or not text.strip():
            return {"text": text, "entities": {}}
        
        try:
            # MGeo模型使用token-classification任务，只需要input参数
            # 根据README示例：pipeline_ins(input=inputs)
            result = self.pipeline(input=text)
            
            # 将numpy类型转换为Python原生类型（解决Pydantic序列化问题）
            def convert_numpy_types(obj):
                """递归转换numpy类型为Python原生类型"""
                import numpy as np
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, dict):
                    return {key: convert_numpy_types(value) for key, value in obj.items()}
                elif isinstance(obj, (list, tuple)):
                    return [convert_numpy_types(item) for item in obj]
                else:
                    return obj
            
            # 转换结果中的numpy类型
            result = convert_numpy_types(result)
            
            # 确保返回格式一致
            if result and isinstance(result, dict):
                return {
                    "text": text,
                    "entities": result
                }
            else:
                return {
                    "text": text,
                    "entities": {"output": result} if result else {}
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

