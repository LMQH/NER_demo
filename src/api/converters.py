"""
格式转换工具函数
用于将不同模型的返回结果转换为统一格式
"""
from typing import Dict, Any, Optional, List
from src.constants import (
    DEFAULT_EBUSINESS_ID, DEFAULT_SUCCESS_CODE, DEFAULT_ERROR_CODE,
    DEFAULT_SUCCESS_REASON, DEFAULT_ERROR_REASON, DEFAULT_ENTITY_MAPPING,
    ENTITY_TYPE_PROVINCE, ENTITY_TYPE_CITY, ENTITY_TYPE_DISTRICT,
    ENTITY_TYPE_STREET, ENTITY_TYPE_ROAD, ENTITY_TYPE_UNIT_ADDRESS,
    ENTITY_TYPE_NUMBER_ENG, ENTITY_TYPE_OTHER, PHONE_PATTERN, CHINESE_NAME_PATTERN
)
from src.utils.address_parser import AddressParser
from src.utils.entity_extractor import EntityExtractor


def convert_mgeo_tagging_to_qwen_flash_format(mgeo_result: Dict[str, Any], original_text: str = "") -> Dict[str, Any]:
    """
    将 mgeo_geographic_elements_tagging_chinese_base 模型的返回结果转换为规定格式
    
    新模型的实体类型映射：
    - prov -> ProvinceName (省)
    - city -> CityName (市)
    - district -> ExpAreaName (区/县)
    - town -> StreetName (街道/镇)
    - road -> Address (路)
    - road_number -> Address (路号)
    - poi -> Address (POI)
    - house_number -> Address (门牌号)
    - other -> 其他信息（用于提取电话和姓名）
    
    Args:
        mgeo_result: mgeo_geographic_elements_tagging_chinese_base 模型的返回结果
        original_text: 原始输入文本（用于提取电话和姓名）
    
    Returns:
        qwen-flash 格式的结果
    """
    # 检查是否是已包装的格式（包含 EBusinessID 和 Data）
    if "EBusinessID" in mgeo_result and "Data" in mgeo_result:
        # 从 Data 中提取 entities 和 text
        data = mgeo_result.get("Data", {})
        entities_data = data.get("entities", {})
        text = data.get("text", original_text)
        ebusiness_id = mgeo_result.get("EBusinessID", "1279441")
        success = mgeo_result.get("Success", True)
        reason = mgeo_result.get("Reason", "解析成功")
        result_code = mgeo_result.get("ResultCode", "100")
    else:
        # 直接格式，从根级别提取
        entities_data = mgeo_result.get("entities", {})
        text = mgeo_result.get("text", original_text)
        ebusiness_id = "1279441"
        success = True
        reason = "解析成功"
        result_code = "100"
    
    # 初始化结果
    result = _create_default_result(ebusiness_id, success, reason, result_code)
    
    # 检查是否有错误
    if "error" in mgeo_result or not success:
        result["Success"] = False
        result["Reason"] = mgeo_result.get("error", reason if not success else DEFAULT_ERROR_REASON)
        result["ResultCode"] = DEFAULT_ERROR_CODE
        return result
    
    # 获取实体列表
    entities = entities_data.get("output", [])
    
    if not entities:
        return result
    
    # 按实体类型分类
    province = ""
    city = ""
    district = ""
    street = ""
    address_entities = []
    other_entities = []
    
    # 按 start 位置排序，确保顺序正确
    sorted_entities = sorted(entities, key=lambda x: x.get("start", 0))
    
    for entity in sorted_entities:
        entity_type = entity.get("type", "")
        span = entity.get("span", "")
        
        # 新模型的实体类型映射
        if entity_type == "prov":
            province = span
        elif entity_type == "city":
            city = span
        elif entity_type == "district":
            district = span
        elif entity_type == "town":
            street = span
        elif entity_type in ["road", "road_number", "poi", "house_number"]:
            # 这些类型都归入详细地址
            address_entities.append(entity)
        elif entity_type == "other":
            other_entities.append(span)
    
    # 填充地址信息
    result["Data"]["ProvinceName"] = province
    result["Data"]["CityName"] = city
    result["Data"]["ExpAreaName"] = district
    result["Data"]["StreetName"] = street
    
    # 按位置顺序组合详细地址
    if address_entities:
        address_entities_sorted = sorted(address_entities, key=lambda x: x.get("start", 0))
        address_parts = [entity.get("span", "") for entity in address_entities_sorted]
        result["Data"]["Address"] = "".join(address_parts)
    
    # 从原始文本中提取电话和姓名
    _extract_phone_and_name_from_mgeo(
        result, other_entities, sorted_entities, original_text or text
    )
    
    return result


