"""
常量定义模块
集中管理项目中使用的常量
"""
from typing import Dict, List

# 模型相关常量
SUPPORTED_MODELS: Dict[str, str] = {
    'chinese-macbert-base': 'model/chinese-macbert-base',
    'nlp_structbert_siamese-uie_chinese-base': 'model/nlp_structbert_siamese-uie_chinese-base',
    'mgeo_geographic_composition_analysis_chinese_base': 'model/mgeo_geographic_composition_analysis_chinese_base',
    'qwen-flash': None  # qwen-flash不需要本地模型路径，使用API调用
}

MODEL_TYPES: Dict[str, str] = {
    'chinese-macbert-base': 'macbert',
    'nlp_structbert_siamese-uie_chinese-base': 'siamese_uie',
    'mgeo_geographic_composition_analysis_chinese_base': 'mgeo',
    'qwen-flash': 'qwen_flash'
}

# 文件扩展名
SUPPORTED_FILE_EXTENSIONS: set = {'.txt', '.md', '.docx', '.doc', '.pdf'}

# 地址相关常量
ADDRESS_KEYWORDS: List[str] = [
    '省', '市', '区', '县', '镇', '街道', '路', '街', '号', '村', '组',
    '小区', '大厦', '广场', '园区', '工业区', '开发区', '新区', '大道',
    '巷', '弄', '里', '幢', '栋', '单元', '室', '层', '自治区', '特别行政区'
]

DIRECT_CITIES: Dict[str, str] = {
    "北京市": "北京",
    "上海市": "上海",
    "天津市": "天津",
    "重庆市": "重庆"
}

# 实体类型常量
ENTITY_TYPE_PROVINCE: str = "PB"
ENTITY_TYPE_CITY: str = "PC"
ENTITY_TYPE_DISTRICT: str = "PD"
ENTITY_TYPE_STREET: str = "PF"
ENTITY_TYPE_ROAD: str = "RD"
ENTITY_TYPE_UNIT_ADDRESS: str = "UA"
ENTITY_TYPE_NUMBER_ENG: str = "NumEng"
ENTITY_TYPE_OTHER: str = "ZZ"

# 正则表达式模式
PHONE_PATTERN: str = r'1[3-9]\d{9}'
FIXED_PHONE_PATTERN: str = r'0\d{2,3}-?\d{7,8}'
CHINESE_NAME_PATTERN: str = r'^[\u4e00-\u9fa5]{2,4}$'

# 地址解析模式
PROVINCE_PATTERN: str = r'^([^省市区县]+(?:省|自治区|特别行政区))'
CITY_PATTERN: str = r'^([^省市区县]+市)'
DISTRICT_PATTERN: str = r'^([^省市区县街道镇乡]+(?:区|县))'
STREET_PATTERN: str = r'^([^省市区县街道镇乡]+(?:街道|镇|乡))'

# 响应格式常量
DEFAULT_EBUSINESS_ID: str = "1279441"
DEFAULT_SUCCESS_CODE: str = "100"
DEFAULT_ERROR_CODE: str = "103"
DEFAULT_SUCCESS_REASON: str = "解析成功"
DEFAULT_ERROR_REASON: str = "解析失败"

# 输出字段映射
OUTPUT_FIELDS = {
    "ProvinceName": "ProvinceName",
    "CityName": "CityName",
    "ExpAreaName": "ExpAreaName",
    "StreetName": "StreetName",
    "Address": "Address",
    "Mobile": "Mobile",
    "Name": "Name"
}

# 默认实体映射配置
DEFAULT_ENTITY_MAPPING = {
    "ProvinceName": {
        "entity_types": ["地理位置"],
        "patterns": ["省", "自治区", "特别行政区"]
    },
    "CityName": {
        "entity_types": ["地理位置"],
        "patterns": ["市"]
    },
    "ExpAreaName": {
        "entity_types": ["地理位置"],
        "patterns": ["区", "县"]
    },
    "StreetName": {
        "entity_types": ["地理位置"],
        "patterns": ["街道", "镇", "乡"]
    },
    "Address": {
        "entity_types": ["地理位置"],
        "patterns": ["路", "街", "大道", "巷", "号", "弄", "里"]
    },
    "Name": {
        "entity_types": ["人物"],
        "patterns": []
    }
}

