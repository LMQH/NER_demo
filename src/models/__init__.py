"""
模型模块
包含所有NER模型相关的类
"""
from .siamese_uie_model import SiameseUIEModel
from .macbert_model import MacBERTModel
from .mgeo_geographic_composition_analysis_chinese_base_model import MGeoGeographicCompositionAnalysisModel
from .mgeo_geographic_elements_tagging_chinese_base_model import MGeoGeographicElementsTaggingModel
from .qwen_flash_model import QwenFlashModel

__all__ = [
    'SiameseUIEModel',
    'MacBERTModel',
    'MGeoGeographicCompositionAnalysisModel',
    'MGeoGeographicElementsTaggingModel',
    'QwenFlashModel'
]