def convert_mgeo_to_qwen_flash_format(mgeo_result: Dict[str, Any], original_text: str = "") -> Dict[str, Any]:
    """
    将 mgeo 模型的返回结果转换为规定格式
    
    Args:
        mgeo_result: mgeo 模型的返回结果，可能是两种格式:
            格式1（直接返回）:
                {
                    "text": "...",
                    "entities": {
                        "output": [
                            {"type": "PB", "start": 0, "end": 3, "prob": ..., "span": "广东省"},
                            ...
                        ]
                    }
                }
            格式2（已包装）:
                {
                    "EBusinessID": "1279441",
                    "Data": {
                        "entities": {"output": [...]},
                        "text": "..."
                    },
                    "Success": true,
                    "Reason": "解析成功",
                    "ResultCode": "100"
                }
        original_text: 原始输入文本（用于提取电话和姓名）
    
    Returns:
        qwen-flash 格式的结果:
        {
            "EBusinessID": "1279441",
            "Data": {
                "ProvinceName": "广东省",
                "StreetName": "坂田街道",
                "Address": "长坑路西2巷2号202",
                "CityName": "深圳市",
                "ExpAreaName": "龙岗区",
                "Mobile": "18273778575",
                "Name": "黄大大"
            },
            "Success": true,
            "Reason": "解析成功",
            "ResultCode": "100"
        }
    """
    # 检查是否是已包装的格式（包含 EBusinessID 和 Data）
    if "EBusinessID" in mgeo_result and "Data" in mgeo_result:
        # 从 Data 中提取 entities 和 text
        data = mgeo_result.get("Data", {})
        entities_data = data.get("entities", {})
        text = data.get("text", original_text)
        ebusiness_id = mgeo_result.get("EBusinessID", "1279441")
        success = mgeo_result.get("Success", True)
        reason = mgeo_result.get("Reason", "解析成功")
        result_code = mgeo_result.get("ResultCode", "100")
    else:
        # 直接格式，从根级别提取
        entities_data = mgeo_result.get("entities", {})
        text = mgeo_result.get("text", original_text)
        ebusiness_id = "1279441"
        success = True
        reason = "解析成功"
        result_code = "100"
    
    # 初始化结果
    result = _create_default_result(ebusiness_id, success, reason, result_code)
    
    # 检查是否有错误
    if "error" in mgeo_result or not success:
        result["Success"] = False
        result["Reason"] = mgeo_result.get("error", reason if not success else DEFAULT_ERROR_REASON)
        result["ResultCode"] = DEFAULT_ERROR_CODE
        return result
    
    # 获取实体列表
    entities = entities_data.get("output", [])
    
    if not entities:
        return result
    
    # 按实体类型分类
    province = ""
    city = ""
    district = ""
    street = ""
    address_entities = []
    other_entities = []
    
    # 按 start 位置排序，确保顺序正确
    sorted_entities = sorted(entities, key=lambda x: x.get("start", 0))
    
    for entity in sorted_entities:
        entity_type = entity.get("type", "")
        span = entity.get("span", "")
        
        if entity_type == ENTITY_TYPE_PROVINCE:
            province = span
        elif entity_type == ENTITY_TYPE_CITY:
            city = span
        elif entity_type == ENTITY_TYPE_DISTRICT:
            district = span
        elif entity_type == ENTITY_TYPE_STREET:
            street = span
        elif entity_type in [ENTITY_TYPE_ROAD, ENTITY_TYPE_UNIT_ADDRESS, ENTITY_TYPE_NUMBER_ENG]:
            address_entities.append(entity)
        elif entity_type == ENTITY_TYPE_OTHER:
            other_entities.append(span)
    
    # 填充地址信息
    result["Data"]["ProvinceName"] = province
    result["Data"]["CityName"] = city
    result["Data"]["ExpAreaName"] = district
    result["Data"]["StreetName"] = street
    
    # 按位置顺序组合详细地址
    if address_entities:
        address_entities_sorted = sorted(address_entities, key=lambda x: x.get("start", 0))
        address_parts = [entity.get("span", "") for entity in address_entities_sorted]
        result["Data"]["Address"] = "".join(address_parts)
    
    # 从原始文本中提取电话和姓名
    _extract_phone_and_name_from_mgeo(
        result, other_entities, sorted_entities, original_text or text
    )
    
    return result


