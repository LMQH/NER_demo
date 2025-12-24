"""
MySQL数据库连接模块
支持通过环境变量配置数据库连接
"""
import os
import logging
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import pymysql
from pymysql.cursors import DictCursor

logger = logging.getLogger("NER_API")


class DatabaseConnection:
    """MySQL数据库连接管理器"""
    
    def __init__(self):
        """初始化数据库连接配置"""
        self.host = os.getenv('MYSQL_HOST', 'localhost')
        self.port = int(os.getenv('MYSQL_PORT', '3306'))
        self.user = os.getenv('MYSQL_USER', 'root')
        self.password = os.getenv('MYSQL_PASSWORD', '')
        self.database = os.getenv('MYSQL_DATABASE', '')
        self.charset = os.getenv('MYSQL_CHARSET', 'utf8mb4')
        
        # 连接池配置
        self.max_connections = int(os.getenv('MYSQL_MAX_CONNECTIONS', '10'))
        self.connect_timeout = int(os.getenv('MYSQL_CONNECT_TIMEOUT', '10'))
        
        # 验证必要配置
        if not self.database:
            logger.warning("MYSQL_DATABASE未配置，数据库功能可能无法使用")
    
    def get_connection(self):
        """
        获取数据库连接
        
        Returns:
            pymysql.Connection: 数据库连接对象
            
        Raises:
            Exception: 连接失败时抛出异常
        """
        try:
            connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset=self.charset,
                connect_timeout=self.connect_timeout,
                cursorclass=DictCursor,
                autocommit=False
            )
            return connection
        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}")
            raise
    
    @contextmanager
    def get_cursor(self):
        """
        获取数据库游标的上下文管理器
        
        Usage:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT * FROM table")
                results = cursor.fetchall()
        """
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            yield cursor
            connection.commit()
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"数据库操作失败: {str(e)}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def execute_query(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        执行查询语句
        
        Args:
            sql: SQL查询语句
            params: 查询参数（可选）
            
        Returns:
            查询结果列表（字典格式）
        """
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    
    def execute_one(self, sql: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """
        执行查询语句，返回单条记录
        
        Args:
            sql: SQL查询语句
            params: 查询参数（可选）
            
        Returns:
            查询结果（字典格式），如果没有结果则返回None
        """
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()
    
    def test_connection(self) -> bool:
        """
        测试数据库连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"数据库连接测试失败: {str(e)}")
            return False

