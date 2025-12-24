"""
地址补全模块
根据数据库查询数据进行地址信息的补全
"""
import os
import logging
from typing import Dict, Any, Optional
from src.db_connection import DatabaseConnection

logger = logging.getLogger("NER_API")


class AddressCompleter:
    """地址补全器"""
    
    def __init__(self, db_connection: DatabaseConnection):
        """
        初始化地址补全器
        
        Args:
            db_connection: 数据库连接对象
        """
        self.db = db_connection
        # 从环境变量获取表名，默认为region_table
        self.table_name = os.getenv('MYSQL_REGION_TABLE', 'region_table')
        # 区域类型映射（根据数据库中的region_type字段）
        # 可通过环境变量配置，格式：REGION_TYPE_PROVINCE=1001,REGION_TYPE_CITY=1002等
        # 默认值：1001=省，1002=市，1003=区/县，1004=街道/镇
        self.region_type_map = {
            'ProvinceName': int(os.getenv('REGION_TYPE_PROVINCE', '1001')),  # 省
            'CityName': int(os.getenv('REGION_TYPE_CITY', '1002')),          # 市
            'ExpAreaName': int(os.getenv('REGION_TYPE_EXP_AREA', '1003')),   # 区/县
            'StreetName': int(os.getenv('REGION_TYPE_STREET', '1004'))       # 街道/镇
        }
    
    def find_region_by_name(self, region_name: str, region_type: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        根据区域名称查找区域信息
        
        Args:
            region_name: 区域名称
            region_type: 区域类型（可选，用于精确匹配）
            
        Returns:
            区域信息字典，包含id, parent_id, region_name, region_type等字段
        """
        if not region_name or not region_name.strip():
            return None
        
        try:
            if region_type:
                # 优化查询：先按region_type筛选（可以利用索引），再按region_name精确匹配
                # 这样可以先利用region_type的索引缩小范围，再精确匹配region_name，提高查询效率
                sql = f"""
                    SELECT id, parent_id, region_name, region_type, alias_name
                    FROM {self.table_name}
                    WHERE region_type = %s AND region_name = %s AND is_deleted = 0
                    LIMIT 1
                """
                result = self.db.execute_one(sql, (region_type, region_name.strip()))
            else:
                # 仅匹配名称
                sql = f"""
                    SELECT id, parent_id, region_name, region_type, alias_name
                    FROM {self.table_name}
                    WHERE region_name = %s AND is_deleted = 0
                    LIMIT 1
                """
                result = self.db.execute_one(sql, (region_name.strip(),))
            
            return result
        except Exception as e:
            logger.error(f"查找区域信息失败: {str(e)}, region_name={region_name}, region_type={region_type}")
            return None
    
    def find_region_by_id(self, region_id: int) -> Optional[Dict[str, Any]]:
        """
        根据区域ID查找区域信息
        
        Args:
            region_id: 区域ID
            
        Returns:
            区域信息字典
        """
        if not region_id:
            return None
        
        try:
            sql = f"""
                SELECT id, parent_id, region_name, region_type, alias_name
                FROM {self.table_name}
                WHERE id = %s AND is_deleted = 0
                LIMIT 1
            """
            result = self.db.execute_one(sql, (region_id,))
            return result
        except Exception as e:
            logger.error(f"根据ID查找区域信息失败: {str(e)}, region_id={region_id}")
            return None
    
    def find_parent_by_type_and_id(self, parent_region_type: int, parent_id: int) -> Optional[Dict[str, Any]]:
        """
        根据父级区域类型和父级ID查找父级区域信息（优化查询）
        
        优化逻辑：
        1. 先根据region_type进行粗筛选（可以利用索引）
        2. 再根据id等于parent_id进行精确匹配
        
        这样可以先利用region_type的索引缩小范围，再精确匹配id，提高查询效率。
        
        Args:
            parent_region_type: 父级区域类型（如1001=省，1002=市，1003=区/县，1004=街道/镇）
            parent_id: 父级区域ID（即当前记录的parent_id字段值）
            
        Returns:
            父级区域信息字典
        """
        if not parent_region_type or not parent_id:
            return None
        
        try:
            # 优化查询：先按region_type筛选，再按id匹配
            # 这样可以利用region_type的索引，减少扫描记录数
            sql = f"""
                SELECT id, parent_id, region_name, region_type, alias_name
                FROM {self.table_name}
                WHERE region_type = %s AND id = %s AND is_deleted = 0
                LIMIT 1
            """
            result = self.db.execute_one(sql, (parent_region_type, parent_id))
            return result
        except Exception as e:
            logger.error(f"根据类型和ID查找父级区域失败: {str(e)}, parent_region_type={parent_region_type}, parent_id={parent_id}")
            return None
    
    def get_parent_region_type(self, current_region_type: int) -> Optional[int]:
        """
        根据当前区域类型推断父级区域类型
        
        Args:
            current_region_type: 当前区域类型
            
        Returns:
            父级区域类型，如果已经是最高级则返回None
        """
        # 根据层级关系推断父级类型
        if current_region_type == self.region_type_map.get('StreetName'):  # 街道(1004) -> 区县(1003)
            return self.region_type_map.get('ExpAreaName')
        elif current_region_type == self.region_type_map.get('ExpAreaName'):  # 区县(1003) -> 市(1002)
            return self.region_type_map.get('CityName')
        elif current_region_type == self.region_type_map.get('CityName'):  # 市(1002) -> 省(1001)
            return self.region_type_map.get('ProvinceName')
        elif current_region_type == self.region_type_map.get('ProvinceName'):  # 省(1001) -> 无父级
            return None
        else:
            # 未知类型，返回None
            return None
    
    def get_parent_chain(self, start_region: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        获取父级链，从当前区域向上查找所有父级（优化版本）
        
        优化逻辑：
        1. 先根据region_type进行粗筛选（可以利用索引）
        2. 再根据id等于parent_id进行精确匹配
        这样可以利用索引，减少扫描记录数，提高查询效率
        
        Args:
            start_region: 起始区域信息（包含id, parent_id, region_name, region_type等）
            
        Returns:
            包含所有父级信息的字典，键为区域类型名称（ProvinceName, CityName, ExpAreaName, StreetName）
            值为包含 region_name 和 alias_name 的字典
        """
        chain = {}
        current = start_region
        
        # 最多向上查找4级（街道->区县->市->省）
        max_levels = 4
        level = 0
        
        while current and level < max_levels:
            region_type = current.get('region_type')
            region_name = current.get('region_name')
            alias_name = current.get('alias_name')  # 可能是 None、空字符串或其他类型
            parent_id = current.get('parent_id')
            
            # 标准化 alias_name：处理 None、空字符串、非字符串类型等情况
            normalized_alias = ''
            if alias_name:
                try:
                    normalized_alias = str(alias_name).strip()
                except Exception:
                    normalized_alias = ''
            
            # 根据region_type确定字段名并记录完整信息（包括region_name和alias_name）
            region_info = {
                'region_name': region_name or '',
                'alias_name': normalized_alias
            }
            
            if region_type == self.region_type_map.get('StreetName'):
                chain['StreetName'] = region_info
            elif region_type == self.region_type_map.get('ExpAreaName'):
                chain['ExpAreaName'] = region_info
            elif region_type == self.region_type_map.get('CityName'):
                chain['CityName'] = region_info
            elif region_type == self.region_type_map.get('ProvinceName'):
                chain['ProvinceName'] = region_info
            
            # 如果没有父级ID，说明已经到顶了
            if not parent_id:
                break
            
            # 根据当前区域类型推断父级区域类型
            parent_region_type = self.get_parent_region_type(region_type)
            
            if not parent_region_type:
                # 无法推断父级类型，使用传统方法通过ID查找
                current = self.find_region_by_id(parent_id)
            else:
                # 使用优化的查询方法：先按region_type筛选，再按id匹配
                current = self.find_parent_by_type_and_id(parent_region_type, parent_id)
            
            level += 1
        
        return chain
    
    def _normalize_region_name(self, name: str) -> str:
        """
        标准化区域名称，用于比较
        
        Args:
            name: 区域名称（可能是字符串、None或其他类型）
            
        Returns:
            标准化后的名称（去除空格，统一格式）
        """
        if not name:
            return ""
        # 转换为字符串，处理非字符串类型（如数字）
        try:
            return str(name).strip()
        except Exception:
            return ""
    
    def _is_region_name_equal(self, name1: str, name2: str) -> bool:
        """
        比较两个区域名称是否相等（忽略空格和大小写）
        
        Args:
            name1: 第一个区域名称
            name2: 第二个区域名称
            
        Returns:
            是否相等
        """
        return self._normalize_region_name(name1) == self._normalize_region_name(name2)
    
    def _update_field_if_needed(self, result: Dict[str, Any], field_name: str, 
                                parent_chain: Dict[str, Dict[str, Any]]) -> bool:
        """
        更新字段值（如果字段为空或与数据库值不一致）
        
        替换逻辑：
        1. 如果字段为空，则补全
        2. 如果字段有值，先与 region_name 对比
        3. 如果与 region_name 不一致，再与 alias_name 对比
        4. 如果与 alias_name 一致，则保留原有值
        5. 如果与 alias_name 也不一致，则用 region_name 替换
        
        Args:
            result: 结果字典
            field_name: 字段名
            parent_chain: 父级链字典（包含从数据库查找到的值，每个值是一个包含 region_name 和 alias_name 的字典）
            
        Returns:
            是否进行了更新
        """
        if field_name not in parent_chain:
            return False
        
        region_info = parent_chain[field_name]
        db_region_name = region_info.get('region_name', '')
        db_alias_name = region_info.get('alias_name', '')
        current_value = result.get(field_name, "").strip() if result.get(field_name) else ""
        
        # 如果字段为空，则补全
        if not current_value:
            result[field_name] = db_region_name
            logger.info(f"补全{field_name}: {db_region_name}")
            return True
        
        # 如果字段有值，先与 region_name 对比
        if self._is_region_name_equal(current_value, db_region_name):
            # 与 region_name 一致，无需更新
            return False
        
        # 与 region_name 不一致，再与 alias_name 对比（如果别名存在且非空）
        if db_alias_name and db_alias_name.strip():
            if self._is_region_name_equal(current_value, db_alias_name):
                # 与 alias_name 一致，保留原有值
                logger.debug(f"保留{field_name}: '{current_value}' (与别名 '{db_alias_name}' 一致)")
                return False
        
        # 与 region_name 和 alias_name 都不一致（或别名不存在），用 region_name 替换
        old_value = current_value
        result[field_name] = db_region_name
        if db_alias_name and db_alias_name.strip():
            logger.info(f"替换{field_name}: '{old_value}' -> '{db_region_name}' (别名: '{db_alias_name}')")
        else:
            logger.info(f"替换{field_name}: '{old_value}' -> '{db_region_name}'")
        return True
    
    def complete_address(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        补全地址信息
        
        补全逻辑：
        1. 如果StreetName存在，从StreetName开始向上查找
        2. 如果StreetName为空，从ExpAreaName开始向上查找
        3. 如果ExpAreaName也为空，从CityName开始向上查找
        4. 如果CityName也为空，从ProvinceName开始向上查找
        
        验证和替换逻辑：
        - 对于每个字段，如果数据库中有值，且与现有值不一致，则使用数据库值替换
        - 如果字段为空，则补全
        
        Args:
            data: 模型返回的数据字典，包含ProvinceName, CityName, ExpAreaName, StreetName等字段
            
        Returns:
            补全后的数据字典
        """
        result = data.copy()
        
        try:
            # 确定起始查找点
            start_field = None
            start_value = None
            start_type = None
            
            # 按优先级查找起始点
            if data.get('StreetName') and data.get('StreetName').strip():
                start_field = 'StreetName'
                start_value = data.get('StreetName')
                start_type = self.region_type_map.get('StreetName')
            elif data.get('ExpAreaName') and data.get('ExpAreaName').strip():
                start_field = 'ExpAreaName'
                start_value = data.get('ExpAreaName')
                start_type = self.region_type_map.get('ExpAreaName')
            elif data.get('CityName') and data.get('CityName').strip():
                start_field = 'CityName'
                start_value = data.get('CityName')
                start_type = self.region_type_map.get('CityName')
            elif data.get('ProvinceName') and data.get('ProvinceName').strip():
                start_field = 'ProvinceName'
                start_value = data.get('ProvinceName')
                start_type = self.region_type_map.get('ProvinceName')
            
            if not start_value:
                logger.warning("地址数据中没有任何可用的区域信息，无法进行补全")
                return result
            
            # 查找起始区域
            start_region = self.find_region_by_name(start_value, start_type)
            
            if not start_region:
                logger.warning(f"未在数据库中找到匹配的区域: {start_field}={start_value}")
                return result
            
            # 获取父级链
            parent_chain = self.get_parent_chain(start_region)
            
            # 补全和验证替换字段（按从高到低的层级顺序）
            # 这样如果上级字段被替换，下级字段也会基于正确的上级进行验证
            self._update_field_if_needed(result, 'ProvinceName', parent_chain)
            self._update_field_if_needed(result, 'CityName', parent_chain)
            self._update_field_if_needed(result, 'ExpAreaName', parent_chain)
            self._update_field_if_needed(result, 'StreetName', parent_chain)
            
        except Exception as e:
            logger.error(f"地址补全失败: {str(e)}")
            # 发生错误时返回原始数据，不中断流程
        
        return result
    
    def complete_extract_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        补全ExtractResponse格式的响应数据
        
        Args:
            response: ExtractResponse格式的响应字典，包含Data字段
            
        Returns:
            补全后的响应字典
        """
        if not response.get('Data'):
            return response
        
        # 补全Data字段中的地址信息
        completed_data = self.complete_address(response['Data'])
        
        # 创建新的响应对象
        result = response.copy()
        result['Data'] = completed_data
        
        return result