def parse_chinese_address(address_text: str) -> Dict[str, str]:
    """
    使用正则表达式和规则解析中文地址字符串
    
    将完整的地址字符串（如"广东省深圳市龙岗区坂田街道长坑路西2巷2号202"）
    分解为省、市、区、街道、详细地址等部分
    
    Args:
        address_text: 完整的地址字符串
    
    Returns:
        包含省、市、区、街道、详细地址的字典
    """
    return AddressParser.parse_chinese_address(address_text)


def convert_ner_to_address_format(
    ner_result: Dict[str, Any], 
    original_text: str = "",
    output_schema: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    将 macbert 和 siameseUIE 模型的 NER 结果转换为规定格式
    
    Args:
        ner_result: NER 模型的返回结果，格式:
            {
                "text": "...",
                "entities": {
                    "output": [
                        [{"type": "人物", "span": "张三", "offset": [0, 2]}],
                        [{"type": "地理位置", "span": "广东省", "offset": [3, 6]}],
                        ...
                    ]
                }
            }
            或者:
            {
                "text": "...",
                "entities": {
                    "人物": [{"text": "张三", "start": 0, "end": 2}],
                    "地理位置": [{"text": "广东省", "start": 3, "end": 6}],
                    ...
                }
            }
        original_text: 原始输入文本（用于提取电话和姓名）
        output_schema: 输出格式映射配置（从entity_config.json中读取）
    
    Returns:
        统一格式的结果:
        {
            "EBusinessID": "1279441",
            "Data": {
                "ProvinceName": "广东省",
                "StreetName": "坂田街道",
                "Address": "长坑路西2巷2号202",
                "CityName": "深圳市",
                "ExpAreaName": "龙岗区",
                "Mobile": "18273778575",
                "Name": "黄大大"
            },
            "Success": true,
            "Reason": "解析成功",
            "ResultCode": "100"
        }
    """
    # 初始化结果
    result = _create_default_result()
    
    # 检查是否有错误
    if "error" in ner_result:
        result["Success"] = False
        result["Reason"] = ner_result.get("error", DEFAULT_ERROR_REASON)
        result["ResultCode"] = DEFAULT_ERROR_CODE
        return result
    
    # 获取文本
    text = ner_result.get("text", original_text) or original_text
    
    # 获取实体数据
    entities_data = ner_result.get("entities", {})
    
    # 解析实体列表（支持两种格式）
    entity_list = EntityExtractor.parse_entity_list(entities_data, text)
    
    # 如果没有实体，尝试从文本中提取基本信息
    if not entity_list:
        phone = EntityExtractor.extract_phone_from_text(text)
        if phone:
            result["Data"]["Mobile"] = phone
        return result
    
    # 加载输出schema配置（如果提供）
    mapping_config = {}
    if output_schema and "mapping" in output_schema:
        mapping_config = output_schema["mapping"]
    else:
        mapping_config = DEFAULT_ENTITY_MAPPING
    
    # 按实体类型和模式分类实体
    classified = EntityExtractor.classify_entities(entity_list, mapping_config)
    
    # 检查是否有大的地理位置实体（包含多个地址层级）
    large_location_entity = EntityExtractor.find_large_location_entity(
        entity_list, mapping_config
    )
    
    # 如果找到了大的地理位置实体，使用地址解析函数
    if large_location_entity:
        parsed_address = AddressParser.parse_chinese_address(large_location_entity)
        result["Data"]["ProvinceName"] = parsed_address.get("province", "")
        result["Data"]["CityName"] = parsed_address.get("city", "")
        result["Data"]["ExpAreaName"] = parsed_address.get("district", "")
        result["Data"]["StreetName"] = parsed_address.get("street", "")
        result["Data"]["Address"] = parsed_address.get("address", "")
    else:
        # 使用分类后的实体填充地址信息
        _fill_address_from_classified_entities(result, classified, entity_list, mapping_config)
    
    # 提取姓名和电话
    address_ranges = EntityExtractor.get_address_ranges(entity_list, mapping_config)
    name = EntityExtractor.extract_name_from_entities(
        classified["person"], text, address_ranges
    )
    if name:
        result["Data"]["Name"] = name
    
    phone = EntityExtractor.extract_phone_from_text(text)
    if phone:
        result["Data"]["Mobile"] = phone
    
    return result


def _create_default_result(
    ebusiness_id: str = DEFAULT_EBUSINESS_ID,
    success: bool = True,
    reason: str = DEFAULT_SUCCESS_REASON,
    result_code: str = DEFAULT_SUCCESS_CODE
) -> Dict[str, Any]:
    """创建默认格式的结果字典"""
    return {
        "EBusinessID": ebusiness_id,
        "Data": {
            "ProvinceName": "",
            "StreetName": "",
            "Address": "",
            "CityName": "",
            "ExpAreaName": "",
            "Mobile": "",
            "Name": ""
        },
        "Success": success,
        "Reason": reason,
        "ResultCode": result_code
    }


def _fill_address_from_classified_entities(
    result: Dict[str, Any],
    classified: Dict[str, List[Dict[str, Any]]],
    entity_list: List[Dict[str, Any]],
    mapping_config: Dict[str, Any]
) -> None:
    """从分类后的实体中填充地址信息"""
    # 填充地址信息（取第一个匹配的实体）
    if classified["province"]:
        classified["province"].sort(key=lambda x: x.get("start", 0))
        result["Data"]["ProvinceName"] = classified["province"][0].get("span", "")
    
    if classified["city"]:
        classified["city"].sort(key=lambda x: x.get("start", 0))
        result["Data"]["CityName"] = classified["city"][0].get("span", "")
    
    if classified["district"]:
        classified["district"].sort(key=lambda x: x.get("start", 0))
        result["Data"]["ExpAreaName"] = classified["district"][0].get("span", "")
    
    if classified["street"]:
        classified["street"].sort(key=lambda x: x.get("start", 0))
        result["Data"]["StreetName"] = classified["street"][0].get("span", "")
    
    # 组合详细地址（按位置排序）
    if classified["address"]:
        classified["address"].sort(key=lambda x: x.get("start", 0))
        address_parts = [entity.get("span", "") for entity in classified["address"]]
        result["Data"]["Address"] = "".join(address_parts)
    
    # 如果某些字段仍然为空，尝试从地理位置实体中解析
    if not result["Data"]["ProvinceName"] or not result["Data"]["CityName"]:
        for entity in entity_list:
            entity_type = entity.get("type", "")
            span = entity.get("span", "")
            entity_types = mapping_config.get("ProvinceName", {}).get("entity_types", [])
            if entity_type in entity_types:
                parsed = AddressParser.parse_chinese_address(span)
                if parsed["province"] and not result["Data"]["ProvinceName"]:
                    result["Data"]["ProvinceName"] = parsed["province"]
                if parsed["city"] and not result["Data"]["CityName"]:
                    result["Data"]["CityName"] = parsed["city"]
                if parsed["district"] and not result["Data"]["ExpAreaName"]:
                    result["Data"]["ExpAreaName"] = parsed["district"]
                if parsed["street"] and not result["Data"]["StreetName"]:
                    result["Data"]["StreetName"] = parsed["street"]
                if parsed["address"] and not result["Data"]["Address"]:
                    result["Data"]["Address"] = parsed["address"]
                break


def _extract_phone_and_name_from_mgeo(
    result: Dict[str, Any],
    other_entities: List[str],
    sorted_entities: List[Dict[str, Any]],
    text: str
) -> None:
    """从MGeo模型的other_entities中提取电话和姓名"""
    import re
    from src.constants import PHONE_PATTERN, CHINESE_NAME_PATTERN, ADDRESS_KEYWORDS
    
    # 首先尝试从 other_entities 中识别
    for entity_text in other_entities:
        if re.match(PHONE_PATTERN, entity_text):
            result["Data"]["Mobile"] = entity_text
        elif re.match(CHINESE_NAME_PATTERN, entity_text):
            result["Data"]["Name"] = entity_text
    
    # 如果从 other_entities 中没有找到，尝试从原始文本中提取
    if not result["Data"]["Mobile"]:
        phone = EntityExtractor.extract_phone_from_text(text)
        if phone:
            result["Data"]["Mobile"] = phone
    
    if not result["Data"]["Name"]:
        # 找到所有地址实体的位置范围
        address_ranges = []
        for entity in sorted_entities:
            entity_type = entity.get("type", "")
            if entity_type in [
                ENTITY_TYPE_PROVINCE, ENTITY_TYPE_CITY, ENTITY_TYPE_DISTRICT,
                ENTITY_TYPE_STREET, ENTITY_TYPE_ROAD, ENTITY_TYPE_UNIT_ADDRESS,
                ENTITY_TYPE_NUMBER_ENG
            ]:
                start = entity.get("start", 0)
                end = entity.get("end", 0)
                address_ranges.append((start, end))
        
        # 在非地址部分查找姓名
        name = AddressParser.find_name_in_non_address_text(text, address_ranges)
        if name:
            result["Data"]["Name"] = name

