"""
数据库连接管理模块
Database Connection Management Module
"""

import pymysql
import logging
import time
from contextlib import contextmanager

class DatabaseManager:
    """数据库连接管理器"""
    
    def __init__(self, config_obj=None):
        self.config = config_obj
        self.pool = None
        self.logger = logging.getLogger(__name__)
        if self.config:
            self._init_connection_pool()
    
    def _init_connection_pool(self):
        """初始化数据库连接池"""
        if not self.config.enable_database_storage:
            self.logger.info("数据库存储功能已禁用")
            return
            
        try:
            # 创建连接池配置
            pool_config = {
                'host': self.config.db_host,
                'port': self.config.db_port,
                'user': self.config.db_username,
                'password': self.config.db_password,
                'database': self.config.db_name,
                'charset': self.config.db_charset,
                'autocommit': True,
                'maxconnections': self.config.db_pool_size,
                'mincached': 1,
                'maxcached': 5,
                'maxshared': 3,
                'blocking': True,
                'maxusage': None,
                'setsession': [],
                'ping': 0
            }
            
            # 使用DBUtils创建连接池（如果可用）
            try:
                from dbutils.pooled_db import PooledDB
                self.pool = PooledDB(pymysql, **pool_config)
                self.logger.info("数据库连接池初始化成功 (DBUtils)")
            except ImportError:
                # 如果DBUtils不可用，使用简单的连接管理
                self.pool = None
                self.logger.warning("DBUtils未安装，使用简单连接管理")
                
        except Exception as e:
            self.logger.error(f"数据库连接池初始化失败: {e}")
            self.pool = None
    
    def _create_simple_connection(self):
        """创建简单的数据库连接"""
        return pymysql.connect(
            host=self.config.db_host,
            port=self.config.db_port,
            user=self.config.db_username,
            password=self.config.db_password,
            database=self.config.db_name,
            charset=self.config.db_charset,
            autocommit=True
        )
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接上下文管理器"""
        if not self.config.enable_database_storage:
            yield None
            return
            
        connection = None
        try:
            if self.pool:
                connection = self.pool.connection()
            else:
                connection = self._create_simple_connection()
            
            yield connection
            
        except Exception as e:
            self.logger.error(f"数据库连接错误: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()
    
    def execute_query(self, sql, params=None, fetch_one=False, fetch_all=True):
        """执行查询语句"""
        if not self.config.enable_database_storage:
            return None
            
        try:
            with self.get_connection() as conn:
                if not conn:
                    return None
                    
                with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute(sql, params or ())
                    
                    if fetch_one:
                        return cursor.fetchone()
                    elif fetch_all:
                        return cursor.fetchall()
                    else:
                        return cursor.rowcount
                        
        except Exception as e:
            self.logger.error(f"执行查询失败: {sql}, 参数: {params}, 错误: {e}")
            return None
    
    def execute_insert(self, sql, params=None):
        """执行插入语句并返回插入ID"""
        if not self.config.enable_database_storage:
            return None
            
        try:
            with self.get_connection() as conn:
                if not conn:
                    return None
                    
                with conn.cursor() as cursor:
                    cursor.execute(sql, params or ())
                    return cursor.lastrowid
                    
        except Exception as e:
            self.logger.error(f"执行插入失败: {sql}, 参数: {params}, 错误: {e}")
            return None
    
    def execute_update(self, sql, params=None):
        """执行更新语句并返回影响行数"""
        if not self.config.enable_database_storage:
            return 0
            
        try:
            with self.get_connection() as conn:
                if not conn:
                    return 0
                    
                with conn.cursor() as cursor:
                    return cursor.execute(sql, params or ())
                    
        except Exception as e:
            self.logger.error(f"执行更新失败: {sql}, 参数: {params}, 错误: {e}")
            return 0
    
    def test_connection(self):
        """测试数据库连接"""
        if not self.config.enable_database_storage:
            return False, "数据库存储功能已禁用"
            
        try:
            with self.get_connection() as conn:
                if not conn:
                    return False, "无法建立数据库连接"
                    
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    
                    if result:
                        return True, "数据库连接正常"
                    else:
                        return False, "数据库查询失败"
                        
        except Exception as e:
            return False, f"数据库连接测试失败: {e}"

# 全局数据库管理器实例（延迟初始化）
db_manager = None

def init_db_manager(config_obj):
    """初始化数据库管理器"""
    global db_manager
    db_manager = DatabaseManager(config_obj) 