"""
聊天数据模型
Chat Data Models
"""

import uuid
from datetime import datetime
from typing import List, Dict, Optional
import app.config
import logging

def get_db_manager():
    """安全地获取数据库管理器"""
    from app.config import get_db_manager as _get_db_manager
    return _get_db_manager()

class ChatSession:
    """聊天会话模型"""
    
    def __init__(self, user_identity: str, ai_provider: str, ai_model: str, 
                 browser_info: str = None, ip_address: str = None, location_info: str = None):
        self.session_id = str(uuid.uuid4())
        self.user_identity = user_identity
        self.browser_info = browser_info
        self.ip_address = ip_address
        self.location_info = location_info
        self.session_start_time = datetime.now()
        self.session_end_time = None
        self.total_messages = 0
        self.ai_provider = ai_provider
        self.ai_model = ai_model
        self.session_status = 'active'
        self.end_reason = None
        self.logger = logging.getLogger(__name__)
    
    def save_to_database(self) -> bool:
        """保存会话到数据库"""
        try:
            sql = """
            INSERT INTO chat_sessions (
                session_id, user_identity, browser_info, ip_address, location_info,
                session_start_time, total_messages, ai_provider, ai_model, session_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                self.session_id,
                self.user_identity,
                self.browser_info,
                self.ip_address,
                self.location_info,
                self.session_start_time,
                self.total_messages,
                self.ai_provider,
                self.ai_model,
                self.session_status
            )
            
            db_mgr = get_db_manager()
            if not db_mgr:
                self.logger.warning("数据库管理器未初始化，跳过保存")
                return False
                
            result = db_mgr.execute_insert(sql, params)
            if result:
                self.logger.info(f"会话已保存到数据库: {self.session_id}")
                return True
            else:
                self.logger.error(f"保存会话失败: {self.session_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"保存会话到数据库失败: {e}")
            return False
    
    def end_session(self, end_reason: str) -> bool:
        """结束会话"""
        try:
            self.session_end_time = datetime.now()
            self.session_status = 'ended'
            self.end_reason = end_reason
            
            sql = """
            UPDATE chat_sessions 
            SET session_end_time = %s, session_status = %s, 
                end_reason = %s, total_messages = %s
            WHERE session_id = %s
            """
            params = (
                self.session_end_time,
                self.session_status,
                self.end_reason,
                self.total_messages,
                self.session_id
            )
            
            db_mgr = get_db_manager()
            if not db_mgr:
                self.logger.warning("数据库管理器未初始化，跳过更新")
                return False
                
            result = db_mgr.execute_update(sql, params)
            if result > 0:
                self.logger.info(f"会话已结束: {self.session_id}, 原因: {end_reason}")
                return True
            else:
                self.logger.error(f"结束会话失败: {self.session_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"结束会话失败: {e}")
            return False
    
    def update_message_count(self, count: int) -> bool:
        """更新消息计数"""
        try:
            self.total_messages = count
            
            sql = "UPDATE chat_sessions SET total_messages = %s WHERE session_id = %s"
            params = (count, self.session_id)
            
            db_mgr = get_db_manager()
            if not db_mgr:
                self.logger.warning("数据库管理器未初始化，跳过更新")
                return False
                
            result = db_mgr.execute_update(sql, params)
            return result > 0
            
        except Exception as e:
            self.logger.error(f"更新消息计数失败: {e}")
            return False
    
    @classmethod
    def get_by_session_id(cls, session_id: str) -> Optional['ChatSession']:
        """根据会话ID获取会话"""
        try:
            sql = """
            SELECT * FROM chat_sessions WHERE session_id = %s
            """
            db_mgr = get_db_manager()
            if not db_mgr:
                logging.getLogger(__name__).warning("数据库管理器未初始化")
                return None
                
            result = db_mgr.execute_query(sql, (session_id,), fetch_one=True)
            
            if result:
                session = cls.__new__(cls)
                session.session_id = result['session_id']
                session.user_identity = result['user_identity']
                session.browser_info = result.get('browser_info')
                session.ip_address = result.get('ip_address')
                session.location_info = result.get('location_info')
                session.session_start_time = result['session_start_time']
                session.session_end_time = result['session_end_time']
                session.total_messages = result['total_messages']
                session.ai_provider = result['ai_provider']
                session.ai_model = result['ai_model']
                session.session_status = result['session_status']
                session.end_reason = result['end_reason']
                session.logger = logging.getLogger(__name__)
                return session
            
            return None
            
        except Exception as e:
            logging.getLogger(__name__).error(f"获取会话失败: {e}")
            return None

class ChatMessage:
    """聊天消息模型"""
    
    def __init__(self, session_id: str, message_order: int, sender_type: str, 
                 sender_name: str, message_content: str, ai_provider: str = None, 
                 ai_model: str = None, response_time_ms: int = None):
        self.session_id = session_id
        self.message_order = message_order
        self.sender_type = sender_type  # 'user' or 'ai'
        self.sender_name = sender_name
        self.message_content = message_content
        self.message_time = datetime.now()
        self.ai_provider = ai_provider
        self.ai_model = ai_model
        self.response_time_ms = response_time_ms
        self.message_tokens = None
        self.logger = logging.getLogger(__name__)
    
    def save_to_database(self) -> bool:
        """保存消息到数据库"""
        try:
            sql = """
            INSERT INTO chat_messages (
                session_id, message_order, sender_type, sender_name,
                message_content, message_time, ai_provider, ai_model,
                response_time_ms, message_tokens
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                self.session_id,
                self.message_order,
                self.sender_type,
                self.sender_name,
                self.message_content,
                self.message_time,
                self.ai_provider,
                self.ai_model,
                self.response_time_ms,
                self.message_tokens
            )
            
            db_mgr = get_db_manager()
            if not db_mgr:
                self.logger.warning("数据库管理器未初始化，跳过保存")
                return False
                
            result = db_mgr.execute_insert(sql, params)
            if result:
                self.logger.debug(f"消息已保存到数据库: {self.session_id}-{self.message_order}")
                return True
            else:
                self.logger.error(f"保存消息失败: {self.session_id}-{self.message_order}")
                return False
                
        except Exception as e:
            self.logger.error(f"保存消息到数据库失败: {e}")
            return False
    
    @classmethod
    def get_session_messages(cls, session_id: str) -> List['ChatMessage']:
        """获取会话的所有消息"""
        try:
            sql = """
            SELECT * FROM chat_messages 
            WHERE session_id = %s 
            ORDER BY message_order
            """
            db_mgr = get_db_manager()
            if not db_mgr:
                logging.getLogger(__name__).warning("数据库管理器未初始化")
                return []
                
            results = db_mgr.execute_query(sql, (session_id,))
            
            messages = []
            if results:
                for result in results:
                    message = cls.__new__(cls)
                    message.session_id = result['session_id']
                    message.message_order = result['message_order']
                    message.sender_type = result['sender_type']
                    message.sender_name = result['sender_name']
                    message.message_content = result['message_content']
                    message.message_time = result['message_time']
                    message.ai_provider = result['ai_provider']
                    message.ai_model = result['ai_model']
                    message.response_time_ms = result['response_time_ms']
                    message.message_tokens = result['message_tokens']
                    message.logger = logging.getLogger(__name__)
                    messages.append(message)
            
            return messages
            
        except Exception as e:
            logging.getLogger(__name__).error(f"获取会话消息失败: {e}")
            return []

