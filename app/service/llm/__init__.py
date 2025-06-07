"""
LLM服务包
包含意图识别和处理相关功能
"""
from .llm_service import LLMService
from .intent_detection_service import IntentDetectionService, IntentType, Intent, intent_detector
from .intent_handler_manager import IntentHandlerManager, intent_handler_manager
from .intent_sync_adapter import IntentSyncAdapter, intent_sync_adapter
from .intent_handler_base import IntentHandlerBase

# 导出各个处理器（便于扩展）
from .chat_handler import ChatHandler
from .kb_search_handler import KBSearchHandler
from .vector_search_handler import VectorSearchHandler
from .mcp_call_handler import MCPCallHandler
from .virtual_human_handler import VirtualHumanHandler

__all__ = [
    # 核心服务
    'LLMService',
    
    # 意图识别
    'IntentDetectionService',
    'IntentType',
    'Intent',
    'intent_detector',
    
    # 意图处理管理
    'IntentHandlerManager',
    'intent_handler_manager',
    
    # 同步适配器
    'IntentSyncAdapter',
    'intent_sync_adapter',
    
    # 基类
    'IntentHandlerBase',
    
    # 具体处理器
    'ChatHandler',
    'KBSearchHandler',
    'VectorSearchHandler',
    'MCPCallHandler',
    'VirtualHumanHandler',
] 