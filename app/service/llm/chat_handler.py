"""
普通聊天意图处理器
处理普通的对话交互
"""
from typing import Dict, Any, Optional
from .intent_handler_base import IntentHandlerBase
from .intent_detection_service import Intent, IntentType


class ChatHandler(IntentHandlerBase):
    """普通聊天处理器"""
    
    def __init__(self):
        super().__init__()
        # 这里可以初始化需要的AI模型或服务
        
    def can_handle(self, intent: Intent) -> bool:
        """判断是否可以处理该意图"""
        return intent.type == IntentType.CHAT
    
    async def handle(self, intent: Intent, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        处理普通聊天意图
        
        Args:
            intent: 意图对象
            message: 用户消息
            context: 上下文信息
            
        Returns:
            处理结果
        """
        try:
            # TODO: 这里调用实际的AI对话服务
            # 暂时返回模拟响应
            
            # 从上下文获取AI管理器（如果有）
            ai_manager = context.get("ai_manager") if context else None
            
            if ai_manager:
                # 使用现有的AI管理器进行对话
                response = ai_manager.get_response_sync(message)
            else:
                # 返回默认响应
                response = f"收到您的消息：'{message}'。这是普通聊天的响应。"
            
            return {
                "success": True,
                "response": response,
                "data": {
                    "intent_type": "chat",
                    "confidence": intent.confidence
                },
                "need_continue": False  # 普通聊天通常不需要继续处理其他意图
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": f"聊天处理失败：{str(e)}",
                "error": str(e),
                "need_continue": False
            }
    
    def preprocess(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """预处理消息"""
        # 可以在这里进行消息清理、过滤等操作
        processed_message = message.strip()
        
        return {
            "message": processed_message,
            "context": context
        } 