class ChatArchiveService:
    """聊天归档服务"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def archive_chat_session(self, conversation_history: List[Dict], 
                           user_identity: str, ai_provider: str, ai_model: str,
                           end_reason: str = 'manual', browser_info: str = None, 
                           ip_address: str = None, location_info: str = None) -> bool:
        """归档聊天会话"""
        if not conversation_history:
            self.logger.info("没有聊天记录需要归档")
            return True
        
        try:
            # 创建会话记录
            session = ChatSession(user_identity, ai_provider, ai_model, browser_info, ip_address, location_info)
            session.total_messages = len(conversation_history)
            
            # 检查数据库管理器是否可用
            db_mgr = get_db_manager()
            if not db_mgr:
                self.logger.warning("数据库管理器未初始化，无法归档聊天记录")
                return False
            
            # 保存会话到数据库
            if not session.save_to_database():
                self.logger.error("保存会话失败，停止归档")
                return False
            
            # 保存所有消息
            failed_messages = 0
            for i, msg in enumerate(conversation_history, 1):
                # 转换sender_type：assistant -> ai
                sender_type = 'ai' if msg['role'] == 'assistant' else msg['role']
                
                message = ChatMessage(
                    session_id=session.session_id,
                    message_order=i,
                    sender_type=sender_type,
                    sender_name=user_identity if msg['role'] == 'user' else ai_model,
                    message_content=msg['content'],
                    ai_provider=ai_provider if msg['role'] == 'assistant' else None,
                    ai_model=ai_model if msg['role'] == 'assistant' else None
                )
                
                if not message.save_to_database():
                    self.logger.error(f"保存消息失败: {i}")
                    failed_messages += 1
            
            # 结束会话
            if not session.end_session(end_reason):
                self.logger.warning("会话结束标记失败")
            
            # 记录归档结果
            if failed_messages > 0:
                self.logger.warning(f"聊天会话部分归档完成: {session.session_id}, 总消息数: {len(conversation_history)}, 失败消息数: {failed_messages}")
            else:
                self.logger.info(f"聊天会话已成功归档: {session.session_id}, 消息数: {len(conversation_history)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"归档聊天会话失败: {e}")
            return False
    
    def get_user_chat_history(self, user_identity: str, limit: int = 10) -> List[Dict]:
        """获取用户的聊天历史"""
        try:
            sql = """
            SELECT session_id, session_start_time, session_end_time, 
                   total_messages, session_status, end_reason,
                   browser_info, ip_address, location_info
            FROM chat_sessions 
            WHERE user_identity = %s 
            ORDER BY session_start_time DESC 
            LIMIT %s
            """
            db_mgr = get_db_manager()
            if not db_mgr:
                self.logger.warning("数据库管理器未初始化")
                return []
                
            results = db_mgr.execute_query(sql, (user_identity, limit))
            
            history = []
            if results:
                for result in results:
                    history.append({
                        'session_id': result['session_id'],
                        'start_time': result['session_start_time'].isoformat() if result['session_start_time'] else None,
                        'end_time': result['session_end_time'].isoformat() if result['session_end_time'] else None,
                        'total_messages': result['total_messages'],
                        'status': result['session_status'],
                        'end_reason': result['end_reason'],
                        'browser_info': result.get('browser_info'),
                        'ip_address': result.get('ip_address'),
                        'location_info': result.get('location_info')
                    })
            
            return history
            
        except Exception as e:
            self.logger.error(f"获取用户聊天历史失败: {e}")
            return []
    
    def get_session_detail(self, session_id: str) -> Dict:
        """获取会话详情"""
        try:
            # 获取会话信息
            session = ChatSession.get_by_session_id(session_id)
            if not session:
                return {}
            
            # 获取消息列表
            messages = ChatMessage.get_session_messages(session_id)
            
            return {
                'session_info': {
                    'session_id': session.session_id,
                    'user_identity': session.user_identity,
                    'browser_info': session.browser_info,
                    'ip_address': session.ip_address,
                    'location_info': session.location_info,
                    'start_time': session.session_start_time.isoformat() if session.session_start_time else None,
                    'end_time': session.session_end_time.isoformat() if session.session_end_time else None,
                    'total_messages': session.total_messages,
                    'ai_provider': session.ai_provider,
                    'ai_model': session.ai_model,
                    'status': session.session_status,
                    'end_reason': session.end_reason
                },
                'messages': [
                    {
                        'order': msg.message_order,
                        'sender_type': msg.sender_type,
                        'sender_name': msg.sender_name,
                        'content': msg.message_content,
                        'time': msg.message_time.isoformat() if msg.message_time else None,
                        'response_time_ms': msg.response_time_ms
                    }
                    for msg in messages
                ]
            }
            
        except Exception as e:
            self.logger.error(f"获取会话详情失败: {e}")
            return {}

# 全局聊天归档服务实例
chat_archive_service = ChatArchiveService() 