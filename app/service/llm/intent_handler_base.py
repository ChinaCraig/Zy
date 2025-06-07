"""
意图处理器基类
所有具体的意图处理器都应该继承这个基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from .intent_detection_service import Intent


class IntentHandlerBase(ABC):
    """意图处理器基类"""
    
    def __init__(self):
        """初始化处理器"""
        self.name = self.__class__.__name__
        
    @abstractmethod
    async def handle(self, intent: Intent, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        处理意图
        
        Args:
            intent: 识别出的意图对象
            message: 用户原始消息
            context: 上下文信息
            
        Returns:
            处理结果字典，应包含:
            - success: bool 是否成功
            - response: str 响应内容
            - data: Any 额外数据（可选）
            - need_continue: bool 是否需要继续处理其他意图
        """
        pass
    
    @abstractmethod
    def can_handle(self, intent: Intent) -> bool:
        """
        判断是否可以处理该意图
        
        Args:
            intent: 意图对象
            
        Returns:
            是否可以处理
        """
        pass
    
    def preprocess(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        预处理（可选覆盖）
        
        Args:
            message: 用户消息
            context: 上下文
            
        Returns:
            预处理结果
        """
        return {"message": message, "context": context}
    
    def postprocess(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        后处理（可选覆盖）
        
        Args:
            result: 处理结果
            
        Returns:
            后处理结果
        """
        return result
    
    async def execute(self, intent: Intent, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        执行完整的处理流程
        
        Args:
            intent: 意图对象
            message: 用户消息
            context: 上下文
            
        Returns:
            最终处理结果
        """
        try:
            # 预处理
            preprocessed = self.preprocess(message, context)
            
            # 主处理
            result = await self.handle(
                intent, 
                preprocessed["message"], 
                preprocessed.get("context")
            )
            
            # 后处理
            final_result = self.postprocess(result)
            
            return final_result
            
        except Exception as e:
            return {
                "success": False,
                "response": f"处理意图时发生错误: {str(e)}",
                "error": str(e),
                "need_continue": False
            }
    
    def __repr__(self):
        return f"<{self.name}>" 