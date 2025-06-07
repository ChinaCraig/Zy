# Config package initialization
from . import database
from .database import DatabaseManager, init_db_manager

def get_db_manager():
    """获取数据库管理器实例"""
    return database.db_manager

__all__ = ['DatabaseManager', 'init_db_manager', 'get_db_manager'] 